"""
tests/test_phase6_live_digital_twin.py — Phase 6: Live Digital Twin Test Suite

Verifies:
1. Robot status changes update Digital Twin state.
2. Robot position & battery telemetry updates.
3. Task assignment links task to robot.
4. Task lifecycle state progression.
5. Route visualization (pathfinding output in state).
6. Dynamic route recalculation (REPLANNED state on obstacle block).
7. Active obstacle visualization.
8. Real-time event broadcasting via SyncBroadcaster.
9. SSE sync stream initial SNAPSHOT state reconciliation.
10. Multi-robot isolation (updates to Robot A do not affect Robot B).
11. Production vs Simulation state separation & inventory isolation.
12. Stale data detection & timestamping.
13. Replenishment & inventory decision support visualization integration.
14. RBAC warehouse security enforcement.
15. Subscription lifecycle and listener queue cleanup.
"""

import json
import pytest
import asyncio
from datetime import datetime, UTC
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.models import (
    Warehouse, Robot, Task, RobotRoute, WarehouseObstacle,
    Inventory, WarehouseLocation, Item, User, UserWarehouseAccess,
    ReplenishmentRecommendation
)
from backend.sync_broadcast import broadcaster
from backend.routers.digital_twin import _build_state
from backend.services.intelligent_assignment import assign_robot_intelligently
from backend.services.operational_pathfinding import validate_and_reroute_robot_path


@pytest.fixture
def setup_phase6_data(db: Session):
    """Setup isolated test warehouse, robots, tasks, items, locations."""
    wh = db.query(Warehouse).filter(Warehouse.id == "WH-P6-01").first()
    if not wh:
        wh = Warehouse(id="WH-P6-01", name="Phase 6 Live Hub", location="Testing Zone")
        db.add(wh)
        db.commit()

    # Create 2 Robots
    r1 = db.query(Robot).filter(Robot.robot_code == "ROB-P6-01").first()
    if not r1:
        r1 = Robot(id=601, robot_code="ROB-P6-01", name="P6 Robot 1", warehouse_id="WH-P6-01", status="AVAILABLE", battery_level=95.0, current_x=1.0, current_y=1.0, max_payload=100.0)
        db.add(r1)

    r2 = db.query(Robot).filter(Robot.robot_code == "ROB-P6-02").first()
    if not r2:
        r2 = Robot(id=602, robot_code="ROB-P6-02", name="P6 Robot 2", warehouse_id="WH-P6-01", status="AVAILABLE", battery_level=80.0, current_x=5.0, current_y=1.0, max_payload=100.0)
        db.add(r2)

    # Item & Location & Inventory
    item = db.query(Item).filter(Item.id == "ITM-P6-01").first()
    if not item:
        item = Item(id="ITM-P6-01", name="P6 Widget", sku="SKU-P6-01", safety_stock=20, reorder_threshold=50)
        db.add(item)

    loc = db.query(WarehouseLocation).filter(WarehouseLocation.id == "LOC-P6-01").first()
    if not loc:
        loc = WarehouseLocation(id="LOC-P6-01", warehouse_id="WH-P6-01", zone="A", aisle="1", rack="1", shelf="1", x=2, y=2, location_type="RACK")
        db.add(loc)

    inv = db.query(Inventory).filter(Inventory.warehouse_id == "WH-P6-01", Inventory.item_id == "ITM-P6-01").first()
    if not inv:
        inv = Inventory(warehouse_id="WH-P6-01", item_id="ITM-P6-01", location_id="LOC-P6-01", on_hand=15, reserved=0, available=15)
        db.add(inv)
    else:
        inv.on_hand = 15
        inv.available = 15

    db.commit()
    return {"wh_id": "WH-P6-01", "r1_code": "ROB-P6-01", "r2_code": "ROB-P6-02", "item_id": "ITM-P6-01"}


@pytest.fixture
def phase6_admin(db: Session):
    from backend.auth import hash_password
    admin = db.query(User).filter(User.username == "phase6_admin").first()
    if not admin:
        admin = User(
            username="phase6_admin", email="p6admin@example.com", role="admin",
            password_hash=hash_password("AdminPass123!"), is_active=True, is_verified=True
        )
        db.add(admin)
        db.commit()
    return admin


@pytest.fixture
def phase6_restricted_user(db: Session):
    from backend.auth import hash_password
    u = db.query(User).filter(User.username == "phase6_staff").first()
    if not u:
        u = User(
            username="phase6_staff", email="p6staff@example.com", role="staff",
            password_hash=hash_password("StaffPass123!"), is_active=True, is_verified=True
        )
        db.add(u)
        db.commit()
    return u


