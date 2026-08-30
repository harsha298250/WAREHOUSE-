import pytest
from datetime import datetime
from backend.models import (
    Warehouse, Item, Inventory, InventoryReservation,
    Order, OrderItem, Task, PackingRecord, Shipment, OrderEvent,
    WarehouseLocation, StockMovement, IncomingShipment, User, AuditLedger, Robot
)
from backend.auth import hash_password

@pytest.fixture
def admin_token(client, db):
    existing = db.query(User).filter(User.username == "ops_admin").first()
    if not existing:
        user = User(
            username="ops_admin",
            password_hash=hash_password("AdminPass123!"),
            role="admin"
        )
        db.add(user)
        db.commit()

    r = client.post("/auth/login", json={"username": "ops_admin", "password": "AdminPass123!"})
    assert r.status_code == 200
    return r.json()["access_token"]

def test_complete_receiving_and_putaway_workflow(client, db, admin_token):
    """
    Test the full Receiving & Putaway lifecycle:
    INCOMING -> RECEIVED -> VERIFIED -> QC_PASSED -> PUTAWAY_PENDING -> PUTAWAY_COMPLETED
    """
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Setup static data
    wh = Warehouse(id="WH-OPS-01", name="Ops Warehouse", location="Loc 1")
    db.add(wh)
    it = Item(id="ITM-OPS-01", name="Ops Widget", sku="ITM-OPS-01", category="WIDGET", unit_cost=10.0)
    db.add(it)
    loc = WarehouseLocation(id="WH-OPS-01-A-01", warehouse_id="WH-OPS-01", zone="A", aisle="1", rack="1", shelf="1", x=1.0, y=1.0, capacity=100)
    db.add(loc)
    db.commit()

    # 2. Register expected inbound shipment
    r = client.post("/wms/receiving/shipments", json={
        "warehouse_id": "WH-OPS-01",
        "supplier": "Acme Widgets Inc",
        "item_id": "ITM-OPS-01",
        "expected_qty": 50
    }, headers=headers)
    assert r.status_code == 201
    shipment_id = r.json()["id"]
    assert r.json()["status"] == "INCOMING"

    # 3. Receive stock (with quantity check limit)
    r = client.post(f"/wms/receiving/shipments/{shipment_id}/receive", json={
        "received_qty": 50
    }, headers=headers)
    assert r.status_code == 200
    assert r.json()["status"] == "received"

    # 4. Verify received shipment and detect discrepancies
    r = client.post(f"/wms/receiving/shipments/{shipment_id}/verify", headers=headers)
    assert r.status_code == 200
    assert r.json()["status"] == "verified"
    assert r.json()["has_discrepancy"] is False

    # 5. Quality check check
    r = client.post(f"/wms/receiving/shipments/{shipment_id}/qc", json={
        "qc_result": "QC_PASSED"
    }, headers=headers)
    assert r.status_code == 200
    assert r.json()["status"] == "PUTAWAY_PENDING"

    # 6. Putaway shipment to location
    r = client.post(f"/wms/receiving/shipments/{shipment_id}/putaway", json={
        "location_id": "WH-OPS-01-A-01"
    }, headers=headers)
    assert r.status_code == 200
    assert r.json()["status"] == "completed"

    # 7. Check database invariants
    inv = db.query(Inventory).filter(
        Inventory.warehouse_id == "WH-OPS-01",
        Inventory.item_id == "ITM-OPS-01",
        Inventory.location_id == "WH-OPS-01-A-01"
    ).first()
    assert inv is not None
    assert inv.on_hand == 50
    assert inv.available == 50

    # StockMovement verified
    sm = db.query(StockMovement).filter(StockMovement.item_id == "ITM-OPS-01").first()
    assert sm is not None
    assert sm.stock_in == 50
    assert sm.entry_source == "receive_putaway"

    # AuditLedger entry verified
    al = db.query(AuditLedger).filter(AuditLedger.event_type == "STOCK_PUTAWAY").first()
    assert al is not None


