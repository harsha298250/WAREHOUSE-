import pytest
import concurrent.futures
from sqlalchemy.orm import Session

from backend.models import (
    Warehouse, Item, Inventory, Order, OrderItem, Task,
    WarehouseLocation, InventoryReservation, User, OrderEvent
)
from backend.auth import hash_password


@pytest.fixture
def admin_token(client, db):
    user = db.query(User).filter(User.username == "phase2_admin").first()
    if not user:
        user = User(
            username="phase2_admin",
            password_hash=hash_password("AdminPass123!"),
            role="admin",
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.commit()

    r = client.post("/auth/login", json={"username": "phase2_admin", "password": "AdminPass123!"})
    assert r.status_code == 200
    return r.json()["access_token"]


@pytest.fixture
def viewer_token(client, db):
    user = db.query(User).filter(User.username == "phase2_viewer").first()
    if not user:
        user = User(
            username="phase2_viewer",
            password_hash=hash_password("ViewerPass123!"),
            role="viewer",
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.commit()

    r = client.post("/auth/login", json={"username": "phase2_viewer", "password": "ViewerPass123!"})
    assert r.status_code == 200
    return r.json()["access_token"]


@pytest.fixture
def setup_p2_data(db):
    wh = db.query(Warehouse).filter(Warehouse.id == "WH-P2-01").first()
    if not wh:
        wh = Warehouse(id="WH-P2-01", name="Phase 2 Test Warehouse", location="Zone 2")
        db.add(wh)

    items = [
        ("ITM-P2-01", "P2 Widget A", 100),
        ("ITM-P2-02", "P2 Gadget B", 100),
        ("ITM-P2-03", "P2 Component C", 100),
    ]

    for item_id, name, qty in items:
        it = db.query(Item).filter(Item.id == item_id).first()
        if not it:
            it = Item(id=item_id, name=name, sku=f"SKU-{item_id}", unit_cost=20.0)
            db.add(it)

        loc_id = f"WH-P2-01-A-{item_id[-2:]}"
        loc = db.query(WarehouseLocation).filter(WarehouseLocation.id == loc_id).first()
        if not loc:
            loc = WarehouseLocation(
                id=loc_id, warehouse_id="WH-P2-01", zone="A", aisle="01", rack="01", shelf="01",
                location_type="STORAGE", x=1.0, y=1.0
            )
            db.add(loc)

        inv = db.query(Inventory).filter(
            Inventory.warehouse_id == "WH-P2-01",
            Inventory.item_id == item_id
        ).first()
        if not inv:
            inv = Inventory(
                warehouse_id="WH-P2-01", item_id=item_id, location_id=loc_id,
                on_hand=qty, reserved=0, available=qty
            )
            db.add(inv)
        else:
            inv.on_hand = qty
            inv.reserved = 0
            inv.available = qty

    db.commit()


def test_01_single_item_order_task_generation(client, admin_token, setup_p2_data):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "customer_ref": "CUST-P2-001",
        "warehouse_id": "WH-P2-01",
        "priority": "MEDIUM",
        "items": [
            {"item_id": "ITM-P2-01", "requested_qty": 10}
        ]
    }
    r = client.post("/wms/orders", json=payload, headers=headers)
    assert r.status_code == 201
    res = r.json()
    order_id = res["order_id"]
    assert res["order_status"] == "RESERVED"

    # Verify task generation
    r_tasks = client.get(f"/wms/picking?order_id={order_id}", headers=headers)
    assert r_tasks.status_code == 200
    tasks_data = r_tasks.json()["tasks"]
    assert len(tasks_data) == 1
    assert tasks_data[0]["item_id"] == "ITM-P2-01"
    assert tasks_data[0]["qty"] == 10
    assert tasks_data[0]["status"] == "QUEUED"


def test_02_multi_item_order_task_generation(client, admin_token, setup_p2_data):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "customer_ref": "CUST-P2-MULTI",
        "warehouse_id": "WH-P2-01",
        "priority": "HIGH",
        "items": [
            {"item_id": "ITM-P2-01", "requested_qty": 5},
            {"item_id": "ITM-P2-02", "requested_qty": 3},
            {"item_id": "ITM-P2-03", "requested_qty": 2}
        ]
    }
    r = client.post("/wms/orders", json=payload, headers=headers)
    assert r.status_code == 201
    order_id = r.json()["order_id"]

    r_tasks = client.get(f"/wms/picking?order_id={order_id}", headers=headers)
    assert r_tasks.status_code == 200
    tasks_data = r_tasks.json()["tasks"]
    assert len(tasks_data) == 3
    # Check all tasks reference the same order_id
    for t in tasks_data:
        assert t["order_id"] == order_id


