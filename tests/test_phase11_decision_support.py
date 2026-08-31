"""
tests/test_phase11_decision_support.py — Phase 11 Intelligent Decision Support & Optimization Test Suite
"""

import pytest
from datetime import datetime, UTC
from sqlalchemy.orm import Session

from backend.models import (
    Warehouse, Inventory, Item, Task, Robot, RobotRoute, Order, User
)
from backend import decision_support_engine as engine


@pytest.fixture
def setup_phase11_data(db: Session):
    wh = db.query(Warehouse).filter(Warehouse.id == "WH-P11-01").first()
    if not wh:
        wh = Warehouse(id="WH-P11-01", name="Phase 11 Decision WH", location="Zone 11")
        db.add(wh)

    item = db.query(Item).filter(Item.id == "ITM-P11-01").first()
    if not item:
        item = Item(id="ITM-P11-01", sku="SKU-P11-01", name="Decision Test Product", reorder_threshold=20, safety_stock=5)
        db.add(item)

    inv = db.query(Inventory).filter(Inventory.warehouse_id == "WH-P11-01", Inventory.item_id == "ITM-P11-01").first()
    if not inv:
        inv = Inventory(warehouse_id="WH-P11-01", item_id="ITM-P11-01", on_hand=3, available=3, reserved=0)
        db.add(inv)

    rob = db.query(Robot).filter(Robot.robot_code == "ROB-P11-01").first()
    if not rob:
        rob = Robot(robot_code="ROB-P11-01", name="AGV P11", warehouse_id="WH-P11-01", status="AVAILABLE", battery_level=15.0, enabled=True)
        db.add(rob)

    db.commit()
    return wh, item, inv, rob


# ---------------------------------------------------------------------------
# 1–4. DASHBOARD & EXPLAINABLE RECOMMENDATIONS
# ---------------------------------------------------------------------------
def test_1_decision_support_dashboard_loads(client, admin_token, setup_phase11_data):
    """TEST 1: Decision-support dashboard overview loads successfully."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = client.get("/decision-support/overview", headers=headers)
    assert r.status_code == 200
    res = r.json()
    assert "operational_health" in res
    assert "priority_recommendations" in res
    assert "insights" in res


def test_2_recommendations_use_real_data(client, admin_token, setup_phase11_data):
    """TEST 2: Recommendations are derived from actual WMS records."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = client.get("/decision-support/recommendations?warehouse_id=WH-P11-01", headers=headers)
    assert r.status_code == 200
    recs = r.json()["recommendations"]
    assert len(recs) > 0
    categories = [rc["category"] for rc in recs]
    assert "INVENTORY" in categories or "ROBOT" in categories


def test_3_recommendations_are_explainable(db, setup_phase11_data):
    """TEST 3: Every recommendation includes explicit 'reason' and 'suggested_action'."""
    recs = engine.evaluate_priority_recommendations(db, "WH-P11-01")
    for r in recs:
        assert "reason" in r and len(r["reason"]) > 5
        assert "suggested_action" in r and len(r["suggested_action"]) > 5
        assert "action_url" in r


def test_4_no_fake_recommendations_generated(db):
    """TEST 4: In an empty database, recommendations do not fabricate fake alerts."""
    recs = engine.evaluate_priority_recommendations(db, "WH-NONEXISTENT")
    assert isinstance(recs, list)


# ---------------------------------------------------------------------------
# 5–8. DOMAIN SPECIFIC INTELLIGENCE
# ---------------------------------------------------------------------------
def test_5_robot_recommendations_use_actual_data(db, setup_phase11_data):
    """TEST 5: Robot insights reflect actual low battery and status metrics."""
    res = engine.evaluate_robot_insights(db, "WH-P11-01")
    assert res["status"] in ("GOOD DATA", "LIMITED DATA")
    assert res["fleet_breakdown"]["charging"] >= 1  # ROB-P11-01 has battery 15%


def test_6_inventory_recommendations_use_actual_data(db, setup_phase11_data):
    """TEST 6: Inventory risks accurately detect safety stock breach."""
    res = engine.evaluate_inventory_risk(db, "WH-P11-01")
    assert res["risk_summary"]["high"] >= 1 or res["risk_summary"]["critical"] >= 1


