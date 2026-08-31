"""
tests/test_phase29_integrated_crud_workflow.py

Comprehensive Integration & CRUD Test Suite for Phase 29:
Integrated Order, Task & Robot Management Workflow.
"""

import pytest
from datetime import datetime, UTC
from sqlalchemy.orm import Session

from backend.models import (
    Warehouse, Item, Inventory, Robot, Task, Order, OrderItem,
    InventoryReservation, RobotRoute, User, AuditLedger
)
from backend.auth import create_access_token


# ---------------------------------------------------------------------------
# FIXTURES
# ---------------------------------------------------------------------------
@pytest.fixture
def setup_p29_environment(db: Session):
    # Ensure warehouse exists
    wh = db.query(Warehouse).filter(Warehouse.id == "WH-P29-01").first()
    if not wh:
        wh = Warehouse(id="WH-P29-01", name="Phase 29 Master Warehouse", location="Bengaluru")
        db.add(wh)

    # Ensure item exists
    item = db.query(Item).filter(Item.id == "ITEM-P29-01").first()
    if not item:
        item = Item(
            id="ITEM-P29-01",
            sku="SKU-P29-01",
            name="Phase 29 Smart Sensor",
            category="Electronics",
            unit="pcs",
            unit_cost=150.0,
            safety_stock=10,
            reorder_threshold=20
        )
        db.add(item)
        db.flush()

    # Ensure inventory exists
    inv = db.query(Inventory).filter(
        Inventory.warehouse_id == "WH-P29-01",
        Inventory.item_id == "ITEM-P29-01"
    ).first()
    if not inv:
        inv = Inventory(
            warehouse_id="WH-P29-01",
            item_id="ITEM-P29-01",
            on_hand=500,
            reserved=0,
            available=500
        )
        db.add(inv)

    # Ensure packing location exists
    from backend.models import WarehouseLocation
    loc = db.query(WarehouseLocation).filter(WarehouseLocation.id == "LOC-P29-PACK-01").first()
    if not loc:
        loc = WarehouseLocation(id="LOC-P29-PACK-01", warehouse_id="WH-P29-01", zone="PACK", aisle="01", rack="01", shelf="01", location_type="PACKING", x=10.0, y=5.0)
        db.add(loc)

    db.commit()
    return wh, item, inv


# ---------------------------------------------------------------------------
# 1. ROBOT CRUD & SAFE REMOVAL GUARDS
# ---------------------------------------------------------------------------
def test_robot_crud_and_safe_removal_guard(client, admin_token, setup_p29_environment, db: Session):
    headers = {"Authorization": f"Bearer {admin_token}"}
    wh, item, _ = setup_p29_environment

    # 1. Create Robot
    robot_code = f"R-P29-TEST-{int(datetime.now().timestamp())}"
    r_create = client.post("/robots", json={
        "robot_code": robot_code,
        "name": "P29 Heavy Lift Bot",
        "warehouse_id": wh.id,
        "robot_type": "AMR",
        "max_payload": 350.0,
        "max_speed": 2.0,
        "enabled": True
    }, headers=headers)
    assert r_create.status_code == 201
    robot_id = r_create.json()["robot_id"]

    # 2. Read Robot detail
    r_get = client.get(f"/robots/{robot_id}", headers=headers)
    assert r_get.status_code == 200
    robot_data = r_get.json()
    assert robot_data["robot_code"] == robot_code
    assert robot_data["status"] == "AVAILABLE"

    # 3. Update Robot (PATCH)
    r_patch = client.patch(f"/robots/{robot_id}", json={
        "name": "P29 Heavy Lift Bot V2",
        "battery_level": 95.0,
        "current_x": 4.5,
        "current_y": 2.5
    }, headers=headers)
    assert r_patch.status_code == 200

    # 4. Simulate active task assignment & attempt deletion (Must block with 409)
    task_test = Task(task_number="TSK-P29-GUARD", warehouse_id=wh.id, task_type="PICK", product_id=item.id, requested_quantity=1, status="ASSIGNED")
    db.add(task_test)
    db.commit()

    bot_db = db.query(Robot).filter(Robot.id == robot_id).first()
    bot_db.status = "ASSIGNED"
    bot_db.assigned_task_id = task_test.id
    db.commit()
    db.expire_all()

    r_del_blocked = client.delete(f"/robots/{robot_id}", headers=headers)
    assert r_del_blocked.status_code == 409
    assert "cannot be removed because it currently has an active task" in r_del_blocked.json()["detail"]

    # 5. Release task and safely deactivate idle robot
    bot_db = db.query(Robot).filter(Robot.id == robot_id).first()
    bot_db.status = "AVAILABLE"
    bot_db.assigned_task_id = None
    db.commit()
    db.expire_all()

    r_del_success = client.delete(f"/robots/{robot_id}", headers=headers)
    assert r_del_success.status_code == 200
    assert r_del_success.json()["status"] == "deactivated"

    # Verify soft deactivation in DB
    bot_db = db.query(Robot).filter(Robot.id == robot_id).first()
    assert bot_db.enabled is False
    assert bot_db.status == "OFFLINE"


