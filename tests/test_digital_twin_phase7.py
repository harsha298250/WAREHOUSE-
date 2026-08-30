import pytest
import json
from datetime import datetime, date
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.main import app
from backend.database import SessionLocal
from backend.models import (
    Warehouse, Robot, Task, RobotRoute, WarehouseGridCell,
    WarehouseObstacle, Inventory, WarehouseLocation, Item, Order, OrderItem,
    DigitalTwinSimulation, SimulationSnapshot, SimulationEvent
)

client = TestClient(app)

# Helper to get authentication token
def get_auth_token():
    r = client.post('/auth/login', json={'username': 'test_admin_hardened', 'password': 'AdminHardened@123'})
    if r.status_code != 200:
        r = client.post('/auth/login', json={'username': 'test_admin', 'password': 'TestAdmin@123'})
    return r.json().get('access_token')

@pytest.fixture(scope="module")
def auth_headers():
    token = get_auth_token()
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="function")
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True)
def setup_dt_test_data(db_session):
    # Purge old simulation/twin test records to keep it clean and isolated
    db_session.query(SimulationEvent).delete()
    db_session.query(SimulationSnapshot).delete()
    db_session.query(DigitalTwinSimulation).delete()
    db_session.query(RobotRoute).delete()
    db_session.query(Robot).delete()
    db_session.query(Task).delete()
    db_session.query(Inventory).delete()
    db_session.query(WarehouseLocation).filter(WarehouseLocation.warehouse_id == "WH-DT-01").delete()
    db_session.query(WarehouseGridCell).filter(WarehouseGridCell.warehouse_id == "WH-DT-01").delete()
    db_session.query(Item).filter(Item.id == "ITM-DT-01").delete()
    db_session.query(Warehouse).filter(Warehouse.id == "WH-DT-01").delete()
    db_session.commit()

    # Create Warehouse
    wh = Warehouse(id="WH-DT-01", name="Digital Twin Warehouse", location="Bengaluru")
    db_session.add(wh)
    db_session.commit()

    # Create Item
    item = Item(id="ITM-DT-01", name="Simulated Processor", unit_cost=250.0, safety_stock=10, sku="SKU-DT-01")
    db_session.add(item)
    db_session.commit()

    # Create Locations
    loc1 = WarehouseLocation(
        id="LOC-DT-01", warehouse_id="WH-DT-01", zone="A", aisle="01", rack="01", shelf="01",
        x=2.0, y=2.0, location_type="PICKING"
    )
    db_session.add(loc1)
    db_session.commit()

    # Create Grid Cells
    for x in range(12):
        for y in range(5):
            cell = WarehouseGridCell(
                warehouse_id="WH-DT-01", x=x, y=y, cell_type="FLOOR", traversable=True
            )
            db_session.add(cell)
    db_session.commit()

    # Create Inventory
    inv = Inventory(
        warehouse_id="WH-DT-01", item_id="ITM-DT-01", location_id="LOC-DT-01",
        on_hand=50, reserved=0, available=50
    )
    db_session.add(inv)
    db_session.commit()

    # Create Robot
    robot = Robot(
        robot_code="ROB-DT-01", name="Twin AGV 1", warehouse_id="WH-DT-01",
        status="AVAILABLE", battery_level=100.0, current_x=0.0, current_y=0.0,
        enabled=True
    )
    db_session.add(robot)
    db_session.commit()

    # Create Task
    task = Task(
        task_number="TSK-DT-01", warehouse_id="WH-DT-01", task_type="PICK",
        status="QUEUED", priority="HIGH", priority_score=80, product_id="ITM-DT-01",
        source_location_id="LOC-DT-01", requested_quantity=5
    )
    db_session.add(task)
    db_session.commit()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_dt_simulation_lifecycle_and_controls(auth_headers, db_session):
    wh_id = "WH-DT-01"
    
    # 1. Create and Start Simulation
    res = client.post("/digital-twin/simulation/start", json={
        "warehouse_id": wh_id,
        "scenario_type": "NORMAL_OPERATIONS",
        "speed_multiplier": 1.0,
        "seed": 42
    }, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "simulation_id" in data
    sim_id = data["simulation_id"]
    assert data["status"] == "RUNNING"
    
    # Verify DB record
    sim = db_session.query(DigitalTwinSimulation).filter(DigitalTwinSimulation.id == sim_id).first()
    assert sim is not None
    assert sim.simulation_status == "RUNNING"
    assert sim.scenario_type == "NORMAL_OPERATIONS"

    # Verify initial snapshot (version 0) exists
    snap = db_session.query(SimulationSnapshot).filter(
        SimulationSnapshot.simulation_id == sim_id,
        SimulationSnapshot.snapshot_version == 0
    ).first()
    assert snap is not None

    # Verify Start Event generated
    start_ev = db_session.query(SimulationEvent).filter(
        SimulationEvent.simulation_id == sim_id,
        SimulationEvent.event_type == "SIMULATION_STARTED"
    ).first()
    assert start_ev is not None

    # 2. Pause Simulation
    res = client.post(f"/digital-twin/simulation/{sim_id}/pause", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["status"] == "PAUSED"
    db_session.refresh(sim)
    assert sim.simulation_status == "PAUSED"

    # Verify Pause Event
    pause_ev = db_session.query(SimulationEvent).filter(
        SimulationEvent.simulation_id == sim_id,
        SimulationEvent.event_type == "SIMULATION_PAUSED"
    ).first()
    assert pause_ev is not None

    # 3. Resume Simulation
    res = client.post(f"/digital-twin/simulation/{sim_id}/resume", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["status"] == "RUNNING"
    db_session.refresh(sim)
    assert sim.simulation_status == "RUNNING"

    # Verify Resume Event
    resume_ev = db_session.query(SimulationEvent).filter(
        SimulationEvent.simulation_id == sim_id,
        SimulationEvent.event_type == "SIMULATION_RESUMED"
    ).first()
    assert resume_ev is not None

    # 4. Step Simulation (Clock increments)
    prev_seconds = sim.simulation_time_seconds
    prev_ticks = sim.tick_count
    
    res = client.post(f"/digital-twin/simulation/{sim_id}/step", headers=auth_headers)
    assert res.status_code == 200
    step_data = res.json()
    assert step_data["tick_count"] == prev_ticks + 1
    assert step_data["simulation_time_seconds"] == prev_seconds + (1.0 * sim.speed_multiplier)

    # 5. Stop Simulation (Preserves results)
    res = client.post(f"/digital-twin/simulation/{sim_id}/stop", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["status"] == "STOPPED"
    db_session.refresh(sim)
    assert sim.simulation_status == "STOPPED"

    # Verify Stop Event
    stop_ev = db_session.query(SimulationEvent).filter(
        SimulationEvent.simulation_id == sim_id,
        SimulationEvent.event_type == "SIMULATION_STOPPED"
    ).first()
    assert stop_ev is not None

    # 6. Reset Simulation
    res = client.post(f"/digital-twin/simulation/{sim_id}/reset", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["status"] == "READY"
    db_session.refresh(sim)
    assert sim.simulation_status == "READY"
    assert sim.tick_count == 0
    assert sim.simulation_time_seconds == 0.0

    # Verify Reset Event
    reset_ev = db_session.query(SimulationEvent).filter(
        SimulationEvent.simulation_id == sim_id,
        SimulationEvent.event_type == "SIMULATION_RESET"
    ).first()
    assert reset_ev is not None


def test_dt_state_reconciliation_and_polling(auth_headers, db_session):
    wh_id = "WH-DT-01"
    
    # Request DT state
    res = client.get(f"/digital-twin/{wh_id}/state", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    
    # Layer validations
    assert data["warehouse_id"] == wh_id
    assert "grid" in data          # Layer 1
    assert "location_inventory" in data  # Layer 2
    assert "robots" in data        # Layer 3
    assert "obstacles" in data     # Layer 4
    assert "routes" in data        # Layer 4
    assert "simulation" in data    # Layer 5
    assert "fleet_summary" in data # Layer 6

    # Verify grid mapping
    assert len(data["grid"]) > 0
    for cell in data["grid"]:
        assert "x" in cell
        assert "y" in cell
        assert "type" in cell
        assert "traversable" in cell


def test_dt_events_stream_and_kpis(auth_headers, db_session):
    wh_id = "WH-DT-01"
    
    # Start a sim session to generate events
    res = client.post("/digital-twin/simulation/start", json={"warehouse_id": wh_id}, headers=auth_headers)
    sim_id = res.json()["simulation_id"]

    # Step simulation to trigger telemetry check ticks
    client.post(f"/digital-twin/simulation/{sim_id}/step", headers=auth_headers)
    client.post(f"/digital-twin/simulation/{sim_id}/step", headers=auth_headers)

    # Get events
    res = client.get(f"/digital-twin/{wh_id}/events?limit=10", headers=auth_headers)
    assert res.status_code == 200
    events = res.json()
    assert len(events) > 0
    for e in events:
        assert "event_type" in e
        assert "severity" in e
        assert "real_timestamp" in e

    # Get metrics
    res = client.get(f"/digital-twin/simulation/{sim_id}/metrics", headers=auth_headers)
    assert res.status_code == 200
    metrics = res.json()
    assert "metric_disclaimer" in metrics
    assert "tasks" in metrics
    assert "robots" in metrics
    assert "navigation" in metrics


def test_dt_isolation_and_snapshot_safety(auth_headers, db_session):
    wh_id = "WH-DT-01"
    
    # Save current physical inventory on hand
    inv = db_session.query(Inventory).filter(Inventory.warehouse_id == wh_id).first()
    assert inv is not None
    initial_on_hand = inv.on_hand

    # Start simulation
    res = client.post("/digital-twin/simulation/start", json={"warehouse_id": wh_id}, headers=auth_headers)
    sim_id = res.json()["simulation_id"]

    # Step simulation several times
    for _ in range(3):
        client.post(f"/digital-twin/simulation/{sim_id}/step", headers=auth_headers)

    # Verify initial stock quantity has not been altered
    db_session.refresh(inv)
    assert inv.on_hand == initial_on_hand, "Production inventory on_hand mutated during simulation!"


def test_dt_heatmap_endpoint(auth_headers):
    wh_id = "WH-DT-01"
    
    # Check robot_traffic heatmap
    res = client.get(f"/digital-twin/{wh_id}/heatmap?metric=robot_traffic", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["metric"] == "robot_traffic"
    assert "heatmap" in data
    
    # Check task_activity heatmap
    res = client.get(f"/digital-twin/{wh_id}/heatmap?metric=task_activity", headers=auth_headers)
    assert res.status_code == 200
    
    # Check inventory_density heatmap
    res = client.get(f"/digital-twin/{wh_id}/heatmap?metric=inventory_density", headers=auth_headers)
    assert res.status_code == 200
