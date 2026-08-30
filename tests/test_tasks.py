import pytest
import json
from datetime import datetime, timedelta
from backend.models import Task, TaskEvent, Inventory, Order, OrderItem, Warehouse, Item, WarehouseLocation, User
from backend.auth import hash_password

@pytest.fixture
def staff_token(client, db):
    """Seed and log in a staff user for testing tasks."""
    existing = db.query(User).filter(User.username == "test_tasks_staff").first()
    if not existing:
        user = User(
            username="test_tasks_staff",
            password_hash=hash_password("StaffPass123!"),
            role="staff"
        )
        db.add(user)
        db.commit()

    # Clear rate limiter
    try:
        from backend.main import _login_attempts
        _login_attempts.clear()
    except ImportError:
        pass

    r = client.post("/auth/login", json={"username": "test_tasks_staff", "password": "StaffPass123!"})
    assert r.status_code == 200
    return r.json()["access_token"]

def setup_tasks_test_data(db):
    """Utility to set up test warehouse data."""
    # Delete test-specific objects to prevent primary key conflicts
    db.query(TaskEvent).delete()
    db.query(Task).delete()
    db.query(OrderItem).delete()
    db.query(Order).delete()
    db.query(Inventory).delete()
    db.query(WarehouseLocation).filter(WarehouseLocation.warehouse_id == "WH-TEST-01").delete()
    db.query(Item).filter(Item.id == "ITM-TEST-01").delete()
    db.query(Warehouse).filter(Warehouse.id == "WH-TEST-01").delete()
    db.commit()

    wh = Warehouse(id="WH-TEST-01", name="Test Warehouse", location="Test Loc")
    db.add(wh)
    db.commit()

    item = Item(id="ITM-TEST-01", name="Test Item", unit_cost=10.0, safety_stock=10, reorder_threshold=15)
    db.add(item)
    db.commit()

    loc_pick = WarehouseLocation(id="WH-TEST-01-A-01", warehouse_id="WH-TEST-01", zone="A", aisle="01", rack="01", shelf="01", location_type="PICKING", capacity=500)
    loc_bulk = WarehouseLocation(id="WH-TEST-01-B-01", warehouse_id="WH-TEST-01", zone="B", aisle="01", rack="01", shelf="01", location_type="BULK", capacity=1000)
    db.add(loc_pick)
    db.add(loc_bulk)
    db.commit()

    inv_pick = Inventory(warehouse_id="WH-TEST-01", item_id="ITM-TEST-01", location_id="WH-TEST-01-A-01", on_hand=30, reserved=0, available=30)
    inv_bulk = Inventory(warehouse_id="WH-TEST-01", item_id="ITM-TEST-01", location_id="WH-TEST-01-B-01", on_hand=200, reserved=0, available=200)
    db.add(inv_pick)
    db.add(inv_bulk)
    db.commit()

def test_manual_task_creation_lifecycle_and_transitions(client, admin_token, staff_token, db):
    setup_tasks_test_data(db)
    
    headers = {'Authorization': f'Bearer {admin_token}'}
    
    # 1. Create a manual PUTAWAY task
    payload = {
        "warehouse_id": "WH-TEST-01",
        "task_type": "PUTAWAY",
        "product_id": "ITM-TEST-01",
        "source_location_id": "WH-TEST-01-B-01",
        "destination_location_id": "WH-TEST-01-A-01",
        "requested_quantity": 50,
        "notes": "Manual putaway check"
    }
    res = client.post("/tasks", json=payload, headers=headers)
    assert res.status_code == 201, f"Expected 201, got {res.status_code}: {res.text}"
    data = res.json()
    assert data["status"] == "created"
    task_id = data["task_id"]
    assert data["task_number"].startswith("TSK-")

    # 2. Get task details
    res = client.get(f"/tasks/{task_id}", headers=headers)
    assert res.status_code == 200
    task_data = res.json()
    assert task_data["status"] == "QUEUED"
    assert task_data["task_type"] == "PUTAWAY"

    # 3. Prioritize task
    res = client.post(f"/tasks/{task_id}/prioritize", headers=headers)
    assert res.status_code == 200
    assert res.json()["status"] == "prioritized"

    # 4. Assign user
    staff_user = db.query(User).filter(User.username == "test_tasks_staff").first()
    assert staff_user is not None
    assign_payload = {
        "assigned_user_id": staff_user.id,
        "notes": "Assigning to staff operator"
    }
    res = client.post(f"/tasks/{task_id}/assign", json=assign_payload, headers=headers)
    assert res.status_code == 200
    assert res.json()["status"] == "assigned"

    # 5. Start task (as staff user)
    staff_headers = {'Authorization': f'Bearer {staff_token}'}
    res = client.post(f"/tasks/{task_id}/start", headers=staff_headers)
    assert res.status_code == 200
    assert res.json()["status"] == "in_progress"

    # 6. Pause task
    res = client.post(f"/tasks/{task_id}/pause", headers=staff_headers)
    assert res.status_code == 200
    assert res.json()["status"] == "paused"

    # 7. Resume task
    res = client.post(f"/tasks/{task_id}/resume", headers=staff_headers)
    assert res.status_code == 200
    assert res.json()["status"] == "in_progress"

    # 8. Complete task (PUTAWAY)
    complete_payload = {
        "completed_quantity": 50,
        "notes": "Finished putaway"
    }
    res = client.post(f"/tasks/{task_id}/complete", json=complete_payload, headers=staff_headers)
    assert res.status_code == 200
    assert res.json()["status"] == "COMPLETED"

    # 9. Verify history timeline log
    res = client.get(f"/tasks/{task_id}/history", headers=headers)
    assert res.status_code == 200
    history = res.json()
    assert len(history) >= 5
    types = [h["event_type"] for h in history]
    assert "TASK_CREATED" in types
    assert "TASK_ASSIGNED" in types
    assert "TASK_IN_PROGRESS" in types
    assert "TASK_COMPLETED" in types

def test_invalid_transitions(client, admin_token, db):
    setup_tasks_test_data(db)
    headers = {'Authorization': f'Bearer {admin_token}'}

    # Create task
    task = Task(
        task_number="TSK-TRANS-TEST",
        warehouse_id="WH-TEST-01",
        task_type="PUTAWAY",
        product_id="ITM-TEST-01",
        requested_quantity=10,
        status="QUEUED"
    )
    db.add(task)
    db.commit()

    # Try to transition COMPLETED directly from QUEUED (invalid)
    complete_payload = {"completed_quantity": 10}
    res = client.post(f"/tasks/{task.id}/complete", json=complete_payload, headers=headers)
    assert res.status_code == 409  # Conflict / Invalid transition

def test_replenishment_generation(client, admin_token, db):
    setup_tasks_test_data(db)
    headers = {'Authorization': f'Bearer {admin_token}'}

    # Set available inventory to 2 across all locations (below safety stock of 10 and threshold of 15)
    for inv in db.query(Inventory).filter(Inventory.warehouse_id == "WH-TEST-01").all():
        inv.on_hand = 2
        inv.available = 2
    db.commit()

    # Trigger replenishment tasks generation
    res = client.post("/tasks/generate-replenishment", headers=headers)
    assert res.status_code == 200
    assert res.json()["status"] == "success"
    assert res.json()["tasks_generated"] > 0

    # Check that REPLENISH task exists in database
    task = db.query(Task).filter(Task.task_type == "REPLENISH", Task.warehouse_id == "WH-TEST-01").first()
    assert task is not None
    assert task.status == "QUEUED"
    assert task.product_id == "ITM-TEST-01"
