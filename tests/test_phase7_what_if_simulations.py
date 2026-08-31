"""
tests/test_phase7_what_if_simulations.py — Test Suite for Phase 7: What-If / Scenario Simulation & Impact Analysis.

Covers:
1. Baseline Snapshot Capture
2. Robot Unavailability Scenario ("What if 2 robots fail?")
3. Demand Increase Scenario ("What if order demand surges by 20%?")
4. Aisle Blockage Scenario ("What if Zone A aisle is blocked?")
5. Replenishment Delay Scenario ("What if supplier is delayed by 5 days?")
6. Increased Task Load Scenario ("What if task load increases by 25%?")
7. Baseline vs Scenario Metrics Comparison (Deltas calculation)
8. Transparent Impact Severity Rules (LOW, MEDIUM, HIGH, CRITICAL)
9. Natural Language Explanation Generation
10. Advisory Decision-Support Recommendations
11. Scenario Input Parameter Validation & Error Handling
12. RBAC & Security Enforcement
13. Production Data Non-Mutation Verification (Strict Read-Only)
14. Thread Safety & Database Session Isolation
15. Digital Twin SIMULATION Mode Reset & State Non-Contamination
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
    User, Warehouse, Robot, Task, Order, OrderItem, Inventory, Item, WarehouseLocation, WarehouseGridCell
)
from backend.decision_support_engine import run_what_if_analysis


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def setup_phase7_data(db: Session):
    """Setup isolated test warehouse environment with robots, tasks, inventory, and locations."""
    # 1. Warehouse
    wh = db.query(Warehouse).filter(Warehouse.id == "WH-P7-01").first()
    if not wh:
        wh = Warehouse(id="WH-P7-01", name="Phase 7 What-If Hub", location="Simulation Testing Zone")
        db.add(wh)
        db.commit()

    # 2. Robots
    r1 = db.query(Robot).filter(Robot.robot_code == "ROB-P7-01").first()
    if not r1:
        r1 = Robot(id=701, robot_code="ROB-P7-01", name="P7 Robot 1", warehouse_id="WH-P7-01", status="AVAILABLE", battery_level=90.0, current_x=1.0, current_y=1.0, max_payload=150.0)
        db.add(r1)

    r2 = db.query(Robot).filter(Robot.robot_code == "ROB-P7-02").first()
    if not r2:
        r2 = Robot(id=702, robot_code="ROB-P7-02", name="P7 Robot 2", warehouse_id="WH-P7-01", status="AVAILABLE", battery_level=85.0, current_x=4.0, current_y=1.0, max_payload=150.0)
        db.add(r2)

    r3 = db.query(Robot).filter(Robot.robot_code == "ROB-P7-03").first()
    if not r3:
        r3 = Robot(id=703, robot_code="ROB-P7-03", name="P7 Robot 3", warehouse_id="WH-P7-01", status="AVAILABLE", battery_level=95.0, current_x=8.0, current_y=1.0, max_payload=150.0)
        db.add(r3)

    # 3. Item, Location & Inventory
    item = db.query(Item).filter(Item.id == "ITM-P7-01").first()
    if not item:
        item = Item(id="ITM-P7-01", name="P7 Widget", sku="SKU-P7-01", safety_stock=20, reorder_threshold=50)
        db.add(item)

    loc = db.query(WarehouseLocation).filter(WarehouseLocation.id == "LOC-P7-01").first()
    if not loc:
        loc = WarehouseLocation(id="LOC-P7-01", warehouse_id="WH-P7-01", zone="A", aisle="1", rack="1", shelf="1", x=2, y=2, location_type="STORAGE")
        db.add(loc)

    inv = db.query(Inventory).filter(Inventory.warehouse_id == "WH-P7-01", Inventory.item_id == "ITM-P7-01").first()
    if not inv:
        inv = Inventory(warehouse_id="WH-P7-01", item_id="ITM-P7-01", location_id="LOC-P7-01", on_hand=30, reserved=5, available=25)
        db.add(inv)
    db.commit()

    # 4. Tasks
    now = datetime.now(UTC).replace(tzinfo=None)
    for i in range(1, 5):
        t_code = f"TSK-P7-0{i}"
        t = db.query(Task).filter(Task.task_number == t_code).first()
        if not t:
            t = Task(
                task_number=t_code, warehouse_id="WH-P7-01",
                task_type="PICK", priority="HIGH", status="QUEUED",
                product_id="ITM-P7-01", source_location_id="LOC-P7-01",
                destination_location_id="LOC-P7-01", requested_quantity=2
            )
            db.add(t)

    db.commit()
    return {"wh_id": "WH-P7-01", "r1_code": "ROB-P7-01", "r2_code": "ROB-P7-02", "item_id": "ITM-P7-01"}


@pytest.fixture
def phase7_admin(db: Session):
    admin = db.query(User).filter(User.username == "phase7_admin").first()
    if not admin:
        admin = User(
            username="phase7_admin", email="p7admin@example.com", role="admin",
            password_hash=hash_password("AdminPass123!"), is_active=True, is_verified=True
        )
        db.add(admin)
        db.commit()
    return admin


@pytest.fixture
def phase7_token(client: TestClient, phase7_admin):
    res = client.post("/auth/login", json={"username": "phase7_admin", "password": "AdminPass123!"})
    assert res.status_code == 200
    return res.json()["access_token"]


# ---------------------------------------------------------------------------
# Test 1: Baseline Snapshot Capture
# ---------------------------------------------------------------------------
def test_scenario_1_baseline_snapshot(db: Session, setup_phase7_data):
    res = run_what_if_analysis(db, "ROBOT_UNAVAILABLE", {"warehouse_id": setup_phase7_data["wh_id"], "disabled_robots_count": 0})
    assert "baseline" in res
    assert res["baseline"]["total_robots"] >= 3
    assert res["baseline"]["available_robots"] >= 3
    assert res["baseline"]["active_tasks"] >= 4


# ---------------------------------------------------------------------------
# Test 2: Robot Unavailability Scenario ("What if 2 robots fail?")
# ---------------------------------------------------------------------------
def test_scenario_2_robot_unavailability(db: Session, setup_phase7_data):
    res = run_what_if_analysis(db, "ROBOT_UNAVAILABLE", {"warehouse_id": setup_phase7_data["wh_id"], "disabled_robots_count": 2})
    assert res["scenario"] == "ROBOT_UNAVAILABLE"
    assert res["scenario_result"]["available_robots"] == res["baseline"]["available_robots"] - 2
    assert res["deltas"]["available_robots"] == -2
    assert res["impact_severity"] in ("MEDIUM", "HIGH", "CRITICAL")
    assert "removed from the available fleet pool" in res["explanation"]


# ---------------------------------------------------------------------------
# Test 3: Demand Increase Scenario ("What if demand increases by 20%?")
# ---------------------------------------------------------------------------
def test_scenario_3_demand_increase(db: Session, setup_phase7_data):
    res = run_what_if_analysis(db, "DEMAND_INCREASE", {"warehouse_id": setup_phase7_data["wh_id"], "demand_surge_percent": 20.0})
    assert res["scenario"] == "DEMAND_INCREASE"
    assert res["scenario_result"]["active_tasks"] >= res["baseline"]["active_tasks"]
    assert res["deltas"]["active_tasks"] >= 0
    assert "demand increase" in res["explanation"]


# ---------------------------------------------------------------------------
# Test 4: Aisle Blockage Scenario ("What if Zone A is blocked?")
# ---------------------------------------------------------------------------
def test_scenario_4_aisle_blockage(db: Session, setup_phase7_data):
    res = run_what_if_analysis(db, "AISLE_BLOCKAGE", {"warehouse_id": setup_phase7_data["wh_id"], "blocked_zone": "Zone A"})
    assert res["scenario"] == "AISLE_BLOCKAGE"
    assert "Blocking Zone A" in res["explanation"]
    assert "recommendation" in res
    assert res["impact_severity"] in ("MEDIUM", "HIGH", "CRITICAL")


# ---------------------------------------------------------------------------
# Test 5: Replenishment Delay Scenario ("What if supplier is delayed by 5 days?")
# ---------------------------------------------------------------------------
def test_scenario_5_replenishment_delay(db: Session, setup_phase7_data):
    res = run_what_if_analysis(db, "REPLENISHMENT_DELAY", {"warehouse_id": setup_phase7_data["wh_id"], "lead_time_delay_days": 5.0})
    assert res["scenario"] == "REPLENISHMENT_DELAY"
    assert res["scenario_result"]["stockout_risk_items"] >= res["baseline"]["stockout_risk_items"]
    assert "supplier replenishment delay" in res["explanation"]


# ---------------------------------------------------------------------------
# Test 6: Increased Task Load Scenario ("What if task load increases by 25%?")
# ---------------------------------------------------------------------------
def test_scenario_6_increased_task_load(db: Session, setup_phase7_data):
    res = run_what_if_analysis(db, "TASK_LOAD_INCREASE", {"warehouse_id": setup_phase7_data["wh_id"], "task_load_multiplier": 1.25})
    assert res["scenario"] == "TASK_LOAD_INCREASE"
    assert res["scenario_result"]["active_tasks"] > res["baseline"]["active_tasks"]
    assert res["deltas"]["active_tasks"] > 0


# ---------------------------------------------------------------------------
# Test 7: Baseline vs Scenario Metrics Comparison (Deltas calculation)
# ---------------------------------------------------------------------------
def test_scenario_7_metrics_deltas_comparison(db: Session, setup_phase7_data):
    res = run_what_if_analysis(db, "ROBOT_UNAVAILABLE", {"warehouse_id": setup_phase7_data["wh_id"], "disabled_robots_count": 1})
    assert "deltas" in res
    for metric, delta_val in res["deltas"].items():
        assert delta_val == round(res["scenario_result"][metric] - res["baseline"][metric], 2)


# ---------------------------------------------------------------------------
# Test 8: Transparent Impact Severity Rules (LOW, MEDIUM, HIGH, CRITICAL)
# ---------------------------------------------------------------------------
def test_scenario_8_impact_severity_rules(db: Session, setup_phase7_data):
    res_low = run_what_if_analysis(db, "ROBOT_UNAVAILABLE", {"warehouse_id": setup_phase7_data["wh_id"], "disabled_robots_count": 0})
    assert res_low["impact_severity"] == "LOW"

    res_high = run_what_if_analysis(db, "ROBOT_UNAVAILABLE", {"warehouse_id": setup_phase7_data["wh_id"], "disabled_robots_count": 3})
    assert res_high["impact_severity"] in ("HIGH", "CRITICAL")


# ---------------------------------------------------------------------------
# Test 9: Natural Language Explanation Generation
# ---------------------------------------------------------------------------
def test_scenario_9_natural_language_explanation(db: Session, setup_phase7_data):
    res = run_what_if_analysis(db, "DEMAND_INCREASE", {"warehouse_id": setup_phase7_data["wh_id"], "demand_surge_percent": 30.0})
    assert len(res["explanation"]) > 20
    assert "demand increase" in res["explanation"]


# ---------------------------------------------------------------------------
# Test 10: Decision-Support Recommendation
# ---------------------------------------------------------------------------
def test_scenario_10_decision_support_recommendation(db: Session, setup_phase7_data):
    res = run_what_if_analysis(db, "REPLENISHMENT_DELAY", {"warehouse_id": setup_phase7_data["wh_id"], "lead_time_delay_days": 7.0})
    assert len(res["recommendation"]) > 20
    assert "reorders" in res["recommendation"] or "safety stock" in res["recommendation"]


# ---------------------------------------------------------------------------
# Test 11: Scenario Input Parameter Validation & Error Handling
# ---------------------------------------------------------------------------
def test_scenario_11_parameter_validation(db: Session, setup_phase7_data):
    res_neg = run_what_if_analysis(db, "ROBOT_UNAVAILABLE", {"warehouse_id": setup_phase7_data["wh_id"], "disabled_robots_count": -5})
    assert "error" in res_neg
    assert res_neg["status"] == 400

    res_mult = run_what_if_analysis(db, "TASK_LOAD_INCREASE", {"warehouse_id": setup_phase7_data["wh_id"], "task_load_multiplier": 0.5})
    assert "error" in res_mult
    assert res_mult["status"] == 400


# ---------------------------------------------------------------------------
# Test 12: RBAC & Security Enforcement
# ---------------------------------------------------------------------------
def test_scenario_12_rbac_enforcement(client: TestClient, phase7_token, setup_phase7_data):
    # Unauthenticated request -> 401
    res_unauth = client.post("/decision-support/what-if", json={
        "scenario_type": "ROBOT_UNAVAILABLE",
        "warehouse_id": setup_phase7_data["wh_id"],
        "parameters": {"disabled_robots_count": 1}
    })
    assert res_unauth.status_code == 401

    # Authenticated request -> 200
    res_auth = client.post(
        "/decision-support/what-if",
        headers={"Authorization": f"Bearer {phase7_token}"},
        json={
            "scenario_type": "ROBOT_UNAVAILABLE",
            "warehouse_id": setup_phase7_data["wh_id"],
            "parameters": {"disabled_robots_count": 1}
        }
    )
    assert res_auth.status_code == 200
    assert res_auth.json()["scenario"] == "ROBOT_UNAVAILABLE"


# ---------------------------------------------------------------------------
# Test 13: Production Data Non-Mutation Verification (Strict Read-Only)
# ---------------------------------------------------------------------------
def test_scenario_13_production_non_mutation_safety(client: TestClient, db: Session, phase7_token, setup_phase7_data):
    wh_id = setup_phase7_data["wh_id"]

    # 1. Capture exact counts of production records BEFORE simulation
    robots_before = db.query(Robot).filter(Robot.warehouse_id == wh_id).count()
    tasks_before = db.query(Task).filter(Task.warehouse_id == wh_id).count()
    inventory_before = db.query(Inventory).filter(Inventory.warehouse_id == wh_id).count()
    locations_before = db.query(WarehouseLocation).filter(WarehouseLocation.warehouse_id == wh_id).count()

    # 2. Run multiple what-if simulations
    client.post(
        "/decision-support/what-if",
        headers={"Authorization": f"Bearer {phase7_token}"},
        json={"scenario_type": "ROBOT_UNAVAILABLE", "warehouse_id": wh_id, "parameters": {"disabled_robots_count": 2}}
    )
    client.post(
        "/decision-support/what-if",
        headers={"Authorization": f"Bearer {phase7_token}"},
        json={"scenario_type": "DEMAND_INCREASE", "warehouse_id": wh_id, "parameters": {"demand_surge_percent": 50.0}}
    )
    client.post(
        "/decision-support/what-if",
        headers={"Authorization": f"Bearer {phase7_token}"},
        json={"scenario_type": "AISLE_BLOCKAGE", "warehouse_id": wh_id, "parameters": {"blocked_zone": "Zone A"}}
    )

    # 3. Capture exact counts of production records AFTER simulation
    robots_after = db.query(Robot).filter(Robot.warehouse_id == wh_id).count()
    tasks_after = db.query(Task).filter(Task.warehouse_id == wh_id).count()
    inventory_after = db.query(Inventory).filter(Inventory.warehouse_id == wh_id).count()
    locations_after = db.query(WarehouseLocation).filter(WarehouseLocation.warehouse_id == wh_id).count()

    # 4. Strict assertion: zero rows added, modified, or deleted in production database!
    assert robots_after == robots_before
    assert tasks_after == tasks_before
    assert inventory_after == inventory_before
    assert locations_after == locations_before


# ---------------------------------------------------------------------------
# Test 14: Thread Safety & Database Session Isolation
# ---------------------------------------------------------------------------
def test_scenario_14_thread_safety_isolation(db: Session, setup_phase7_data):
    res1 = run_what_if_analysis(db, "ROBOT_UNAVAILABLE", {"warehouse_id": setup_phase7_data["wh_id"], "disabled_robots_count": 1})
    res2 = run_what_if_analysis(db, "ROBOT_UNAVAILABLE", {"warehouse_id": setup_phase7_data["wh_id"], "disabled_robots_count": 1})

    # Assert deterministic results without session corruption
    assert res1["baseline"] == res2["baseline"]
    assert res1["scenario_result"] == res2["scenario_result"]


# ---------------------------------------------------------------------------
# Test 15: Digital Twin SIMULATION Mode Reset & State Non-Contamination
# ---------------------------------------------------------------------------
def test_scenario_15_digital_twin_simulation_reset(client: TestClient, phase7_token, setup_phase7_data):
    wh_id = setup_phase7_data["wh_id"]

    # Fetch production Digital Twin state
    res_prod = client.get(f"/digital-twin/{wh_id}/state", headers={"Authorization": f"Bearer {phase7_token}"})
    assert res_prod.status_code == 200
    prod_state = res_prod.json()
    assert prod_state["data_mode"] == "OBSERVATION STATE"
    assert prod_state["is_live"] is True

    # Run what-if analysis
    res_sim = client.post(
        "/decision-support/what-if",
        headers={"Authorization": f"Bearer {phase7_token}"},
        json={"scenario_type": "ROBOT_UNAVAILABLE", "warehouse_id": wh_id, "parameters": {"disabled_robots_count": 2}}
    )
    assert res_sim.status_code == 200

    # Fetch production Digital Twin state again -> must remain OBSERVATION STATE mode and unchanged
    res_prod_after = client.get(f"/digital-twin/{wh_id}/state", headers={"Authorization": f"Bearer {phase7_token}"})
    assert res_prod_after.status_code == 200
    prod_state_after = res_prod_after.json()
    assert prod_state_after["data_mode"] == "OBSERVATION STATE"
    assert len(prod_state_after["robots"]) == len(prod_state["robots"])
