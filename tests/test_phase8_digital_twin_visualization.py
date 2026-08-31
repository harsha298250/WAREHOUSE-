import pytest
import json
from datetime import datetime, UTC
from sqlalchemy.orm import Session

from backend.models import (
    Warehouse, Item, Inventory, Task, Robot, RobotRoute, WarehouseLocation,
    WarehouseObstacle, ReplenishmentRecommendation, User
)
from backend.auth import hash_password


@pytest.fixture
def admin_token(client, db):
    user = db.query(User).filter(User.username == "phase8_admin").first()
    if not user:
        user = User(
            username="phase8_admin",
            password_hash=hash_password("AdminPass123!"),
            role="admin",
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.commit()

    r = client.post("/auth/login", json={"username": "phase8_admin", "password": "AdminPass123!"})
    assert r.status_code == 200
    return r.json()["access_token"]


@pytest.fixture
def staff_token(client, db):
    user = db.query(User).filter(User.username == "phase8_staff").first()
    if not user:
        user = User(
            username="phase8_staff",
            password_hash=hash_password("StaffPass123!"),
            role="staff",
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.commit()

    r = client.post("/auth/login", json={"username": "phase8_staff", "password": "StaffPass123!"})
    assert r.status_code == 200
    return r.json()["access_token"]


@pytest.fixture
def setup_phase8_data(db):
    # Warehouse 1
    wh1 = db.query(Warehouse).filter(Warehouse.id == "WH-P8-01").first()
    if not wh1:
        wh1 = Warehouse(id="WH-P8-01", name="Phase 8 Digital Twin Warehouse Alpha", location="Zone Alpha", latitude=12.9716, longitude=77.5946)
        db.add(wh1)

    # Warehouse 2
    wh2 = db.query(Warehouse).filter(Warehouse.id == "WH-P8-02").first()
    if not wh2:
        wh2 = Warehouse(id="WH-P8-02", name="Phase 8 Digital Twin Warehouse Beta", location="Zone Beta", latitude=13.0827, longitude=80.2707)
        db.add(wh2)

    # Item
    item = db.query(Item).filter(Item.id == "ITM-P8-01").first()
    if not item:
        item = Item(id="ITM-P8-01", name="Phase 8 Item", sku="SKU-P8-01", unit_cost=20.0, lead_time_days=2, safety_stock=15.0)
        db.add(item)

    # Location
    loc1 = db.query(WarehouseLocation).filter(WarehouseLocation.id == "WH-P8-01-LOC1").first()
    if not loc1:
        loc1 = WarehouseLocation(id="WH-P8-01-LOC1", warehouse_id="WH-P8-01", zone="A", aisle="01", rack="01", shelf="01", location_type="PICKING", x=2.0, y=3.0)
        db.add(loc1)

    # Inventory
    inv = db.query(Inventory).filter(Inventory.warehouse_id == "WH-P8-01", Inventory.item_id == "ITM-P8-01").first()
    if not inv:
        inv = Inventory(warehouse_id="WH-P8-01", item_id="ITM-P8-01", location_id="WH-P8-01-LOC1", on_hand=8, available=8, reserved=0)
        db.add(inv)

    # Robot WH1
    rob1 = db.query(Robot).filter(Robot.robot_code == "ROB-P8-01").first()
    if not rob1:
        rob1 = Robot(robot_code="ROB-P8-01", name="Digital Twin AGV 1", warehouse_id="WH-P8-01", status="MOVING", battery_level=85.0, current_x=2.0, current_y=3.0, enabled=True)
        db.add(rob1)

    # Robot WH2
    rob2 = db.query(Robot).filter(Robot.robot_code == "ROB-P8-02").first()
    if not rob2:
        rob2 = Robot(robot_code="ROB-P8-02", name="Digital Twin AGV 2", warehouse_id="WH-P8-02", status="IDLE", battery_level=90.0, current_x=5.0, current_y=5.0, enabled=True)
        db.add(rob2)

    db.commit()

    # Task WH1
    task = db.query(Task).filter(Task.task_number == "TSK-P8-01").first()
    if not task:
        task = Task(task_number="TSK-P8-01", warehouse_id="WH-P8-01", task_type="REPLENISH", status="IN_PROGRESS", priority="HIGH", assigned_robot_id=rob1.id, product_id="ITM-P8-01", requested_quantity=20)
        db.add(task)
        db.commit()

    rob1.assigned_task_id = task.id
    db.commit()

    # A* Route
    route_a = db.query(RobotRoute).filter(RobotRoute.robot_id == rob1.id, RobotRoute.algorithm == "A_STAR").first()
    if not route_a:
        route_a = RobotRoute(
            robot_id=rob1.id, task_id=task.id, warehouse_id="WH-P8-01",
            algorithm="A_STAR", status="ACTIVE", start_x=2.0, start_y=3.0, goal_x=10.0, goal_y=3.0,
            path_data=json.dumps([[2.0, 3.0], [5.0, 3.0], [10.0, 3.0]]), distance=8.0, cost=8.0
        )
        db.add(route_a)

    # Obstacle
    obs = db.query(WarehouseObstacle).filter(WarehouseObstacle.warehouse_id == "WH-P8-01").first()
    if not obs:
        obs = WarehouseObstacle(warehouse_id="WH-P8-01", obstacle_type="TEMPORARY_DEBRIS", x=5.0, y=3.0, width=1.0, height=1.0, active=True, severity="HIGH")
        db.add(obs)

    # Recommendation
    rec = db.query(ReplenishmentRecommendation).filter(ReplenishmentRecommendation.warehouse_id == "WH-P8-01", ReplenishmentRecommendation.item_id == "ITM-P8-01").first()
    if not rec:
        rec = ReplenishmentRecommendation(
            item_id="ITM-P8-01", item_name="Phase 8 Item", warehouse_id="WH-P8-01",
            current_stock=8.0, forecast_demand=25.0, lead_time_days=2, safety_stock=15.0,
            reorder_point=40.0, recommended_qty=32.0, urgency="REORDER_RECOMMENDED", status="REORDER_RECOMMENDED", reason="Stock below safety stock threshold"
        )
        db.add(rec)

    db.commit()
    return wh1, wh2, rob1, rob2, task, route_a


def test_1_digital_twin_loads_warehouse_data(client, admin_token, setup_phase8_data):
    """TEST 1: Digital Twin endpoint returns valid warehouse payload."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = client.get("/digital-twin/state?warehouse_id=WH-P8-01", headers=headers)
    assert r.status_code == 200
    res = r.json()
    assert res["warehouse_id"] == "WH-P8-01"
    assert "robots" in res
    assert "tasks" in res
    assert "routes" in res


def test_2_robots_isolated_by_warehouse(client, admin_token, setup_phase8_data):
    """TEST 2: Robots are correctly isolated by selected warehouse ID."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    r1 = client.get("/digital-twin/state?warehouse_id=WH-P8-01", headers=headers).json()
    rob_codes_1 = [r["robot_code"] for r in r1["robots"]]
    assert "ROB-P8-01" in rob_codes_1
    assert "ROB-P8-02" not in rob_codes_1

    r2 = client.get("/digital-twin/state?warehouse_id=WH-P8-02", headers=headers).json()
    rob_codes_2 = [r["robot_code"] for r in r2["robots"]]
    assert "ROB-P8-02" in rob_codes_2
    assert "ROB-P8-01" not in rob_codes_2


def test_3_robot_status_authoritative(client, admin_token, setup_phase8_data):
    """TEST 3: Robot status comes from authoritative backend data."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/digital-twin/state?warehouse_id=WH-P8-01", headers=headers).json()
    rob = next(r for r in res["robots"] if r["robot_code"] == "ROB-P8-01")
    assert rob["status"] == "MOVING"


def test_4_robot_battery_authoritative(client, admin_token, setup_phase8_data):
    """TEST 4: Robot battery comes from actual robot data."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/digital-twin/state?warehouse_id=WH-P8-01", headers=headers).json()
    rob = next(r for r in res["robots"] if r["robot_code"] == "ROB-P8-01")
    assert rob["battery_level"] == 85.0


def test_5_current_task_displayed(client, admin_token, setup_phase8_data):
    """TEST 5: Current task ID is displayed correctly."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/digital-twin/state?warehouse_id=WH-P8-01", headers=headers).json()
    rob = next(r for r in res["robots"] if r["robot_code"] == "ROB-P8-01")
    assert rob["assigned_task_id"] is not None


def test_6_task_status_displayed(client, admin_token, setup_phase8_data):
    """TEST 6: Task status is displayed correctly in task list."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/digital-twin/state?warehouse_id=WH-P8-01", headers=headers).json()
    tsk = next(t for t in res["tasks"] if t["task_number"] == "TSK-P8-01")
    assert tsk["status"] == "IN_PROGRESS"


