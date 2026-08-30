import pytest
from sqlalchemy.orm import Session
from backend.models import (
    Warehouse, WarehouseLocation, WarehouseGridCell,
    Robot, Task, Order, OrderItem, Inventory, Item,
    SimulationRun, SimulationResult
)
from backend.simulation.engine import SimulationEngine


def setup_test_warehouse(db: Session, warehouse_id: str = "WH-TEST-SIM"):
    """Helper to seed template warehouse structure, locations, grid cells, and items."""
    # Ensure warehouse doesn't already exist in this transaction
    wh = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not wh:
        wh = Warehouse(id=warehouse_id, name="Sim Test WH", location="Sim City")
        db.add(wh)
        db.commit()

    # Add locations
    loc_ids = ["LOC-S1", "LOC-S2", "LOC-P1", "LOC-C1"]
    for lid in loc_ids:
        loc = db.query(WarehouseLocation).filter(WarehouseLocation.id == lid).first()
        if not loc:
            loc_type = "STORAGE" if "S" in lid else ("PACKING" if "P" in lid else "CHARGING")
            db.add(WarehouseLocation(
                id=lid, warehouse_id=warehouse_id,
                x=1.0 if "1" in lid else 3.0,
                y=1.0 if "1" in lid else 3.0,
                location_type=loc_type,
                zone="Z", aisle=1, rack=1, shelf=1
            ))
    db.commit()

    # Add grid cells
    cell_count = db.query(WarehouseGridCell).filter(WarehouseGridCell.warehouse_id == warehouse_id).count()
    if cell_count == 0:
        for x in range(10):
            for y in range(10):
                db.add(WarehouseGridCell(
                    warehouse_id=warehouse_id, x=x, y=y, traversable=True, cost=1.0, cell_type="NORMAL"
                ))
        db.commit()

    # Add items
    itm = db.query(Item).filter(Item.id == "ITM-SIM-A").first()
    if not itm:
        itm = Item(id="ITM-SIM-A", name="Sim Item A", sku="SIM-SKU-A", safety_stock=10, reorder_threshold=5)
        db.add(itm)
        db.commit()


def test_simulation_engine_initialization_and_run(db: Session):
    """Verifies that the SimPy SimulationEngine initializes and executes successfully on snapshot."""
    setup_test_warehouse(db)

    # Instantiate engine
    config = {
        "robots": {
            "robot_count": 2,
            "robot_speed": 1.0,
            "initial_battery_pct": 100.0
        },
        "demand": {
            "order_arrival_rate": 10.0
        },
        "simulation": {
            "picking_duration": 2.0
        }
    }

    engine = SimulationEngine(
        db=db,
        warehouse_id="WH-TEST-SIM",
        mode="OFFLINE_SNAPSHOT",
        duration=60.0,  # 1 hour
        random_seed=42,
        config=config
    )

    kpis = engine.run()

    assert kpis["duration_minutes"] == 60.0
    assert kpis["fleet_size"] == 2
    assert "throughput_orders_per_hour" in kpis
    assert "average_robot_utilization_pct" in kpis
    assert "completed_tasks" in kpis


def test_simulation_reproducibility(db: Session):
    """Verifies that running the simulation twice with the exact same seed produces identical outcomes."""
    setup_test_warehouse(db)

    config = {
        "robots": {"robot_count": 2, "robot_speed": 1.0},
        "demand": {"order_arrival_rate": 15.0},
        "simulation": {"picking_duration": 3.0}
    }

    # Run 1
    engine_1 = SimulationEngine(
        db=db, warehouse_id="WH-TEST-SIM", mode="OFFLINE_SNAPSHOT",
        duration=100.0, random_seed=100, config=config
    )
    kpis_1 = engine_1.run()

    # Run 2
    engine_2 = SimulationEngine(
        db=db, warehouse_id="WH-TEST-SIM", mode="OFFLINE_SNAPSHOT",
        duration=100.0, random_seed=100, config=config
    )
    kpis_2 = engine_2.run()

    # Assert exact match of KPIs
    assert kpis_1["completed_orders"] == kpis_2["completed_orders"]
    assert kpis_1["fulfillment_rate_pct"] == kpis_2["fulfillment_rate_pct"]
    assert kpis_1["average_robot_utilization_pct"] == kpis_2["average_robot_utilization_pct"]
    assert kpis_1["total_distance_traveled"] == kpis_2["total_distance_traveled"]
    assert kpis_1["collision_conflicts"] == kpis_2["collision_conflicts"]
    assert kpis_1["replanning_events"] == kpis_2["replanning_events"]


def test_simulation_database_isolation(db: Session):
    """Asserts that running the SimPy simulation tick events does NOT modify live operational PostgreSQL state."""
    setup_test_warehouse(db)

    # Seed live operational tables
    # Clean old items if any
    db.query(Robot).filter(Robot.warehouse_id == "WH-TEST-SIM").delete()
    db.query(Order).filter(Order.warehouse_id == "WH-TEST-SIM").delete()
    db.query(Task).filter(Task.warehouse_id == "WH-TEST-SIM").delete()
    db.commit()

    db.add(Robot(
        robot_code="ROB-LIVE", name="Live Robot", warehouse_id="WH-TEST-SIM",
        status="AVAILABLE", battery_level=99.0, max_speed=1.0, enabled=True,
        current_x=1.0, current_y=1.0
    ))
    db.add(Order(id="ORD-LIVE", customer_ref="Live Client", warehouse_id="WH-TEST-SIM", status="CREATED"))
    db.add(Task(
        task_number="TSK-LIVE", warehouse_id="WH-TEST-SIM", task_type="PICK",
        status="QUEUED", product_id="ITM-SIM-A", source_location_id="LOC-S1",
        destination_location_id="LOC-P1", requested_quantity=1
    ))
    db.commit()

    # Snapshot state of live tables before simulation run
    robots_before = db.query(Robot).filter(Robot.warehouse_id == "WH-TEST-SIM").all()
    tasks_before = db.query(Task).filter(Task.warehouse_id == "WH-TEST-SIM").all()
    orders_before = db.query(Order).filter(Order.warehouse_id == "WH-TEST-SIM").all()

    robot_state_before = {r.robot_code: (r.status, r.battery_level, r.current_x, r.current_y) for r in robots_before}
    task_state_before = {t.task_number: t.status for t in tasks_before}
    order_state_before = {o.id: o.status for o in orders_before}

    # Execute simulation
    config = {
        "robots": {"robot_count": 2, "robot_speed": 1.0},
        "demand": {"order_arrival_rate": 5.0},
        "simulation": {"picking_duration": 2.0}
    }
    engine = SimulationEngine(
        db=db, warehouse_id="WH-TEST-SIM", mode="OFFLINE_SNAPSHOT",
        duration=120.0, random_seed=42, config=config
    )
    engine.run()

    # Query state of live tables after simulation run
    robots_after = db.query(Robot).filter(Robot.warehouse_id == "WH-TEST-SIM").all()
    tasks_after = db.query(Task).filter(Task.warehouse_id == "WH-TEST-SIM").all()
    orders_after = db.query(Order).filter(Order.warehouse_id == "WH-TEST-SIM").all()

    robot_state_after = {r.robot_code: (r.status, r.battery_level, r.current_x, r.current_y) for r in robots_after}
    task_state_after = {t.task_number: t.status for t in tasks_after}
    order_state_after = {o.id: o.status for o in orders_after}

    # Verify absolutely NO mutation occurred on live records
    assert robot_state_before == robot_state_after
    assert task_state_before == task_state_after
    assert order_state_before == order_state_after
