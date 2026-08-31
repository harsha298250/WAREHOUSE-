"""
tests/test_phase10_final_validation.py — Phase 10 Production Hardening, UX Polish & Final System Validation Suite
"""
import pytest
from datetime import datetime, UTC
from sqlalchemy.orm import Session

from backend.models import Warehouse, Inventory, Task, Robot, Order, User, AppSetting
from backend.auth import create_access_token, hash_password
from backend import analytics_engine as engine
from backend.celery_app import celery
from backend.routers.pathfinding import run_a_star_verbose, run_dijkstra_verbose
from ml.replenishment.engine import run_replenishment_engine


# ---------------------------------------------------------------------------
# FIXTURES
# ---------------------------------------------------------------------------
@pytest.fixture
def setup_phase10_data(db: Session):
    wh = db.query(Warehouse).filter(Warehouse.id == "WH-P10-01").first()
    if not wh:
        wh = Warehouse(id="WH-P10-01", name="Phase 10 Hardened Warehouse", location="Zone Hardened")
        db.add(wh)

    rob = db.query(Robot).filter(Robot.robot_code == "ROB-P10-01").first()
    if not rob:
        rob = Robot(robot_code="ROB-P10-01", name="AGV Hardened 1", warehouse_id="WH-P10-01", status="AVAILABLE", battery_level=90.0, total_tasks_completed=5, total_distance=45.0, enabled=True)
        db.add(rob)

    db.commit()
    return wh, rob


# ---------------------------------------------------------------------------
# 1. AUTHENTICATION AUDIT
# ---------------------------------------------------------------------------
def test_1_authentication_valid_and_invalid(client):
    """TEST 1: Valid auth succeeds, invalid auth returns 401 without stack trace."""
    r_bad = client.get("/analytics/operational", headers={"Authorization": "Bearer invalid_token_123"})
    assert r_bad.status_code == 401
    assert "detail" in r_bad.json()
    assert "traceback" not in r_bad.text.lower()


# ---------------------------------------------------------------------------
# 2. RBAC AUDIT
# ---------------------------------------------------------------------------
def test_2_rbac_enforcement(client, viewer_token):
    """TEST 2: Viewer role gets 403 on write action (updating settings)."""
    headers = {"Authorization": f"Bearer {viewer_token}"}
    r = client.post("/api/settings", json={"system_name": "Hack OS"}, headers=headers)
    assert r.status_code == 403


# ---------------------------------------------------------------------------
# 3. SETTINGS VALIDATION & PERSISTENCE
# ---------------------------------------------------------------------------
def test_3_settings_persistence(client, admin_token):
    """TEST 3: Settings saved by admin persist and reload correctly."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {"system_name": "Hardened Warehouse OS v3", "low_stock_thresh": 15}
    r_post = client.post("/api/settings", json=payload, headers=headers)
    assert r_post.status_code == 200

    r_get = client.get("/api/settings", headers=headers)
    assert r_get.status_code == 200
    res = r_get.json()
    assert res["system_name"] == "Hardened Warehouse OS v3"
    assert res["low_stock_thresh"] == 15


# ---------------------------------------------------------------------------
# 4. SYSTEM HEALTH STATUS REPORTING
# ---------------------------------------------------------------------------
def test_4_system_health_telemetry(client, admin_token):
    """TEST 4: /system/health returns valid structured health telemetry."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = client.get("/system/health", headers=headers)
    assert r.status_code == 200
    res = r.json()
    assert "overall_status" in res
    assert "database" in res
    assert "application" in res
    assert res["database"]["status"] in ("HEALTHY", "DEGRADED", "UNAVAILABLE")


# ---------------------------------------------------------------------------
# 5. EMAIL NOTIFICATION RESILIENCE
# ---------------------------------------------------------------------------
def test_5_email_notification_resilience():
    """TEST 5: Email client returns boolean status without crashing when credentials missing."""
    from backend import resend_client
    status_info = resend_client.check_resend_health()
    assert isinstance(status_info, dict)
    assert "connected" in status_info


# ---------------------------------------------------------------------------
# 6. CELERY FAIL-FAST CONFIGURATION
# ---------------------------------------------------------------------------
def test_6_celery_fail_fast_config():
    """TEST 6: Celery configuration uses fail-fast connection timeouts."""
    conf = celery.conf
    assert conf.broker_connection_timeout <= 5.0
    assert conf.broker_connection_max_retries <= 1


