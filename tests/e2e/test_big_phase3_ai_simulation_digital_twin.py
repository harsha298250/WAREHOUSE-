import pytest
import json
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, UTC

from backend.main import app
from backend.models import (
    User, Warehouse, Item, Inventory, WarehouseLocation,
    Robot, Task, RobotRoute, WarehouseGridCell, WarehouseObstacle,
    DigitalTwinSimulation, SimulationSnapshot, SimulationEvent,
    Scenario, Experiment, ExperimentRun
)
from backend.auth import hash_password
from backend.routers.pathfinding import initialize_warehouse_grid_if_empty
from backend.routers.robots import execute_simulation_tick

client = TestClient(app)

def run_async(coro_creator):
    import queue
    import threading
    import asyncio
    q = queue.Queue()
    
    def worker():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            res = loop.run_until_complete(coro_creator())
            q.put((True, res))
        except Exception as e:
            q.put((False, e))
        finally:
            loop.close()
            
    t = threading.Thread(target=worker)
    t.start()
    t.join()
    
    success, val = q.get()
    if success:
        return val
    else:
        raise val

@pytest.fixture
def p3_admin(db):
    user = db.query(User).filter(User.username == "p3_admin").first()
    if not user:
        user = User(
            username="p3_admin",
            password_hash=hash_password("AdminPass123!"),
            role="admin"
        )
        db.add(user)
        db.commit()
    return user

@pytest.fixture
def admin_token(client, p3_admin):
    # Clear rate limiter
    try:
        from backend.main import _login_attempts
        _login_attempts.clear()
    except ImportError:
        pass
    r = client.post("/auth/login", json={"username": "p3_admin", "password": "AdminPass123!"})
    assert r.status_code == 200
    return r.json()["access_token"]

def setup_p3_data(db):
    # Purge Digital Twin and WMS tables for isolations
    db.query(SimulationEvent).delete()
    db.query(SimulationSnapshot).delete()
    db.query(DigitalTwinSimulation).delete()
    db.query(ExperimentRun).delete()
    db.query(Experiment).delete()
    db.query(Scenario).delete()
    db.query(RobotRoute).delete()
    db.query(Robot).delete()
    db.query(Task).delete()
    db.query(Inventory).delete()
    db.query(WarehouseGridCell).filter(WarehouseGridCell.warehouse_id == "WH-P3-01").delete()
    db.query(WarehouseObstacle).filter(WarehouseObstacle.warehouse_id == "WH-P3-01").delete()
    db.query(WarehouseLocation).filter(WarehouseLocation.warehouse_id == "WH-P3-01").delete()
    db.query(Item).filter(Item.id == "ITM-P3-01").delete()
    db.query(Warehouse).filter(Warehouse.id == "WH-P3-01").delete()
    db.commit()

    wh = Warehouse(id="WH-P3-01", name="Phase 3 E2E Warehouse", location="P3 Loc")
    db.add(wh)
    db.commit()

    initialize_warehouse_grid_if_empty(db, "WH-P3-01")

    item = Item(id="ITM-P3-01", name="P3 Test Item", unit_cost=25.0, safety_stock=5, reorder_threshold=10)
    db.add(item)
    db.commit()

    loc_pick = WarehouseLocation(
        id="WH-P3-01-A-01", warehouse_id="WH-P3-01", zone="A", aisle="01", rack="01", shelf="01",
        location_type="PICKING", capacity=100, x=3.0, y=2.0
    )
    loc_dest = WarehouseLocation(
        id="WH-P3-01-B-01", warehouse_id="WH-P3-01", zone="B", aisle="01", rack="01", shelf="01",
        location_type="SHIPPING", capacity=100, x=6.0, y=4.0
    )
    loc_charge = WarehouseLocation(
        id="WH-P3-01-C-01", warehouse_id="WH-P3-01", zone="C", aisle="01", rack="01", shelf="01",
        location_type="CHARGING", capacity=10, x=11.0, y=5.0
    )
    db.add(loc_pick)
    db.add(loc_dest)
    db.add(loc_charge)
    db.commit()

    # Make location grid cells traversable for route planners
    for cell in db.query(WarehouseGridCell).filter(
        WarehouseGridCell.warehouse_id == "WH-P3-01",
        WarehouseGridCell.x.in_([3, 6, 11]),
        WarehouseGridCell.y.in_([2, 4, 5])
    ).all():
        cell.traversable = True
        cell.cell_type = "FLOOR"
    db.commit()

    inv = Inventory(warehouse_id="WH-P3-01", item_id="ITM-P3-01", location_id="WH-P3-01-A-01", on_hand=50, reserved=0, available=50)
    db.add(inv)
    db.commit()


