import pytest
import json
from datetime import datetime, timedelta, date
from backend.models import (
    Warehouse, Item, StockMovement, AIRecommendation, Task, TaskEvent,
    WarehouseLocation, Inventory, AuditLedger, User, ShrinkageFlag, Robot
)
from backend.auth import hash_password

@pytest.fixture
def manager_token(client, db):
    existing = db.query(User).filter(User.username == "test_ai_manager").first()
    if not existing:
        user = User(
            username="test_ai_manager",
            password_hash=hash_password("ManagerPass123!"),
            role="manager"
        )
        db.add(user)
        db.commit()

    try:
        from backend.main import _login_attempts
        _login_attempts.clear()
    except ImportError:
        pass

    r = client.post("/auth/login", json={"username": "test_ai_manager", "password": "ManagerPass123!"})
    assert r.status_code == 200
    return r.json()["access_token"]

@pytest.fixture
def viewer_token(client, db):
    existing = db.query(User).filter(User.username == "test_ai_viewer").first()
    if not existing:
        user = User(
            username="test_ai_viewer",
            password_hash=hash_password("ViewerPass123!"),
            role="viewer"
        )
        db.add(user)
        db.commit()

    try:
        from backend.main import _login_attempts
        _login_attempts.clear()
    except ImportError:
        pass

    r = client.post("/auth/login", json={"username": "test_ai_viewer", "password": "ViewerPass123!"})
    assert r.status_code == 200
    return r.json()["access_token"]

def setup_ai_test_data(db):
    """Seed sufficient chronological stock movements for items to fit forecast regression model."""
    db.query(TaskEvent).delete()
    db.query(Task).delete()
    db.query(AIRecommendation).delete()
    db.query(StockMovement).delete()
    db.query(Inventory).delete()
    db.query(ShrinkageFlag).delete()
    db.query(WarehouseLocation).filter(WarehouseLocation.warehouse_id == "WH-AI-TEST").delete()
    db.query(Item).filter(Item.id == "ITM-AI-TEST").delete()
    db.query(Warehouse).filter(Warehouse.id == "WH-AI-TEST").delete()
    db.commit()

    wh = Warehouse(id="WH-AI-TEST", name="AI Testing Lab", location="Staging Area")
    db.add(wh)
    db.commit()

    item = Item(
        id="ITM-AI-TEST",
        name="AI Smart Sensor",
        category="Sensors",
        unit_cost=150.0,
        lead_time_days=3,
        safety_stock=20,
        sku="SKU-AI-TEST-1004"
    )
    db.add(item)
    db.commit()

    # Seed 20 days of stock movements to prevent "insufficient_data" in forecasting
    start_date = date.today() - timedelta(days=20)
    for i in range(21):
        d = start_date + timedelta(days=i)
        # Weekday seasonality pattern
        wd = d.weekday()
        base_demand = 5 + (wd * 2) # weekday demand variation
        
        sm = StockMovement(
            date=d,
            warehouse_id="WH-AI-TEST",
            item_id="ITM-AI-TEST",
            stock_in=10,
            stock_out=base_demand,
            closing_stock=100 - (i * 3),
            entry_source="manual"
        )
        db.add(sm)
    db.commit()

    # Add locations & inventory
    loc = WarehouseLocation(
        id="LOC-AI-TEST-01",
        warehouse_id="WH-AI-TEST",
        zone="A",
        aisle="1",
        rack="1",
        shelf="1",
        location_type="PICKING"
    )
    db.add(loc)
    inv = Inventory(
        warehouse_id="WH-AI-TEST",
        item_id="ITM-AI-TEST",
        location_id="LOC-AI-TEST-01",
        on_hand=35,
        available=35,
        reserved=0
    )
    db.add(inv)
    db.commit()


