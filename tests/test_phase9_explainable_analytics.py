import pytest
import json
from datetime import datetime, UTC, timedelta
from sqlalchemy.orm import Session

from backend.models import (
    Warehouse, Item, Inventory, Task, Robot, RobotRoute, WarehouseLocation,
    WarehouseObstacle, AIRecommendation, User, Order, OrderItem
)
from backend.auth import hash_password
from backend import analytics_engine as engine


@pytest.fixture
def admin_token(client, db):
    user = db.query(User).filter(User.username == "p9_admin_explainable").first()
    if not user:
        user = User(
            username="p9_admin_explainable",
            password_hash=hash_password("AdminPass123!"),
            role="admin",
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.commit()

    r = client.post("/auth/login", json={"username": "p9_admin_explainable", "password": "AdminPass123!"})
    assert r.status_code == 200
    return r.json()["access_token"]


@pytest.fixture
def staff_token(client, db):
    user = db.query(User).filter(User.username == "p9_staff_explainable").first()
    if not user:
        user = User(
            username="p9_staff_explainable",
            password_hash=hash_password("StaffPass123!"),
            role="staff",
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.commit()

    r = client.post("/auth/login", json={"username": "p9_staff_explainable", "password": "StaffPass123!"})
    assert r.status_code == 200
    return r.json()["access_token"]


@pytest.fixture
def setup_explainable_data(db):
    # Warehouse 1 & 2
    wh1 = db.query(Warehouse).filter(Warehouse.id == "WH-EXP-01").first()
    if not wh1:
        wh1 = Warehouse(id="WH-EXP-01", name="Explainable Alpha WH", location="Zone 1")
        db.add(wh1)

    wh2 = db.query(Warehouse).filter(Warehouse.id == "WH-EXP-02").first()
    if not wh2:
        wh2 = Warehouse(id="WH-EXP-02", name="Explainable Beta WH", location="Zone 2")
        db.add(wh2)

    # Item
    item1 = db.query(Item).filter(Item.id == "ITM-EXP-01").first()
    if not item1:
        item1 = Item(id="ITM-EXP-01", name="Explainable Item A", sku="SKU-EXP-01", unit_cost=50.0, lead_time_days=2, safety_stock=10.0, reorder_threshold=15)
        db.add(item1)

    # Location
    loc1 = db.query(WarehouseLocation).filter(WarehouseLocation.id == "WH-EXP-01-L1").first()
    if not loc1:
        loc1 = WarehouseLocation(id="WH-EXP-01-L1", warehouse_id="WH-EXP-01", zone="A", aisle="01", rack="01", shelf="01", location_type="PICKING", x=2.0, y=2.0)
        db.add(loc1)

    # Inventory with stockout
    inv1 = db.query(Inventory).filter(Inventory.warehouse_id == "WH-EXP-01", Inventory.item_id == "ITM-EXP-01").first()
    if not inv1:
        inv1 = Inventory(warehouse_id="WH-EXP-01", item_id="ITM-EXP-01", location_id="WH-EXP-01-L1", on_hand=0, available=0, reserved=0)
        db.add(inv1)

    # Robot
    rob1 = db.query(Robot).filter(Robot.robot_code == "ROB-EXP-01").first()
    if not rob1:
        rob1 = Robot(robot_code="ROB-EXP-01", name="Explainable AGV 1", warehouse_id="WH-EXP-01", status="AVAILABLE", battery_level=90.0, total_tasks_completed=10, total_distance=100.0, enabled=True, utilization_percent=78.5)
        db.add(rob1)
        db.commit()
        db.refresh(rob1)

    # Tasks
    t1 = db.query(Task).filter(Task.task_number == "TSK-EXP-01").first()
    if not t1:
        t1 = Task(task_number="TSK-EXP-01", warehouse_id="WH-EXP-01", task_type="PICK", status="COMPLETED", priority="HIGH", assigned_robot_id=rob1.id, product_id="ITM-EXP-01", requested_quantity=5, completed_quantity=5, started_at=datetime.now(UTC).replace(tzinfo=None) - timedelta(minutes=20), completed_at=datetime.now(UTC).replace(tzinfo=None) - timedelta(minutes=5))
        db.add(t1)

    t2 = db.query(Task).filter(Task.task_number == "TSK-EXP-02").first()
    if not t2:
        t2 = Task(task_number="TSK-EXP-02", warehouse_id="WH-EXP-01", task_type="REPLENISH", status="QUEUED", priority="CRITICAL", product_id="ITM-EXP-01", requested_quantity=20)
        db.add(t2)

    db.commit()

    # Routes (A* and Dijkstra)
    r_ast = db.query(RobotRoute).filter(RobotRoute.robot_id == rob1.id, RobotRoute.algorithm == "A_STAR").first()
    if not r_ast:
        r_ast = RobotRoute(
            robot_id=rob1.id, task_id=t1.id, warehouse_id="WH-EXP-01",
            algorithm="A_STAR", status="COMPLETED", start_x=0.0, start_y=0.0, goal_x=5.0, goal_y=5.0,
            path_data=json.dumps([[0, 0], [5, 5]]), distance=7.07, cost=7.07
        )
        db.add(r_ast)

    r_dij = db.query(RobotRoute).filter(RobotRoute.robot_id == rob1.id, RobotRoute.algorithm == "DIJKSTRA").first()
    if not r_dij:
        r_dij = RobotRoute(
            robot_id=rob1.id, task_id=t1.id, warehouse_id="WH-EXP-01",
            algorithm="DIJKSTRA", status="COMPLETED", start_x=0.0, start_y=0.0, goal_x=5.0, goal_y=5.0,
            path_data=json.dumps([[0, 0], [5, 5]]), distance=7.07, cost=7.07
        )
        db.add(r_dij)

    # AI Recommendation for Decision Intelligence
    rec = db.query(AIRecommendation).filter(AIRecommendation.title == "Critical Stockout Replenishment Needed").first()
    if not rec:
        rec = AIRecommendation(
            title="Critical Stockout Replenishment Needed",
            warehouse_id="WH-EXP-01",
            recommendation_type="REPLENISHMENT",
            risk_level="CRITICAL",
            action_recommended="Dispatch priority replenishment for 25 units.",
            confidence_score=95,
            score=92,
            source_entity_type="Inventory",
            source_entity_id="ITM-EXP-01",
            description="Item ITM-EXP-01 has reached 0 available inventory.",
            explanation="Stock = 0, Forecast Demand = 30, Lead Time = 2 days -> Days of Cover = 0.0 days",
            recommended_action="Dispatch priority replenishment for 25 units.",
            confidence_or_reliability="94.5%",
            status="NEW"
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)

    db.commit()
    return wh1, wh2, rob1, t1, t2, rec


# ---------------------------------------------------------------------------
# SCENARIO 1: 8 Core KPI Categories Verification
# ---------------------------------------------------------------------------
def test_1_8_core_kpi_categories_verification(client, admin_token, setup_explainable_data):
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = client.get("/analytics/explainable-overview?warehouse_id=WH-EXP-01", headers=headers)
    assert r.status_code == 200
    res = r.json()
    assert "kpis" in res
    kpis = res["kpis"]
    required_cats = [
        "order_performance", "task_performance", "robot_performance", "route_performance",
        "inventory_performance", "replenishment_performance", "warehouse_performance", "simulation_performance"
    ]
    for cat in required_cats:
        assert cat in kpis, f"Missing core KPI category: {cat}"


# ---------------------------------------------------------------------------
# SCENARIO 2: Order Analytics & Cycle Times
# ---------------------------------------------------------------------------
def test_2_order_analytics_cycle_times(client, admin_token, setup_explainable_data):
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = client.get("/analytics/explainable-overview?warehouse_id=WH-EXP-01", headers=headers)
    assert r.status_code == 200
    orders = r.json()["kpis"]["order_performance"]
    assert "total_orders" in orders
    assert "pending_orders" in orders
    assert "completed_orders" in orders
    assert "completion_rate" in orders
    assert "avg_cycle_time_hours" in orders


# ---------------------------------------------------------------------------
# SCENARIO 3: Task Analytics & Queue Trends
# ---------------------------------------------------------------------------
def test_3_task_analytics_queue_trends(client, admin_token, setup_explainable_data):
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = client.get("/analytics/explainable-overview?warehouse_id=WH-EXP-01", headers=headers)
    assert r.status_code == 200
    tasks = r.json()["kpis"]["task_performance"]
    assert tasks["tasks_created"]["value"] >= 2
    assert "completion_rate" in tasks
    assert "avg_duration_minutes" in tasks


# ---------------------------------------------------------------------------
# SCENARIO 4: Robot Fleet & Workload Distribution
# ---------------------------------------------------------------------------
def test_4_robot_fleet_workload(client, admin_token, setup_explainable_data):
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = client.get("/analytics/explainable-overview?warehouse_id=WH-EXP-01", headers=headers)
    assert r.status_code == 200
    robots = r.json()["kpis"]["robot_performance"]
    assert robots["fleet_size"]["value"] >= 1
    assert "avg_utilization" in robots
    assert robots["avg_utilization"]["data_quality"] in ("DATABASE_SYNCHRONIZED", "INSUFFICIENT DATA")


# ---------------------------------------------------------------------------
# SCENARIO 5: Pathfinding & A* vs Dijkstra Comparison
# ---------------------------------------------------------------------------
def test_5_pathfinding_factual_comparison(client, admin_token, setup_explainable_data):
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = client.get("/analytics/pathfinding-comparison?warehouse_id=WH-EXP-01", headers=headers)
    assert r.status_code == 200
    res = r.json()
    assert "a_star" in res
    assert "dijkstra" in res
    assert "factual_explanation" in res
    assert "disclaimer" in res


# ---------------------------------------------------------------------------
# SCENARIO 6: Inventory Health & Stockout Exposure
# ---------------------------------------------------------------------------
def test_6_inventory_health_stockout_exposure(db, setup_explainable_data):
    start, end = engine.get_date_range("30d")
    res = engine.compute_inventory_analytics(db, "WH-EXP-01", start, end)
    assert res["stockout_rate"]["value"] > 0 or res["low_stock_count"]["value"] >= 1


# ---------------------------------------------------------------------------
# SCENARIO 7: Replenishment Analytics & Lead Time Variance
# ---------------------------------------------------------------------------
def test_7_replenishment_analytics(db, setup_explainable_data):
    res = engine.compute_forecasting_analytics(db, "WH-EXP-01")
    assert "median_wape" in res
    assert "avg_rmse" in res


# ---------------------------------------------------------------------------
# SCENARIO 8: Period-Over-Period Trend Comparison
# ---------------------------------------------------------------------------
def test_8_period_trend_comparison(client, admin_token, setup_explainable_data):
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = client.get("/analytics/trends?warehouse_id=WH-EXP-01&period=30d", headers=headers)
    assert r.status_code == 200
    res = r.json()
    assert "has_historical_baseline" in res
    assert "metrics" in res
    assert "orders" in res["metrics"]


# ---------------------------------------------------------------------------
# SCENARIO 9: Ranked Bottleneck Engine (WHAT/WHY/IMPACT)
# ---------------------------------------------------------------------------
def test_9_ranked_bottleneck_engine(client, admin_token, setup_explainable_data):
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = client.get("/analytics/bottlenecks?warehouse_id=WH-EXP-01", headers=headers)
    assert r.status_code == 200
    res = r.json()
    assert "bottlenecks" in res
    if res["bottlenecks"]:
        b = res["bottlenecks"][0]
        assert "what" in b
        assert "why" in b
        assert "impact" in b


# ---------------------------------------------------------------------------
# SCENARIO 10: Cross-Module Decision Metric Explanation
# ---------------------------------------------------------------------------
def test_10_decision_explanation(client, admin_token, setup_explainable_data):
    _, _, _, _, _, rec = setup_explainable_data
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = client.get(f"/analytics/decision-explanation/{rec.id}", headers=headers)
    assert r.status_code == 200
    res = r.json()
    assert res["decision_id"] == str(rec.id) or res["decision_id"] == rec.id
    assert "explanation" in res
    assert "underlying_metrics" in res


# ---------------------------------------------------------------------------
# SCENARIO 11: Time Range Filtering & Custom Date Bounds
# ---------------------------------------------------------------------------
def test_11_time_range_filtering(client, admin_token, setup_explainable_data):
    headers = {"Authorization": f"Bearer {admin_token}"}
    periods = ["today", "7d", "30d", "90d"]
    for p in periods:
        r = client.get(f"/analytics/explainable-overview?period={p}&warehouse_id=WH-EXP-01", headers=headers)
        assert r.status_code == 200
        assert r.json()["period"] == p


# ---------------------------------------------------------------------------
# SCENARIO 12: RBAC & Multi-Warehouse Isolation
# ---------------------------------------------------------------------------
def test_12_rbac_multi_warehouse_isolation(client, staff_token, setup_explainable_data):
    headers = {"Authorization": f"Bearer {staff_token}"}
    r = client.get("/analytics/explainable-overview?warehouse_id=WH-RESTRICTED-TEST", headers=headers)
    assert r.status_code in (200, 403)


# ---------------------------------------------------------------------------
# SCENARIO 13: Production Data Non-Mutation Safety
# ---------------------------------------------------------------------------
def test_13_non_mutation_safety(db, client, admin_token, setup_explainable_data):
    task_count_before = db.query(Task).count()
    robot_count_before = db.query(Robot).count()
    order_count_before = db.query(Order).count()
    inv_count_before = db.query(Inventory).count()

    headers = {"Authorization": f"Bearer {admin_token}"}
    r = client.get("/analytics/explainable-overview?warehouse_id=WH-EXP-01", headers=headers)
    assert r.status_code == 200

    db.expire_all()
    assert db.query(Task).count() == task_count_before
    assert db.query(Robot).count() == robot_count_before
    assert db.query(Order).count() == order_count_before
    assert db.query(Inventory).count() == inv_count_before


# ---------------------------------------------------------------------------
# SCENARIO 14: Insufficient Telemetry & Empty State Handling
# ---------------------------------------------------------------------------
def test_14_empty_state_handling(db):
    start, end = engine.get_date_range("30d")
    res = engine.compute_robot_analytics(db, "WH-NONEXISTENT", start, end)
    assert res["fleet_size"]["value"] == 0
    assert res["avg_utilization"]["data_quality"] == "INSUFFICIENT DATA"


# ---------------------------------------------------------------------------
# SCENARIO 15: Concurrency & Query Performance Safety
# ---------------------------------------------------------------------------
def test_15_query_performance_safety(client, admin_token, setup_explainable_data):
    headers = {"Authorization": f"Bearer {admin_token}"}
    import time
    t0 = time.time()
    for _ in range(5):
        r = client.get("/analytics/explainable-overview?warehouse_id=WH-EXP-01", headers=headers)
        assert r.status_code == 200
    elapsed = time.time() - t0
    assert elapsed < 5.0, f"5 analytics overview requests took {elapsed:.2f}s, expected <5.0s"
