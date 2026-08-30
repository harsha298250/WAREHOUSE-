import pytest
import json
from datetime import datetime, UTC
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from backend.models import (
    Robot, RobotTelemetryEvent, Task, TaskEvent, Warehouse, Item, WarehouseLocation,
    User, AuditLedger, WarehouseGridCell, WarehouseObstacle, RobotRoute, RobotReservation
)
from backend.auth import hash_password
from backend.routers.robots import execute_simulation_tick, transition_robot_status
from backend.routers.pathfinding import run_a_star, validate_path
from backend.routers.or_tools_scheduler import benchmark_ortools_assignment
from backend.audit_ledger import verify_chain, append_entry


@pytest.fixture
def test_admin_token(client, db):
    """Seed and log in an admin user for testing robotics."""
    existing = db.query(User).filter(User.username == "rob_admin").first()
    if not existing:
        user = User(
            username="rob_admin",
            password_hash=hash_password("AdminPass123!"),
            role="admin"
        )
        db.add(user)
        db.commit()

    # Clear login attempts rate limit
    try:
        from backend.main import _login_attempts
        _login_attempts.clear()
    except ImportError:
        pass

    r = client.post("/auth/login", json={"username": "rob_admin", "password": "AdminPass123!"})
    assert r.status_code == 200
    return r.json()["access_token"]


@pytest.fixture
def test_viewer_token(client, db):
    """Seed and log in a viewer user for testing RBAC."""
    existing = db.query(User).filter(User.username == "rob_viewer").first()
    if not existing:
        user = User(
            username="rob_viewer",
            password_hash=hash_password("ViewerPass123!"),
            role="viewer"
        )
        db.add(user)
        db.commit()

    r = client.post("/auth/login", json={"username": "rob_viewer", "password": "ViewerPass123!"})
    assert r.status_code == 200
    return r.json()["access_token"]


def setup_robotics_e2e_data(db):
    """Helper to initialize E2E data clean of conflicts."""
    db.query(RobotReservation).delete()
    db.query(RobotRoute).delete()
    db.query(RobotTelemetryEvent).delete()
    db.query(Robot).delete()
    db.query(TaskEvent).delete()
    db.query(Task).delete()
    db.query(WarehouseObstacle).delete()
    db.query(WarehouseGridCell).delete()
    db.query(WarehouseLocation).filter(WarehouseLocation.warehouse_id.in_(["WH-E2E-01", "WH-E2E-02"])).delete()
    db.query(Item).filter(Item.id == "ITM-E2E-01").delete()
    db.query(Warehouse).filter(Warehouse.id.in_(["WH-E2E-01", "WH-E2E-02"])).delete()
    db.commit()

    # Seed Warehouses
    wh1 = Warehouse(id="WH-E2E-01", name="Robotics Warehouse 1", location="Zone 1")
    wh2 = Warehouse(id="WH-E2E-02", name="Robotics Warehouse 2", location="Zone 2")
    db.add(wh1)
    db.add(wh2)
    db.commit()

    # Seed Item
    item = Item(id="ITM-E2E-01", name="AGV Test Item", unit_cost=50.0, weight_kg=10.0)
    db.add(item)
    db.commit()

    # Locations
    loc_pick = WarehouseLocation(
        id="WH-E2E-01-PICK", warehouse_id="WH-E2E-01", zone="A", aisle="01", rack="01", shelf="01",
        location_type="PICKING", capacity=100, x=1.0, y=1.0
    )
    loc_dest = WarehouseLocation(
        id="WH-E2E-01-DEST", warehouse_id="WH-E2E-01", zone="B", aisle="01", rack="01", shelf="01",
        location_type="SHIPPING", capacity=200, x=5.0, y=5.0
    )
    loc_charge = WarehouseLocation(
        id="WH-E2E-01-CHARGE", warehouse_id="WH-E2E-01", zone="C", aisle="01", rack="01", shelf="01",
        location_type="CHARGING", capacity=5, x=3.0, y=3.0
    )
    db.add(loc_pick)
    db.add(loc_dest)
    db.add(loc_charge)
    db.commit()

    # Grid map setup for WH-E2E-01 (6x6 grid)
    for x in range(6):
        for y in range(6):
            cell_type = "FLOOR"
            if x == 3 and y == 3:
                cell_type = "CHARGING"
            db.add(WarehouseGridCell(
                warehouse_id="WH-E2E-01",
                x=x,
                y=y,
                cell_type=cell_type,
                traversable=True,
                restricted=False,
                cost=1.0
            ))
    db.commit()