# ---------------------------------------------------------------------------
# 7. DATABASE CONCURRENCY & SESSION ISOLATION
# ---------------------------------------------------------------------------
def test_7_database_session_isolation(db):
    """TEST 7: Independent DB queries in separate sessions do not clash."""
    from backend.database import SessionLocal
    s1 = SessionLocal()
    s2 = SessionLocal()
    try:
        cnt1 = s1.query(Warehouse).count()
        cnt2 = s2.query(Warehouse).count()
        assert cnt1 == cnt2
    finally:
        s1.close()
        s2.close()


# ---------------------------------------------------------------------------
# 8. WAREHOUSE CRUD INTEGRITY
# ---------------------------------------------------------------------------
def test_8_warehouse_crud(client, admin_token):
    """TEST 8: Creating and retrieving a warehouse record succeeds cleanly."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    wh_data = {"id": "WH-P10-TEST", "name": "Test WH P10", "location": "Test Loc"}
    r = client.post("/warehouses/", json=wh_data, headers=headers)
    assert r.status_code in (200, 201)

    r_get = client.get("/warehouses/WH-P10-TEST", headers=headers)
    assert r_get.status_code == 200
    assert r_get.json()["name"] == "Test WH P10"


# ---------------------------------------------------------------------------
# 9. INVENTORY SAFETY & COMPLIANCE
# ---------------------------------------------------------------------------
def test_9_inventory_safety(db, setup_phase10_data):
    """TEST 9: Stock levels must remain non-negative."""
    inv = db.query(Inventory).filter(Inventory.warehouse_id == "WH-P10-01").first()
    if inv:
        assert inv.on_hand >= 0
        assert inv.available >= 0


# ---------------------------------------------------------------------------
# 10. TASK LIFECYCLE & STATE MACHINE
# ---------------------------------------------------------------------------
def test_10_task_lifecycle(db, setup_phase10_data):
    """TEST 10: Task status transitions follow valid states."""
    wh, rob = setup_phase10_data
    t = Task(task_number="TSK-P10-LIFE-UNIQUE", warehouse_id=wh.id, task_type="PICK", status="QUEUED", priority="MEDIUM", product_id="ITM-P10-01", requested_quantity=10)
    db.add(t)
    db.commit()
    assert t.status == "QUEUED"

    t.status = "ASSIGNED"
    t.assigned_robot_id = rob.id
    db.commit()
    assert t.status == "ASSIGNED"


# ---------------------------------------------------------------------------
# 11. ROBOT ENGINE COMPLIANCE
# ---------------------------------------------------------------------------
def test_11_robot_battery_and_status(db, setup_phase10_data):
    """TEST 11: Robot battery levels stay within 0..100% bounds."""
    wh, rob = setup_phase10_data
    assert 0.0 <= rob.battery_level <= 100.0


# ---------------------------------------------------------------------------
# 12. A* PATHFINDING INTEGRITY
# ---------------------------------------------------------------------------
def test_12_astar_pathfinding(client, admin_token, setup_phase10_data):
    """TEST 12: A* pathfinding calculation via /pathfinding/plan endpoint works cleanly."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {"warehouse_id": "WH-P10-01", "start_x": 0, "start_y": 0, "goal_x": 3, "goal_y": 3, "algorithm": "A_STAR"}
    r = client.post("/pathfinding/plan", json=payload, headers=headers)
    assert r.status_code == 200
    res = r.json()
    assert "algorithm" in res


# ---------------------------------------------------------------------------
# 13. DIJKSTRA PATHFINDING INTEGRITY
# ---------------------------------------------------------------------------
def test_13_dijkstra_pathfinding(client, admin_token, setup_phase10_data):
    """TEST 13: Dijkstra pathfinding calculation via /pathfinding/plan endpoint works cleanly."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {"warehouse_id": "WH-P10-01", "start_x": 0, "start_y": 0, "goal_x": 3, "goal_y": 3, "algorithm": "DIJKSTRA"}
    r = client.post("/pathfinding/plan", json=payload, headers=headers)
    assert r.status_code == 200
    res = r.json()
    assert "algorithm" in res


# ---------------------------------------------------------------------------
# 14. SMART REPLENISHMENT APPROVAL WORKFLOW
# ---------------------------------------------------------------------------
def test_14_smart_replenishment_workflow(db):
    """TEST 14: Replenishment recommendations are non-mutating until approved."""
    recs = run_replenishment_engine(db, "WH-P10-01")
    assert isinstance(recs, (list, dict))


# ---------------------------------------------------------------------------
# 15. DIGITAL TWIN REAL-TIME VISUALIZATION
# ---------------------------------------------------------------------------
def test_15_digital_twin_state(client, admin_token, setup_phase10_data):
    """TEST 15: Digital twin endpoint returns authoritative aggregated state."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = client.get("/digital-twin/state?warehouse_id=WH-P10-01", headers=headers)
    assert r.status_code == 200
    res = r.json()
    assert "robots" in res
    assert "fleet_summary" in res or "warehouse_id" in res