def test_03_high_priority_order_task_priority(client, admin_token, db, setup_p2_data):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "customer_ref": "CUST-P2-CRITICAL",
        "warehouse_id": "WH-P2-01",
        "priority": "CRITICAL",
        "items": [
            {"item_id": "ITM-P2-01", "requested_qty": 2}
        ]
    }
    r = client.post("/wms/orders", json=payload, headers=headers)
    assert r.status_code == 201
    order_id = r.json()["order_id"]

    task = db.query(Task).filter(Task.order_id == order_id).first()
    assert task is not None
    assert task.priority == "CRITICAL"
    assert task.priority_score >= 40  # Critical baseline priority score


def test_04_invalid_quantity_validation(client, admin_token, setup_p2_data):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "customer_ref": "CUST-P2-ZERO",
        "warehouse_id": "WH-P2-01",
        "items": [
            {"item_id": "ITM-P2-01", "requested_qty": 0}
        ]
    }
    r = client.post("/wms/orders", json=payload, headers=headers)
    assert r.status_code == 422  # Validation error for requested_qty <= 0


def test_05_invalid_warehouse_and_item_validation(client, admin_token, setup_p2_data):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Invalid Warehouse
    payload_bad_wh = {
        "customer_ref": "CUST-P2-BAD",
        "warehouse_id": "WH-NONEXISTENT",
        "items": [{"item_id": "ITM-P2-01", "requested_qty": 1}]
    }
    r1 = client.post("/wms/orders", json=payload_bad_wh, headers=headers)
    assert r1.status_code == 404

    # Invalid Item
    payload_bad_item = {
        "customer_ref": "CUST-P2-BAD",
        "warehouse_id": "WH-P2-01",
        "items": [{"item_id": "ITM-NONEXISTENT", "requested_qty": 1}]
    }
    r2 = client.post("/wms/orders", json=payload_bad_item, headers=headers)
    assert r2.status_code == 404


def test_06_duplicate_task_generation_prevention(client, admin_token, db, setup_p2_data):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "customer_ref": "CUST-P2-DUP",
        "warehouse_id": "WH-P2-01",
        "items": [{"item_id": "ITM-P2-01", "requested_qty": 2}]
    }
    r = client.post("/wms/orders", json=payload, headers=headers)
    assert r.status_code == 201
    order_id = r.json()["order_id"]

    # Re-call task generation endpoint for the same order
    r_gen = client.post(f"/wms/orders/{order_id}/generate-tasks", headers=headers)
    assert r_gen.status_code == 200

    tasks = db.query(Task).filter(Task.order_id == order_id).all()
    assert len(tasks) == 1  # Exactly 1 task, duplicate generation prevented!


def test_07_concurrent_task_generation(client, admin_token, db, setup_p2_data):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "customer_ref": "CUST-P2-CONCURRENCY",
        "warehouse_id": "WH-P2-01",
        "items": [{"item_id": "ITM-P2-01", "requested_qty": 4}]
    }
    r = client.post("/wms/orders", json=payload, headers=headers)
    assert r.status_code == 201
    order_id = r.json()["order_id"]

    # Multiple rapid attempts to generate tasks for the same order
    results = []
    for _ in range(5):
        res = client.post(f"/wms/orders/{order_id}/generate-tasks", headers=headers)
        results.append(res)

    for res in results:
        assert res.status_code == 200

    # Verify task count remains exactly 1
    r_tasks = client.get(f"/wms/picking?order_id={order_id}", headers=headers)
    assert len(r_tasks.json()["tasks"]) == 1


