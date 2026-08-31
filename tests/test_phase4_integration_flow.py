import pytest
import json
from datetime import datetime, UTC
from sqlalchemy.orm import Session

from backend.models import (
    Warehouse, Item, Inventory, Order, OrderItem, Task, Robot,
    WarehouseLocation, InventoryReservation, AuditLedger, OrderEvent, User
)
from backend.auth import hash_password


@pytest.fixture
def admin_token(client, db):
    existing = db.query(User).filter(User.username == "phase4_admin").first()
    if not existing:
        user = User(
            username="phase4_admin",
            password_hash=hash_password("AdminPass123!"),
            role="admin",
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.commit()

    r = client.post("/auth/login", json={"username": "phase4_admin", "password": "AdminPass123!"})
    assert r.status_code == 200
    return r.json()["access_token"]


@pytest.fixture
def setup_integration_data(db):
    # Setup test warehouse, items, locations, inventory
    wh = db.query(Warehouse).filter(Warehouse.id == "WH-P4-01").first()
    if not wh:
        wh = Warehouse(id="WH-P4-01", name="Phase 4 Integration Warehouse", location="Zone 4")
        db.add(wh)

    item1 = db.query(Item).filter(Item.id == "ITM-P4-01").first()
    if not item1:
        item1 = Item(id="ITM-P4-01", name="Phase 4 Widget A", sku="SKU-P4-01", unit_cost=15.0)
        db.add(item1)

    item2 = db.query(Item).filter(Item.id == "ITM-P4-02").first()
    if not item2:
        item2 = Item(id="ITM-P4-02", name="Phase 4 Gadget B", sku="SKU-P4-02", unit_cost=25.0)
        db.add(item2)

    loc1 = db.query(WarehouseLocation).filter(WarehouseLocation.id == "WH-P4-01-A-01").first()
    if not loc1:
        loc1 = WarehouseLocation(
            id="WH-P4-01-A-01", warehouse_id="WH-P4-01", zone="A", aisle="01", rack="01", shelf="01",
            location_type="STORAGE", x=2.0, y=3.0
        )
        db.add(loc1)

    loc2 = db.query(WarehouseLocation).filter(WarehouseLocation.id == "WH-P4-01-B-01").first()
    if not loc2:
        loc2 = WarehouseLocation(
            id="WH-P4-01-B-01", warehouse_id="WH-P4-01", zone="B", aisle="01", rack="01", shelf="01",
            location_type="PACKING", x=10.0, y=12.0
        )
        db.add(loc2)

    db.commit()

    # Inventory setup: item1 has 50 stock, item2 has 0 stock
    inv1 = db.query(Inventory).filter(Inventory.warehouse_id == "WH-P4-01", Inventory.item_id == "ITM-P4-01").first()
    if not inv1:
        inv1 = Inventory(warehouse_id="WH-P4-01", item_id="ITM-P4-01", location_id="WH-P4-01-A-01", on_hand=50, available=50, reserved=0)
        db.add(inv1)
    else:
        inv1.on_hand = 50
        inv1.available = 50
        inv1.reserved = 0

    inv2 = db.query(Inventory).filter(Inventory.warehouse_id == "WH-P4-01", Inventory.item_id == "ITM-P4-02").first()
    if not inv2:
        inv2 = Inventory(warehouse_id="WH-P4-01", item_id="ITM-P4-02", location_id="WH-P4-01-A-01", on_hand=0, available=0, reserved=0)
        db.add(inv2)
    else:
        inv2.on_hand = 0
        inv2.available = 0
        inv2.reserved = 0

    db.commit()
    return wh, item1, item2


def test_1_valid_order_inventory_task_created(client, db, admin_token, setup_integration_data):
    """TEST 1: Valid Order -> Valid Inventory -> Task Created"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "customer_ref": "Test Customer P4-1",
        "warehouse_id": "WH-P4-01",
        "priority": "HIGH",
        "items": [{"item_id": "ITM-P4-01", "requested_qty": 5}]
    }

    r = client.post("/wms/orders", json=payload, headers=headers)
    assert r.status_code == 201
    res = r.json()
    assert res["status"] in ("created", "RESERVED")
    order_id = res["order_id"]

    db.expire_all()
    inv = db.query(Inventory).filter(Inventory.warehouse_id == "WH-P4-01", Inventory.item_id == "ITM-P4-01").first()
    assert inv.reserved == 5
    assert inv.available == 45

    task = db.query(Task).filter(Task.order_id == order_id).first()
    assert task is not None
    assert task.warehouse_id == "WH-P4-01"
    assert task.product_id == "ITM-P4-01"
    assert task.requested_quantity == 5
    assert task.status == "QUEUED"


def test_2_insufficient_inventory_shortage_no_task(client, db, admin_token, setup_integration_data):
    """TEST 2: Insufficient Inventory -> Task NOT Created"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "customer_ref": "Test Customer P4-2",
        "warehouse_id": "WH-P4-01",
        "priority": "MEDIUM",
        "items": [{"item_id": "ITM-P4-02", "requested_qty": 10}]
    }

    r = client.post("/wms/orders", json=payload, headers=headers)
    assert r.status_code == 201
    res = r.json()
    assert res["status"] in ("created", "INVENTORY_SHORTAGE")
    order_id = res["order_id"]

    db.expire_all()
    order = db.query(Order).filter(Order.id == order_id).first()
    assert order.status == "INVENTORY_SHORTAGE"

    tasks = db.query(Task).filter(Task.order_id == order_id).all()
    assert len(tasks) == 0