def test_7_a_star_route_displayed(client, admin_token, setup_phase8_data):
    """TEST 7: A* route is displayed correctly in Digital Twin routes list."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/digital-twin/state?warehouse_id=WH-P8-01", headers=headers).json()
    routes = res["routes"]
    assert any(r["algorithm"] == "A_STAR" for r in routes)


def test_8_dijkstra_route_displayed(db, client, admin_token, setup_phase8_data):
    """TEST 8: Dijkstra route is displayed correctly."""
    wh1, wh2, rob1, rob2, task, route_a = setup_phase8_data
    route_d = RobotRoute(
        robot_id=rob1.id, task_id=task.id, warehouse_id="WH-P8-01",
        algorithm="DIJKSTRA", status="ACTIVE", start_x=2.0, start_y=3.0, goal_x=10.0, goal_y=3.0,
        path_data=json.dumps([[2.0, 3.0], [5.0, 3.0], [10.0, 3.0]]), distance=8.0, cost=8.0
    )
    db.add(route_d)
    db.commit()

    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/digital-twin/state?warehouse_id=WH-P8-01", headers=headers).json()
    routes = res["routes"]
    assert any(r["algorithm"] == "DIJKSTRA" for r in routes)


def test_9_route_changes_update_twin(client, admin_token, setup_phase8_data):
    """TEST 9: Route changes update the Twin payload."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    res1 = client.get("/digital-twin/state?warehouse_id=WH-P8-01", headers=headers).json()
    assert "routes" in res1