def test_robot_management_e2e(client, db, test_admin_token):
    setup_robotics_e2e_data(db)
    headers = {"Authorization": f"Bearer {test_admin_token}"}

    # 1. Create robot
    res = client.post("/robots", json={
        "robot_code": "ROB-E2E-01",
        "name": "E2E Bot 1",
        "warehouse_id": "WH-E2E-01",
        "robot_type": "AGV",
        "max_payload": 150.0
    }, headers=headers)
    assert res.status_code == 201
    bot_id = res.json()["robot_id"]

    # 2. Retrieve Robot
    res = client.get(f"/robots/{bot_id}", headers=headers)
    assert res.status_code == 200
    assert res.json()["robot_code"] == "ROB-E2E-01"
    assert res.json()["status"] == "AVAILABLE"

    # 3. State transition checks
    res = client.patch(f"/robots/{bot_id}", json={"status": "OFFLINE"}, headers=headers)
    assert res.status_code == 200

    # Invalid state transition (OFFLINE to MOVING directly is invalid)
    res = client.patch(f"/robots/{bot_id}", json={"status": "MOVING"}, headers=headers)
    assert res.status_code == 409


def test_robot_task_assignment_constraints(client, db, test_admin_token):
    setup_robotics_e2e_data(db)
    headers = {"Authorization": f"Bearer {test_admin_token}"}

    # Add available robot
    db.add(Robot(
        robot_code="ROB-ASSIGN-1", name="Assign Bot 1", warehouse_id="WH-E2E-01",
        status="AVAILABLE", battery_level=100.0, current_x=0.0, current_y=0.0, max_payload=150.0
    ))
    # Add unavailable (OFFLINE) robot
    db.add(Robot(
        robot_code="ROB-ASSIGN-2", name="Assign Bot 2", warehouse_id="WH-E2E-01",
        status="OFFLINE", battery_level=100.0, current_x=0.0, current_y=0.0, max_payload=150.0
    ))
    # Add low-battery robot
    db.add(Robot(
        robot_code="ROB-ASSIGN-3", name="Assign Bot 3", warehouse_id="WH-E2E-01",
        status="AVAILABLE", battery_level=5.0, current_x=0.0, current_y=0.0, max_payload=150.0
    ))
    # Add low-capacity robot
    db.add(Robot(
        robot_code="ROB-ASSIGN-4", name="Assign Bot 4", warehouse_id="WH-E2E-01",
        status="AVAILABLE", battery_level=100.0, current_x=0.0, current_y=0.0, max_payload=5.0
    ))
    db.commit()

    # Heavy task (10 units * 10kg = 100kg)
    task = Task(
        task_number="TSK-E2E-1", warehouse_id="WH-E2E-01", task_type="PICK", status="QUEUED",
        product_id="ITM-E2E-01", source_location_id="WH-E2E-01-PICK", destination_location_id="WH-E2E-01-DEST",
        requested_quantity=10
    )
    db.add(task)
    db.commit()

    # Try auto-assign with query param
    res = client.post("/robots/auto-assign?warehouse_id=WH-E2E-01", headers=headers)
    assert res.status_code == 200
    # Should assign ROB-ASSIGN-1 (it has enough payload capacity and battery)
    assert res.json()["status"] == "success"
    assert res.json()["selected_robot"] == "ROB-ASSIGN-1"


def test_astar_routing_and_obstacles(db):
    setup_robotics_e2e_data(db)

    # Fetch grid map
    cells = db.query(WarehouseGridCell).filter(WarehouseGridCell.warehouse_id == "WH-E2E-01").all()
    grid_map = {(c.x, c.y): {"traversable": c.traversable, "cost": c.cost, "type": c.cell_type} for c in cells}

    # 1. Straight path planning
    path, cost, duration, msg, expanded = run_a_star((0, 0), (2, 2), grid_map)
    assert path is not None
    assert path[0] == (0, 0)
    assert path[-1] == (2, 2)
    assert len(path) == 5  # (0,0) -> (1,0) -> (2,0) -> (2,1) -> (2,2) or similar

    # 2. Obstacle block path planning
    obstacles = {(1, 0), (0, 1)} # Block all paths out of (0, 0)
    path_blocked, _, _, _, _ = run_a_star((0, 0), (2, 2), grid_map, obstacles)
    assert path_blocked is None

    # 3. Path Validation helper
    valid, reason = validate_path(path, grid_map)
    assert valid is True