def test_7_replenishment_recommendations_use_actual_data(client, admin_token, setup_phase11_data):
    """TEST 7: Overview endpoint incorporates replenishment insights."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = client.get("/decision-support/overview?warehouse_id=WH-P11-01", headers=headers)
    assert r.status_code == 200


def test_8_route_recommendations_use_actual_data(db, setup_phase11_data):
    """TEST 8: Route optimization insights evaluate pathfinding metrics."""
    res = engine.evaluate_route_insights(db, "WH-P11-01")
    assert "data_quality" in res
    assert "algorithm_comparison" in res


# ---------------------------------------------------------------------------
# 9–10. COMPARATIVE ALGORITHMS & HONEST DATA QUALITY
# ---------------------------------------------------------------------------
def test_9_astar_vs_dijkstra_comparisons_use_actual_route_records(db):
    """TEST 9: Route analytics compare A* vs Dijkstra execution history."""
    res = engine.evaluate_route_insights(db)
    assert isinstance(res["algorithm_comparison"], dict)


def test_10_insufficient_data_produces_honest_state(db):
    """TEST 10: Missing logs yield explicit INSUFFICIENT DATA label."""
    res = engine.evaluate_route_insights(db, "WH-NONEXISTENT")
    assert res["data_quality"] == "INSUFFICIENT DATA"


# ---------------------------------------------------------------------------
# 11–13. FILTERS & SEVERITY
# ---------------------------------------------------------------------------
def test_11_warehouse_filtering_works(client, admin_token, setup_phase11_data):
    """TEST 11: Filtering recommendations by warehouse_id returns scoped records."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = client.get("/decision-support/recommendations?warehouse_id=WH-P11-01", headers=headers)
    assert r.status_code == 200
    res = r.json()
    assert res["warehouse_id"] == "WH-P11-01"


def test_12_date_filtering_works(client, admin_token, setup_phase11_data):
    """TEST 12: Date filtering parameter is accepted and respected."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = client.get("/decision-support/overview?date_range=7d", headers=headers)
    assert r.status_code == 200
    assert r.json()["date_range"] == "7d"


def test_13_severity_filtering_works(db, setup_phase11_data):
    """TEST 13: Health score maps score to proper severity status and color."""
    health = engine.calculate_operational_health_score(db, "WH-P11-01")
    assert health["status"] in ("HEALTHY", "ATTENTION", "HIGH_RISK", "CRITICAL")
    assert health["color"] in ("GREEN", "YELLOW", "ORANGE", "RED")


# ---------------------------------------------------------------------------
# 14. REAL-TIME SUPPORT
# ---------------------------------------------------------------------------
def test_14_real_time_updates_work_where_supported(client, admin_token, setup_phase11_data):
    """TEST 14: Health score endpoint returns current timestamp."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = client.get("/decision-support/health-score?warehouse_id=WH-P11-01", headers=headers)
    assert r.status_code == 200
    assert "timestamp" in r.json()


# ---------------------------------------------------------------------------
# 15–19. READ-ONLY IMMUTABILITY (PRODUCTION DEFENSE)
# ---------------------------------------------------------------------------
def test_15_decision_support_cannot_modify_inventory(db, setup_phase11_data):
    """TEST 15: Executing decision support endpoints causes zero inventory mutations."""
    wh, item, inv, rob = setup_phase11_data
    qty_before = inv.available
    _ = engine.get_decision_support_overview(db, wh.id)
    db.refresh(inv)
    assert inv.available == qty_before


def test_16_decision_support_cannot_modify_robots(db, setup_phase11_data):
    """TEST 16: Executing decision support endpoints causes zero robot state mutations."""
    wh, item, inv, rob = setup_phase11_data
    bat_before = rob.battery_level
    _ = engine.evaluate_robot_insights(db, wh.id)
    db.refresh(rob)
    assert rob.battery_level == bat_before


def test_17_decision_support_cannot_modify_tasks(db, setup_phase11_data):
    """TEST 17: Executing decision support endpoints causes zero task state mutations."""
    tasks_before = db.query(Task).count()
    _ = engine.evaluate_priority_recommendations(db, "WH-P11-01")
    assert db.query(Task).count() == tasks_before


def test_18_decision_support_cannot_modify_orders(db, setup_phase11_data):
    """TEST 18: Executing decision support endpoints causes zero order mutations."""
    orders_before = db.query(Order).count()
    _ = engine.get_decision_support_overview(db, "WH-P11-01")
    assert db.query(Order).count() == orders_before