# ---------------------------------------------------------------------------
# Test Scenario 1: Robot Status Update in State
# ---------------------------------------------------------------------------
def test_scenario_1_robot_status_update(db: Session, setup_phase6_data):
    wh_id = setup_phase6_data["wh_id"]
    r1_code = setup_phase6_data["r1_code"]

    rob = db.query(Robot).filter(Robot.robot_code == r1_code).first()
    rob.status = "MAINTENANCE"
    db.commit()

    state = _build_state(db, wh_id)
    r_state = next(r for r in state["robots"] if r["robot_code"] == r1_code)
    assert r_state["status"] == "MAINTENANCE"


# ---------------------------------------------------------------------------
# Test Scenario 2: Robot Position & Battery Telemetry Updates
# ---------------------------------------------------------------------------
def test_scenario_2_robot_position_and_telemetry(db: Session, setup_phase6_data):
    wh_id = setup_phase6_data["wh_id"]
    r1_code = setup_phase6_data["r1_code"]

    rob = db.query(Robot).filter(Robot.robot_code == r1_code).first()
    rob.current_x = 4.0
    rob.current_y = 3.0
    rob.battery_level = 42.5
    db.commit()

    state = _build_state(db, wh_id)
    r_state = next(r for r in state["robots"] if r["robot_code"] == r1_code)
    assert r_state["current_x"] == 4.0
    assert r_state["current_y"] == 3.0
    assert r_state["battery_level"] == 42.5


# ---------------------------------------------------------------------------
# Test Scenario 3: Task Assignment Integration
# ---------------------------------------------------------------------------
def test_scenario_3_task_assignment(db: Session, setup_phase6_data, phase6_admin):
    wh_id = setup_phase6_data["wh_id"]
    r1_code = setup_phase6_data["r1_code"]

    now = datetime.now(UTC).replace(tzinfo=None)
    t = Task(
        task_number=f"TSK-P6-S3-{now.timestamp()}", warehouse_id=wh_id,
        task_type="PICK", priority="HIGH", status="QUEUED",
        source_location_id="LOC-P6-01", destination_location_id="LOC-P6-01",
        requested_quantity=5, product_id="ITM-P6-01"
    )
    db.add(t)
    db.commit()

    # Assign task using Phase 3 engine
    assign_robot_intelligently(db, task_id=t.id, robot_identifier=r1_code, user_id=phase6_admin.id, username=phase6_admin.username)

    state = _build_state(db, wh_id)
    task_in_state = next((tk for tk in state["tasks"] if tk["id"] == t.id), None)
    rob_in_state = next(r for r in state["robots"] if r["robot_code"] == r1_code)

    assert task_in_state is not None
    assert task_in_state["assigned_robot_id"] in (rob_in_state["id"], rob_in_state["robot_code"])
    assert rob_in_state["assigned_task_id"] == t.id


# ---------------------------------------------------------------------------
# Test Scenario 4: Task Lifecycle Progression
# ---------------------------------------------------------------------------
def test_scenario_4_task_lifecycle(db: Session, setup_phase6_data):
    wh_id = setup_phase6_data["wh_id"]
    now = datetime.now(UTC).replace(tzinfo=None)

    t = Task(
        task_number=f"TSK-P6-S4-{now.timestamp()}", warehouse_id=wh_id,
        task_type="MOVE", priority="MEDIUM", status="QUEUED", product_id="ITM-P6-01", requested_quantity=1
    )
    db.add(t)
    db.commit()

    # 1. QUEUED state
    state1 = _build_state(db, wh_id)
    t1 = next(tk for tk in state1["tasks"] if tk["id"] == t.id)
    assert t1["status"] == "QUEUED"

    # 2. IN_PROGRESS state
    t.status = "IN_PROGRESS"
    db.commit()
    state2 = _build_state(db, wh_id)
    t2 = next(tk for tk in state2["tasks"] if tk["id"] == t.id)
    assert t2["status"] == "IN_PROGRESS"

    # 3. COMPLETED state (should drop out of active task list in DT state)
    t.status = "COMPLETED"
    db.commit()
    state3 = _build_state(db, wh_id)
    active_ids = [tk["id"] for tk in state3["tasks"]]
    assert t.id not in active_ids


# ---------------------------------------------------------------------------
# Test Scenario 5: Route Visualization Output
# ---------------------------------------------------------------------------
def test_scenario_5_route_visualization_output(db: Session, setup_phase6_data):
    wh_id = setup_phase6_data["wh_id"]
    r1 = db.query(Robot).filter(Robot.robot_code == setup_phase6_data["r1_code"]).first()

    route = RobotRoute(
        warehouse_id=wh_id, robot_id=r1.id,
        start_x=1, start_y=1, goal_x=3, goal_y=3,
        path_data=json.dumps([[1,1], [1,2], [2,2], [3,2], [3,3]]),
        algorithm="A_STAR", distance=4.0, cost=4.0, status="ACTIVE"
    )
    db.add(route)
    db.commit()

    state = _build_state(db, wh_id)
    assert len(state["routes"]) >= 1
    rt = next(r for r in state["routes"] if r["id"] == route.id)
    assert rt["status"] == "ACTIVE"
    assert len(rt["path_data"]) == 5