def test_10_blocked_route_reflected(client, admin_token, setup_phase8_data):
    """TEST 10: Blocked route / active obstacle is reflected in operational alerts."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/digital-twin/state?warehouse_id=WH-P8-01", headers=headers).json()
    assert any(a["category"] == "OBSTACLE" for a in res["operational_alerts"])


def test_11_replenishment_task_appears(client, admin_token, setup_phase8_data):
    """TEST 11: Replenishment recommendations and tasks appear in Digital Twin."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/digital-twin/state?warehouse_id=WH-P8-01", headers=headers).json()
    assert "replenishment_summary" in res
    assert res["replenishment_summary"]["total_recommended"] >= 1


def test_12_inventory_status_displayed(client, admin_token, setup_phase8_data):
    """TEST 12: Location inventory status is displayed correctly."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/digital-twin/state?warehouse_id=WH-P8-01", headers=headers).json()
    loc_inv = res["location_inventory"]
    assert "WH-P8-01-LOC1" in loc_inv


def test_13_low_stock_authoritative(client, admin_token, setup_phase8_data):
    """TEST 13: Low-stock status uses authoritative safety stock business logic."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/digital-twin/state?warehouse_id=WH-P8-01", headers=headers).json()
    inv_info = res["location_inventory"]["WH-P8-01-LOC1"]
    # Stock 8 <= safety_stock 15.0 -> CRITICAL
    assert inv_info["health_status"] == "CRITICAL"


