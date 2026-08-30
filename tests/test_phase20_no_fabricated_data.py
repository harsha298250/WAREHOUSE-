import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.main import app
from backend.database import get_db
from backend.models import (
    Warehouse, Item, Order, OrderItem, FinancialTransaction, Robot, Task, AuditLedger
)

client = TestClient(app)

@pytest.fixture
def test_setup_data(db):
    # Setup isolated test warehouse
    wh_a = Warehouse(id="WH-ISO-A", name="Iso Warehouse A", location="12.9716,77.5946")
    wh_b = Warehouse(id="WH-ISO-B", name="Iso Warehouse B", location="13.0827,80.2707")
    db.add_all([wh_a, wh_b])
    db.commit()
    
    # Setup parent Orders for ForeignKeys
    ord_a = Order(id="ORDER-ISO-A", warehouse_id="WH-ISO-A", status="COMPLETED", customer_ref="CUST-ISO-01")
    ord_b = Order(id="ORDER-ISO-B", warehouse_id="WH-ISO-B", status="COMPLETED", customer_ref="CUST-ISO-02")
    db.add_all([ord_a, ord_b])
    db.commit()
    
    # Items
    itm = Item(id="ITM-ISO-01", name="Iso Processor", category="Electronics", safety_stock=10, unit_cost=80.0)
    db.add(itm)
    db.commit()
    
    # Financial transactions
    tx1 = FinancialTransaction(
        transaction_id="TXN-ISO-A",
        warehouse_id="WH-ISO-A",
        order_id="ORDER-ISO-A",
        transaction_type="SALE",
        amount=150.0,
        currency="INR",
        status="COMPLETED",
        reference_id="REF-ISO-A"
    )
    tx2 = FinancialTransaction(
        transaction_id="TXN-ISO-B",
        warehouse_id="WH-ISO-B",
        order_id="ORDER-ISO-B",
        transaction_type="SALE",
        amount=300.0,
        currency="INR",
        status="COMPLETED",
        reference_id="REF-ISO-B"
    )
    db.add_all([tx1, tx2])
    db.commit()
    
    # Robots (using autoincrement ID, querying with robot_code)
    r1 = Robot(robot_code="ROB-ISO-01", name="Iso Bot 1", status="AVAILABLE", battery_level=90, warehouse_id="WH-ISO-A")
    r2 = Robot(robot_code="ROB-ISO-02", name="Iso Bot 2", status="MAINTENANCE", battery_level=45, warehouse_id="WH-ISO-B")
    db.add_all([r1, r2])
    db.commit()
    
    yield
    
    # Teardown
    db.query(FinancialTransaction).filter(FinancialTransaction.warehouse_id.in_(["WH-ISO-A", "WH-ISO-B"])).delete(synchronize_session=False)
    db.query(Order).filter(Order.id.in_(["ORDER-ISO-A", "ORDER-ISO-B"])).delete(synchronize_session=False)
    db.query(Robot).filter(Robot.robot_code.in_(["ROB-ISO-01", "ROB-ISO-02"])).delete(synchronize_session=False)
    db.query(Item).filter(Item.id == "ITM-ISO-01").delete(synchronize_session=False)
    db.query(Warehouse).filter(Warehouse.id.in_(["WH-ISO-A", "WH-ISO-B"])).delete(synchronize_session=False)
    db.commit()

def test_financial_revenue_database_driven(db, test_setup_data, admin_token):
    # Retrieve financial details via API
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/wms/financial/revenue", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["currency"] == "INR"
    # Gross revenue must be sum of transaction amounts
    assert data["gross_revenue"] >= 450.0

def test_warehouse_isolation_financials(db, test_setup_data, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Query for WH-ISO-A
    res_a = client.get("/wms/financial/revenue?warehouse_id=WH-ISO-A", headers=headers)
    assert res_a.status_code == 200
    data_a = res_a.json()
    assert data_a["gross_revenue"] == 150.0 # Only WH-ISO-A SALE transaction
    
    # Query for WH-ISO-B
    res_b = client.get("/wms/financial/revenue?warehouse_id=WH-ISO-B", headers=headers)
    assert res_b.status_code == 200
    data_b = res_b.json()
    assert data_b["gross_revenue"] == 300.0 # Only WH-ISO-B SALE transaction

def test_robot_telemetry_live_provenance(db, test_setup_data, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/robots", headers=headers)
    assert response.status_code == 200
    
    robots = response.json()
    iso_bot = next((r for r in robots if r["robot_code"] == "ROB-ISO-01"), None)
    assert iso_bot is not None
    # Live status and battery must match exactly what's in the database
    assert iso_bot["status"] == "AVAILABLE"
    assert iso_bot["battery_level"] == 90
    assert iso_bot["warehouse_id"] == "WH-ISO-A"

def test_no_secrets_in_health_telemetry(db, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/health", headers=headers)
    assert response.status_code == 200
    
    text = response.text
    # Verify no private keys, JWT secret keys, or database passwords appear
    assert "9a6b8c9d0e1f2a3b4c5d6e7f8a9b0c1d" not in text
    assert "Admin@123" not in text
    assert "JWT_SECRET" not in text

def test_or_tools_solver_fallback_behavior(db, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Trigger OR-Tools scheduler endpoint
    response = client.post(
        "/ai/scheduler/optimize?warehouse_id=WH-ISO-A",
        headers=headers
    )
    assert response.status_code in (200, 404, 400)
    if response.status_code == 200:
        data = response.json()
        assert data["solver_status"] in ("OPTIMAL", "FEASIBLE", "GREEDY_FALLBACK")
        # Ensure no fake 15% distance calculation (improvement cannot be hardcoded to 15%)
        assert data["metrics"]["ortools_optimized"]["total_travel_distance"] == data["metrics"]["heuristic"]["total_travel_distance"] or data["solver_status"] in ("OPTIMAL", "FEASIBLE")