# ---------------------------------------------------------------------------
# Test Scenario 6: Route Recalculation (Blocked by Obstacle)
# ---------------------------------------------------------------------------
def test_scenario_6_route_recalculation(db: Session, setup_phase6_data, phase6_admin):
    wh_id = setup_phase6_data["wh_id"]
    r1_code = setup_phase6_data["r1_code"]
    r1 = db.query(Robot).filter(Robot.robot_code == r1_code).first()

    now = datetime.now(UTC).replace(tzinfo=None)
    t = Task(
        task_number=f"TSK-P6-S6-{now.timestamp()}", warehouse_id=wh_id,
        task_type="PICK", priority="HIGH", status="ASSIGNED",
        source_location_id="LOC-P6-01", destination_location_id="LOC-P6-01", product_id="ITM-P6-01", requested_quantity=1
    )
    db.add(t)
    db.commit()
    r1.assigned_task_id = t.id
    db.commit()

    # Create active route passing through (2, 2)
    route = RobotRoute(
        warehouse_id=wh_id, robot_id=r1.id, task_id=t.id,
        start_x=1, start_y=1, goal_x=2, goal_y=2,
        path_data=json.dumps([[1,1], [1,2], [2,2]]),
        algorithm="A_STAR", distance=2.0, cost=2.0, status="ACTIVE"
    )
    db.add(route)
    db.commit()

    # Place an active obstacle at (2, 2)
    obs = WarehouseObstacle(warehouse_id=wh_id, x=2, y=2, width=1, height=1, active=True, obstacle_type="SPILL")
    db.add(obs)
    db.commit()

    # Run dynamic rerouting
    reroute_res = validate_and_reroute_robot_path(db, r1_code, algorithm="A_STAR")
    assert reroute_res["rerouted"] is True

    # Check state
    db.refresh(route)
    assert route.status == "REPLANNED"


# ---------------------------------------------------------------------------
# Test Scenario 7: Active Obstacle Visualization
# ---------------------------------------------------------------------------
def test_scenario_7_obstacle_visualization(db: Session, setup_phase6_data):
    wh_id = setup_phase6_data["wh_id"]

    obs = WarehouseObstacle(warehouse_id=wh_id, x=4, y=4, width=1, height=1, active=True, obstacle_type="TEMPORARY_BLOCK")
    db.add(obs)
    db.commit()

    state = _build_state(db, wh_id)
    obs_in_state = next((o for o in state["obstacles"] if o["id"] == obs.id), None)
    assert obs_in_state is not None
    assert obs_in_state["active"] is True
    assert obs_in_state["x"] == 4 and obs_in_state["y"] == 4


# ---------------------------------------------------------------------------
# Test Scenario 8: Real-Time Event Broadcasting
# ---------------------------------------------------------------------------
def test_scenario_8_broadcaster_event_dispatch():
    """Verify SyncBroadcaster dispatches live events to subscriber queue."""
    def run_async_test():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            async def main():
                q = asyncio.Queue()
                broadcaster.subscribe_live("WH-P6-TEST", q)

                payload = {"event_type": "ROBOT_MOVED", "entity_type": "robot", "entity_id": "ROB-P6-01", "data": {"x": 3.0, "y": 3.0}}
                broadcaster.broadcast_live("WH-P6-TEST", payload)

                await asyncio.sleep(0.01)
                assert q.qsize() == 1
                item = q.get_nowait()
                assert item["event_type"] == "ROBOT_MOVED"
                assert item["entity_id"] == "ROB-P6-01"

                broadcaster.unsubscribe_live("WH-P6-TEST", q)
            loop.run_until_complete(main())
        finally:
            loop.close()

    run_async_test()


# ---------------------------------------------------------------------------
# Test Scenario 9: State Reconciliation Snapshot
# ---------------------------------------------------------------------------
def test_scenario_9_state_reconciliation_snapshot(db: Session, setup_phase6_data):
    wh_id = setup_phase6_data["wh_id"]
    state = _build_state(db, wh_id)

    assert "warehouse_id" in state
    assert state["warehouse_id"] == wh_id
    assert "robots" in state
    assert "tasks" in state
    assert "obstacles" in state
    assert "routes" in state
    assert "kpis" in state