def test_digital_twin_state_loading(client, db, admin_token):
    setup_p3_data(db)
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Retrieve Digital Twin state
    r = client.get("/digital-twin/WH-P3-01/state", headers=headers)
    assert r.status_code == 200
    res = r.json()
    assert res["warehouse_id"] == "WH-P3-01"
    assert res["telemetry_mode"] == "SIMULATED TELEMETRY"
    assert len(res["grid"]) == 60 # 12 x 5 grid cells
    assert "location_inventory" in res


def test_robot_telemetry_and_route_sync(client, db, admin_token):
    setup_p3_data(db)
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Add a robot and active route
    bot = Robot(robot_code="ROB-P3-01", name="P3 Bot", warehouse_id="WH-P3-01", robot_type="AGV", current_x=1.0, current_y=1.0, status="AVAILABLE")
    db.add(bot)
    db.commit()

    # Check state retrieves robot and its status
    r = client.get("/digital-twin/WH-P3-01/state", headers=headers)
    assert r.status_code == 200
    res = r.json()
    assert len(res["robots"]) == 1
    assert res["robots"][0]["robot_code"] == "ROB-P3-01"
    assert res["robots"][0]["status"] == "AVAILABLE"


def test_simpy_simulation_isolation_and_kpis(client, db, admin_token):
    setup_p3_data(db)
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Verify starting a Digital Twin simulation
    r = client.post("/digital-twin/simulation/start", json={
        "warehouse_id": "WH-P3-01",
        "scenario_type": "NORMAL_OPERATIONS",
        "speed_multiplier": 1.0,
        "seed": 42,
        "mode": "SIMULATION"
    }, headers=headers)
    assert r.status_code == 200
    sim_data = r.json()
    sim_id = sim_data["simulation_id"]
    assert sim_data["status"] == "RUNNING"

    # Advance tick
    r_step = client.post(f"/digital-twin/simulation/{sim_id}/step", headers=headers)
    assert r_step.status_code == 200
    assert r_step.json()["tick_count"] == 2

    # Pause
    r_pause = client.post(f"/digital-twin/simulation/{sim_id}/pause", headers=headers)
    assert r_pause.status_code == 200
    assert r_pause.json()["status"] == "PAUSED"

    # Reset
    r_reset = client.post(f"/digital-twin/simulation/{sim_id}/reset", headers=headers)
    assert r_reset.status_code == 200
    assert r_reset.json()["status"] == "READY"


def test_scenario_creation_and_experiments(client, db, admin_token):
    setup_p3_data(db)
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Create a custom scenario
    r_scen = client.post("/scenarios", json={
        "name": "E2E P3 Custom Scenario",
        "description": "Scenario testing charging constraint detours.",
        "warehouse_id": "WH-P3-01",
        "scenario_type": "CUSTOM",
        "random_seed": 42,
        "configuration": {
            "robots": {"robot_count": 2, "robot_speed": 1.2}
        }
    }, headers=headers)
    assert r_scen.status_code == 200
    scen = r_scen.json()
    assert scen["name"] == "E2E P3 Custom Scenario"

    # Create an experiment run based on the scenario
    r_exp = client.post("/scenarios/experiments", json={
        "scenario_id": scen["id"],
        "experiment_name": "E2E Experiment charging detours",
        "repetitions": 1
    }, headers=headers)
    assert r_exp.status_code == 200
    exp = r_exp.json()
    assert exp["status"] == "QUEUED"


def test_sse_broadcast_sync_flow(db, p3_admin):
    setup_p3_data(db)
    from backend.routers.digital_twin import sync_dt_state
    
    async def run():
        response = await sync_dt_state(
            warehouse_id="WH-P3-01",
            mode="LIVE",
            db=db,
            user=p3_admin
        )
        assert response.status_code == 200
        iterator = response.body_iterator
        first_item = await iterator.__anext__()
        assert first_item.startswith("data: ")
        payload = json.loads(first_item[6:])
        assert payload["event_type"] == "SNAPSHOT"
        assert payload["warehouse_id"] == "WH-P3-01"
        assert "data" in payload
        
    run_async(run)