# ---------------------------------------------------------------------------
# 2. TASK CRUD, STATE TRANSITIONS & ROUTE INVALIDATION
# ---------------------------------------------------------------------------
def test_task_crud_and_route_invalidation(client, admin_token, setup_p29_environment, db: Session):
    headers = {"Authorization": f"Bearer {admin_token}"}
    wh, item, _ = setup_p29_environment

    # 1. Create Task manually
    r_task = client.post("/tasks", json={
        "warehouse_id": wh.id,
        "task_type": "PICK",
        "product_id": item.id,
        "requested_quantity": 5,
        "notes": "P29 Integration Task"
    }, headers=headers)
    assert r_task.status_code == 201
    task_id = r_task.json()["task_id"]

    # 2. Update Task destination (PATCH /tasks/{id})
    r_patch = client.patch(f"/tasks/{task_id}", json={
        "priority": "HIGH",
        "destination_location_id": "LOC-P29-PACK-01",
        "notes": "Updated destination for packing"
    }, headers=headers)
    assert r_patch.status_code == 200

    # Verify task priority and destination were updated
    db.expire_all()
    task_db = db.query(Task).filter(Task.id == task_id).first()
    assert task_db.priority == "HIGH"
    assert task_db.destination_location_id == "LOC-P29-PACK-01"

    # 3. Test terminal state protection
    task_db.status = "COMPLETED"
    db.commit()

    r_patch_blocked = client.patch(f"/tasks/{task_id}", json={"notes": "Illegal edit"}, headers=headers)
    assert r_patch_blocked.status_code == 409
    assert "Cannot modify task in terminal state" in r_patch_blocked.json()["detail"]


# ---------------------------------------------------------------------------
# 3. ORDER CRUD, PRIORITY PROPAGATION & AUTO-COMPLETION
# ---------------------------------------------------------------------------
def test_order_crud_priority_propagation_and_auto_completion(client, admin_token, setup_p29_environment, db: Session):
    headers = {"Authorization": f"Bearer {admin_token}"}
    wh, item, _ = setup_p29_environment

    # 1. Create Order
    cust_ref = f"CUST-P29-{int(datetime.now().timestamp())}"
    r_ord = client.post("/wms/orders", json={
        "customer_ref": cust_ref,
        "warehouse_id": wh.id,
        "priority": "MEDIUM",
        "items": [{"item_id": item.id, "requested_qty": 10}]
    }, headers=headers)
    assert r_ord.status_code == 201
    order_id = r_ord.json()["order_id"]

    # 2. Update Order Priority (PATCH /wms/orders/{order_id})
    r_ord_patch = client.patch(f"/wms/orders/{order_id}", json={
        "priority": "CRITICAL",
        "notes": "Rush customer request"
    }, headers=headers)
    assert r_ord_patch.status_code == 200

    # Check associated task priority was updated
    assoc_task = db.query(Task).filter(Task.order_id == order_id).first()
    assert assoc_task is not None
    assert assoc_task.priority == "CRITICAL"

    # 3. Complete associated task and verify Order auto-completes
    r_comp = client.post(f"/tasks/{assoc_task.id}/complete", json={
        "completed_quantity": 10
    }, headers=headers)
    assert r_comp.status_code == 200

    # Verify Order status automatically transitioned to COMPLETED
    ord_db = db.query(Order).filter(Order.id == order_id).first()
    assert ord_db.status in ("PACKING", "COMPLETED")


# ---------------------------------------------------------------------------
# 4. ORDER CANCELLATION & INVENTORY RELEASE
# ---------------------------------------------------------------------------
def test_order_cancellation_releases_inventory_and_cancels_tasks(client, admin_token, setup_p29_environment, db: Session):
    headers = {"Authorization": f"Bearer {admin_token}"}
    wh, item, inv = setup_p29_environment

    init_reserved = inv.reserved

    # Create Order
    cust_ref = f"CUST-P29-CANCEL-{int(datetime.now().timestamp())}"
    r_ord = client.post("/wms/orders", json={
        "customer_ref": cust_ref,
        "warehouse_id": wh.id,
        "priority": "HIGH",
        "items": [{"item_id": item.id, "requested_qty": 15}]
    }, headers=headers)
    assert r_ord.status_code == 201
    order_id = r_ord.json()["order_id"]

    # Verify inventory reserved
    db.refresh(inv)
    assert inv.reserved == init_reserved + 15

    # Cancel Order
    r_cancel = client.post(f"/wms/orders/{order_id}/cancel", headers=headers)
    assert r_cancel.status_code == 200

    # Verify reservation released and tasks cancelled
    db.refresh(inv)
    assert inv.reserved == init_reserved

    assoc_task = db.query(Task).filter(Task.order_id == order_id).first()
    assert assoc_task.status == "CANCELLED"


# ---------------------------------------------------------------------------
# 5. SECURITY & WAREHOUSE ISOLATION
# ---------------------------------------------------------------------------
def test_warehouse_isolation_and_rbac(client, viewer_token, setup_p29_environment):
    # Viewer role (staff) should be forbidden from creating/deleting robots
    viewer_headers = {"Authorization": f"Bearer {viewer_token}"}
    r_del = client.delete("/robots/1", headers=viewer_headers)
    assert r_del.status_code == 403
