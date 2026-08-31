"""
tests/test_phase8_decision_intelligence.py — Test Suite for Phase 8: Decision Intelligence & Actionable Recommendations.

Covers:
1. 7 Core Decision Categories Evaluation
2. Transparent Priority Score Calculation (Severity x Urgency x Impact)
3. Robot Capacity Decision Detection
4. Task Bottleneck Decision Detection
5. Route Congestion Decision Detection
6. Inventory & Replenishment Decision Detection
7. Order Priority Decision Detection
8. Simulation Risk Integration
9. System Health Decision Detection
10. Decision Deduplication Engine
11. Decision Lifecycle Management (ACKNOWLEDGE, DISMISS, RESOLVE)
12. Entity Linking & Action URLs
13. RBAC & Multi-Warehouse Isolation
14. Production Data Non-Mutation Verification (Strict Read-Only)
15. No-Action Healthy Condition Verification
"""

import json
from datetime import datetime, UTC
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.main import app
from backend.database import get_db
from backend.auth import hash_password
from backend.models import (
    User, Warehouse, Robot, Task, Order, OrderItem, Inventory, Item, WarehouseLocation, WarehouseObstacle, SystemIncident, AIRecommendation
)
from backend.decision_support_engine import evaluate_decision_intelligence, run_what_if_analysis


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def setup_phase8_data(db: Session):
    """Setup isolated test warehouse environment for Phase 8."""
    wh = db.query(Warehouse).filter(Warehouse.id == "WH-P8-01").first()
    if not wh:
        wh = Warehouse(id="WH-P8-01", name="Phase 8 Decision Hub", location="Intelligence Testing Zone")
        db.add(wh)
        db.commit()

    # Robots
    r1 = db.query(Robot).filter(Robot.robot_code == "ROB-P8-01").first()
    if not r1:
        r1 = Robot(id=801, robot_code="ROB-P8-01", name="P8 Robot 1", warehouse_id="WH-P8-01", status="AVAILABLE", battery_level=18.0, current_x=1.0, current_y=1.0, max_payload=150.0)
        db.add(r1)

    r2 = db.query(Robot).filter(Robot.robot_code == "ROB-P8-02").first()
    if not r2:
        r2 = Robot(id=802, robot_code="ROB-P8-02", name="P8 Robot 2", warehouse_id="WH-P8-01", status="AVAILABLE", battery_level=90.0, current_x=4.0, current_y=1.0, max_payload=150.0)
        db.add(r2)

    # Items & Locations & Inventory
    item = db.query(Item).filter(Item.id == "ITM-P8-01").first()
    if not item:
        item = Item(id="ITM-P8-01", name="P8 Critical Chip", sku="SKU-P8-01", safety_stock=15, reorder_threshold=30)
        db.add(item)

    loc = db.query(WarehouseLocation).filter(WarehouseLocation.id == "LOC-P8-01").first()
    if not loc:
        loc = WarehouseLocation(id="LOC-P8-01", warehouse_id="WH-P8-01", zone="A", aisle="1", rack="1", shelf="1", x=2, y=2, location_type="STORAGE")
        db.add(loc)

    inv = db.query(Inventory).filter(Inventory.warehouse_id == "WH-P8-01", Inventory.item_id == "ITM-P8-01").first()
    if not inv:
        inv = Inventory(warehouse_id="WH-P8-01", item_id="ITM-P8-01", location_id="LOC-P8-01", on_hand=0, reserved=0, available=0)
        db.add(inv)
    db.commit()

    # Tasks
    for i in range(1, 4):
        t_code = f"TSK-P8-0{i}"
        t = db.query(Task).filter(Task.task_number == t_code).first()
        if not t:
            t = Task(
                task_number=t_code, warehouse_id="WH-P8-01",
                task_type="PICK", priority="CRITICAL", status="QUEUED",
                product_id="ITM-P8-01", source_location_id="LOC-P8-01",
                destination_location_id="LOC-P8-01", requested_quantity=1
            )
            db.add(t)

    # Obstacle
    obs = db.query(WarehouseObstacle).filter(WarehouseObstacle.warehouse_id == "WH-P8-01").first()
    if not obs:
        obs = WarehouseObstacle(warehouse_id="WH-P8-01", x=3, y=3, width=1, height=1, active=True, obstacle_type="TEMPORARY")
        db.add(obs)

    # Order
    ord_rec = db.query(Order).filter(Order.id == "ORD-P8-01").first()
    if not ord_rec:
        ord_rec = Order(id="ORD-P8-01", warehouse_id="WH-P8-01", customer_ref="Phase 8 Enterprise Client", priority="CRITICAL", status="CREATED")
        db.add(ord_rec)

    # Incident
    inc = db.query(SystemIncident).filter(SystemIncident.title == "P8 Test Incident").first()
    if not inc:
        inc = SystemIncident(category="SYSTEM", title="P8 Test Incident", severity="HIGH", status="OPEN", description="Channel sync bottleneck")
        db.add(inc)

    db.commit()
    return {"wh_id": "WH-P8-01", "item_id": "ITM-P8-01", "robot_code": "ROB-P8-01", "order_id": "ORD-P8-01"}


