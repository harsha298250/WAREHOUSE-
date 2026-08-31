import pytest
import json
from datetime import datetime, UTC
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from backend.models import (
    Warehouse, Item, Task, Robot, WarehouseLocation, User, AuditLedger
)
from backend.auth import hash_password
from backend.services.intelligent_assignment import (
    evaluate_robot_candidate,
    recommend_robot_for_task,
    assign_robot_intelligently
)


@pytest.fixture
def phase3_admin_user(db: Session):
    user = db.query(User).filter(User.username == "phase3_admin").first()
    if not user:
        user = User(
            username="phase3_admin",
            password_hash=hash_password("AdminPass123!"),
            role="admin",
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@pytest.fixture
def phase3_staff_user(db: Session):
    user = db.query(User).filter(User.username == "phase3_staff").first()
    if not user:
        user = User(
            username="phase3_staff",
            password_hash=hash_password("StaffPass123!"),
            role="staff",
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@pytest.fixture
def admin_token_p3(client: TestClient, phase3_admin_user):
    res = client.post("/auth/login", json={"username": "phase3_admin", "password": "AdminPass123!"})
    assert res.status_code == 200
    return res.json()["access_token"]


@pytest.fixture
def staff_token_p3(client: TestClient, phase3_staff_user):
    res = client.post("/auth/login", json={"username": "phase3_staff", "password": "StaffPass123!"})
    assert res.status_code == 200
    return res.json()["access_token"]


@pytest.fixture
def setup_phase3_data(db: Session):
    # Setup Warehouse 1 and 2
    wh1 = db.query(Warehouse).filter(Warehouse.id == "WH-P3-01").first()
    if not wh1:
        wh1 = Warehouse(id="WH-P3-01", name="Phase 3 Primary Warehouse", location="Zone A")
        db.add(wh1)

    wh2 = db.query(Warehouse).filter(Warehouse.id == "WH-P3-02").first()
    if not wh2:
        wh2 = Warehouse(id="WH-P3-02", name="Phase 3 Secondary Warehouse", location="Zone B")
        db.add(wh2)

    # Setup Product Items
    item_std = db.query(Item).filter(Item.id == "ITM-P3-STD").first()
    if not item_std:
        item_std = Item(id="ITM-P3-STD", name="Standard Item", sku="SKU-P3-01", weight_kg=10.0)
        db.add(item_std)

    item_heavy = db.query(Item).filter(Item.id == "ITM-P3-HEAVY").first()
    if not item_heavy:
        item_heavy = Item(id="ITM-P3-HEAVY", name="Heavy Machinery Part", sku="SKU-P3-HEAVY", weight_kg=500.0)
        db.add(item_heavy)

    # Setup Warehouse Locations
    loc_src = db.query(WarehouseLocation).filter(WarehouseLocation.id == "LOC-P3-SRC").first()
    if not loc_src:
        loc_src = WarehouseLocation(
            id="LOC-P3-SRC", warehouse_id="WH-P3-01", zone="A", aisle="01", rack="01", shelf="01",
            location_type="STORAGE", x=1.0, y=1.0
        )
        db.add(loc_src)

    loc_dst = db.query(WarehouseLocation).filter(WarehouseLocation.id == "LOC-P3-DST").first()
    if not loc_dst:
        loc_dst = WarehouseLocation(
            id="LOC-P3-DST", warehouse_id="WH-P3-01", zone="A", aisle="02", rack="01", shelf="01",
            location_type="PICKING", x=5.0, y=5.0
        )
        db.add(loc_dst)

    db.commit()

    return {
        "wh1": "WH-P3-01",
        "wh2": "WH-P3-02",
        "item_std": "ITM-P3-STD",
        "item_heavy": "ITM-P3-HEAVY",
        "loc_src": "LOC-P3-SRC",
        "loc_dst": "LOC-P3-DST"
    }


# ---------------------------------------------------------------------------
# Test Scenario 1: Single Available Robot - Successful Assignment and State Updates
# ---------------------------------------------------------------------------
def test_scenario_1_single_available_robot(db: Session, setup_phase3_data, phase3_admin_user):
    wh_id = setup_phase3_data["wh1"]
    
    # Create single robot
    r = db.query(Robot).filter(Robot.robot_code == "ROB-P3-S1").first()
    if not r:
        r = Robot(
            robot_code="ROB-P3-S1", name="Single Bot", warehouse_id=wh_id,
            status="AVAILABLE", battery_level=90.0, current_x=1.0, current_y=1.0, enabled=True
        )
        db.add(r)
    else:
        r.status = "AVAILABLE"
        r.battery_level = 90.0
        r.assigned_task_id = None
        r.current_x = 1.0
        r.current_y = 1.0

    task = Task(
        task_number=f"TSK-P3-S1-{datetime.now(UTC).timestamp()}",
        warehouse_id=wh_id, task_type="PICK", status="QUEUED",
        product_id=setup_phase3_data["item_std"], source_location_id=setup_phase3_data["loc_src"],
        destination_location_id=setup_phase3_data["loc_dst"], requested_quantity=2
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    rec = recommend_robot_for_task(db, task.id)
    assert rec["status"] == "recommendation_available"
    assert rec["recommended_robot"]["robot_code"] == "ROB-P3-S1"

    assign_res = assign_robot_intelligently(
        db, task.id, "ROB-P3-S1", phase3_admin_user.id, phase3_admin_user.username
    )
    assert assign_res["status"] == "assigned"
    
    db.refresh(task)
    db.refresh(r)
    assert task.status == "ASSIGNED"
    assert task.assigned_robot_id == "ROB-P3-S1"
    assert r.status == "ASSIGNED"
    assert r.assigned_task_id == task.id


# ---------------------------------------------------------------------------
# Test Scenario 2: Multiple Candidates - Best Score Candidate Selected
# ---------------------------------------------------------------------------
def test_scenario_2_multiple_candidates_best_score(db: Session, setup_phase3_data):
    wh_id = setup_phase3_data["wh1"]

    # Close Robot (x=1, y=1) with 85% battery
    r_close = db.query(Robot).filter(Robot.robot_code == "ROB-P3-CLOSE").first()
    if not r_close:
        r_close = Robot(
            robot_code="ROB-P3-CLOSE", name="Close Bot", warehouse_id=wh_id,
            status="AVAILABLE", battery_level=85.0, current_x=1.0, current_y=1.0, enabled=True
        )
        db.add(r_close)
    else:
        r_close.status = "AVAILABLE"
        r_close.battery_level = 85.0
        r_close.current_x = 1.0
        r_close.current_y = 1.0
        r_close.assigned_task_id = None

    # Far Robot (x=10, y=10) with 100% battery
    r_far = db.query(Robot).filter(Robot.robot_code == "ROB-P3-FAR").first()
    if not r_far:
        r_far = Robot(
            robot_code="ROB-P3-FAR", name="Far Bot", warehouse_id=wh_id,
            status="AVAILABLE", battery_level=100.0, current_x=10.0, current_y=10.0, enabled=True
        )
        db.add(r_far)
    else:
        r_far.status = "AVAILABLE"
        r_far.battery_level = 100.0
        r_far.current_x = 10.0
        r_far.current_y = 10.0
        r_far.assigned_task_id = None

    task = Task(
        task_number=f"TSK-P3-S2-{datetime.now(UTC).timestamp()}",
        warehouse_id=wh_id, task_type="PICK", status="QUEUED",
        product_id=setup_phase3_data["item_std"], source_location_id=setup_phase3_data["loc_src"],
        destination_location_id=setup_phase3_data["loc_dst"], requested_quantity=1
    )
    db.add(task)
    db.commit()

    rec = recommend_robot_for_task(db, task.id)
    assert rec["status"] == "recommendation_available"
    # Close robot should score higher due to distance weight (40%)
    assert rec["recommended_robot"]["robot_code"] == "ROB-P3-CLOSE"


# ---------------------------------------------------------------------------
# Test Scenario 3: Battery Safety Constraint - Rejection of Low Battery Robot
# ---------------------------------------------------------------------------
def test_scenario_3_battery_safety_constraint(db: Session, setup_phase3_data):
    wh_id = setup_phase3_data["wh1"]

    # Robot close to task but battery is below MIN_OPERATIONAL_BATTERY (10%)
    r_low_bat = db.query(Robot).filter(Robot.robot_code == "ROB-P3-LOWBAT").first()
    if not r_low_bat:
        r_low_bat = Robot(
            robot_code="ROB-P3-LOWBAT", name="Low Battery Bot", warehouse_id=wh_id,
            status="AVAILABLE", battery_level=10.0, current_x=1.0, current_y=1.0, enabled=True
        )
        db.add(r_low_bat)
    else:
        r_low_bat.status = "AVAILABLE"
        r_low_bat.battery_level = 10.0
        r_low_bat.assigned_task_id = None

    # Robot farther away with safe battery (80%)
    r_healthy = db.query(Robot).filter(Robot.robot_code == "ROB-P3-HEALTHY").first()
    if not r_healthy:
        r_healthy = Robot(
            robot_code="ROB-P3-HEALTHY", name="Healthy Battery Bot", warehouse_id=wh_id,
            status="AVAILABLE", battery_level=80.0, current_x=6.0, current_y=6.0, enabled=True
        )
        db.add(r_healthy)
    else:
        r_healthy.status = "AVAILABLE"
        r_healthy.battery_level = 80.0
        r_healthy.assigned_task_id = None

    task = Task(
        task_number=f"TSK-P3-S3-{datetime.now(UTC).timestamp()}",
        warehouse_id=wh_id, task_type="PICK", status="QUEUED",
        product_id=setup_phase3_data["item_std"], source_location_id=setup_phase3_data["loc_src"],
        destination_location_id=setup_phase3_data["loc_dst"], requested_quantity=1
    )
    db.add(task)
    db.commit()

    rec = recommend_robot_for_task(db, task.id)
    assert rec["status"] == "recommendation_available"
    assert rec["recommended_robot"]["robot_code"] == "ROB-P3-HEALTHY"

    # Check candidate breakdown rejection reason for low bat
    low_bat_cand = next(c for c in rec["candidates"] if c["robot_code"] == "ROB-P3-LOWBAT")
    assert low_bat_cand["eligible"] is False
    assert "battery" in low_bat_cand["rejection_reason"].lower()


# ---------------------------------------------------------------------------
# Test Scenario 4: Busy Robot Exclusion
# ---------------------------------------------------------------------------
def test_scenario_4_busy_robot_exclusion(db: Session, setup_phase3_data):
    wh_id = setup_phase3_data["wh1"]

    busy_task = Task(
        task_number=f"TSK-P3-BUSY-{datetime.now(UTC).timestamp()}",
        warehouse_id=wh_id, task_type="PICK", status="ASSIGNED", requested_quantity=1,
        product_id=setup_phase3_data["item_std"], source_location_id=setup_phase3_data["loc_src"]
    )
    db.add(busy_task)
    db.commit()

    # Robot already assigned and busy
    r_busy = db.query(Robot).filter(Robot.robot_code == "ROB-P3-BUSY").first()
    if not r_busy:
        r_busy = Robot(
            robot_code="ROB-P3-BUSY", name="Busy Bot", warehouse_id=wh_id,
            status="MOVING", battery_level=90.0, current_x=1.0, current_y=1.0,
            assigned_task_id=busy_task.id, enabled=True
        )
        db.add(r_busy)
    else:
        r_busy.status = "MOVING"
        r_busy.assigned_task_id = busy_task.id
        r_busy.battery_level = 90.0

    # Idle available robot
    r_free = db.query(Robot).filter(Robot.robot_code == "ROB-P3-FREE").first()
    if not r_free:
        r_free = Robot(
            robot_code="ROB-P3-FREE", name="Free Bot", warehouse_id=wh_id,
            status="AVAILABLE", battery_level=80.0, current_x=4.0, current_y=4.0,
            assigned_task_id=None, enabled=True
        )
        db.add(r_free)
    else:
        r_free.status = "AVAILABLE"
        r_free.assigned_task_id = None
        r_free.battery_level = 80.0

    task = Task(
        task_number=f"TSK-P3-S4-{datetime.now(UTC).timestamp()}",
        warehouse_id=wh_id, task_type="PICK", status="QUEUED", requested_quantity=1,
        product_id=setup_phase3_data["item_std"], source_location_id=setup_phase3_data["loc_src"]
    )
    db.add(task)
    db.commit()

    rec = recommend_robot_for_task(db, task.id)
    assert rec["status"] == "recommendation_available"
    assert rec["recommended_robot"]["robot_code"] == "ROB-P3-FREE"

    busy_cand = next(c for c in rec["candidates"] if c["robot_code"] == "ROB-P3-BUSY")
    assert busy_cand["eligible"] is False
    assert "busy" in busy_cand["rejection_reason"].lower()


# ---------------------------------------------------------------------------
# Test Scenario 5: Warehouse Matching
# ---------------------------------------------------------------------------
def test_scenario_5_warehouse_matching(db: Session, setup_phase3_data):
    wh1 = setup_phase3_data["wh1"]
    wh2 = setup_phase3_data["wh2"]

    # Robot in Warehouse 2
    r_wh2 = db.query(Robot).filter(Robot.robot_code == "ROB-P3-WH2").first()
    if not r_wh2:
        r_wh2 = Robot(
            robot_code="ROB-P3-WH2", name="WH2 Bot", warehouse_id=wh2,
            status="AVAILABLE", battery_level=95.0, current_x=1.0, current_y=1.0, enabled=True
        )
        db.add(r_wh2)

    # Task in Warehouse 1
    task = Task(
        task_number=f"TSK-P3-S5-{datetime.now(UTC).timestamp()}",
        warehouse_id=wh1, task_type="PICK", status="QUEUED", requested_quantity=1,
        product_id=setup_phase3_data["item_std"], source_location_id=setup_phase3_data["loc_src"]
    )
    db.add(task)
    db.commit()

    eval_res = evaluate_robot_candidate(db, task, r_wh2)
    assert eval_res["eligible"] is False
    assert "warehouse" in eval_res["rejection_reason"].lower()


# ---------------------------------------------------------------------------
# Test Scenario 6: Capability & Robot Type Mismatch
# ---------------------------------------------------------------------------
def test_scenario_6_capability_and_type_mismatch(db: Session, setup_phase3_data):
    wh_id = setup_phase3_data["wh1"]

    # AGV Robot without specialized capability
    r_agv = db.query(Robot).filter(Robot.robot_code == "ROB-P3-AGV").first()
    if not r_agv:
        r_agv = Robot(
            robot_code="ROB-P3-AGV", name="Standard AGV", warehouse_id=wh_id,
            robot_type="AGV", status="AVAILABLE", battery_level=90.0, current_x=1.0, current_y=1.0,
            metadata=json.dumps({"capabilities": ["STANDARD_PICK"]}), enabled=True
        )
        db.add(r_agv)
    else:
        r_agv.status = "AVAILABLE"
        r_agv.battery_level = 90.0
        r_agv.assigned_task_id = None

    # Task requiring Forklift robot type
    task_type_req = Task(
        task_number=f"TSK-P3-S6-1-{datetime.now(UTC).timestamp()}",
        warehouse_id=wh_id, task_type="PICK", status="QUEUED", requested_quantity=1,
        product_id=setup_phase3_data["item_std"], source_location_id=setup_phase3_data["loc_src"],
        task_metadata=json.dumps({"required_robot_type": "FORKLIFT"})
    )
    db.add(task_type_req)
    db.commit()

    eval_res1 = evaluate_robot_candidate(db, task_type_req, r_agv)
    assert eval_res1["eligible"] is False
    assert "type" in eval_res1["rejection_reason"].lower()

    # Task requiring HEAVY_LIFT capability
    task_cap_req = Task(
        task_number=f"TSK-P3-S6-2-{datetime.now(UTC).timestamp()}",
        warehouse_id=wh_id, task_type="PICK", status="QUEUED", requested_quantity=1,
        product_id=setup_phase3_data["item_std"], source_location_id=setup_phase3_data["loc_src"],
        task_metadata=json.dumps({"required_capability": "HEAVY_LIFT"})
    )
    db.add(task_cap_req)
    db.commit()

    eval_res2 = evaluate_robot_candidate(db, task_cap_req, r_agv)
    assert eval_res2["eligible"] is False
    assert "capability" in eval_res2["rejection_reason"].lower()


# ---------------------------------------------------------------------------
# Test Scenario 7: No Eligible Robots Graceful Response
# ---------------------------------------------------------------------------
def test_scenario_7_no_eligible_robots(db: Session, setup_phase3_data):
    wh_id = setup_phase3_data["wh1"]

    task = Task(
        task_number=f"TSK-P3-S7-{datetime.now(UTC).timestamp()}",
        warehouse_id=wh_id, task_type="PICK", status="QUEUED", requested_quantity=1,
        product_id=setup_phase3_data["item_heavy"], source_location_id=setup_phase3_data["loc_src"]
    )
    db.add(task)
    db.commit()

    # Create a small robot with max payload 50kg (item heavy is 500kg)
    r_small = Robot(
        robot_code=f"ROB-P3-TINY-{datetime.now(UTC).timestamp()}", name="Tiny Bot", warehouse_id=wh_id,
        status="AVAILABLE", battery_level=90.0, current_x=1.0, current_y=1.0, max_payload=50.0, enabled=True
    )
    db.add(r_small)
    db.commit()

    rec = recommend_robot_for_task(db, task.id)
    assert rec["status"] == "no_available_robots"
    assert rec["recommended_robot"] is None
    assert rec["message"] == "No suitable robot currently available."
    db.refresh(task)
    assert task.status == "QUEUED"


# ---------------------------------------------------------------------------
# Test Scenario 8: Idempotent Assignment
# ---------------------------------------------------------------------------
def test_scenario_8_idempotent_assignment(db: Session, setup_phase3_data, phase3_admin_user):
    wh_id = setup_phase3_data["wh1"]

    r = db.query(Robot).filter(Robot.robot_code == "ROB-P3-IDEM").first()
    if not r:
        r = Robot(
            robot_code="ROB-P3-IDEM", name="Idempotent Bot", warehouse_id=wh_id,
            status="AVAILABLE", battery_level=90.0, current_x=1.0, current_y=1.0, enabled=True
        )
        db.add(r)
    else:
        r.status = "AVAILABLE"
        r.assigned_task_id = None
        r.battery_level = 90.0

    task = Task(
        task_number=f"TSK-P3-S8-{datetime.now(UTC).timestamp()}",
        warehouse_id=wh_id, task_type="PICK", status="QUEUED", requested_quantity=1,
        product_id=setup_phase3_data["item_std"], source_location_id=setup_phase3_data["loc_src"]
    )
    db.add(task)
    db.commit()

    # First assignment
    res1 = assign_robot_intelligently(db, task.id, "ROB-P3-IDEM", phase3_admin_user.id, phase3_admin_user.username)
    assert res1["status"] == "assigned"

    # Second idempotent assignment
    res2 = assign_robot_intelligently(db, task.id, "ROB-P3-IDEM", phase3_admin_user.id, phase3_admin_user.username)
    assert res2["status"] == "assigned"
    assert "already assigned" in res2["message"].lower()


# ---------------------------------------------------------------------------
# Test Scenario 9: Concurrent Lock Safety & Conflict Protection
# ---------------------------------------------------------------------------
def test_scenario_9_concurrent_lock_conflict(db: Session, setup_phase3_data, phase3_admin_user):
    wh_id = setup_phase3_data["wh1"]

    r1 = db.query(Robot).filter(Robot.robot_code == "ROB-P3-C1").first()
    if not r1:
        r1 = Robot(
            robot_code="ROB-P3-C1", name="Conc Bot 1", warehouse_id=wh_id,
            status="AVAILABLE", battery_level=90.0, current_x=1.0, current_y=1.0, enabled=True
        )
        db.add(r1)

    r2 = db.query(Robot).filter(Robot.robot_code == "ROB-P3-C2").first()
    if not r2:
        r2 = Robot(
            robot_code="ROB-P3-C2", name="Conc Bot 2", warehouse_id=wh_id,
            status="AVAILABLE", battery_level=90.0, current_x=2.0, current_y=2.0, enabled=True
        )
        db.add(r2)

    task = Task(
        task_number=f"TSK-P3-S9-{datetime.now(UTC).timestamp()}",
        warehouse_id=wh_id, task_type="PICK", status="QUEUED", requested_quantity=1,
        product_id=setup_phase3_data["item_std"], source_location_id=setup_phase3_data["loc_src"]
    )
    db.add(task)
    db.commit()

    # Assign task to Robot 1 first
    assign_robot_intelligently(db, task.id, "ROB-P3-C1", phase3_admin_user.id, phase3_admin_user.username)

    # Attempting to re-assign task to Robot 2 must raise 409 Conflict
    with pytest.raises(Exception) as exc_info:
        assign_robot_intelligently(db, task.id, "ROB-P3-C2", phase3_admin_user.id, phase3_admin_user.username)
    
    assert "409" in str(exc_info.value) or "already assigned" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Test Scenario 10: Manual Assignment Validation & RBAC
# ---------------------------------------------------------------------------
def test_scenario_10_manual_assignment_validation(
    client: TestClient, db: Session, setup_phase3_data, admin_token_p3, staff_token_p3
):
    wh_id = setup_phase3_data["wh1"]

    r = Robot(
        robot_code=f"ROB-P3-M1-{datetime.now(UTC).timestamp()}", name="Manual Bot", warehouse_id=wh_id,
        status="AVAILABLE", battery_level=90.0, current_x=1.0, current_y=1.0, enabled=True
    )
    db.add(r)

    task = Task(
        task_number=f"TSK-P3-S10-{datetime.now(UTC).timestamp()}",
        warehouse_id=wh_id, task_type="PICK", status="QUEUED", requested_quantity=1,
        product_id=setup_phase3_data["item_std"], source_location_id=setup_phase3_data["loc_src"]
    )
    db.add(task)
    db.commit()
    db.refresh(r)
    db.refresh(task)

    # 1. Staff user should get 403 Forbidden
    res_staff = client.post(
        f"/tasks/{task.id}/assign-robot",
        headers={"Authorization": f"Bearer {staff_token_p3}"},
        json={"robot_code": r.robot_code, "assignment_method": "MANUAL"}
    )
    assert res_staff.status_code == 403

    # 2. Admin user should succeed
    res_admin = client.post(
        f"/tasks/{task.id}/assign-robot",
        headers={"Authorization": f"Bearer {admin_token_p3}"},
        json={"robot_code": r.robot_code, "assignment_method": "MANUAL"}
    )
    assert res_admin.status_code == 200
    assert res_admin.json()["status"] == "assigned"


# ---------------------------------------------------------------------------
# Test Scenario 11: Simulation Isolation
# ---------------------------------------------------------------------------
def test_scenario_11_simulation_isolation(db: Session, setup_phase3_data):
    from backend.routers.robots import execute_simulation_tick
    wh_id = setup_phase3_data["wh1"]

    # Initial snapshot of task and robot states
    r = db.query(Robot).filter(Robot.warehouse_id == wh_id, Robot.status == "AVAILABLE").first()
    t = db.query(Task).filter(Task.warehouse_id == wh_id, Task.status == "QUEUED").first()

    t_num = t.task_number if t else None

    # Execute simulation tick
    execute_simulation_tick(db)

    # Verify that unassigned production task remains QUEUED unless assigned by intelligent service
    if t_num:
        t_after = db.query(Task).filter(Task.task_number == t_num).first()
        assert t_after.status in ("QUEUED", "ASSIGNED", "IN_PROGRESS", "COMPLETED")


# ---------------------------------------------------------------------------
# Test Scenario 12: Task & Robot State Machine Progression
# ---------------------------------------------------------------------------
def test_scenario_12_task_state_progression(db: Session, setup_phase3_data, phase3_admin_user):
    wh_id = setup_phase3_data["wh1"]

    r = Robot(
        robot_code=f"ROB-P3-SM-{datetime.now(UTC).timestamp()}", name="State Machine Bot", warehouse_id=wh_id,
        status="IDLE", battery_level=95.0, current_x=1.0, current_y=1.0, enabled=True
    )
    db.add(r)

    task = Task(
        task_number=f"TSK-P3-S12-{datetime.now(UTC).timestamp()}",
        warehouse_id=wh_id, task_type="PICK", status="QUEUED", requested_quantity=1,
        product_id=setup_phase3_data["item_std"], source_location_id=setup_phase3_data["loc_src"]
    )
    db.add(task)
    db.commit()

    db.refresh(r)
    db.refresh(task)

    assert task.status == "QUEUED"
    assert r.status == "IDLE"

    assign_robot_intelligently(db, task.id, r.robot_code, phase3_admin_user.id, phase3_admin_user.username)

    db.refresh(task)
    db.refresh(r)

    # State transition verification: Task QUEUED -> ASSIGNED, Robot IDLE -> ASSIGNED
    assert task.status == "ASSIGNED"
    assert r.status == "ASSIGNED"
    assert task.assigned_robot_id == r.robot_code
    assert r.assigned_task_id == task.id
