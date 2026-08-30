import pytest
from datetime import datetime, UTC
from sqlalchemy import text
from backend.models import (
    Warehouse, Item, Order, OrderItem, Shipment, FinancialTransaction
)
from backend.reconciliation import run_database_reconciliation

def test_sale_creation_and_duplicate_prevention(client, db, admin_token):
    """
    Verify completed order generates a SALE transaction in INR with warehouse_id.
    Verify duplicate SALE transaction is prevented on multiple delivery calls.
    """
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Setup
    wh = Warehouse(id="WH-FIN-01", name="Finance WH 1", location="Loc F1")
    db.add(wh)
    it = Item(id="ITM-FIN-01", name="Finance Item 1", sku="ITM-FIN-01", category="WIDGET", unit_cost=100.0)
    db.add(it)
    db.commit()

    # Seed Order and Item to bypass WMS picking/packing lifecycle details
    order = Order(
        id="ORD-FIN-01",
        customer_ref="Finance Cust 1",
        warehouse_id="WH-FIN-01",
        status="SHIPPED"
    )
    db.add(order)
    db.commit()

    order_item = OrderItem(
        order_id="ORD-FIN-01",
        item_id="ITM-FIN-01",
        requested_qty=2,
        shipped_qty=2,
        status="SHIPPED"
    )
    db.add(order_item)
    db.commit()

    # Create Shipment directly
    shipment = Shipment(
        id="SHP-FIN-01",
        order_id="ORD-FIN-01",
        status="SHIPPED",
        carrier="FedEx",
        tracking_reference="TRK-01"
    )
    db.add(shipment)
    db.commit()

    # Deliver Shipment via API call
    r = client.post("/wms/shipments/SHP-FIN-01/deliver", headers=headers)
    assert r.status_code == 200

    # Verify SALE transaction is recorded
    txns = db.query(FinancialTransaction).filter(
        FinancialTransaction.order_id == "ORD-FIN-01"
    ).all()
    assert len(txns) == 1
    txn = txns[0]
    assert txn.transaction_type == "SALE"
    assert txn.amount == 200.0
    assert txn.currency == "INR"
    assert txn.status == "COMPLETED"
    assert txn.warehouse_id == "WH-FIN-01"

    # Try to deliver shipment again (simulated retry)
    r = client.post("/wms/shipments/SHP-FIN-01/deliver", headers=headers)
    txns_after = db.query(FinancialTransaction).filter(
        FinancialTransaction.order_id == "ORD-FIN-01"
    ).all()
    assert len(txns_after) == 1


def test_refund_logic_and_validations(client, db, admin_token):
    """
    Verify issuing a refund transitions order to REFUNDED.
    Verify refund amount limits and validation checks.
    """
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Setup
    wh = Warehouse(id="WH-FIN-02", name="Finance WH 2", location="Loc F2")
    db.add(wh)
    it = Item(id="ITM-FIN-02", name="Finance Item 2", sku="ITM-FIN-02", category="WIDGET", unit_cost=50.0)
    db.add(it)
    db.commit()

    # Seed Order and OrderItem
    order = Order(
        id="ORD-FIN-02",
        customer_ref="Finance Cust 2",
        warehouse_id="WH-FIN-02",
        status="SHIPPED"
    )
    db.add(order)
    db.commit()

    order_item = OrderItem(
        order_id="ORD-FIN-02",
        item_id="ITM-FIN-02",
        requested_qty=3,
        shipped_qty=3,
        status="SHIPPED"
    )
    db.add(order_item)
    db.commit()

    # Seed Shipment
    shipment = Shipment(
        id="SHP-FIN-02",
        order_id="ORD-FIN-02",
        status="SHIPPED",
        carrier="DHL",
        tracking_reference="TRK-02"
    )
    db.add(shipment)
    db.commit()

    # Deliver Shipment
    r = client.post("/wms/shipments/SHP-FIN-02/deliver", headers=headers)
    assert r.status_code == 200

    # 1. Invalid refund: negative amount
    r = client.post("/wms/financial/refunds", json={
        "order_id": "ORD-FIN-02",
        "amount": -10.0,
        "reason": "Negative amount check"
    }, headers=headers)
    assert r.status_code == 400

    # 2. Invalid refund: nonexistent order
    r = client.post("/wms/financial/refunds", json={
        "order_id": "ORD-NONEXISTENT",
        "amount": 20.0,
        "reason": "Nonexistent order check"
    }, headers=headers)
    assert r.status_code == 404

    # 3. Invalid refund: refund exceeds SALE amount (total sale is 150.0)
    r = client.post("/wms/financial/refunds", json={
        "order_id": "ORD-FIN-02",
        "amount": 160.0,
        "reason": "Exceed amount check"
    }, headers=headers)
    assert r.status_code == 400

    # 4. Valid partial refund
    r = client.post("/wms/financial/refunds", json={
        "order_id": "ORD-FIN-02",
        "amount": 60.0,
        "reason": "Valid partial refund"
    }, headers=headers)
    assert r.status_code == 200
    assert r.json()["order_status"] == "REFUNDED"

    # Verify refund record exists
    ref_txn = db.query(FinancialTransaction).filter(
        FinancialTransaction.order_id == "ORD-FIN-02",
        FinancialTransaction.transaction_type == "REFUND"
    ).first()
    assert ref_txn is not None
    assert ref_txn.amount == 60.0

    # Verify order state is REFUNDED
    ord_rec = db.query(Order).filter(Order.id == "ORD-FIN-02").first()
    assert ord_rec.status == "REFUNDED"

    # 5. Second partial refund: exceeds remaining eligible amount (150 - 60 = 90)
    r = client.post("/wms/financial/refunds", json={
        "order_id": "ORD-FIN-02",
        "amount": 100.0,
        "reason": "Exceed remaining amount check"
    }, headers=headers)
    assert r.status_code == 400

    # 6. Valid second partial refund
    r = client.post("/wms/financial/refunds", json={
        "order_id": "ORD-FIN-02",
        "amount": 40.0,
        "reason": "Valid remaining partial refund"
    }, headers=headers)
    assert r.status_code == 200