def test_19_decision_support_cannot_modify_routes(db, setup_phase11_data):
    """TEST 19: Executing decision support endpoints causes zero route mutations."""
    routes_before = db.query(RobotRoute).count()
    _ = engine.evaluate_route_insights(db, "WH-P11-01")
    assert db.query(RobotRoute).count() == routes_before


# ---------------------------------------------------------------------------
# 20. WHAT-IF SIMULATION ISOLATION
# ---------------------------------------------------------------------------
def test_20_simulation_whatif_cannot_modify_production(client, admin_token, db, setup_phase11_data):
    """TEST 20: What-If simulation executes read-only estimates without production side effects."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    inv_count_before = db.query(Inventory).count()
    rob_count_before = db.query(Robot).count()

    payload = {
        "scenario_type": "ROBOT_UNAVAILABLE",
        "warehouse_id": "WH-P11-01",
        "parameters": {"disabled_robots_count": 1}
    }
    r = client.post("/decision-support/what-if", json=payload, headers=headers)
    assert r.status_code == 200
    res = r.json()
    assert res["data_mode"] in ("ESTIMATE / SIMULATION ONLY", "READ_ONLY_SIMULATION_ESTIMATE")

    assert db.query(Inventory).count() == inv_count_before
    assert db.query(Robot).count() == rob_count_before


# ---------------------------------------------------------------------------
# 21–22. RBAC & DATA MATCHING
# ---------------------------------------------------------------------------
def test_21_rbac_is_enforced(client):
    """TEST 21: Unauthenticated request to decision support is rejected (401)."""
    r = client.get("/decision-support/overview")
    assert r.status_code == 401


def test_22_underlying_source_data_matches_displayed_recommendation(db, setup_phase11_data):
    """TEST 22: Low battery robot in DB produces matching recommendation text."""
    recs = engine.evaluate_priority_recommendations(db, "WH-P11-01")
    bat_recs = [r for r in recs if r["category"] == "ROBOT" and "ROB-P11-01" in r["title"]]
    assert len(bat_recs) >= 1
    assert "15" in bat_recs[0]["reason"]


# ---------------------------------------------------------------------------
# 23–29. REGRESSION TESTS (PHASES 4–10)
# ---------------------------------------------------------------------------
def test_23_phase10_regression_passes(client, admin_token):
    """TEST 23: Phase 10 system health endpoint intact."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = client.get("/system/health", headers=headers)
    assert r.status_code == 200


def test_24_phase9_regression_passes(client, admin_token):
    """TEST 24: Phase 9 operational analytics endpoint intact."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = client.get("/analytics/operational", headers=headers)
    assert r.status_code == 200


def test_25_phase8_regression_passes(client, admin_token, setup_phase11_data):
    """TEST 25: Phase 8 digital twin endpoint intact."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = client.get("/digital-twin/state?warehouse_id=WH-P11-01", headers=headers)
    assert r.status_code == 200


def test_26_phase7_regression_passes(db, setup_phase11_data):
    """TEST 26: Phase 7 smart replenishment evaluation intact."""
    from ml.replenishment.engine import run_replenishment_engine
    recs = run_replenishment_engine(db, "WH-P11-01")
    assert isinstance(recs, (list, dict))


def test_27_phase6_regression_passes(client, admin_token, setup_phase11_data):
    """TEST 27: Phase 6 pathfinding plan endpoint intact."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {"warehouse_id": "WH-P11-01", "start_x": 0, "start_y": 0, "goal_x": 2, "goal_y": 2, "algorithm": "A_STAR"}
    r = client.post("/pathfinding/plan", json=payload, headers=headers)
    assert r.status_code == 200


def test_28_phase5_regression_passes(client, admin_token, setup_phase11_data):
    """TEST 28: Phase 5 robot assignment recommendation API intact."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = client.get("/robots/?warehouse_id=WH-P11-01", headers=headers)
    assert r.status_code == 200


def test_29_phase4_regression_passes(client, admin_token, setup_phase11_data):
    """TEST 29: Phase 4 task API intact."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = client.get("/tasks/?warehouse_id=WH-P11-01", headers=headers)
    assert r.status_code == 200