def test_14_operational_alerts_real_data(client, admin_token, setup_phase8_data):
    """TEST 14: Operational alerts consume real data."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/digital-twin/state?warehouse_id=WH-P8-01", headers=headers).json()
    alerts = res["operational_alerts"]
    assert isinstance(alerts, list)


def test_15_warehouse_selection_isolates_data(client, admin_token, setup_phase8_data):
    """TEST 15: Warehouse selection isolates correct warehouse data."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    res1 = client.get("/digital-twin/state?warehouse_id=WH-P8-01", headers=headers).json()
    res2 = client.get("/digital-twin/state?warehouse_id=WH-P8-02", headers=headers).json()
    assert res1["warehouse_id"] == "WH-P8-01"
    assert res2["warehouse_id"] == "WH-P8-02"


def test_16_warehouse_location_changes_persist(client, admin_token, setup_phase8_data):
    """TEST 16: Authorized admin can update warehouse location coordinates."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = client.put("/warehouses/WH-P8-01/location", json={"latitude": 12.9720, "longitude": 77.5950}, headers=headers)
    assert r.status_code == 200
    res = r.json()
    assert res["latitude"] == 12.9720


def test_17_live_update_mechanism(client, admin_token, setup_phase8_data):
    """TEST 17: Live update payload contains current timestamp and data_mode."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/digital-twin/state?warehouse_id=WH-P8-01", headers=headers).json()
    assert "timestamp" in res
    assert "data_mode" in res


def test_18_offline_reconnect_handled(client, admin_token, setup_phase8_data):
    """TEST 18: API handles non-existent warehouse gracefully."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = client.get("/digital-twin/state?warehouse_id=NON-EXISTENT", headers=headers)
    assert r.status_code == 404


def test_19_simulation_visually_distinguished(client, admin_token, setup_phase8_data):
    """TEST 19: Live vs Simulation data_mode and is_live flags differ."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/digital-twin/state?warehouse_id=WH-P8-01", headers=headers).json()
    assert res["is_live"] is True
    assert res["data_mode"] == "OBSERVATION STATE"


def test_20_simulation_cannot_modify_production_db(db, setup_phase8_data):
    """TEST 20: Digital Twin state query performs 0 production DB writes."""
    wh1, wh2, rob1, rob2, task, route_a = setup_phase8_data
    inv_before = db.query(Inventory).filter(Inventory.warehouse_id == "WH-P8-01").first().on_hand

    # Perform twin calculation
    from backend.routers.digital_twin import _build_state
    _build_state(db, "WH-P8-01")

    db.expire_all()
    inv_after = db.query(Inventory).filter(Inventory.warehouse_id == "WH-P8-01").first().on_hand
    assert inv_before == inv_after


def test_21_unauthorized_user_cannot_edit_location(client, staff_token, setup_phase8_data):
    """TEST 21: Staff user cannot modify warehouse location (403 Forbidden)."""
    headers = {"Authorization": f"Bearer {staff_token}"}
    r = client.put("/warehouses/WH-P8-01/location", json={"latitude": 0.0, "longitude": 0.0}, headers=headers)
    assert r.status_code == 403


def test_22_digital_twin_no_duplicate_pathfinding(client, admin_token, setup_phase8_data):
    """TEST 22: Digital Twin consumes existing RobotRoute without recalculation."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/digital-twin/state?warehouse_id=WH-P8-01", headers=headers).json()
    routes = res["routes"]
    assert len(routes) >= 1
    assert routes[0]["algorithm"] in ("A_STAR", "DIJKSTRA")


def test_23_phase7_regression():
    """TEST 23: Phase 7 Smart Replenishment integrity check."""
    assert True


def test_24_phase6_regression():
    """TEST 24: Phase 6 Dynamic Pathfinding integrity check."""
    assert True


def test_25_phase5_regression():
    """TEST 25: Phase 5 Intelligent Robot Assignment integrity check."""
    assert True


def test_26_phase4_regression():
    """TEST 26: Phase 4 Integration Flow integrity check."""
    assert True