def test_collision_avoidance_deadlocks_and_movement(db):
    setup_robotics_e2e_data(db)

    # Add two robots: r1 starts at (0, 0), r2 occupies (1, 0) and r3 occupies (0, 1) to block all routes
    r1 = Robot(
        robot_code="ROB-COL-1", name="Col Bot 1", warehouse_id="WH-E2E-01",
        status="AVAILABLE", battery_level=100.0, current_x=0.0, current_y=0.0, max_payload=150.0
    )
    r2 = Robot(
        robot_code="ROB-COL-2", name="Col Bot 2", warehouse_id="WH-E2E-01",
        status="AVAILABLE", battery_level=100.0, current_x=1.0, current_y=0.0, max_payload=150.0
    )
    r3 = Robot(
        robot_code="ROB-COL-3", name="Col Bot 3", warehouse_id="WH-E2E-01",
        status="AVAILABLE", battery_level=100.0, current_x=0.0, current_y=1.0, max_payload=150.0
    )
    db.add(r1)
    db.add(r2)
    db.add(r3)
    db.commit()

    # Create task for ROB-COL-1 moving to (2, 0)
    t1 = Task(
        task_number="TSK-COL-1", warehouse_id="WH-E2E-01", task_type="PICK", status="QUEUED",
        product_id="ITM-E2E-01", source_location_id="WH-E2E-01-PICK", destination_location_id="WH-E2E-01-DEST",
        requested_quantity=1
    )
    db.add(t1)
    db.commit()

    # Assign task to r1
    r1.assigned_task_id = t1.id
    r1.status = "ASSIGNED"
    db.commit()

    # Run tick 1: plans route and moves to WAITING because next cell is blocked by r2/r3
    execute_simulation_tick(db)
    db.refresh(r1)

    # ROB-COL-1 is blocked, transitions immediately to WAITING
    assert r1.status == "WAITING"

    # Simulate waiting ticks to check replanning / deadlocks
    for _ in range(3):
        execute_simulation_tick(db)
    
    # Path replanning triggers on tick 3
    db.refresh(r1)
    replanned_route = db.query(RobotRoute).filter(RobotRoute.robot_id == r1.id, RobotRoute.status == "ACTIVE").first()
    assert replanned_route is not None


def test_battery_depletion_and_charging(db):
    setup_robotics_e2e_data(db)

    r = Robot(
        robot_code="ROB-BAT-1", name="Bat Bot 1", warehouse_id="WH-E2E-01",
        status="CHARGING", battery_level=80.0, current_x=3.0, current_y=3.0
    )
    db.add(r)
    db.commit()

    # Charging state tick increments battery by +15.0%
    execute_simulation_tick(db)
    db.refresh(r)
    assert r.battery_level == 95.0

    # Charge again to complete charging
    execute_simulation_tick(db)
    db.refresh(r)
    assert r.battery_level == 100.0
    assert r.status == "AVAILABLE"


def test_ortools_assignment_benchmark(db):
    setup_robotics_e2e_data(db)

    # Seed robots & tasks
    db.add(Robot(
        robot_code="ROB-OPT-1", name="Opt Bot 1", warehouse_id="WH-E2E-01",
        status="AVAILABLE", battery_level=100.0, current_x=0.0, current_y=0.0
    ))
    db.add(Task(
        task_number="TSK-OPT-1", warehouse_id="WH-E2E-01", task_type="PICK", status="QUEUED",
        product_id="ITM-E2E-01", source_location_id="WH-E2E-01-PICK", destination_location_id="WH-E2E-01-DEST",
        requested_quantity=2
    ))
    db.commit()

    # Run optimizer benchmark
    res = benchmark_ortools_assignment(db, "WH-E2E-01")
    assert res["status"] == "success"
    # Should resolve valid schedules
    assert "ortools_optimized" in res["metrics"]


def test_security_rbac_robot_creation(client, db, test_viewer_token):
    setup_robotics_e2e_data(db)
    headers = {"Authorization": f"Bearer {test_viewer_token}"}

    # Attempt robot creation by viewer should fail with 403 Forbidden
    res = client.post("/robots", json={
        "robot_code": "ROB-RBAC",
        "name": "RBAC Bot",
        "warehouse_id": "WH-E2E-01"
    }, headers=headers)
    assert res.status_code == 403


def test_audit_ledger_integrity(db):
    setup_robotics_e2e_data(db)
    
    # Write some valid chained entries to ensure chain checks successfully
    append_entry(db, "TEST_START", {"msg": "Initial entry"})
    append_entry(db, "TEST_PROGRESS", {"msg": "Chained entry"})
    
    # Verify that all entries written comply with the hash chaining verification rule
    res = verify_chain(db)
    assert res["valid"] is True
    assert res["checked"] >= 2
