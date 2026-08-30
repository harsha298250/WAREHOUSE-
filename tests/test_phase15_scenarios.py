import pytest
import time
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import get_db
from backend.models import Base, Warehouse, Scenario, Experiment, ExperimentRun, Robot, Task, AuditLedger
from backend.services.ai_service import (
    create_scenario, run_scenario_experiment, get_scenario_result,
    compare_scenarios, compare_scenario_with_baseline
)
from backend.experiment_runner import execute_single_repetition

@pytest.fixture(scope="module")
def temp_db_engine():
    # Setup in-memory sqlite engine for fast local tests
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return engine

@pytest.fixture
def db_session(temp_db_engine):
    Session = sessionmaker(bind=temp_db_engine)
    session = Session()
    
    # Seed minimal baseline data
    wh = Warehouse(id="WH-TEST-P15", name="P15 Test Wh", location="Lab")
    session.add(wh)
    
    # Add active robot
    session.add(Robot(
        robot_code="ROB-T1", name="Test Bot", warehouse_id="WH-TEST-P15",
        status="AVAILABLE", battery_level=90.0, max_speed=1.5,
        current_x=1.0, current_y=1.0
    ))
    
    # Add Item
    from backend.models import Item, WarehouseLocation, WarehouseGridCell
    item = Item(id=1, name="Test Item", sku="SKU-TEST-P15", unit_cost=10.0, safety_stock=5, reorder_threshold=2)
    session.add(item)
    
    # Add Locations
    session.add(WarehouseLocation(
        id="L-01", warehouse_id="WH-TEST-P15", x=1.0, y=2.0, location_type="STORAGE",
        zone="A", aisle=1, rack="R1", shelf="S1"
    ))
    session.add(WarehouseLocation(
        id="L-02", warehouse_id="WH-TEST-P15", x=2.0, y=2.0, location_type="PACKING",
        zone="B", aisle=2, rack="R1", shelf="S1"
    ))
    
    # Add Grid Cell
    session.add(WarehouseGridCell(warehouse_id="WH-TEST-P15", x=1, y=1, traversable=True, cost=1.0, cell_type="FLOOR"))
    session.add(WarehouseGridCell(warehouse_id="WH-TEST-P15", x=1, y=2, traversable=True, cost=1.0, cell_type="FLOOR"))
    session.add(WarehouseGridCell(warehouse_id="WH-TEST-P15", x=2, y=2, traversable=True, cost=1.0, cell_type="FLOOR"))
    
    session.commit()
    
    yield session
    
    # Cleanup session
    session.query(AuditLedger).delete()
    session.query(ExperimentRun).delete()
    session.query(Experiment).delete()
    session.query(Scenario).delete()
    session.query(Robot).delete()
    session.query(WarehouseLocation).delete()
    session.query(WarehouseGridCell).delete()
    session.query(Item).delete()
    session.query(Warehouse).delete()
    session.commit()
    session.close()

def test_scenario_creation_ai(db_session):
    # Enforces role permissions (auditor/viewer cannot create scenarios)
    with pytest.raises(Exception):
        create_scenario(db_session, "viewer", "AI Fail Test", "WH-TEST-P15", "desc", 4, 10, 30)

    res = create_scenario(db_session, "admin", "AI custom fleet test", "WH-TEST-P15", "testing", 5, 8, 40)
    assert res["status"] == "success"
    assert res["name"] == "AI custom fleet test"
    
    # Verify DB entry exists
    scen = db_session.query(Scenario).filter(Scenario.id == res["scenario_id"]).first()
    assert scen is not None
    assert scen.configuration["robots"]["robot_count"] == 5

def test_run_scenario_experiment_ai(db_session):
    # Setup scenario first
    res_scen = create_scenario(db_session, "admin", "Target Scen", "WH-TEST-P15", "desc", 3, 5, 50)
    scen_id = res_scen["scenario_id"]
    
    res = run_scenario_experiment(db_session, "manager", scenario_id=scen_id, repetitions=2)
    assert res["status"] == "QUEUED"
    
    exp = db_session.query(Experiment).filter(Experiment.id == res["experiment_id"]).first()
    assert exp is not None
    assert exp.repetitions == 2

def test_get_scenario_result_ai(db_session):
    res_scen = create_scenario(db_session, "admin", "Outcome Scen", "WH-TEST-P15", "desc", 2, 4, 60)
    exp = Experiment(
        scenario_id=res_scen["scenario_id"],
        experiment_name="Mock Outcome",
        status="COMPLETED",
        algorithm_name="A_STAR_CONGESTION_AWARE",
        configuration={},
        metrics_summary={"orders_completed": {"mean": 10.0, "median": 10.0, "min": 10, "max": 10, "stddev": 0.0}}
    )
    db_session.add(exp)
    db_session.commit()
    
    res = get_scenario_result(db_session, "viewer", exp.id)
    assert res["status"] == "COMPLETED"
    assert res["metrics_summary"]["orders_completed"]["mean"] == 10.0

def test_compare_scenarios_ai(db_session):
    res_scen = create_scenario(db_session, "admin", "Compare Scen", "WH-TEST-P15", "desc", 2, 4, 60)
    
    exp_a = Experiment(
        scenario_id=res_scen["scenario_id"],
        experiment_name="Mock A",
        status="COMPLETED",
        algorithm_name="A_STAR_BASELINE",
        configuration={},
        metrics_summary={"orders_completed": {"mean": 10.0}}
    )
    exp_b = Experiment(
        scenario_id=res_scen["scenario_id"],
        experiment_name="Mock B",
        status="COMPLETED",
        algorithm_name="A_STAR_CONGESTION_AWARE",
        configuration={},
        metrics_summary={"orders_completed": {"mean": 12.0}}
    )
    db_session.add(exp_a)
    db_session.add(exp_b)
    db_session.commit()
    
    res = compare_scenarios(db_session, "admin", exp_a.id, exp_b.id)
    assert res["comparison"]["orders_completed"]["difference"] == 2.0
    assert res["comparison"]["orders_completed"]["percent_difference"] == 20.0

def test_database_non_mutation_safety(db_session):
    """Asserts that running a scenario repetition does not mutate live PostgreSQL state."""
    # Capture state before
    before_robots = db_session.query(Robot).filter(Robot.warehouse_id == "WH-TEST-P15").all()
    before_robot_statuses = {r.robot_code: r.status for r in before_robots}
    
    # Configure mock scenario
    config = {
        "demand": {"order_volume": 2, "order_arrival_rate": 50},
        "robots": {"robot_count": 2, "initial_battery_pct": 100.0, "robot_speed": 1.0},
        "failures": {"enabled": False, "failure_tick": 100},
        "simulation": {"duration_ticks": 50},
        "inventory": {"initial_stock_units": 100, "reorder_threshold_units": 20},
        "warehouse": {"blocked_cells": []}
    }
    
    # Run repetition inside isolated sqlite
    res = execute_single_repetition(
        prod_db_session=db_session,
        warehouse_id="WH-TEST-P15",
        scenario_type="HIGH_DEMAND",
        config=config,
        algorithm_name="CURRENT_HEURISTIC",
        seed=100
    )
    
    assert res["status"] == "COMPLETED"
    
    # Capture state after
    after_robots = db_session.query(Robot).filter(Robot.warehouse_id == "WH-TEST-P15").all()
    after_robot_statuses = {r.robot_code: r.status for r in after_robots}
    
    # Verify live robot states remained untouched
    assert before_robot_statuses == after_robot_statuses