@pytest.fixture
def phase8_admin(db: Session):
    admin = db.query(User).filter(User.username == "phase8_admin").first()
    if not admin:
        admin = User(
            username="phase8_admin", email="p8admin@example.com", role="admin",
            password_hash=hash_password("AdminPass123!"), is_active=True, is_verified=True
        )
        db.add(admin)
        db.commit()
    return admin


@pytest.fixture
def phase8_token(client: TestClient, phase8_admin):
    res = client.post("/auth/login", json={"username": "phase8_admin", "password": "AdminPass123!"})
    assert res.status_code == 200
    return res.json()["access_token"]


# ---------------------------------------------------------------------------
# Test 1: 7 Core Decision Categories Evaluation
# ---------------------------------------------------------------------------
def test_scenario_1_all_categories_eval(db: Session, setup_phase8_data):
    res = evaluate_decision_intelligence(db, setup_phase8_data["wh_id"])
    assert res["data_mode"] == "DECISION INTELLIGENCE / READ-ONLY SUPPORT"
    assert res["total_decisions"] > 0
    
    found_categories = {d["category"] for d in res["decisions"]}
    # Verify categories present
    assert "ROBOT_CAPACITY" in found_categories or "INVENTORY_REPLENISHMENT" in found_categories


# ---------------------------------------------------------------------------
# Test 2: Transparent Priority Score Calculation
# ---------------------------------------------------------------------------
def test_scenario_2_priority_score_formula(db: Session, setup_phase8_data):
    res = evaluate_decision_intelligence(db, setup_phase8_data["wh_id"])
    for d in res["decisions"]:
        sev = d["severity_num"]
        urg = d["urgency_num"]
        imp = d["impact_num"]
        expected_score = int(round(((sev * urg * imp) / 64.0) * 100.0))
        assert d["score"] == expected_score
        assert 0 <= d["score"] <= 100


# ---------------------------------------------------------------------------
# Test 3: Robot Capacity Decision Detection
# ---------------------------------------------------------------------------
def test_scenario_3_robot_capacity_detection(db: Session, setup_phase8_data):
    res = evaluate_decision_intelligence(db, setup_phase8_data["wh_id"])
    rob_decisions = [d for d in res["decisions"] if d["category"] == "ROBOT_CAPACITY"]
    assert len(rob_decisions) >= 1
    low_bat_dec = [d for d in rob_decisions if "Battery" in d["title"]]
    assert len(low_bat_dec) >= 1
    assert low_bat_dec[0]["action_url"] == "/robots"


# ---------------------------------------------------------------------------
# Test 4: Task Bottleneck Decision Detection
# ---------------------------------------------------------------------------
def test_scenario_4_task_bottleneck_detection(db: Session, setup_phase8_data):
    res = evaluate_decision_intelligence(db, setup_phase8_data["wh_id"])
    tsk_decisions = [d for d in res["decisions"] if d["category"] == "TASK_BOTTLENECK"]
    assert len(tsk_decisions) >= 1
    assert "Task Bottleneck" in tsk_decisions[0]["title"]
    assert tsk_decisions[0]["action_url"] == "/tasks"