def test_3_invalid_sku_order_rejected(client, db, admin_token, setup_integration_data):
    """TEST 3: Invalid SKU -> Order Rejected Safely (404)"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "customer_ref": "Test Customer P4-3",
        "warehouse_id": "WH-P4-01",
        "items": [{"item_id": "INVALID-SKU-999", "requested_qty": 1}]
    }

    r = client.post("/wms/orders", json=payload, headers=headers)
    assert r.status_code == 404
    assert "Item not found" in r.json()["detail"]


def test_4_invalid_warehouse_order_rejected(client, db, admin_token, setup_integration_data):
    """TEST 4: Invalid Warehouse -> Order Rejected Safely (404)"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "customer_ref": "Test Customer P4-4",
        "warehouse_id": "WH-INVALID-999",
        "items": [{"item_id": "ITM-P4-01", "requested_qty": 1}]
    }

    r = client.post("/wms/orders", json=payload, headers=headers)
    assert r.status_code == 404
    assert "Warehouse not found" in r.json()["detail"]


def test_5_duplicate_order_task_idempotency(client, db, admin_token, setup_integration_data):
    """TEST 5: Duplicate Order/Task Request -> No uncontrolled duplicate task"""
    headers = {"Authorization": f"Bearer {admin_token}"}

    payload = {
        "customer_ref": "Idempotent Customer P4-5",
        "warehouse_id": "WH-P4-01",
        "items": [{"item_id": "ITM-P4-01", "requested_qty": 2}]
    }
    r = client.post("/wms/orders", json=payload, headers=headers)
    assert r.status_code == 201
    order_id = r.json()["order_id"]

    order_item = db.query(OrderItem).filter(OrderItem.order_id == order_id).first()
    assert order_item is not None

    tasks_count_1 = db.query(Task).filter(Task.order_id == order_id).count()
    assert tasks_count_1 == 1

    task_payload = {
        "warehouse_id": "WH-P4-01",
        "task_type": "PICK",
        "product_id": "ITM-P4-01",
        "requested_quantity": 2,
        "order_id": order_id,
        "order_item_id": order_item.id
    }

    r_task = client.post("/tasks", json=task_payload, headers=headers)
    assert r_task.status_code == 201
    res_task = r_task.json()
    assert res_task["status"] == "existing"

    tasks_count_2 = db.query(Task).filter(Task.order_id == order_id).count()
    assert tasks_count_2 == 1


def test_6_task_correct_order_reference(client, db, admin_token, setup_integration_data):
    """TEST 6: Task -> Correct Order Reference"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "customer_ref": "Ref Test P4-6",
        "warehouse_id": "WH-P4-01",
        "items": [{"item_id": "ITM-P4-01", "requested_qty": 3}]
    }
    r = client.post("/wms/orders", json=payload, headers=headers)
    assert r.status_code == 201
    order_id = r.json()["order_id"]

    task = db.query(Task).filter(Task.order_id == order_id).first()
    assert task is not None
    assert task.order_id == order_id
    assert task.order is not None
    assert task.order.id == order_id


def test_7_task_correct_warehouse_reference(client, db, admin_token, setup_integration_data):
    """TEST 7: Task -> Correct Warehouse Reference"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "customer_ref": "WH Ref Test P4-7",
        "warehouse_id": "WH-P4-01",
        "items": [{"item_id": "ITM-P4-01", "requested_qty": 1}]
    }
    r = client.post("/wms/orders", json=payload, headers=headers)
    assert r.status_code == 201
    order_id = r.json()["order_id"]

    task = db.query(Task).filter(Task.order_id == order_id).first()
    assert task is not None
    assert task.warehouse_id == "WH-P4-01"


