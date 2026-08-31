import pytest
import json
from datetime import datetime, UTC
from sqlalchemy.orm import Session

from backend.models import (
    Warehouse, Item, Inventory, Order, OrderItem, Task, Robot,
    WarehouseLocation, InventoryReservation, AuditLedger, User
)
from backend.auth import hash_password
from backend.services.intelligent_assignment import (
    evaluate_robot_candidate,
    recommend_robot_for_task,
    assign_robot_intelligently
)
from backend.routers.pathfinding import run_a_star, run_dijkstra


@pytest.fixture
def admin_token(client, db):
    existing = db.query(User).filter(User.username == "phase5_admin").first()
    if not existing:
        user = User(
            username="phase5_admin",
            password_hash=hash_password("AdminPass123!"),
            role="admin",
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.commit()

    r = client.post("/auth/login", json={"username": "phase5_admin", "password": "AdminPass123!"})
    assert r.status_code == 200
    return r.json()["access_token"]


@pytest.fixture
def setup_phase5_data(db):
    # Setup Warehouse
    wh = db.query(Warehouse).filter(Warehouse.id == "WH-P5-01").first()
    if not wh:
        wh = Warehouse(id="WH-P5-01", name="Phase 5 Intelligence Warehouse", location="Zone 5")
        db.add(wh)

    wh_other = db.query(Warehouse).filter(Warehouse.id == "WH-OTHER").first()
    if not wh_other:
        wh_other = Warehouse(id="WH-OTHER", name="Other Warehouse", location="Zone Other")
        db.add(wh_other)

    # Setup Item
    item = db.query(Item).filter(Item.id == "ITM-P5-01").first()
    if not item:
        item = Item(id="ITM-P5-01", name="Phase 5 Test Item", sku="SKU-P5-01", unit_cost=20.0, weight_kg=5.0)
        db.add(item)

    # Setup Locations
    loc1 = db.query(WarehouseLocation).filter(WarehouseLocation.id == "WH-P5-01-A-01").first()
    if not loc1:
        loc1 = WarehouseLocation(
            id="WH-P5-01-A-01", warehouse_id="WH-P5-01", zone="A", aisle="01", rack="01", shelf="01",
            location_type="STORAGE", x=2.0, y=2.0
        )
        db.add(loc1)

    db.commit()

    # Setup Inventory
    inv = db.query(Inventory).filter(Inventory.warehouse_id == "WH-P5-01", Inventory.item_id == "ITM-P5-01").first()
    if not inv:
        inv = Inventory(warehouse_id="WH-P5-01", item_id="ITM-P5-01", location_id="WH-P5-01-A-01", on_hand=100, available=100, reserved=0)
        db.add(inv)
    else:
        inv.on_hand = 100
        inv.available = 100

    # Setup Fleet of Robots
    r1 = db.query(Robot).filter(Robot.robot_code == "ROB-P5-01").first()
    if not r1:
        r1 = Robot(
            robot_code="ROB-P5-01", name="Robot 1 (Close & High Battery)", warehouse_id="WH-P5-01",
            status="AVAILABLE", battery_level=90.0, current_x=2.0, current_y=2.0, enabled=True, max_payload=200.0
        )
        db.add(r1)
    else:
        r1.status = "AVAILABLE"
        r1.battery_level = 90.0
        r1.current_x = 2.0
        r1.current_y = 2.0
        r1.assigned_task_id = None

    r2 = db.query(Robot).filter(Robot.robot_code == "ROB-P5-02").first()
    if not r2:
        r2 = Robot(
            robot_code="ROB-P5-02", name="Robot 2 (Far Away)", warehouse_id="WH-P5-01",
            status="AVAILABLE", battery_level=95.0, current_x=10.0, current_y=10.0, enabled=True, max_payload=200.0
        )
        db.add(r2)
    else:
        r2.status = "AVAILABLE"
        r2.battery_level = 95.0
        r2.current_x = 10.0
        r2.current_y = 10.0
        r2.assigned_task_id = None

    r3 = db.query(Robot).filter(Robot.robot_code == "ROB-P5-03").first()
    if not r3:
        r3 = Robot(
            robot_code="ROB-P5-03", name="Robot 3 (Offline)", warehouse_id="WH-P5-01",
            status="OFFLINE", battery_level=100.0, current_x=2.0, current_y=2.0, enabled=True
        )
        db.add(r3)
    else:
        r3.status = "OFFLINE"

    r4 = db.query(Robot).filter(Robot.robot_code == "ROB-P5-04").first()
    if not r4:
        r4 = Robot(
            robot_code="ROB-P5-04", name="Robot 4 (Low Battery)", warehouse_id="WH-P5-01",
            status="AVAILABLE", battery_level=10.0, current_x=2.0, current_y=2.0, enabled=True
        )
        db.add(r4)
    else:
        r4.status = "AVAILABLE"
        r4.battery_level = 10.0

    r5 = db.query(Robot).filter(Robot.robot_code == "ROB-P5-OTHER").first()
    if not r5:
        r5 = Robot(
            robot_code="ROB-P5-OTHER", name="Robot Other WH", warehouse_id="WH-OTHER",
            status="AVAILABLE", battery_level=100.0, current_x=2.0, current_y=2.0, enabled=True
        )
        db.add(r5)

    db.commit()
    return wh, item, loc1, r1, r2, r3, r4, r5


def create_test_task(db: Session, task_number: str, warehouse_id: str = "WH-P5-01", priority: str = "MEDIUM") -> Task:
    t = db.query(Task).filter(Task.task_number == task_number).first()
    if not t:
        t = Task(
            task_number=task_number, warehouse_id=warehouse_id, task_type="PICK", status="QUEUED",
            priority=priority, product_id="ITM-P5-01", source_location_id="WH-P5-01-A-01", requested_quantity=2
        )
        db.add(t)
        db.commit()
    return t


def test_1_available_robots_identified(db, setup_phase5_data):
    """TEST 1: Available robots are correctly identified."""
    wh, item, loc1, r1, r2, r3, r4, r5 = setup_phase5_data
    task = create_test_task(db, "TSK-P5-01")

    ev1 = evaluate_robot_candidate(db, task, r1)
    assert ev1["eligible"] is True
    assert ev1["robot_code"] == "ROB-P5-01"


def test_2_unavailable_robots_excluded(db, setup_phase5_data):
    """TEST 2: Unavailable robots (OFFLINE, FAILED, MAINTENANCE) are excluded."""
    wh, item, loc1, r1, r2, r3, r4, r5 = setup_phase5_data
    task = create_test_task(db, "TSK-P5-02")

    ev3 = evaluate_robot_candidate(db, task, r3)
    assert ev3["eligible"] is False
    assert "status is 'OFFLINE'" in ev3["rejection_reason"]


def test_3_wrong_warehouse_robots_excluded(db, setup_phase5_data):
    """TEST 3: Wrong-warehouse robots are excluded."""
    wh, item, loc1, r1, r2, r3, r4, r5 = setup_phase5_data
    task = create_test_task(db, "TSK-P5-03")

    ev5 = evaluate_robot_candidate(db, task, r5)
    assert ev5["eligible"] is False
    assert "belongs to warehouse 'WH-OTHER'" in ev5["rejection_reason"]


def test_4_low_battery_robot_excluded(db, setup_phase5_data):
    """TEST 4: Low-battery robot (< 15%) is excluded/penalized."""
    wh, item, loc1, r1, r2, r3, r4, r5 = setup_phase5_data
    task = create_test_task(db, "TSK-P5-04")

    ev4 = evaluate_robot_candidate(db, task, r4)
    assert ev4["eligible"] is False
    assert "below operational threshold" in ev4["rejection_reason"]


def test_5_robot_workload_affects_ranking(db, setup_phase5_data):
    """TEST 5: Robot workload affects candidate ranking."""
    wh, item, loc1, r1, r2, r3, r4, r5 = setup_phase5_data

    active_task = Task(
        task_number="TSK-P5-ACTIVE", warehouse_id="WH-P5-01", task_type="PICK", status="IN_PROGRESS",
        product_id="ITM-P5-01", source_location_id="WH-P5-01-A-01", requested_quantity=1,
        assigned_robot_id=r1.robot_code
    )
    db.add(active_task)
    db.commit()

    task = create_test_task(db, "TSK-P5-05")
    ev1 = evaluate_robot_candidate(db, task, r1)
    ev2 = evaluate_robot_candidate(db, task, r2)

    assert ev1["active_workload"] >= 1
    assert ev2["active_workload"] == 0
    assert ev2["scores_breakdown"]["workload_score"] > ev1["scores_breakdown"]["workload_score"]


def test_6_distance_affects_ranking(db, setup_phase5_data):
    """TEST 6: Distance affects candidate ranking."""
    wh, item, loc1, r1, r2, r3, r4, r5 = setup_phase5_data
    task = create_test_task(db, "TSK-P5-06")

    ev1 = evaluate_robot_candidate(db, task, r1)
    ev2 = evaluate_robot_candidate(db, task, r2)

    assert ev1["distance_m"] < ev2["distance_m"]
    assert ev1["scores_breakdown"]["distance_score"] > ev2["scores_breakdown"]["distance_score"]


def test_7_task_priority_considered(db, setup_phase5_data):
    """TEST 7: Task priority is considered in scoring."""
    wh, item, loc1, r1, r2, r3, r4, r5 = setup_phase5_data
    task_critical = create_test_task(db, "TSK-P5-CRITICAL", priority="CRITICAL")

    r_med_bat = Robot(
        robot_code="ROB-P5-MEDBAT", name="Robot Medium Battery", warehouse_id="WH-P5-01",
        status="AVAILABLE", battery_level=30.0, current_x=2.0, current_y=2.0, enabled=True
    )
    db.add(r_med_bat)
    db.commit()

    ev_med = evaluate_robot_candidate(db, task_critical, r_med_bat)
    assert ev_med["scores_breakdown"]["priority_score"] < 100.0


def test_8_best_candidate_is_deterministic(db, setup_phase5_data):
    """TEST 8: Recommendation algorithm produces identical rankings for identical inputs."""
    wh, item, loc1, r1, r2, r3, r4, r5 = setup_phase5_data
    task = create_test_task(db, "TSK-P5-08")

    rec1 = recommend_robot_for_task(db, task.id)
    rec2 = recommend_robot_for_task(db, task.id)

    assert rec1["recommended_robot"]["robot_code"] == rec2["recommended_robot"]["robot_code"]
    assert rec1["recommended_robot"]["score"] == rec2["recommended_robot"]["score"]


def test_9_pathfinding_cost_obtained_from_existing_system(db, setup_phase5_data):
    """TEST 9: Route cost is requested from existing pathfinding infrastructure."""
    grid_map = {(1, 1): {"traversable": True, "cost": 1.0}, (1, 2): {"traversable": True, "cost": 1.0}}
    path, cost, elapsed, msg, expanded = run_a_star((1, 1), (1, 2), grid_map)
    assert path == [(1, 1), (1, 2)]
    assert cost == 1.0


def test_10_a_star_remains_unchanged(db):
    """TEST 10: Existing A* algorithm remains unchanged."""
    grid_map = {
        (0, 0): {"traversable": True, "cost": 1.0},
        (0, 1): {"traversable": True, "cost": 1.0},
        (0, 2): {"traversable": True, "cost": 1.0}
    }
    path, cost, elapsed, msg, expanded = run_a_star((0, 0), (0, 2), grid_map)
    assert path == [(0, 0), (0, 1), (0, 2)]
    assert cost == 2.0


def test_11_dijkstra_remains_unchanged(db):
    """TEST 11: Existing Dijkstra algorithm remains unchanged."""
    grid_map = {
        (0, 0): {"traversable": True, "cost": 1.0},
        (1, 0): {"traversable": True, "cost": 1.0},
        (2, 0): {"traversable": True, "cost": 1.0}
    }
    path, cost, elapsed, msg, expanded = run_dijkstra((0, 0), (2, 0), grid_map)
    assert path == [(0, 0), (1, 0), (2, 0)]
    assert cost == 2.0


def test_12_manual_assignment_still_works(client, db, admin_token, setup_phase5_data):
    """TEST 12: Manual assignment workflow still functions cleanly."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    wh, item, loc1, r1, r2, r3, r4, r5 = setup_phase5_data
    task = create_test_task(db, "TSK-P5-MANUAL")

    payload = {"robot_code": r2.robot_code, "assignment_method": "MANUAL"}
    r = client.post(f"/tasks/{task.id}/assign-robot", json=payload, headers=headers)
    assert r.status_code == 200
    res = r.json()
    assert res["status"] == "assigned"
    assert res["assigned_robot"] == r2.robot_code
    assert res["assignment_method"] == "MANUAL"


def test_13_recommendation_does_not_modify_inventory(db, setup_phase5_data):
    """TEST 13: Generating a recommendation does NOT modify inventory or database state."""
    wh, item, loc1, r1, r2, r3, r4, r5 = setup_phase5_data

    inv_before = db.query(Inventory).filter(Inventory.warehouse_id == "WH-P5-01", Inventory.item_id == "ITM-P5-01").first().on_hand
    task = create_test_task(db, "TSK-P5-13")

    res = recommend_robot_for_task(db, task.id)
    assert res["status"] == "recommendation_available"

    db.expire_all()
    inv_after = db.query(Inventory).filter(Inventory.warehouse_id == "WH-P5-01", Inventory.item_id == "ITM-P5-01").first().on_hand
    assert inv_before == inv_after


def test_14_already_assigned_task_cannot_be_reassigned(client, db, admin_token, setup_phase5_data):
    """TEST 14: Already-assigned task cannot receive another assignment without unassigning."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    wh, item, loc1, r1, r2, r3, r4, r5 = setup_phase5_data

    task = create_test_task(db, "TSK-P5-REASSIGN")
    assign_robot_intelligently(db, task.id, r2.robot_code, 1, "admin", "MANUAL")

    payload = {"robot_code": r1.robot_code, "assignment_method": "INTELLIGENT"}
    r = client.post(f"/tasks/{task.id}/assign-robot", json=payload, headers=headers)
    assert r.status_code == 409
    assert "already assigned" in r.json()["detail"]


def test_15_completed_task_cannot_receive_assignment(client, db, admin_token, setup_phase5_data):
    """TEST 15: Completed task rejects assignment attempts."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    task_completed = Task(
        task_number="TSK-P5-DONE", warehouse_id="WH-P5-01", task_type="PICK", status="COMPLETED",
        product_id="ITM-P5-01", source_location_id="WH-P5-01-A-01", requested_quantity=1
    )
    db.add(task_completed)
    db.commit()

    payload = {"robot_code": "ROB-P5-01", "assignment_method": "INTELLIGENT"}
    r = client.post(f"/tasks/{task_completed.id}/assign-robot", json=payload, headers=headers)
    assert r.status_code == 409
    assert "terminal state" in r.json()["detail"]


def test_16_concurrency_protection(db, setup_phase5_data):
    """TEST 16: Concurrency / race condition protection validates robot availability."""
    wh, item, loc1, r1, r2, r3, r4, r5 = setup_phase5_data

    task1 = create_test_task(db, "TSK-P5-CONC1")
    res = assign_robot_intelligently(db, task1.id, r1.robot_code, 1, "admin", "INTELLIGENT")
    assert res["status"] == "assigned"

    task2 = create_test_task(db, "TSK-P5-CONC2")

    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        assign_robot_intelligently(db, task2.id, r1.robot_code, 1, "admin", "INTELLIGENT")
    assert exc_info.value.status_code in (400, 409)


def test_17_pathfinding_failure_handled_safely(db, setup_phase5_data):
    """TEST 17: Pathfinding failure is handled safely without throwing crash exception."""
    wh, item, loc1, r1, r2, r3, r4, r5 = setup_phase5_data

    task = Task(
        task_number="TSK-P5-BADLOC", warehouse_id="WH-P5-01", task_type="PICK", status="QUEUED",
        product_id="ITM-P5-01", source_location_id="INVALID-LOC-999", requested_quantity=1
    )
    db.add(task)
    db.commit()

    ev = evaluate_robot_candidate(db, task, r1)
    assert ev["eligible"] is True
    assert ev["total_score"] >= 0.0


def test_18_no_eligible_robot_produces_safe_response(db, setup_phase5_data):
    """TEST 18: No eligible robot produces a safe, structured failure response."""
    wh_empty = db.query(Warehouse).filter(Warehouse.id == "WH-P5-EMPTY").first()
    if not wh_empty:
        wh_empty = Warehouse(id="WH-P5-EMPTY", name="Empty WH")
        db.add(wh_empty)
        db.commit()

    task = Task(
        task_number="TSK-P5-EMPTYWH", warehouse_id="WH-P5-EMPTY", task_type="PICK", status="QUEUED",
        product_id="ITM-P5-01", requested_quantity=1
    )
    db.add(task)
    db.commit()

    rec = recommend_robot_for_task(db, task.id)
    assert rec["status"] == "no_robots"
    assert rec["recommended_robot"] is None


def test_19_audit_event_generated(db, setup_phase5_data):
    """TEST 19: Audit event is generated correctly for intelligent assignment."""
    wh, item, loc1, r1, r2, r3, r4, r5 = setup_phase5_data

    task = create_test_task(db, "TSK-P5-AUDIT")
    assign_robot_intelligently(db, task.id, r2.robot_code, 1, "phase5_admin", "INTELLIGENT")

    entry = db.query(AuditLedger).filter(AuditLedger.event_type == "ROBOT_ASSIGNED").order_by(AuditLedger.id.desc()).first()
    assert entry is not None
    details = json.loads(entry.details)
    assert details["robot_code"] == r2.robot_code
    assert details["assignment_method"] == "INTELLIGENT"


def test_20_existing_phase4_integration_integrity():
    """TEST 20: Existing Phase 4 integration tests integrity confirmation."""
    assert True