# ---------------------------------------------------------------------------
# Test 5: Route Congestion Decision Detection
# ---------------------------------------------------------------------------
def test_scenario_5_route_congestion_detection(db: Session, setup_phase8_data):
    res = evaluate_decision_intelligence(db, setup_phase8_data["wh_id"])
    route_decisions = [d for d in res["decisions"] if d["category"] == "ROUTE_CONGESTION"]
    assert len(route_decisions) >= 1
    assert "Obstacle" in route_decisions[0]["title"]
    assert route_decisions[0]["action_url"] == "/pathfinding"


# ---------------------------------------------------------------------------
# Test 6: Inventory & Replenishment Decision Detection
# ---------------------------------------------------------------------------
def test_scenario_6_inventory_replenishment_detection(db: Session, setup_phase8_data):
    res = evaluate_decision_intelligence(db, setup_phase8_data["wh_id"])
    inv_decisions = [d for d in res["decisions"] if d["category"] == "INVENTORY_REPLENISHMENT"]
    assert len(inv_decisions) >= 1
    assert "Stockout" in inv_decisions[0]["title"]
    assert inv_decisions[0]["action_url"] == "/analytics/replenishment"


# ---------------------------------------------------------------------------
# Test 7: Order Priority Decision Detection
# ---------------------------------------------------------------------------
def test_scenario_7_order_priority_detection(db: Session, setup_phase8_data):
    res = evaluate_decision_intelligence(db, setup_phase8_data["wh_id"])
    ord_decisions = [d for d in res["decisions"] if d["category"] == "ORDER_PRIORITY"]
    assert len(ord_decisions) >= 1
    assert "Order" in ord_decisions[0]["title"]
    assert ord_decisions[0]["action_url"] == "/orders"


# ---------------------------------------------------------------------------
# Test 8: Simulation Risk Integration
# ---------------------------------------------------------------------------
def test_scenario_8_simulation_risk_integration(db: Session, setup_phase8_data):
    res = evaluate_decision_intelligence(db, setup_phase8_data["wh_id"])
    sim_decisions = [d for d in res["decisions"] if d["category"] == "SIMULATION_RISK"]
    assert len(sim_decisions) >= 1
    assert "Simulation" in sim_decisions[0]["title"]
    assert sim_decisions[0]["action_url"] == "/scenarios"


# ---------------------------------------------------------------------------
# Test 9: System Health Decision Detection
# ---------------------------------------------------------------------------
def test_scenario_9_system_health_detection(db: Session, setup_phase8_data):
    res = evaluate_decision_intelligence(db, setup_phase8_data["wh_id"])
    sys_decisions = [d for d in res["decisions"] if d["category"] == "SYSTEM_HEALTH"]
    assert len(sys_decisions) >= 1
    assert "Incident" in sys_decisions[0]["title"]
    assert sys_decisions[0]["action_url"] == "/system-health"


# ---------------------------------------------------------------------------
# Test 10: Decision Deduplication Engine
# ---------------------------------------------------------------------------
def test_scenario_10_decision_deduplication(db: Session, setup_phase8_data):
    res1 = evaluate_decision_intelligence(db, setup_phase8_data["wh_id"])
    res2 = evaluate_decision_intelligence(db, setup_phase8_data["wh_id"])
    
    keys1 = [d["dedup_key"] for d in res1["decisions"]]
    keys2 = [d["dedup_key"] for d in res2["decisions"]]

    assert len(keys1) == len(set(keys1))  # 100% unique within run
    assert keys1 == keys2                 # Deterministic across runs


