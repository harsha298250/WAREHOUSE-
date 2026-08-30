import pytest
import json
from datetime import datetime, timedelta
from backend.models import (
    Robot, RobotTelemetryEvent, Task, TaskEvent, Inventory, Order, OrderItem,
    Warehouse, Item, WarehouseLocation, User, AuditLedger
)
from backend.auth import hash_password
from backend.routers.robots import calculate_manhattan_distance

@pytest.fixture
def admin_token(client, db):
    """Seed and log in an admin user for testing robots."""
    existing = db.query(User).filter(User.username == "test_robots_admin").first()
    if not existing:
        user = User(
            username="test_robots_admin",
            password_hash=hash_password("AdminPass123!"),
            role="admin"
        )
        db.add(user)
        db.commit()

    # Clear rate limiter
    try:
        from backend.main import _login_attempts
        _login_attempts.clear()
    except ImportError:
        pass

    r = client.post("/auth/login", json={"username": "test_robots_admin", "password": "AdminPass123!"})
    assert r.status_code == 200
    return r.json()["access_token"]

def setup_robots_test_data(db):
    """Utility to set up test warehouse and robot data."""
    # Delete test objects to prevent foreign key or primary key conflicts
    db.query(RobotTelemetryEvent).delete()
    db.query(Robot).delete()
    db.query(TaskEvent).delete()
    db.query(Task).delete()
    db.query(OrderItem).delete()
    db.query(Order).delete()
    db.query(Inventory).delete()
    db.query(WarehouseLocation).filter(WarehouseLocation.warehouse_id == "WH-ROB-01").delete()
    db.query(Item).filter(Item.id == "ITM-ROB-01").delete()
    db.query(Warehouse).filter(Warehouse.id == "WH-ROB-01").delete()
    db.commit()

    wh = Warehouse(id="WH-ROB-01", name="Robot Test Warehouse", location="Robot Loc")
    db.add(wh)
    db.commit()

    item = Item(id="ITM-ROB-01", name="Robot Test Item", unit_cost=20.0, safety_stock=10, reorder_threshold=15)
    db.add(item)
    db.commit()

    # Add locations with coordinates (x, y)
    loc_pick = WarehouseLocation(
        id="WH-ROB-01-A-01", warehouse_id="WH-ROB-01", zone="A", aisle="01", rack="01", shelf="01",
        location_type="PICKING", capacity=500, x=2.0, y=4.0
    )
    loc_dest = WarehouseLocation(
        id="WH-ROB-01-B-01", warehouse_id="WH-ROB-01", zone="B", aisle="01", rack="01", shelf="01",
        location_type="SHIPPING", capacity=1000, x=8.0, y=10.0
    )
    loc_charge = WarehouseLocation(
        id="WH-ROB-01-C-01", warehouse_id="WH-ROB-01", zone="C", aisle="01", rack="01", shelf="01",
        location_type="CHARGING", capacity=10, x=5.0, y=5.0
    )
    db.add(loc_pick)
    db.add(loc_dest)
    db.add(loc_charge)
    db.commit()

    inv = Inventory(warehouse_id="WH-ROB-01", item_id="ITM-ROB-01", location_id="WH-ROB-01-A-01", on_hand=100, reserved=0, available=100)
    db.add(inv)
    db.commit()

def test_robot_uniqueness_and_creation(client, db, admin_token):
    setup_robots_test_data(db)
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Register ROB-001
    r = client.post("/robots", json={
        "robot_code": "ROB-001",
        "name": "Test AGV 1",
        "warehouse_id": "WH-ROB-01",
        "robot_type": "AGV"
    }, headers=headers)
    assert r.status_code == 201
    
    # Conflict check
    r = client.post("/robots", json={
        "robot_code": "ROB-001",
        "name": "Dup Bot",
        "warehouse_id": "WH-ROB-01"
    }, headers=headers)
    assert r.status_code == 409

