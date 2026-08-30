import pytest
import os
import json
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.models import Base, User, Scenario, Experiment, ExperimentRun, Warehouse, Item, Inventory, WarehouseGridCell, Robot, Order, Task
from backend.experiment_runner import execute_single_repetition

# In-memory SQLite for unit tests database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(name="db_session")
def fixture_db_session():
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Seed dummy data
    wh = Warehouse(id="WH-TEST-01", name="Test Warehouse", location="Test Zone")
    db.add(wh)
    
    item = Item(id="ITM-SIM-01", name="Simulated GPU", sku="SKU-SIM-GPU", unit_cost=500.0, reorder_threshold=10)
    db.add(item)
    db.commit()
    
    yield db
    
    db.close()
    Base.metadata.drop_all(bind=engine)


def test_scenario_creation_and_duplication(db_session):
    # 1. Creation
    scen = Scenario(
        name="High Demand Festival Surge",
        description="Stress testing inventory under high volume",
        warehouse_id="WH-TEST-01",
        scenario_type="HIGH_DEMAND",
        configuration={
            "demand": {"order_volume": 10, "order_arrival_rate": 30},
            "robots": {"robot_count": 4, "initial_battery_pct": 100.0, "robot_speed": 1.2},
            "failures": {"enabled": False, "failure_tick": 100},
            "simulation": {"duration_ticks": 400},
            "inventory": {"initial_stock_units": 100, "reorder_threshold_units": 15},
            "warehouse": {"blocked_cells": []}
        },
        random_seed=1234,
        created_by="manager_user"
    )
    db_session.add(scen)
    db_session.commit()
    
    assert scen.id is not None
    assert scen.scenario_type == "HIGH_DEMAND"
    assert scen.configuration["robots"]["robot_count"] == 4
    
    # 2. Duplication
    dup = Scenario(
        name=f"Copy of {scen.name}",
        description=scen.description,
        warehouse_id=scen.warehouse_id,
        scenario_type=scen.scenario_type,
        configuration=scen.configuration,
        random_seed=scen.random_seed,
        status="ACTIVE",
        tags=scen.tags,
        notes=scen.notes,
        created_by="admin_user"
    )
    db_session.add(dup)
    db_session.commit()
    
    assert dup.id is not None
    assert dup.id != scen.id
    assert dup.name == "Copy of High Demand Festival Surge"
    assert dup.random_seed == 1234


def test_experiment_runs_isolation_and_reproducibility(db_session):
    # Seed layout details to support pathfinding
    # A simplified traversable grid cells
    for x in range(5):
        for y in range(5):
            db_session.add(WarehouseGridCellMirror(db_session, x, y))
    
    db_session.commit()

    config = {
        "demand": {"order_volume": 2, "order_arrival_rate": 20},
        "robots": {"robot_count": 2, "initial_battery_pct": 100.0, "robot_speed": 1.0},
        "failures": {"enabled": False, "failure_tick": 100},
        "simulation": {"duration_ticks": 100},
        "inventory": {"initial_stock_units": 50, "reorder_threshold_units": 10},
        "warehouse": {"blocked_cells": []}
    }

    # Run execution run A
    run_a = execute_single_repetition(
        prod_db_session=db_session,
        warehouse_id="WH-TEST-01",
        scenario_type="CUSTOM",
        config=config,
        algorithm_name="CURRENT_HEURISTIC",
        seed=999
    )

    # Run execution run B (identical parameters and seed)
    run_b = execute_single_repetition(
        prod_db_session=db_session,
        warehouse_id="WH-TEST-01",
        scenario_type="CUSTOM",
        config=config,
        algorithm_name="CURRENT_HEURISTIC",
        seed=999
    )

    # Assert completed status
    assert run_a["status"] == "COMPLETED"
    assert run_b["status"] == "COMPLETED"

    # Assert exact seed reproducibility (reproducible seed produces identical metrics)
    metrics_a = run_a["metrics"]
    metrics_b = run_b["metrics"]
    
    assert metrics_a["orders_completed"] == metrics_b["orders_completed"]
    assert metrics_a["tasks_created"] == metrics_b["tasks_created"]
    assert metrics_a["avg_robot_utilization"] == metrics_b["avg_robot_utilization"]

    # Assert database isolation: primary database sessions should NOT contain simulation entries
    # Verify no mock robots (ROB-S1, etc.) or mock orders are created in production DB
    robots_in_prod = db_session.query(Robot).filter(Robot.robot_code.like("ROB-S%")).all()
    assert len(robots_in_prod) == 0

    orders_in_prod = db_session.query(Order).filter(Order.id.like("ORD-S%")).all()
    assert len(orders_in_prod) == 0


def test_failure_injection_behavior(db_session):
    # Verify that failure enabled configuration injects a failure
    # Seed grid
    for x in range(3):
        for y in range(3):
            db_session.add(WarehouseGridCellMirror(db_session, x, y))
    db_session.commit()

    config = {
        "demand": {"order_volume": 1, "order_arrival_rate": 50},
        "robots": {"robot_count": 2, "initial_battery_pct": 100.0, "robot_speed": 1.0},
        "failures": {"enabled": True, "failure_tick": 10},
        "simulation": {"duration_ticks": 20},
        "inventory": {"initial_stock_units": 50, "reorder_threshold_units": 10},
        "warehouse": {"blocked_cells": []}
    }

    run = execute_single_repetition(
        prod_db_session=db_session,
        warehouse_id="WH-TEST-01",
        scenario_type="ROBOT_FAILURE",
        config=config,
        algorithm_name="CURRENT_HEURISTIC",
        seed=888
    )

    assert run["status"] == "COMPLETED"


# Helper function to generate cell mirrors dynamically
def WarehouseGridCellMirror(db, x, y):
    return WarehouseGridCell(
        warehouse_id="WH-TEST-01",
        x=x,
        y=y,
        traversable=True,
        cost=1.0,
        cell_type="FLOOR"
    )