def test_08_order_cancellation_and_task_invalidation(client, admin_token, db, setup_p2_data):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "customer_ref": "CUST-P2-CANCEL",
        "warehouse_id": "WH-P2-01",
        "items": [{"item_id": "ITM-P2-01", "requested_qty": 3}]
    }
    r = client.post("/wms/orders", json=payload, headers=headers)
    assert r.status_code == 201
    order_id = r.json()["order_id"]

    r_cancel = client.post(f"/wms/orders/{order_id}/cancel", headers=headers)
    assert r_cancel.status_code == 200

    order = db.query(Order).filter(Order.id == order_id).first()
    assert order.status == "CANCELLED"

    tasks = db.query(Task).filter(Task.order_id == order_id).all()
    for t in tasks:
        assert t.status == "CANCELLED"


def test_09_task_failure_handling(client, admin_token, db, setup_p2_data):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "customer_ref": "CUST-P2-FAIL",
        "warehouse_id": "WH-P2-01",
        "items": [{"item_id": "ITM-P2-01", "requested_qty": 2}]
    }
    r = client.post("/wms/orders", json=payload, headers=headers)
    order_id = r.json()["order_id"]

    t = db.query(Task).filter(Task.order_id == order_id).first()
    assert t is not None

    r_fail = client.post(f"/wms/picking/{t.id}/fail", headers=headers)
    assert r_fail.status_code == 200

    order = db.query(Order).filter(Order.id == order_id).first()
    assert order.status == "PICKING_FAILED"


def test_10_task_completion_order_status_progression(client, admin_token, db, setup_p2_data):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "customer_ref": "CUST-P2-COMPLETE",
        "warehouse_id": "WH-P2-01",
        "items": [{"item_id": "ITM-P2-01", "requested_qty": 5}]
    }
    r = client.post("/wms/orders", json=payload, headers=headers)
    order_id = r.json()["order_id"]

    t = db.query(Task).filter(Task.order_id == order_id).first()
    assert t is not None

    # Start picking
    r_start = client.post(f"/wms/picking/{t.id}/start", headers=headers)
    assert r_start.status_code == 200

    # Complete picking
    r_comp = client.post(f"/wms/picking/{t.id}/complete", json={"picked_qty": 5}, headers=headers)
    assert r_comp.status_code == 200

    order = db.query(Order).filter(Order.id == order_id).first()
    assert order.status == "PACKING"


def test_11_rbac_and_authorization_checks(client, viewer_token, setup_p2_data):
    headers = {"Authorization": f"Bearer {viewer_token}"}
    payload = {
        "customer_ref": "CUST-P2-UNAUTH",
        "warehouse_id": "WH-P2-01",
        "items": [{"item_id": "ITM-P2-01", "requested_qty": 1}]
    }
    r = client.post("/wms/orders", json=payload, headers=headers)
    assert r.status_code == 403  # Viewer cannot create order


def test_12_data_integrity_references(client, admin_token, db, setup_p2_data):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "customer_ref": "CUST-P2-INTEGRITY",
        "warehouse_id": "WH-P2-01",
        "items": [{"item_id": "ITM-P2-01", "requested_qty": 2}]
    }
    r = client.post("/wms/orders", json=payload, headers=headers)
    order_id = r.json()["order_id"]

    order = db.query(Order).filter(Order.id == order_id).first()
    assert order is not None
    assert len(order.items) == 1
    oi = order.items[0]
    assert oi.item_id == "ITM-P2-01"

    task = db.query(Task).filter(Task.order_id == order_id).first()
    assert task is not None
    assert task.order_item_id == oi.id
    assert task.product_id == "ITM-P2-01"
    assert task.warehouse_id == "WH-P2-01"