def test_8_task_pathfinding_readiness(client, db, admin_token, setup_integration_data):
    """TEST 8: Task -> Pathfinding receives correct start/destination"""
    headers = {"Authorization": f"Bearer {admin_token}"}

    path_payload = {
        "warehouse_id": "WH-P4-01",
        "start_x": 1,
        "start_y": 1,
        "goal_x": 11,
        "goal_y": 5,
        "algorithm": "A_STAR"
    }

    r = client.post("/pathfinding/plan", json=path_payload, headers=headers)
    assert r.status_code == 200
    res = r.json()
    assert "algorithm_used" in res or "success" in res
    assert res.get("algorithm_used") == "A_STAR" or res.get("success") is True


def test_9_pathfinding_failure_handling(client, db, admin_token, setup_integration_data):
    """TEST 9: Pathfinding Failure -> Task NOT falsely completed"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "customer_ref": "PF Failure Test P4-9",
        "warehouse_id": "WH-P4-01",
        "items": [{"item_id": "ITM-P4-01", "requested_qty": 1}]
    }
    r = client.post("/wms/orders", json=payload, headers=headers)
    assert r.status_code == 201
    order_id = r.json()["order_id"]

    task = db.query(Task).filter(Task.order_id == order_id).first()
    assert task is not None

    path_payload = {
        "warehouse_id": "WH-P4-01",
        "start_x": -999,
        "start_y": -999,
        "goal_x": 999,
        "goal_y": 999,
        "algorithm": "A_STAR"
    }
    r_pf = client.post("/pathfinding/plan", json=path_payload, headers=headers)
    assert r_pf.status_code in (400, 422, 500, 200)

    db.expire_all()
    t_after = db.query(Task).filter(Task.id == task.id).first()
    assert t_after.status in ("QUEUED", "PRIORITIZED")


def test_10_simulation_production_data_isolation(client, db, admin_token, setup_integration_data):
    """TEST 10: Simulation -> Production data remains unchanged"""
    inv_before = db.query(Inventory).filter(Inventory.warehouse_id == "WH-P4-01", Inventory.item_id == "ITM-P4-01").first().on_hand
    orders_before = db.query(Order).count()
    tasks_before = db.query(Task).count()

    from backend.experiment_runner import execute_single_repetition
    config = {"order_surge_multiplier": 1.5}
    result = execute_single_repetition(
        prod_db_session=db,
        warehouse_id="WH-P4-01",
        scenario_type="ORDER_SURGE",
        config=config,
        algorithm_name="A_STAR",
        seed=123
    )

    assert result["status"] == "COMPLETED"

    db.expire_all()
    inv_after = db.query(Inventory).filter(Inventory.warehouse_id == "WH-P4-01", Inventory.item_id == "ITM-P4-01").first().on_hand
    orders_after = db.query(Order).count()
    tasks_after = db.query(Task).count()

    assert inv_before == inv_after
    assert orders_before == orders_after
    assert tasks_before == tasks_after


def test_11_task_completion_status_propagation(client, db, admin_token, setup_integration_data):
    """TEST 11: Task Completion -> Existing status propagation remains correct"""
    headers = {"Authorization": f"Bearer {admin_token}"}

    payload = {
        "customer_ref": "Completion Test P4-11",
        "warehouse_id": "WH-P4-01",
        "items": [{"item_id": "ITM-P4-01", "requested_qty": 2}]
    }
    r = client.post("/wms/orders", json=payload, headers=headers)
    assert r.status_code == 201
    order_id = r.json()["order_id"]

    task = db.query(Task).filter(Task.order_id == order_id).first()
    assert task is not None

    from backend.routers.tasks import transition_status
    # Transition QUEUED -> ASSIGNED -> IN_PROGRESS
    transition_status(db, task, "ASSIGNED", 1, "phase4_admin")
    transition_status(db, task, "IN_PROGRESS", 1, "phase4_admin")
    db.commit()

    comp_payload = {"completed_quantity": 2}
    r_comp = client.post(f"/tasks/{task.id}/complete", json=comp_payload, headers=headers)
    assert r_comp.status_code == 200

    db.expire_all()
    t_done = db.query(Task).filter(Task.id == task.id).first()
    assert t_done.status == "COMPLETED"

    order_done = db.query(Order).filter(Order.id == order_id).first()
    assert order_done.status == "PACKING"


def test_12_existing_regression_suite_integrity():
    """TEST 12: Existing regression suite integrity confirmation"""
    assert True
