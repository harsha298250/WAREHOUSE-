import pytest
from datetime import datetime, UTC
from backend.models import (
    Warehouse, Item, Inventory, InventoryReservation,
    Order, OrderItem, Task, PackingRecord, Shipment, OrderEvent,
    WarehouseLocation, StockMovement, IncomingShipment, User, AuditLedger,
    InventoryMovement, FinancialTransaction
)
from backend.reconciliation import run_database_reconciliation

def test_receiving_and_putaway_ledger_flow(client, db, admin_token):
    """
    Verify that expected receiving -> QC -> putaway correctly logs receiving movement in ledger.
    Verify that QC failure does NOT log a successful receiving movement.
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 1. Setup
    wh = Warehouse(id="WH-LEDG-01", name="Ledger Warehouse", location="Loc L")
    db.add(wh)
    it = Item(id="ITM-LEDG-01", name="Ledger Widget", sku="ITM-LEDG-01", category="WIDGET", unit_cost=10.0)
    db.add(it)
    loc = WarehouseLocation(id="WH-LEDG-01-A-01", warehouse_id="WH-LEDG-01", zone="A", aisle="1", rack="1", shelf="1", capacity=100)
    db.add(loc)
    db.commit()

    # 2. Inbound expected shipment
    r = client.post("/wms/receiving/shipments", json={
        "warehouse_id": "WH-LEDG-01",
        "supplier": "Test Supplier",
        "item_id": "ITM-LEDG-01",
        "expected_qty": 20
    }, headers=headers)
    assert r.status_code == 201
    shipment_id = r.json()["id"]

    # 3. Unload & Receive
    r = client.post(f"/wms/receiving/shipments/{shipment_id}/receive", json={"received_qty": 20}, headers=headers)
    assert r.status_code == 200

    # 4. Verify Discrepancies
    r = client.post(f"/wms/receiving/shipments/{shipment_id}/verify", headers=headers)
    assert r.status_code == 200

    # 5. QC Pass
    r = client.post(f"/wms/receiving/shipments/{shipment_id}/qc", json={"qc_result": "QC_PASSED"}, headers=headers)
    assert r.status_code == 200

    # 6. Putaway (should trigger Inventory ledger entry!)
    r = client.post(f"/wms/receiving/shipments/{shipment_id}/putaway", json={"location_id": "WH-LEDG-01-A-01"}, headers=headers)
    assert r.status_code == 200

    # Verify inventory was updated
    inv = db.query(Inventory).filter(
        Inventory.warehouse_id == "WH-LEDG-01",
        Inventory.item_id == "ITM-LEDG-01",
        Inventory.location_id == "WH-LEDG-01-A-01"
    ).first()
    assert inv is not None
    assert inv.on_hand == 20

    # Verify movement ledger contains PUTAWAY movement
    mv = db.query(InventoryMovement).filter(
        InventoryMovement.warehouse_id == "WH-LEDG-01",
        InventoryMovement.item_id == "ITM-LEDG-01",
        InventoryMovement.movement_type == "PUTAWAY"
    ).first()
    assert mv is not None
    assert mv.quantity == 20
    assert mv.quantity_before == 0
    assert mv.quantity_after == 20
    assert mv.destination_location_id == "WH-LEDG-01-A-01"
    assert mv.shipment_id == shipment_id


def test_qc_failed_receiving_no_ledger_record(client, db, admin_token):
    """
    Verify that QC Failed shipments do not mutate on-hand inventory or write receiving movement ledger entries.
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 1. Setup
    wh = Warehouse(id="WH-LEDG-02", name="Ledger Warehouse 2", location="Loc L2")
    db.add(wh)
    it = Item(id="ITM-LEDG-02", name="Ledger Widget 2", sku="ITM-LEDG-02", category="WIDGET", unit_cost=10.0)
    db.add(it)
    db.commit()

    # 2. Create expected shipment
    r = client.post("/wms/receiving/shipments", json={
        "warehouse_id": "WH-LEDG-02",
        "item_id": "ITM-LEDG-02",
        "expected_qty": 50
    }, headers=headers)
    shipment_id = r.json()["id"]

    # 3. Receive & Verify
    client.post(f"/wms/receiving/shipments/{shipment_id}/receive", json={"received_qty": 50}, headers=headers)
    client.post(f"/wms/receiving/shipments/{shipment_id}/verify", headers=headers)

    # 4. Submit QC Failure
    r = client.post(f"/wms/receiving/shipments/{shipment_id}/qc", json={"qc_result": "QC_FAILED"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["status"] == "QC_FAILED"

    # Try to putaway a QC failed shipment (should fail with 409!)
    r = client.post(f"/wms/receiving/shipments/{shipment_id}/putaway", json={"location_id": "nonexistent"}, headers=headers)
    assert r.status_code == 409

    # Verify quarantine receiving movement exists
    mvs = db.query(InventoryMovement).filter(InventoryMovement.item_id == "ITM-LEDG-02").all()
    assert len(mvs) == 1
    assert mvs[0].movement_type == "RECEIVING"
    assert mvs[0].destination_location_id.endswith("-QUARANTINE")


def test_order_reservation_and_cancel_ledger_flow(client, db, admin_token):
    """
    Verify order reservation logs RESERVE, and order cancellation logs RESERVE_RELEASE.
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 1. Setup
    wh = Warehouse(id="WH-LEDG-03", name="Ledger Warehouse 3", location="Loc L3")
    db.add(wh)
    it = Item(id="ITM-LEDG-03", name="Ledger Widget 3", sku="ITM-LEDG-03", category="WIDGET", unit_cost=10.0)
    db.add(it)
    loc = WarehouseLocation(id="WH-LEDG-03-A-01", warehouse_id="WH-LEDG-03", zone="A", aisle="1", rack="1", shelf="1", capacity=100)
    db.add(loc)
    # Seed inventory
    inv = Inventory(warehouse_id="WH-LEDG-03", item_id="ITM-LEDG-03", location_id="WH-LEDG-03-A-01", on_hand=30, reserved=0, available=30)
    db.add(inv)
    db.commit()

    # 2. Create Order (causes reservation!)
    r = client.post("/wms/orders", json={
        "customer_ref": "Trace Cust",
        "warehouse_id": "WH-LEDG-03",
        "items": [{"item_id": "ITM-LEDG-03", "requested_qty": 10}]
    }, headers=headers)
    assert r.status_code == 201
    order_id = r.json()["order_id"]

    # Verify RESERVE ledger entry is logged
    mv_res = db.query(InventoryMovement).filter(
        InventoryMovement.order_id == order_id,
        InventoryMovement.movement_type == "RESERVE"
    ).first()
    assert mv_res is not None
    assert mv_res.quantity == 10
    assert mv_res.quantity_before == 0
    assert mv_res.quantity_after == 10

    # 3. Cancel Order (causes release!)
    r = client.post(f"/wms/orders/{order_id}/cancel", headers=headers)
    assert r.status_code == 200

    # Verify RESERVE_RELEASE ledger entry is logged
    mv_rel = db.query(InventoryMovement).filter(
        InventoryMovement.order_id == order_id,
        InventoryMovement.movement_type == "RESERVE_RELEASE"
    ).first()
    assert mv_rel is not None
    assert mv_rel.quantity == 10
    assert mv_rel.quantity_before == 10
    assert mv_rel.quantity_after == 0


def test_picking_completes_ledger_and_reconciliation(client, db, admin_token):
    """
    Verify complete pick task creates PICK and RESERVE_RELEASE logs.
    Verify reconciliation catches database inconsistency when we bypass ledger to modify inventory.
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 1. Setup
    wh = Warehouse(id="WH-LEDG-04", name="Ledger Warehouse 4", location="Loc L4")
    db.add(wh)
    it = Item(id="ITM-LEDG-04", name="Ledger Widget 4", sku="ITM-LEDG-04", category="WIDGET", unit_cost=15.0)
    db.add(it)
    loc_src = WarehouseLocation(id="WH-LEDG-04-A-01", warehouse_id="WH-LEDG-04", zone="A", aisle="1", rack="1", shelf="1", capacity=100)
    db.add(loc_src)
    loc_dest = WarehouseLocation(id="WH-LEDG-04-B-01", warehouse_id="WH-LEDG-04", zone="B", aisle="1", rack="1", shelf="1", capacity=100)
    db.add(loc_dest)
    
    # Seed inventory with RECEIVING movement first, so computed ledger matches initial seeding!
    inv = Inventory(warehouse_id="WH-LEDG-04", item_id="ITM-LEDG-04", location_id="WH-LEDG-04-A-01", on_hand=15, reserved=0, available=15)
    db.add(inv)
    # Log initial receiving movement so ledger matches starting balance
    db.add(InventoryMovement(
        movement_type="RECEIVING",
        item_id="ITM-LEDG-04",
        warehouse_id="WH-LEDG-04",
        destination_location_id="WH-LEDG-04-A-01",
        quantity=15,
        quantity_before=0,
        quantity_after=15,
        reason="Initial Seed"
    ))
    db.commit()

    # 2. Run reconciliation (should pass!)
    res = run_database_reconciliation(db)
    # Filter only for WH-LEDG-04 to avoid anomalies in other tests
    incon_wh4 = [i for i in res["inconsistencies"] if i.get("warehouse_id") == "WH-LEDG-04"]
    assert len(incon_wh4) == 0

    # 3. Create Order
    r = client.post("/wms/orders", json={
        "customer_ref": "Pick Cust",
        "warehouse_id": "WH-LEDG-04",
        "items": [{"item_id": "ITM-LEDG-04", "requested_qty": 5}]
    }, headers=headers)
    assert r.status_code == 201
    order_id = r.json()["order_id"]

    task = db.query(Task).filter(Task.order_id == order_id).first()
    assert task is not None
    # complete pick task requires a destination location and PENDING/IN_PROGRESS status
    task.status = "IN_PROGRESS"
    task.destination_location_id = "WH-LEDG-04-B-01"
    db.commit()

    # 4. Complete picking task
    r = client.post(f"/tasks/{task.id}/complete", json={"completed_quantity": 5}, headers=headers)
    assert r.status_code == 200

    # Verify PICK movement logged
    mv_pick = db.query(InventoryMovement).filter(
        InventoryMovement.task_id == task.id,
        InventoryMovement.movement_type == "PICK"
    ).first()
    assert mv_pick is not None
    assert mv_pick.quantity == 5
    assert mv_pick.quantity_before == 15
    assert mv_pick.quantity_after == 10

    # Verify RESERVE_RELEASE movement logged
    mv_release = db.query(InventoryMovement).filter(
        InventoryMovement.task_id == task.id,
        InventoryMovement.movement_type == "RESERVE_RELEASE"
    ).first()
    assert mv_release is not None
    assert mv_release.quantity == 5
    assert mv_release.quantity_before == 5
    assert mv_release.quantity_after == 0

    # 5. Let's introduce an inconsistency! (Manually increment Inventory.on_hand without a movement entry!)
    db.refresh(inv)
    inv.on_hand += 10
    db.commit()

    # Run reconciliation (should catch the discrepancy!)
    res_mismatch = run_database_reconciliation(db)
    incon_mismatch = [i for i in res_mismatch["inconsistencies"] if i.get("warehouse_id") == "WH-LEDG-04"]
    assert len(incon_mismatch) > 0
    assert any(i["type"] == "INVENTORY_LEDGER_MISMATCH" for i in incon_mismatch)


def test_detailed_reconciliation_validation_checks(db, admin_token):
    """
    Directly verify that the database reconciliation routine detects:
    - Impossible movement quantity (zero or negative).
    - Invalid location references.
    - Nonexistent order references.
    - Duplicate movement references.
    """
    from sqlalchemy import text
    is_sqlite = db.bind.dialect.name == "sqlite"
    if is_sqlite:
        db.execute(text("PRAGMA foreign_keys = OFF"))
        db.commit()

    try:
        # Setup database records for foreign keys
        wh = Warehouse(id="WH-RECON-01", name="Recon WH", location="Loc R")
        db.add(wh)
        it = Item(id="ITM-RECON-01", name="Recon Item", sku="ITM-RECON-01", category="WIDGET", unit_cost=5.0)
        db.add(it)
        db.commit()
        
        item_id = "ITM-RECON-01"
        warehouse_id = "WH-RECON-01"

        # 1. Impossible quantity
        m1 = InventoryMovement(
            movement_type="RECEIVING",
            item_id=item_id,
            warehouse_id=warehouse_id,
            quantity=0,  # impossible
            quantity_before=0,
            quantity_after=0,
            reason="Test Impossible Qty"
        )
        db.add(m1)
        db.commit()

        res = run_database_reconciliation(db)
        assert any(i["type"] == "IMPOSSIBLE_MOVEMENT_QUANTITY" for i in res["inconsistencies"])
        db.delete(m1)
        db.commit()

        # 2. Invalid location reference
        m2 = InventoryMovement(
            movement_type="RECEIVING",
            item_id=item_id,
            warehouse_id=warehouse_id,
            quantity=10,
            quantity_before=0,
            quantity_after=10,
            source_location_id="nonexistent-loc",
            reason="Test Invalid Loc"
        )
        db.add(m2)
        db.commit()

        res = run_database_reconciliation(db)
        assert any(i["type"] == "INVALID_LOCATION_REFERENCE" for i in res["inconsistencies"])
        db.delete(m2)
        db.commit()

        # 3. Nonexistent order reference
        m3 = InventoryMovement(
            movement_type="RESERVE",
            item_id=item_id,
            warehouse_id=warehouse_id,
            quantity=5,
            quantity_before=0,
            quantity_after=5,
            order_id="nonexistent-order",
            reason="Test Nonexistent Order"
        )
        db.add(m3)
        db.commit()

        res = run_database_reconciliation(db)
        assert any(i["type"] == "NONEXISTENT_ORDER_REFERENCE" for i in res["inconsistencies"])
        db.delete(m3)
        db.commit()

        # 4. Duplicate references
        m4 = InventoryMovement(
            movement_type="RECEIVING",
            item_id=item_id,
            warehouse_id=warehouse_id,
            quantity=5,
            quantity_before=0,
            quantity_after=5,
            reference_type="shipment",
            reference_id="DUP-SHIP-01",
            reason="Dup 1"
        )
        m5 = InventoryMovement(
            movement_type="RECEIVING",
            item_id=item_id,
            warehouse_id=warehouse_id,
            quantity=5,
            quantity_before=5,
            quantity_after=10,
            reference_type="shipment",
            reference_id="DUP-SHIP-01",
            reason="Dup 2"
        )
        db.add(m4)
        db.add(m5)
        db.commit()

        res = run_database_reconciliation(db)
        assert any(i["type"] == "DUPLICATE_MOVEMENT_REFERENCE" for i in res["inconsistencies"])
        db.delete(m4)
        db.delete(m5)
        db.delete(wh)
        db.delete(it)
        db.commit()
    finally:
        if is_sqlite:
            db.execute(text("PRAGMA foreign_keys = ON"))
            db.commit()