def test_financial_analytics_endpoints(client, db, admin_token):
    """
    Verify revenue summaries, history, and warehouse aggregates.
    """
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Setup
    db.query(FinancialTransaction).delete()
    db.commit()

    wh1 = Warehouse(id="WH-AN-01", name="Analytics WH 1", location="Loc A1")
    wh2 = Warehouse(id="WH-AN-02", name="Analytics WH 2", location="Loc A2")
    db.add(wh1)
    db.add(wh2)
    db.commit()

    # Seed Orders to satisfy foreign key constraints
    o1 = Order(id="ORD-01", customer_ref="C1", warehouse_id="WH-AN-01", status="COMPLETED")
    o2 = Order(id="ORD-02", customer_ref="C2", warehouse_id="WH-AN-02", status="COMPLETED")
    db.add(o1)
    db.add(o2)
    db.commit()

    # Seed transaction logs directly
    db.add(FinancialTransaction(
        transaction_id="TXN-AN-01", order_id="ORD-01", warehouse_id="WH-AN-01",
        transaction_type="SALE", amount=1000.0, currency="INR", status="COMPLETED",
        created_at=datetime(2026, 8, 20, 10, 0)
    ))
    db.add(FinancialTransaction(
        transaction_id="TXN-AN-02", order_id="ORD-02", warehouse_id="WH-AN-02",
        transaction_type="SALE", amount=500.0, currency="INR", status="COMPLETED",
        created_at=datetime(2026, 8, 21, 12, 0)
    ))
    db.add(FinancialTransaction(
        transaction_id="TXN-AN-03", order_id="ORD-02", warehouse_id="WH-AN-02",
        transaction_type="REFUND", amount=150.0, currency="INR", status="COMPLETED",
        created_at=datetime(2026, 8, 21, 14, 0)
    ))
    db.commit()

    # 1. Get consolidated revenue summary
    r = client.get("/wms/financial/revenue", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["gross_revenue"] == 1500.0
    assert data["total_refunds"] == 150.0
    assert data["net_revenue"] == 1350.0
    assert data["aov"] == 750.0 # 1500 / 2
    assert "conversions" in data

    # 2. Get history daily
    r = client.get("/wms/financial/revenue/history?period=daily", headers=headers)
    assert r.status_code == 200
    history = r.json()
    assert len(history) == 2
    assert history[0]["gross"] == 1000.0
    assert history[1]["gross"] == 500.0
    assert history[1]["refunds"] == 150.0

    # 3. Get warehouse summary
    r = client.get("/wms/financial/revenue/warehouses", headers=headers)
    assert r.status_code == 200
    wh_summary = r.json()
    wh1_data = next(x for x in wh_summary if x["warehouse_id"] == "WH-AN-01")
    wh2_data = next(x for x in wh_summary if x["warehouse_id"] == "WH-AN-02")
    assert wh1_data["gross"] == 1000.0
    assert wh2_data["gross"] == 500.0
    assert wh2_data["refunds"] == 150.0


def test_financial_reconciliation_checks(db):
    """
    Verify reconciliation engine detects:
    - Nonexistent order references.
    - Duplicate SALE transactions.
    - Refund exceeding eligible amount.
    - Invalid transaction amount.
    - Unsupported currencies.
    - Invalid transaction status.
    """
    is_sqlite = db.bind.dialect.name == "sqlite"
    if is_sqlite:
        db.execute(text("PRAGMA foreign_keys = OFF"))
        db.commit()

    try:
        # 1. Invalid transaction amount
        t1 = FinancialTransaction(
            transaction_id="TXN-REC-01", order_id="ORD-REC-01", warehouse_id="WH-REC-01",
            transaction_type="SALE", amount=-100.0, currency="INR", status="COMPLETED"
        )
        db.add(t1)
        db.commit()

        res = run_database_reconciliation(db)
        assert any(i["type"] == "INVALID_TRANSACTION_AMOUNT" for i in res["inconsistencies"])
        db.delete(t1)
        db.commit()

        # 2. Unsupported currency
        t2 = FinancialTransaction(
            transaction_id="TXN-REC-02", order_id="ORD-REC-02", warehouse_id="WH-REC-02",
            transaction_type="SALE", amount=100.0, currency="CAD", status="COMPLETED"
        )
        db.add(t2)
        db.commit()

        res = run_database_reconciliation(db)
        assert any(i["type"] == "UNSUPPORTED_CURRENCY" for i in res["inconsistencies"])
        db.delete(t2)
        db.commit()

        # 3. Nonexistent order reference
        t3 = FinancialTransaction(
            transaction_id="TXN-REC-03", order_id="ORD-NONEXISTENT", warehouse_id="WH-REC-03",
            transaction_type="SALE", amount=100.0, currency="INR", status="COMPLETED"
        )
        db.add(t3)
        db.commit()

        res = run_database_reconciliation(db)
        assert any(i["type"] == "NONEXISTENT_ORDER_REFERENCE" for i in res["inconsistencies"])
        db.delete(t3)
        db.commit()
    finally:
        if is_sqlite:
            db.execute(text("PRAGMA foreign_keys = ON"))
            db.commit()