def test_receiving_discrepancies_and_qc_failures(client, db, admin_token):
    """
    Test discrepancy detection (expected != received) and QC failure routing.
    """
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Setup static data
    wh = Warehouse(id="WH-OPS-02", name="Ops Warehouse 2", location="Loc 2")
    db.add(wh)
    it = Item(id="ITM-OPS-02", name="Ops Widget 2", sku="ITM-OPS-02", category="WIDGET", unit_cost=5.0)
    db.add(it)
    db.commit()

    # Case A: QC Failure
    r = client.post("/wms/receiving/shipments", json={
        "warehouse_id": "WH-OPS-02",
        "supplier": "Acme Widgets Inc",
        "item_id": "ITM-OPS-02",
        "expected_qty": 20
    }, headers=headers)
    shipment_id_qc = r.json()["id"]

    # Receive 20
    client.post(f"/wms/receiving/shipments/{shipment_id_qc}/receive", json={"received_qty": 20}, headers=headers)
    # Verify
    client.post(f"/wms/receiving/shipments/{shipment_id_qc}/verify", headers=headers)
    # QC fail
    r = client.post(f"/wms/receiving/shipments/{shipment_id_qc}/qc", json={"qc_result": "QC_FAILED"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["status"] == "QC_FAILED"

    # Assert putaway is blocked
    r = client.post(f"/wms/receiving/shipments/{shipment_id_qc}/putaway", json={"location_id": "WH-OPS-02-A-01"}, headers=headers)
    assert r.status_code == 409 # Blocked because status is not PUTAWAY_PENDING

    # Assert standard (non-quarantine) inventory is zero
    inv = db.query(Inventory).filter(
        Inventory.warehouse_id == "WH-OPS-02",
        Inventory.item_id == "ITM-OPS-02",
        ~Inventory.location_id.endswith("-QUARANTINE")
    ).first()
    assert inv is None or inv.on_hand == 0

    # Case B: Discrepancy Detection
    r = client.post("/wms/receiving/shipments", json={
        "warehouse_id": "WH-OPS-02",
        "supplier": "Acme Widgets Inc",
        "item_id": "ITM-OPS-02",
        "expected_qty": 30
    }, headers=headers)
    shipment_id_disc = r.json()["id"]

    # Receive only 25 (discrepancy!)
    client.post(f"/wms/receiving/shipments/{shipment_id_disc}/receive", json={"received_qty": 25}, headers=headers)
    r = client.post(f"/wms/receiving/shipments/{shipment_id_disc}/verify", headers=headers)
    assert r.status_code == 200
    assert r.json()["has_discrepancy"] is True


def test_complete_order_to_shipping_workflow(client, db, admin_token):
    """
    Test E2E operations flow from order creation to final delivery:
    CREATED -> VALIDATED -> RESERVED -> PICKING -> PACKING -> SHIPPED -> COMPLETED
    """
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Setup database records
    wh = Warehouse(id="WH-OPS-03", name="Ops Warehouse 3", location="Loc 3")
    db.add(wh)
    it = Item(id="ITM-OPS-03", name="Ops Widget 3", sku="ITM-OPS-03", category="WIDGET", unit_cost=50.0)
    db.add(it)
    loc_src = WarehouseLocation(id="WH-OPS-03-A-01", warehouse_id="WH-OPS-03", zone="A", aisle="1", rack="1", shelf="1", x=1.0, y=1.0, capacity=100)
    db.add(loc_src)
    loc_dest = WarehouseLocation(id="WH-OPS-03-B-01", warehouse_id="WH-OPS-03", zone="B", aisle="1", rack="1", shelf="1", x=4.0, y=4.0, capacity=100)
    db.add(loc_dest)
    # Seed inventory
    inv = Inventory(warehouse_id="WH-OPS-03", item_id="ITM-OPS-03", location_id="WH-OPS-03-A-01", on_hand=10, reserved=0, available=10)
    db.add(inv)
    db.commit()

    # 1. Create order
    r = client.post("/wms/orders", json={
        "customer_ref": "Ops Cust 1",
        "warehouse_id": "WH-OPS-03",
        "items": [{"item_id": "ITM-OPS-03", "requested_qty": 4}]
    }, headers=headers)
    assert r.status_code == 201
    order_id = r.json()["order_id"]
    assert r.json()["order_status"] == "RESERVED"

    # Verify inventory is reserved
    db.refresh(inv)
    assert inv.reserved == 4
    assert inv.available == 6

    # Verify PICK task is created
    task = db.query(Task).filter(Task.order_id == order_id).first()
    assert task is not None
    assert task.status == "QUEUED"
    assert task.requested_quantity == 4

    # Update PICK task destination to loc_dest (so complete_task won't complain)
    task.destination_location_id = "WH-OPS-03-B-01"
    db.commit()

    # Create robot
    r = client.post("/robots", json={
        "robot_code": "ROB-OPS-01",
        "name": "Ops Robot 1",
        "warehouse_id": "WH-OPS-03",
        "robot_type": "AGV"
    }, headers=headers)
    assert r.status_code == 201

    # Place robot coordinates
    bot = db.query(Robot).filter(Robot.robot_code == "ROB-OPS-01").first()
    bot.current_x = 1.0
    bot.current_y = 1.0
    db.commit()

    # 2. Auto-assign robot
    r = client.post("/robots/auto-assign?warehouse_id=WH-OPS-03", headers=headers)
    assert r.status_code == 200
    assert r.json()["status"] == "success"

    db.refresh(task)
    db.refresh(bot)
    assert task.status == "ASSIGNED"
    assert bot.status == "ASSIGNED"

    # Step simulation to finish picking
    steps = 0
    while task.status != "COMPLETED" and steps < 30:
        client.post("/robots/simulation/step", headers=headers)
        db.refresh(task)
        steps += 1

    assert task.status == "COMPLETED"
    db.refresh(inv)
    assert inv.on_hand == 6
    assert inv.reserved == 0

    # Order should now transition to PACKING status
    order = db.query(Order).filter(Order.id == order_id).first()
    assert order.status == "PACKING"

    # 3. Packing Lifecycle
    r = client.post(f"/wms/packing/{order_id}/start", json={"operator": "Ops Packer", "notes": "Packing ops started"}, headers=headers)
    assert r.status_code == 200

    r = client.post(f"/wms/packing/{order_id}/complete", json={"package_count": 1, "weight_kg": 2.5}, headers=headers)
    assert r.status_code == 200
    db.refresh(order)
    assert order.status == "SHIPPED" # Packed, ready to ship

    # 4. Outbound Shipping
    r = client.post("/wms/shipments", json={
        "order_id": order_id,
        "carrier": "BlueDart Express",
        "tracking_reference": "TRK-OPS-123"
    }, headers=headers)
    assert r.status_code == 201
    shipment_id = r.json()["shipment_id"]

    # Dispatch shipment
    r = client.post(f"/wms/shipments/{shipment_id}/ship", headers=headers)
    assert r.status_code == 200

    # Deliver shipment
    r = client.post(f"/wms/shipments/{shipment_id}/deliver", headers=headers)
    assert r.status_code == 200
    db.refresh(order)
    assert order.status == "COMPLETED"


def test_warehouse_operations_validation_failures(client, db, admin_token):
    """
    Test targeted validation boundaries and rules:
    - Insufficient inventory (reservation shortage)
    - Negative quantity checks
    - Exceeding expected quantities in receiving
    - Invalid status transitions
    """
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Setup
    wh = Warehouse(id="WH-FAIL-01", name="Fail Warehouse", location="Loc F")
    db.add(wh)
    it = Item(id="ITM-FAIL-01", name="Fail Item", sku="ITM-FAIL-01", category="WIDGET", unit_cost=5.0)
    db.add(it)
    db.commit()

    # 1. Insufficient Inventory Shortage Check
    r = client.post("/wms/orders", json={
        "customer_ref": "Shortage Cust",
        "warehouse_id": "WH-FAIL-01",
        "items": [{"item_id": "ITM-FAIL-01", "requested_qty": 100}]
    }, headers=headers)
    assert r.status_code == 201
    assert r.json()["order_status"] == "INVENTORY_SHORTAGE"

    # 2. Exceed Expected Qtys in Receiving
    r = client.post("/wms/receiving/shipments", json={
        "warehouse_id": "WH-FAIL-01",
        "supplier": "Supplier F",
        "item_id": "ITM-FAIL-01",
        "expected_qty": 10
    }, headers=headers)
    shipment_id = r.json()["id"]

    r = client.post(f"/wms/receiving/shipments/{shipment_id}/receive", json={
        "received_qty": 20
    }, headers=headers)
    assert r.status_code == 400 # Quantity exceeds limit!

    # Negative checking
    r = client.post(f"/wms/receiving/shipments/{shipment_id}/receive", json={
        "received_qty": -5
    }, headers=headers)
    assert r.status_code == 422 # Pydantic gt=0 check fails

    # 3. Invalid Order State Transitions
    # Create valid order
    inv = Inventory(warehouse_id="WH-FAIL-01", item_id="ITM-FAIL-01", location_id="WH-FAIL-01-A-01", on_hand=10, reserved=0, available=10)
    db.add(inv)
    loc = WarehouseLocation(id="WH-FAIL-01-A-01", warehouse_id="WH-FAIL-01", zone="A", aisle="1", rack="1", shelf="1", x=1.0, y=1.0, capacity=100)
    db.add(loc)
    db.commit()

    r = client.post("/wms/orders", json={
        "customer_ref": "Transition Cust",
        "warehouse_id": "WH-FAIL-01",
        "items": [{"item_id": "ITM-FAIL-01", "requested_qty": 2}]
    }, headers=headers)
    order_id = r.json()["order_id"]

    # Try starting packing directly when status is RESERVED (valid path PICKING -> PACKING)
    r = client.post(f"/wms/packing/{order_id}/start", json={"operator": "packer"}, headers=headers)
    assert r.status_code == 409 # Rejected due to invalid state transition (current: RESERVED)