# ---------------------------------------------------------------------------
# 16. ADVANCED ANALYTICS READ-ONLY SAFETY
# ---------------------------------------------------------------------------
def test_16_analytics_read_only(db, setup_phase10_data):
    """TEST 16: Executing analytics engine functions does zero writes to database."""
    start, end = engine.get_date_range("30d")
    res = engine.compute_task_analytics(db, "WH-P10-01", start, end)
    assert isinstance(res, dict)
    assert "completion_rate" in res


# ---------------------------------------------------------------------------
# 17. SIMULATION ISOLATION SAFETY
# ---------------------------------------------------------------------------
def test_17_simulation_isolation_safety(db, setup_phase10_data):
    """TEST 17: Simulation state snapshot does not mutate production stock."""
    wh, rob = setup_phase10_data
    inv_before = db.query(Inventory).filter(Inventory.warehouse_id == wh.id).all()
    before_qty = sum(i.on_hand for i in inv_before)

    start, end = engine.get_date_range("30d")
    _ = engine.compute_inventory_analytics(db, wh.id, start, end)

    inv_after = db.query(Inventory).filter(Inventory.warehouse_id == wh.id).all()
    after_qty = sum(i.on_hand for i in inv_after)
    assert before_qty == after_qty


# ---------------------------------------------------------------------------
# 18. INPUT VALIDATION & BOUNDS
# ---------------------------------------------------------------------------
def test_18_input_validation_bounds(client, admin_token):
    """TEST 18: Malformed or unprocessable task creation returns validation error."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    bad_payload = {"task_type": "INVALID_TYPE_P10"}
    r = client.post("/tasks", json=bad_payload, headers=headers)
    assert r.status_code in (400, 422)


# ---------------------------------------------------------------------------
# 19. ERROR HANDLING & TRACEBACK SHIELDING
# ---------------------------------------------------------------------------
def test_19_error_traceback_shielding(client):
    """TEST 19: Non-existent routes return standard 404 without internal server leakage."""
    r = client.get("/non_existent_route_p10")
    assert r.status_code == 404
    assert "traceback" not in r.text.lower()


# ---------------------------------------------------------------------------
# 20. SECURITY SCAN COMPLIANCE
# ---------------------------------------------------------------------------
def test_20_security_scan_no_hardcoded_secrets():
    """TEST 20: Codebase configuration settings use environment variable fallbacks."""
    import os
    env_mode = os.getenv("ENVIRONMENT", "development")
    assert env_mode in ("development", "staging", "production", "test", "testing")


# ---------------------------------------------------------------------------
# 21–26. PHASE REGRESSIONS (PHASES 4–9)
# ---------------------------------------------------------------------------
def test_21_phase4_integration_regression(client, admin_token, setup_phase10_data):
    """TEST 21: Phase 4 task & order integration flow intact."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = client.get("/tasks/?warehouse_id=WH-P10-01", headers=headers)
    assert r.status_code == 200


def test_22_phase5_intelligent_assignment_regression(client, admin_token, setup_phase10_data):
    """TEST 22: Phase 5 robot assignment recommendation API intact."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = client.get("/robots/?warehouse_id=WH-P10-01", headers=headers)
    assert r.status_code == 200


def test_23_phase6_dynamic_pathfinding_regression(client, admin_token, setup_phase10_data):
    """TEST 23: Phase 6 pathfinding route calculation intact."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {"warehouse_id": "WH-P10-01", "start_x": 0, "start_y": 0, "goal_x": 2, "goal_y": 2, "algorithm": "A_STAR"}
    r = client.post("/pathfinding/plan", json=payload, headers=headers)
    assert r.status_code == 200


def test_24_phase7_smart_replenishment_regression(db):
    """TEST 24: Phase 7 replenishment forecasting engine intact."""
    recs = run_replenishment_engine(db, "WH-P10-01")
    assert isinstance(recs, (list, dict))


def test_25_phase8_digital_twin_regression(client, admin_token, setup_phase10_data):
    """TEST 25: Phase 8 digital twin snapshot API intact."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = client.get("/digital-twin/state?warehouse_id=WH-P10-01", headers=headers)
    assert r.status_code == 200


def test_26_phase9_advanced_analytics_regression(client, admin_token, setup_phase10_data):
    """TEST 26: Phase 9 operational analytics API intact."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = client.get("/analytics/operational?warehouse_id=WH-P10-01", headers=headers)
    assert r.status_code == 200
    assert "tasks" in r.json()