# ---------------------------------------------------------------------------
# Test Scenario 10: Multi-Robot Isolation
# ---------------------------------------------------------------------------
def test_scenario_10_multi_robot_isolation(db: Session, setup_phase6_data):
    wh_id = setup_phase6_data["wh_id"]
    r1_code = setup_phase6_data["r1_code"]
    r2_code = setup_phase6_data["r2_code"]

    r1 = db.query(Robot).filter(Robot.robot_code == r1_code).first()
    r2 = db.query(Robot).filter(Robot.robot_code == r2_code).first()

    r1.current_x = 10.0
    r1.status = "CHARGING"
    db.commit()

    state = _build_state(db, wh_id)
    r1_st = next(r for r in state["robots"] if r["robot_code"] == r1_code)
    r2_st = next(r for r in state["robots"] if r["robot_code"] == r2_code)

    assert r1_st["current_x"] == 10.0
    assert r1_st["status"] == "CHARGING"
    assert r2_st["current_x"] == 5.0  # Robot 2 unchanged
    assert r2_st["status"] == "AVAILABLE"


# ---------------------------------------------------------------------------
# Test Scenario 11: Production vs Simulation Separation
# ---------------------------------------------------------------------------
def test_scenario_11_production_simulation_separation(db: Session, setup_phase6_data):
    wh_id = setup_phase6_data["wh_id"]
    inv_before = db.query(Inventory).filter(Inventory.warehouse_id == wh_id).first().on_hand

    state = _build_state(db, wh_id, sim=None)
    assert state["data_mode"] == "OBSERVATION STATE"
    assert state["is_live"] is True

    inv_after = db.query(Inventory).filter(Inventory.warehouse_id == wh_id).first().on_hand
    assert inv_before == inv_after


# ---------------------------------------------------------------------------
# Test Scenario 12: Stale Data & Timestamp Tracking
# ---------------------------------------------------------------------------
def test_scenario_12_stale_data_detection(db: Session, setup_phase6_data):
    wh_id = setup_phase6_data["wh_id"]
    state = _build_state(db, wh_id)

    assert "timestamp" in state
    ts = datetime.fromisoformat(state["timestamp"])
    assert ts is not None


# ---------------------------------------------------------------------------
# Test Scenario 13: Replenishment Visualization Integration
# ---------------------------------------------------------------------------
def test_scenario_13_replenishment_visualization_integration(db: Session, setup_phase6_data):
    wh_id = setup_phase6_data["wh_id"]
    item_id = setup_phase6_data["item_id"]

    rec = ReplenishmentRecommendation(
        warehouse_id=wh_id, item_id=item_id, item_name="P6 Widget",
        current_stock=15, reorder_point=50, recommended_qty=100,
        urgency="URGENT_REORDER", status="REORDER_REQUIRED", reason="Stock critically low"
    )
    db.add(rec)
    db.commit()

    state = _build_state(db, wh_id)
    assert "replenishment_summary" in state
    assert state["replenishment_summary"]["urgent_count"] >= 1
    assert any(loc["health_status"] in ("CRITICAL", "LOW") for loc in state["location_inventory"].values())


# ---------------------------------------------------------------------------
# Test Scenario 14: RBAC Warehouse Authorization Enforcement
# ---------------------------------------------------------------------------
def test_scenario_14_rbac_security_enforcement(client: TestClient, phase6_restricted_user, phase6_admin, setup_phase6_data):
    wh_id = setup_phase6_data["wh_id"]

    # Login staff user without warehouse access -> 403
    staff_token = client.post("/auth/login", json={"username": phase6_restricted_user.username, "password": "StaffPass123!"}).json().get("access_token")
    res_staff = client.get(f"/digital-twin/{wh_id}/state", headers={"Authorization": f"Bearer {staff_token}"})
    assert res_staff.status_code == 403

    # Login admin -> 200
    admin_token = client.post("/auth/login", json={"username": phase6_admin.username, "password": "AdminPass123!"}).json().get("access_token")
    res_admin = client.get(f"/digital-twin/{wh_id}/state", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_admin.status_code == 200


# ---------------------------------------------------------------------------
# Test Scenario 15: Subscription Lifecycle & Queue Cleanup
# ---------------------------------------------------------------------------
def test_scenario_15_subscription_lifecycle_and_cleanup():
    """Verify subscribing and unsubscribing cleans up live listeners."""
    q = asyncio.Queue()
    broadcaster.subscribe_live("WH-P6-CLEANUP", q)
    assert "WH-P6-CLEANUP" in broadcaster.live_listeners
    assert q in broadcaster.live_listeners["WH-P6-CLEANUP"]

    broadcaster.unsubscribe_live("WH-P6-CLEANUP", q)
    assert "WH-P6-CLEANUP" not in broadcaster.live_listeners
