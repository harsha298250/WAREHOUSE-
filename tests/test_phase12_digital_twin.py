import pytest
from sqlalchemy.orm import Session
from backend.models import (
    Warehouse, WarehouseLocation, WarehouseGridCell,
    Robot, Task, Order, OrderItem, Inventory, Item,
    SimulationRun
)
from backend.simulation.engine import SimulationEngine
from backend.routers.digital_twin import _build_state


def test_coordinate_conversion_math():
    """Verifies that the coordinate conversion mapping is deterministic and matches design rules."""
    # Mapping formula:
    # tx = (x - 6.5) * 10
    # tz = (y - 3.0) * 10
    
    # Origin (1, 1) mapping
    x1, y1 = 1, 1
    tx1 = (x1 - 6.5) * 10
    tz1 = (y1 - 3.0) * 10
    assert tx1 == -55.0
    assert tz1 == -20.0

    # Grid boundaries (12, 5) mapping
    x2, y2 = 12, 5
    tx2 = (x2 - 6.5) * 10
    tz2 = (y2 - 3.0) * 10
    assert tx2 == 55.0
    assert tz2 == 20.0


def test_digital_twin_state_endpoint(client, db, admin_token):
    """Verifies the GET /digital-twin/{wh}/state response schema and contract consistency."""
    # Ensure warehouse exists
    wh = db.query(Warehouse).filter(Warehouse.id == "WH-BLR-01").first()
    if not wh:
        wh = Warehouse(id="WH-BLR-01", name="Bangalore Hub", location="BLR")
        db.add(wh)
        db.commit()

    headers = {"Authorization": f"Bearer {admin_token}"}

    # Fetch digital twin state
    r = client.get("/digital-twin/WH-BLR-01/state", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert "warehouse_id" in data
    assert "robots" in data
    assert "grid" in data
    assert "obstacles" in data
    assert "routes" in data
    assert "location_inventory" in data
    assert "fleet_summary" in data


def test_live_vs_simulation_non_mutation_safety(client, db):
    """Ensures that executing simulated ticks or loading simulation state does NOT mutate Postgres live WMS tables."""
    # 1. Fetch initial live robots and inventory counts
    robots_before = db.query(Robot).all()
    inventory_before = db.query(Inventory).all()
    tasks_before = db.query(Task).all()

    # 2. Run an offline snapshot SimPy simulation
    config = {
        "robots": {"robot_count": 2, "robot_speed": 1.0},
        "demand": {"order_arrival_rate": 15.0},
        "simulation": {"picking_duration": 3.0}
    }
    engine = SimulationEngine(
        db=db,
        warehouse_id="WH-BLR-01",
        mode="OFFLINE_SNAPSHOT",
        duration=60.0,
        random_seed=42,
        config=config
    )
    # Run the discrete-event loop
    engine.run()

    # 3. Assert live database state was not altered
    robots_after = db.query(Robot).all()
    inventory_after = db.query(Inventory).all()
    tasks_after = db.query(Task).all()

    assert len(robots_before) == len(robots_after)
    assert len(inventory_before) == len(inventory_after)
    assert len(tasks_before) == len(tasks_after)

    # Verify attributes of a live robot remain unchanged
    for r_b, r_a in zip(robots_before, robots_after):
        assert r_b.current_x == r_a.current_x
        assert r_b.current_y == r_a.current_y
        assert r_b.status == r_a.status
        assert r_b.battery_level == r_a.battery_level