def test_robot_status_transitions(client, db, admin_token):
    setup_robots_test_data(db)
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Register ROB-001
    client.post("/robots", json={
        "robot_code": "ROB-001",
        "name": "Test AGV 1",
        "warehouse_id": "WH-ROB-01"
    }, headers=headers)

    bot = db.query(Robot).filter(Robot.robot_code == "ROB-001").first()
    assert bot.status == "AVAILABLE"

    # Valid patch
    r = client.patch(f"/robots/{bot.id}", json={"status": "OFFLINE"}, headers=headers)
    assert r.status_code == 200
    db.refresh(bot)
    assert bot.status == "OFFLINE"

    # Invalid transition (OFFLINE cannot go straight to MOVING without AVAILABLE)
    r = client.patch(f"/robots/{bot.id}", json={"status": "MOVING"}, headers=headers)
    assert r.status_code == 409

def test_manhattan_distance_calculation():
    dist = calculate_manhattan_distance(2.0, 4.0, 8.0, 10.0)
    assert dist == 12.0 # abs(8 - 2) + abs(10 - 4) = 6 + 6 = 12

def test_manual_and_auto_robot_assignment(client, db, admin_token):
    setup_robots_test_data(db)
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Add robot
    r_bot = client.post("/robots", json={
        "robot_code": "ROB-AUTO",
        "name": "Auto Bot",
        "warehouse_id": "WH-ROB-01"
    }, headers=headers)
    bot_id = r_bot.json()["robot_id"]

    # Create task
    task = Task(
        task_number="TSK-ROB-1",
        warehouse_id="WH-ROB-01",
        task_type="PICK",
        status="QUEUED",
        product_id="ITM-ROB-01",
        source_location_id="WH-ROB-01-A-01",
        destination_location_id="WH-ROB-01-B-01",
        requested_quantity=5,
        priority_score=100
    )
    db.add(task)
    db.commit()

    # Manual assign checks
    r = client.post(f"/robots/{bot_id}/assign", json={"task_id": task.id}, headers=headers)
    assert r.status_code == 200
    
    db.refresh(task)
    bot = db.query(Robot).filter(Robot.id == bot_id).first()
    assert task.status == "ASSIGNED"
    assert task.assigned_robot_id == "ROB-AUTO"
    assert bot.status == "ASSIGNED"
    assert bot.assigned_task_id == task.id

    # Release task
    r = client.post(f"/robots/{bot_id}/release", headers=headers)
    assert r.status_code == 200
    db.refresh(task)
    db.refresh(bot)
    assert task.status == "QUEUED"
    assert bot.status == "AVAILABLE"
    assert bot.assigned_task_id is None

    # Test auto assignment
    r = client.post(f"/robots/auto-assign?warehouse_id=WH-ROB-01", headers=headers)
    assert r.status_code == 200
    res = r.json()
    assert res["status"] == "success"
    assert res["selected_robot"] == "ROB-AUTO"
    assert "explanation" in res

def test_simulated_failure_and_recovery(client, db, admin_token):
    setup_robots_test_data(db)
    headers = {"Authorization": f"Bearer {admin_token}"}

    r_bot = client.post("/robots", json={
        "robot_code": "ROB-FAIL",
        "name": "Fail Bot",
        "warehouse_id": "WH-ROB-01"
    }, headers=headers)
    bot_id = r_bot.json()["robot_id"]

    task = Task(
        task_number="TSK-ROB-2",
        warehouse_id="WH-ROB-01",
        task_type="PICK",
        status="QUEUED",
        product_id="ITM-ROB-01",
        source_location_id="WH-ROB-01-A-01",
        destination_location_id="WH-ROB-01-B-01",
        requested_quantity=5
    )
    db.add(task)
    db.commit()

    # Assign and fail
    client.post(f"/robots/{bot_id}/assign", json={"task_id": task.id}, headers=headers)
    r = client.post(f"/robots/{bot_id}/simulate-failure", headers=headers)
    assert r.status_code == 200

    bot = db.query(Robot).filter(Robot.id == bot_id).first()
    db.refresh(bot)
    db.refresh(task)
    assert bot.status == "FAILED"
    assert bot.assigned_task_id is None
    assert task.status == "FAILED"
    assert task.assigned_robot_id is None

    # Recover robot
    r = client.post(f"/robots/{bot_id}/recover", headers=headers)
    assert r.status_code == 200
    db.refresh(bot)
    assert bot.status == "AVAILABLE"
    assert bot.battery_level == 100.0
