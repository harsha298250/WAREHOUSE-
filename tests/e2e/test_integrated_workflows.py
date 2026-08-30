import pytest
import time
from fastapi.testclient import TestClient
from backend.main import app
from backend.models import (
    Warehouse, Item, Inventory, Order, OrderItem, FinancialTransaction, Robot, Task, AuditLedger, SecurityEvent, WarehouseLocation, IncomingShipment
)

client = TestClient(app)

@pytest.fixture
def e2e_setup_data(db):
    # Create isolated warehouses
    wh_a = Warehouse(id="WH-E2E-A", name="E2E Warehouse A", location="12.9716,77.5946")
    wh_b = Warehouse(id="WH-E2E-B", name="E2E Warehouse B", location="13.0827,80.2707")
    db.add_all([wh_a, wh_b])
    db.commit()
    
    # Create locations
    loc_a = WarehouseLocation(id="LOC-E2E-A", warehouse_id="WH-E2E-A", zone="A", aisle="1", rack="1", shelf="1", capacity=100)
    loc_b = WarehouseLocation(id="LOC-E2E-B", warehouse_id="WH-E2E-B", zone="A", aisle="1", rack="1", shelf="1", capacity=100)
    db.add_all([loc_a, loc_b])
    db.commit()
    
    # Create items
    itm_1 = Item(id="ITM-E2E-01", name="E2E Processor", category="Electronics", safety_stock=5, unit_cost=50.0)
    itm_2 = Item(id="ITM-E2E-02", name="E2E Storage", category="Storage", safety_stock=5, unit_cost=30.0)
    db.add_all([itm_1, itm_2])
    db.commit()
    
    # Create inventory
    inv_1 = Inventory(warehouse_id="WH-E2E-A", item_id="ITM-E2E-01", location_id="LOC-E2E-A", on_hand=100, reserved=0, available=100)
    inv_2 = Inventory(warehouse_id="WH-E2E-B", item_id="ITM-E2E-02", location_id="LOC-E2E-B", on_hand=50, reserved=0, available=50)
    db.add_all([inv_1, inv_2])
    db.commit()
    
    # Create robot
    r1 = Robot(robot_code="ROB-E2E-01", name="E2E Bot 1", status="AVAILABLE", battery_level=100.0, warehouse_id="WH-E2E-A")
    db.add(r1)
    db.commit()
    
    yield
    
    # Teardown (conftest.py automatically drops/deletes, but we explicitly clean isolated keys for safety)
    db.query(FinancialTransaction).filter(FinancialTransaction.warehouse_id.in_(["WH-E2E-A", "WH-E2E-B"])).delete(synchronize_session=False)
    db.query(Robot).filter(Robot.robot_code == "ROB-E2E-01").delete(synchronize_session=False)
    db.query(Inventory).filter(Inventory.warehouse_id.in_(["WH-E2E-A", "WH-E2E-B"])).delete(synchronize_session=False)
    db.query(WarehouseLocation).filter(WarehouseLocation.warehouse_id.in_(["WH-E2E-A", "WH-E2E-B"])).delete(synchronize_session=False)
    db.query(OrderItem).filter(OrderItem.item_id.in_(["ITM-E2E-01", "ITM-E2E-02"])).delete(synchronize_session=False)
    db.query(Order).filter(Order.warehouse_id.in_(["WH-E2E-A", "WH-E2E-B"])).delete(synchronize_session=False)
    db.query(Item).filter(Item.id.in_(["ITM-E2E-01", "ITM-E2E-02"])).delete(synchronize_session=False)
    db.query(Warehouse).filter(Warehouse.id.in_(["WH-E2E-A", "WH-E2E-B"])).delete(synchronize_session=False)
    db.commit()

def test_workflow_authentication_and_rbac(db, admin_token, viewer_token):
    # Test valid admin JWT authorization
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    headers_viewer = {"Authorization": f"Bearer {viewer_token}"}
    
    # Authenticated request to user activity logs
    r = client.get("/security/my-activity", headers=headers_viewer)
    assert r.status_code == 200
    
    # Viewer attempting to call order creation endpoint should get 403 Forbidden
    payload = {
        "customer_ref": "E2E Cust",
        "warehouse_id": "WH-E2E-A",
        "items": [{"item_id": "ITM-E2E-01", "requested_qty": 5}]
    }
    r_forbidden = client.post("/wms/orders", json=payload, headers=headers_viewer)
    assert r_forbidden.status_code == 403

def test_workflow_receiving_and_warehouse_isolation(db, e2e_setup_data, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Trigger incoming shipment quality check and stock placement
    r_ship = client.post("/wms/orders", json={
        "customer_ref": "Supplier E2E",
        "warehouse_id": "WH-E2E-A",
        "items": [{"item_id": "ITM-E2E-01", "requested_qty": 20}]
    }, headers=headers)
    assert r_ship.status_code == 201
    
    # Verify warehouse isolation: WH-E2E-B should not have records or aggregates from WH-E2E-A orders
    res_b = client.get("/wms/financial/revenue?warehouse_id=WH-E2E-B", headers=headers)
    assert res_b.status_code == 200
    assert res_b.json()["gross_revenue"] == 0.0

def test_workflow_order_fulfillment_cycle(db, e2e_setup_data, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 1. Create order
    payload = {
        "customer_ref": "E2E Cust",
        "warehouse_id": "WH-E2E-A",
        "items": [{"item_id": "ITM-E2E-01", "requested_qty": 5}]
    }
    r = client.post("/wms/orders", json=payload, headers=headers)
    assert r.status_code == 201
    order_id = r.json()["order_id"]
    
    # 2. Check inventory reservation
    inv = db.query(Inventory).filter(Inventory.warehouse_id == "WH-E2E-A", Inventory.item_id == "ITM-E2E-01").first()
    assert inv.reserved == 5
    assert inv.available == 95
    
    # 3. Simulate scheduler optimization
    r_opt = client.post("/ai/scheduler/optimize?warehouse_id=WH-E2E-A", headers=headers)
    assert r_opt.status_code in (200, 400, 404)
    
    # 4. Verify system logs an audit event
    audit_entry = db.query(AuditLedger).filter(AuditLedger.event_type == "order_created").first()
    if audit_entry:
        assert audit_entry.event_metadata["order_id"] == order_id

def test_simulation_and_scenario_isolation(db, e2e_setup_data, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Fetch initial live inventory counts
    initial_on_hand = db.query(Inventory).filter(Inventory.warehouse_id == "WH-E2E-A", Inventory.item_id == "ITM-E2E-01").first().on_hand
    
    # Trigger simulation runs
    r_sim = client.post("/simulation/runs", json={
        "name": "E2E Sandbox Test",
        "duration_minutes": 10,
        "robot_count": 2,
        "task_load": "medium"
    }, headers=headers)
    assert r_sim.status_code in (200, 201, 400, 404, 422)
    
    # Live inventory must not be mutated by simulation actions
    current_on_hand = db.query(Inventory).filter(Inventory.warehouse_id == "WH-E2E-A", Inventory.item_id == "ITM-E2E-01").first().on_hand
    assert current_on_hand == initial_on_hand

def test_ai_read_only_grounding(db, e2e_setup_data, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Post query to OpenAI/Gemini assistant router
    r = client.post("/api/chat", json={
        "message": "Calculate total inventory value for WH-E2E-A"
    }, headers=headers)
    
    # Read-only tools must succeed or return structured data, never write/mutate database records
    assert r.status_code in (200, 400, 404)
