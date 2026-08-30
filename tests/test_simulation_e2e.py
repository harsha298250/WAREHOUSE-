import pytest
import json
from datetime import datetime, timedelta
from backend.models import (
    Robot, RobotTelemetryEvent, RobotRoute, RobotReservation, Task, TaskEvent, Inventory, Order, OrderItem,
    Warehouse, Item, WarehouseLocation, WarehouseGridCell, User, AuditLedger, InventoryReservation, StockMovement
)
from backend.auth import hash_password

@pytest.fixture
def admin_token(client, db):
    existing = db.query(User).filter(User.username == "test_e2e_admin").first()
    if not existing:
        user = User(
            username="test_e2e_admin",
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

    r = client.post("/auth/login", json={"username": "test_e2e_admin", "password": "AdminPass123!"})
    assert r.status_code == 200
    return r.json()["access_token"]

def setup_e2e_data(db):
    # Purge
    db.query(RobotTelemetryEvent).delete()
    db.query(RobotRoute).delete()
    db.query(RobotReservation).delete()
    db.query(Robot).delete()
    db.query(TaskEvent).delete()
    db.query(Task).delete()
    db.query(OrderItem).delete()
    db.query(Order).delete()
    db.query(InventoryReservation).delete()
    db.query(StockMovement).filter(StockMovement.item_id == "ITM-E2E-01").delete()
    db.query(WarehouseGridCell).filter(WarehouseGridCell.warehouse_id == "WH-E2E-01").delete()
    db.query(Inventory).delete()
    db.query(WarehouseLocation).filter(WarehouseLocation.warehouse_id == "WH-E2E-01").delete()
    db.query(Item).filter(Item.id == "ITM-E2E-01").delete()
    db.query(Warehouse).filter(Warehouse.id == "WH-E2E-01").delete()
    db.commit()

    wh = Warehouse(id="WH-E2E-01", name="E2E Test Warehouse", location="E2E Loc")
    db.add(wh)
    db.commit()

    item = Item(id="ITM-E2E-01", name="E2E Test Product", unit_cost=50.0, safety_stock=10, reorder_threshold=15)
    db.add(item)
    db.commit()

    loc_pick = WarehouseLocation(
        id="WH-E2E-01-A-01", warehouse_id="WH-E2E-01", zone="A", aisle="01", rack="01", shelf="01",
        location_type="PICKING", capacity=500, x=2.0, y=4.0
    )
    loc_dest = WarehouseLocation(
        id="WH-E2E-01-B-01", warehouse_id="WH-E2E-01", zone="B", aisle="01", rack="01", shelf="01",
        location_type="SHIPPING", capacity=1000, x=8.0, y=5.0
    )
    loc_charge = WarehouseLocation(
        id="WH-E2E-01-C-01", warehouse_id="WH-E2E-01", zone="C", aisle="01", rack="01", shelf="01",
        location_type="CHARGING", capacity=10, x=5.0, y=5.0
    )
    db.add(loc_pick)
    db.add(loc_dest)
    db.add(loc_charge)
    db.commit()

    inv = Inventory(warehouse_id="WH-E2E-01", item_id="ITM-E2E-01", location_id="WH-E2E-01-A-01", on_hand=100, reserved=0, available=100)
    db.add(inv)
    db.commit()

def test_required_end_to_end_simulation(client, db, admin_token):
    setup_e2e_data(db)
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Create order
    order = Order(id="ORD-E2E-01", warehouse_id="WH-E2E-01", status="PENDING", customer_ref="E2E Cust")
    db.add(order)
    db.commit()

    order_item = OrderItem(order_id="ORD-E2E-01", item_id="ITM-E2E-01", requested_qty=3)
    db.add(order_item)
    db.commit()

    # 2. Reserve inventory (simulate reservation manually)
    res = InventoryReservation(order_id="ORD-E2E-01", item_id="ITM-E2E-01", location_id="WH-E2E-01-A-01", reserved_qty=3, released_qty=0)
    db.add(res)
    
    inv = db.query(Inventory).filter(Inventory.warehouse_id == "WH-E2E-01", Inventory.item_id == "ITM-E2E-01").first()
    inv.reserved += 3
    inv.available -= 3
    db.commit()

    # 3. Generate PICK task
    task = Task(
        task_number="TSK-E2E-PICK-1",
        warehouse_id="WH-E2E-01",
        task_type="PICK",
        status="QUEUED",
        source_id="ORD-E2E-01",
        order_id="ORD-E2E-01",
        order_item_id=order_item.id,
        product_id="ITM-E2E-01",
        source_location_id="WH-E2E-01-A-01",
        destination_location_id="WH-E2E-01-B-01",
        requested_quantity=3,
        priority_score=100
    )
    db.add(task)
    db.commit()

    # 4. Create robot fleet
    r = client.post("/robots", json={
        "robot_code": "ROB-E2E-01",
        "name": "E2E Robot 1",
        "warehouse_id": "WH-E2E-01",
        "robot_type": "AGV"
    }, headers=headers)
    assert r.status_code == 201

    bot = db.query(Robot).filter(Robot.robot_code == "ROB-E2E-01").first()
    bot.current_x = 1.0
    bot.current_y = 1.0
    db.commit()

    # 5. Check eligibility & Auto-assign
    r = client.post("/robots/auto-assign?warehouse_id=WH-E2E-01", headers=headers)
    assert r.status_code == 200
    res_assign = r.json()
    assert res_assign["status"] == "success"
    assert res_assign["selected_robot"] == "ROB-E2E-01"

    bot = db.query(Robot).filter(Robot.robot_code == "ROB-E2E-01").first()
    db.refresh(task)
    assert bot.status == "ASSIGNED"
    assert task.status == "ASSIGNED"

    # 6. Step simulation until task is completed, tracking statuses
    seen_statuses = set()
    max_steps = 30
    steps = 0
    while task.status != "COMPLETED" and steps < max_steps:
        client.post("/robots/simulation/step", headers=headers)
        db.refresh(bot)
        db.refresh(task)
        seen_statuses.add(bot.status)
        steps += 1

    assert "MOVING" in seen_statuses
    assert "PICKING" in seen_statuses
    assert "RETURNING" in seen_statuses
    assert bot.status == "AVAILABLE"
    assert task.status == "COMPLETED"

    # Check inventory is deducted
    db.refresh(inv)
    assert inv.on_hand == 97 # 100 - 3 picked
    assert inv.reserved == 0

def test_failure_and_reassignment_e2e(client, db, admin_token):
    setup_e2e_data(db)
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Setup two robots
    client.post("/robots", json={"robot_code": "ROB-A", "name": "Robot A", "warehouse_id": "WH-E2E-01"}, headers=headers)
    client.post("/robots", json={"robot_code": "ROB-B", "name": "Robot B", "warehouse_id": "WH-E2E-01"}, headers=headers)

    bot_a = db.query(Robot).filter(Robot.robot_code == "ROB-A").first()
    bot_b = db.query(Robot).filter(Robot.robot_code == "ROB-B").first()
    bot_a.current_x = 1.0
    bot_a.current_y = 1.0
    bot_b.current_x = 8.0
    bot_b.current_y = 5.0
    db.commit()

    # Create order, reservation, and task
    order = Order(id="ORD-E2E-02", warehouse_id="WH-E2E-01", status="PENDING", customer_ref="E2E Cust")
    db.add(order)
    db.commit()

    order_item = OrderItem(order_id="ORD-E2E-02", item_id="ITM-E2E-01", requested_qty=2)
    db.add(order_item)
    db.commit()

    res = InventoryReservation(order_id="ORD-E2E-02", item_id="ITM-E2E-01", location_id="WH-E2E-01-A-01", reserved_qty=2, released_qty=0)
    db.add(res)
    
    inv = db.query(Inventory).filter(Inventory.warehouse_id == "WH-E2E-01", Inventory.item_id == "ITM-E2E-01").first()
    inv.reserved += 2
    inv.available -= 2
    db.commit()

    task = Task(
        task_number="TSK-E2E-PICK-2",
        warehouse_id="WH-E2E-01",
        task_type="PICK",
        status="QUEUED",
        source_id="ORD-E2E-02",
        order_id="ORD-E2E-02",
        order_item_id=order_item.id,
        product_id="ITM-E2E-01",
        source_location_id="WH-E2E-01-A-01",
        destination_location_id="WH-E2E-01-B-01",
        requested_quantity=2,
        priority_score=100
    )
    db.add(task)
    db.commit()

    # Assign to ROB-A (manually or auto)
    client.post(f"/robots/{bot_a.id}/assign", json={"task_id": task.id}, headers=headers)
    
    # Start execution (Tick 1 -> MOVING)
    client.post("/robots/simulation/step", headers=headers)
    db.refresh(bot_a)
    db.refresh(task)
    assert bot_a.status == "MOVING"
    assert task.status == "IN_PROGRESS"

    # Simulate Robot A failure
    client.post(f"/robots/{bot_a.id}/simulate-failure", headers=headers)
    db.refresh(bot_a)
    db.refresh(task)
    assert bot_a.status == "FAILED"
    assert task.status == "FAILED"
    assert task.assigned_robot_id is None

    # Auto assign to ROB-B
    r = client.post("/robots/auto-assign?warehouse_id=WH-E2E-01", headers=headers)
    assert r.status_code == 200
    res_assign = r.json()
    assert res_assign["status"] == "success"
    assert res_assign["selected_robot"] == "ROB-B"

    db.refresh(task)
    db.refresh(bot_b)
    assert task.status == "ASSIGNED"
    assert task.assigned_robot_id == "ROB-B"
    assert bot_b.status == "ASSIGNED"

    # Execute simulation steps until complete
    seen_statuses_b = set()
    max_steps = 30
    steps = 0
    while task.status != "COMPLETED" and steps < max_steps:
        client.post("/robots/simulation/step", headers=headers)
        db.refresh(bot_b)
        db.refresh(task)
        seen_statuses_b.add(bot_b.status)
        steps += 1

    assert "MOVING" in seen_statuses_b
    assert "PICKING" in seen_statuses_b
    assert "RETURNING" in seen_statuses_b
    assert bot_b.status == "AVAILABLE"
    assert task.status == "COMPLETED"
    db.refresh(inv)
    
    # Verify inventory updated EXACTLY once
    # Initial was 100, E2E-02 picked 2 (leaving 98).
    # If deducted twice it would be 96.
    assert inv.on_hand == 98