def test_forecast_and_metrics(client, db, manager_token):
    setup_ai_test_data(db)
    headers = {"Authorization": f"Bearer {manager_token}"}
    r = client.get("/ai/forecast/WH-AI-TEST/ITM-AI-TEST", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    assert "forecast_next_days" in data
    assert "holdout_validation" in data
    assert "walk_forward_validation" in data
    
    # Verify baseline metrics presence
    holdout = data["holdout_validation"]
    assert "wape_pct" in holdout
    assert "ma_baseline_wape_pct" in holdout
    assert "naive_baseline_wape_pct" in holdout
    assert "reliability_score" in data


def test_inventory_risk_endpoint(client, db, manager_token):
    setup_ai_test_data(db)
    headers = {"Authorization": f"Bearer {manager_token}"}
    r = client.get("/ai/inventory-risk?warehouse_id=WH-AI-TEST", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    assert len(data["items"]) > 0
    item_risk = data["items"][0]
    assert "risk_level" in item_risk
    assert "days_of_supply" in item_risk


def test_abc_analysis_endpoint(client, db, manager_token):
    setup_ai_test_data(db)
    headers = {"Authorization": f"Bearer {manager_token}"}
    r = client.get("/ai/abc-analysis?warehouse_id=WH-AI-TEST", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    assert "abc_items" in data
    first_item = data["abc_items"][0]
    assert "classification" in first_item
    assert first_item["classification"] in ("A", "B", "C")


def test_warehouse_risk_endpoint(client, db, manager_token):
    setup_ai_test_data(db)
    headers = {"Authorization": f"Bearer {manager_token}"}
    
    # Seed a failed robot and stockout to trigger risk drivers
    bot = Robot(
        robot_code="ROB-AI-TEST-99",
        name="Failed Bot",
        warehouse_id="WH-AI-TEST",
        status="FAILED",
        battery_level=12.0
    )
    db.add(bot)
    db.commit()

    r = client.get("/ai/warehouse-risk?warehouse_id=WH-AI-TEST", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    assert "operational_risk_score" in data
    assert "risk_level" in data
    assert len(data["risk_drivers"]) > 0


def test_model_performance_endpoint(client, db, manager_token):
    setup_ai_test_data(db)
    headers = {"Authorization": f"Bearer {manager_token}"}
    r = client.get("/ai/model-performance", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    assert "forecasting" in data
    assert "anomalies" in data
    assert "recommendation_engine" in data


def test_recommendation_lifecycle_workflow(client, db, manager_token):
    setup_ai_test_data(db)
    headers = {"Authorization": f"Bearer {manager_token}"}
    
    # 1. Generate active recommendations
    r = client.get("/ai/recommendations?warehouse_id=WH-AI-TEST&refresh=true", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["total_recommendations"] > 0
    
    rec = data["recommendations"][0]
    rec_id = rec["id"]
    assert rec["status"] == "NEW"
    assert rec["explanation"] is not None
    assert rec["recommended_action"] is not None

    # 2. Reject recommendation
    reject_res = client.post(
        f"/ai/recommendations/{rec_id}/reject",
        json={"action": "REJECTED", "notes": "Hold reorder for physical count verification"},
        headers=headers
    )
    assert reject_res.status_code == 200
    assert reject_res.json()["new_status"] == "REJECTED"

    # Verify audit entry generated in Trust Ledger
    audit = db.query(AuditLedger).filter(AuditLedger.event_type == "AI_RECOMMENDATION_REJECTED").first()
    assert audit is not None
    assert str(rec_id) in audit.details

    # 3. Dismiss recommendation
    # Generate another and dismiss it
    db.query(AIRecommendation).filter(AIRecommendation.id == rec_id).delete()
    db.commit()
    r = client.get("/ai/recommendations?warehouse_id=WH-AI-TEST&refresh=true", headers=headers)
    new_rec_id = r.json()["recommendations"][0]["id"]
    
    dismiss_res = client.post(f"/ai/recommendations/{new_rec_id}/dismiss", headers=headers)
    assert dismiss_res.status_code == 200
    assert dismiss_res.json()["new_status"] == "DISMISSED"

    # 4. Approve and execute recommendation (Automatically triggers WMS task dispatch)
    db.query(AIRecommendation).filter(AIRecommendation.id == new_rec_id).delete()
    db.commit()
    r = client.get("/ai/recommendations?warehouse_id=WH-AI-TEST&refresh=true", headers=headers)
    exec_rec = [rec for rec in r.json()["recommendations"] if rec["recommendation_type"] == "REPLENISHMENT"][0]
    exec_rec_id = exec_rec["id"]

    approve_res = client.post(
        f"/ai/recommendations/{exec_rec_id}/approve",
        json={"action": "APPROVED", "notes": "Approved reorder"},
        headers=headers
    )
    assert approve_res.status_code == 200
    res_data = approve_res.json()
    assert res_data["new_status"] == "EXECUTED"
    assert res_data["task_id"] is not None

    # Verify Task is created in WMS
    task = db.query(Task).filter(Task.id == res_data["task_id"]).first()
    assert task is not None
    assert task.task_type == "REPLENISH"
    assert task.status == "QUEUED"
    assert task.product_id == "ITM-AI-TEST"


def test_rbac_security_restrictions(client, db, manager_token, viewer_token):
    setup_ai_test_data(db)
    
    # Generate recommendations
    headers_manager = {"Authorization": f"Bearer {manager_token}"}
    r = client.get("/ai/recommendations?warehouse_id=WH-AI-TEST&refresh=true", headers=headers_manager)
    rec_id = r.json()["recommendations"][0]["id"]

    # Try to approve recommendation using a viewer token (RBAC blocks this)
    headers_viewer = {"Authorization": f"Bearer {viewer_token}"}
    block_res = client.post(
        f"/ai/recommendations/{rec_id}/approve",
        json={"action": "APPROVED", "notes": "Unauthorized attempt"},
        headers=headers_viewer
    )
    assert block_res.status_code == 403
    print("[PASS] RBAC blocked non-manager viewer from executing AI recommendations")