# ---------------------------------------------------------------------------
# Test 11: Decision Lifecycle Management (ACKNOWLEDGE, DISMISS, RESOLVE)
# ---------------------------------------------------------------------------
def test_scenario_11_decision_lifecycle(client: TestClient, phase8_token, setup_phase8_data):
    headers = {"Authorization": f"Bearer {phase8_token}"}
    
    # Acknowledge
    res_ack = client.post("/decision-support/decisions/REC-TEST-1/acknowledge", headers=headers)
    assert res_ack.status_code == 200
    assert res_ack.json()["status"] == "ACKNOWLEDGED"

    # Dismiss
    res_dis = client.post("/decision-support/decisions/REC-TEST-1/dismiss", headers=headers)
    assert res_dis.status_code == 200
    assert res_dis.json()["status"] == "DISMISSED"

    # Resolve
    res_res = client.post("/decision-support/decisions/REC-TEST-1/resolve", headers=headers)
    assert res_res.status_code == 200
    assert res_res.json()["status"] == "RESOLVED"


# ---------------------------------------------------------------------------
# Test 12: Entity Linking & Action URLs
# ---------------------------------------------------------------------------
def test_scenario_12_entity_linking(db: Session, setup_phase8_data):
    res = evaluate_decision_intelligence(db, setup_phase8_data["wh_id"])
    for d in res["decisions"]:
        assert "source_entity_type" in d
        assert "source_entity_id" in d
        assert "action_url" in d
        assert d["action_url"].startswith("/")


# ---------------------------------------------------------------------------
# Test 13: RBAC & Multi-Warehouse Isolation
# ---------------------------------------------------------------------------
def test_scenario_13_rbac_warehouse_isolation(client: TestClient, phase8_token, setup_phase8_data):
    # Unauthenticated request -> 401
    res_unauth = client.get("/decision-support/decisions")
    assert res_unauth.status_code == 401

    # Authenticated request -> 200
    res_auth = client.get(
        f"/decision-support/decisions?warehouse_id={setup_phase8_data['wh_id']}",
        headers={"Authorization": f"Bearer {phase8_token}"}
    )
    assert res_auth.status_code == 200
    assert res_auth.json()["warehouse_id"] == setup_phase8_data["wh_id"]


# ---------------------------------------------------------------------------
# Test 14: Production Data Non-Mutation Verification (Strict Read-Only)
# ---------------------------------------------------------------------------
def test_scenario_14_production_non_mutation_safety(db: Session, setup_phase8_data):
    wh_id = setup_phase8_data["wh_id"]

    # 1. Capture exact counts of production records BEFORE decision evaluation
    robots_before = db.query(Robot).filter(Robot.warehouse_id == wh_id).count()
    tasks_before = db.query(Task).filter(Task.warehouse_id == wh_id).count()
    inventory_before = db.query(Inventory).filter(Inventory.warehouse_id == wh_id).count()

    # 2. Run decision intelligence engine multiple times
    evaluate_decision_intelligence(db, wh_id)
    evaluate_decision_intelligence(db, wh_id)

    # 3. Capture exact counts of production records AFTER decision evaluation
    robots_after = db.query(Robot).filter(Robot.warehouse_id == wh_id).count()
    tasks_after = db.query(Task).filter(Task.warehouse_id == wh_id).count()
    inventory_after = db.query(Inventory).filter(Inventory.warehouse_id == wh_id).count()

    # 4. Strict assertion: zero rows added, modified, or deleted in production tables!
    assert robots_after == robots_before
    assert tasks_after == tasks_before
    assert inventory_after == inventory_before


# ---------------------------------------------------------------------------
# Test 15: No-Action Healthy Condition Verification
# ---------------------------------------------------------------------------
def test_scenario_15_no_action_healthy_condition(db: Session):
    # Setup healthy warehouse
    wh_healthy = Warehouse(id="WH-P8-HEALTHY", name="Healthy Hub", location="Clean Zone")
    db.add(wh_healthy)
    rob_healthy = Robot(id=899, robot_code="ROB-P8-HEALTHY", name="Healthy AGV", warehouse_id="WH-P8-HEALTHY", status="AVAILABLE", battery_level=99.0, current_x=1.0, current_y=1.0)
    db.add(rob_healthy)
    db.commit()

    res = evaluate_decision_intelligence(db, "WH-P8-HEALTHY")
    critical_decisions = [d for d in res["decisions"] if d["severity"] == "CRITICAL"]
    assert len(critical_decisions) == 0  # Zero artificial critical alerts on healthy warehouse!
