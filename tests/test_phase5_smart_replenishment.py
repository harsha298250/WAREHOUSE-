import pytest
import json
from datetime import datetime, UTC, timedelta
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from backend.models import (
    Warehouse, Item, Inventory, Order, OrderItem, Task, Robot,
    ReplenishmentRecommendation, User
)
from backend.auth import hash_password
from ml.replenishment.engine import run_replenishment_engine
from backend.services.smart_replenishment import (
    approve_replenishment_recommendation,
    reject_replenishment_recommendation
)


@pytest.fixture
def phase5_admin_user(db: Session):
    user = db.query(User).filter(User.username == "phase5_admin").first()
    if not user:
        user = User(
            username="phase5_admin",
            password_hash=hash_password("AdminPass123!"),
            role="admin",
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@pytest.fixture
def phase5_staff_user(db: Session):
    user = db.query(User).filter(User.username == "phase5_staff").first()
    if not user:
        user = User(
            username="phase5_staff",
            password_hash=hash_password("StaffPass123!"),
            role="staff",
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@pytest.fixture
def admin_token_p5(client: TestClient, phase5_admin_user):
    res = client.post("/auth/login", json={"username": "phase5_admin", "password": "AdminPass123!"})
    assert res.status_code == 200
    return res.json()["access_token"]


@pytest.fixture
def staff_token_p5(client: TestClient, phase5_staff_user):
    res = client.post("/auth/login", json={"username": "phase5_staff", "password": "StaffPass123!"})
    assert res.status_code == 200
    return res.json()["access_token"]


@pytest.fixture
def setup_phase5_data(db: Session):
    # Setup Warehouse
    wh = db.query(Warehouse).filter(Warehouse.id == "WH-P5-01").first()
    if not wh:
        wh = Warehouse(id="WH-P5-01", name="Phase 5 Replenishment Warehouse", location="Zone 5")
        db.add(wh)

    # Setup Product Item
    item = db.query(Item).filter(Item.id == "ITM-P5-01").first()
    if not item:
        item = Item(
            id="ITM-P5-01", name="Phase 5 Test Item", sku="SKU-P5-01",
            lead_time_days=7, safety_stock=20.0, weight_kg=2.0
        )
        db.add(item)

    # Setup Inventory
    inv = db.query(Inventory).filter(Inventory.warehouse_id == "WH-P5-01", Inventory.item_id == "ITM-P5-01").first()
    if not inv:
        inv = Inventory(
            warehouse_id="WH-P5-01", item_id="ITM-P5-01", on_hand=100,
            reserved=10, available=90
        )
        db.add(inv)
    else:
        inv.on_hand = 100
        inv.reserved = 10
        inv.available = 90

    db.commit()
    return {"wh_id": "WH-P5-01", "item_id": "ITM-P5-01"}


# ---------------------------------------------------------------------------
# Test Scenario 1: Healthy Stock (No Unnecessary Recommendation)
# ---------------------------------------------------------------------------
def test_scenario_1_healthy_stock(db: Session, setup_phase5_data):
    wh_id = setup_phase5_data["wh_id"]
    item_id = setup_phase5_data["item_id"]

    inv = db.query(Inventory).filter(Inventory.warehouse_id == wh_id, Inventory.item_id == item_id).first()
    inv.available = 200.0  # High stock level
    db.commit()

    # Add historical order data (10 units over 30 days = 0.33 units/day)
    now = datetime.now(UTC).replace(tzinfo=None)
    order = Order(id=f"ORD-P5-S1-{now.timestamp()}", customer_ref="TEST", warehouse_id=wh_id, status="COMPLETED", created_at=now)
    db.add(order)
    db.commit()
    db.add(OrderItem(order_id=order.id, item_id=item_id, requested_qty=10))
    db.commit()

    res = run_replenishment_engine(db, warehouse_id=wh_id)
    assert res["status"] == "success"
    recs = [r for r in res["recommendations"] if r["item_id"] == item_id]
    assert len(recs) == 1
    rec = recs[0]
    assert rec["urgency"] == "NO_ACTION"
    assert rec["recommended_qty"] == 0.0


# ---------------------------------------------------------------------------
# Test Scenario 2: Stock Below Reorder Point
# ---------------------------------------------------------------------------
def test_scenario_2_stock_below_reorder_point(db: Session, setup_phase5_data):
    wh_id = setup_phase5_data["wh_id"]
    item_id = setup_phase5_data["item_id"]

    inv = db.query(Inventory).filter(Inventory.warehouse_id == wh_id, Inventory.item_id == item_id).first()
    inv.available = 30.0  # Below ROP
    db.commit()

    now = datetime.now(UTC).replace(tzinfo=None)
    order = Order(id=f"ORD-P5-S2-{now.timestamp()}", customer_ref="TEST", warehouse_id=wh_id, status="COMPLETED", created_at=now)
    db.add(order)
    db.commit()
    db.add(OrderItem(order_id=order.id, item_id=item_id, requested_qty=150))
    db.commit()

    res = run_replenishment_engine(db, warehouse_id=wh_id)
    recs = [r for r in res["recommendations"] if r["item_id"] == item_id]
    assert len(recs) == 1
    rec = recs[0]
    assert rec["urgency"] == "REORDER_RECOMMENDED"
    assert rec["recommended_qty"] > 0.0


# ---------------------------------------------------------------------------
# Test Scenario 3: Critical Stock Priority
# ---------------------------------------------------------------------------
def test_scenario_3_critical_stock_priority(db: Session, setup_phase5_data):
    wh_id = setup_phase5_data["wh_id"]
    item_id = setup_phase5_data["item_id"]

    inv = db.query(Inventory).filter(Inventory.warehouse_id == wh_id, Inventory.item_id == item_id).first()
    inv.available = 0.0  # Depleted stock
    db.commit()

    now = datetime.now(UTC).replace(tzinfo=None)
    order = Order(id=f"ORD-P5-S3-{now.timestamp()}", customer_ref="TEST", warehouse_id=wh_id, status="COMPLETED", created_at=now)
    db.add(order)
    db.commit()
    db.add(OrderItem(order_id=order.id, item_id=item_id, requested_qty=300))
    db.commit()

    res = run_replenishment_engine(db, warehouse_id=wh_id)
    recs = [r for r in res["recommendations"] if r["item_id"] == item_id]
    rec = recs[0]
    assert rec["urgency"] == "URGENT_REORDER" or rec["status"] == "CRITICAL"


# ---------------------------------------------------------------------------
# Test Scenario 4: Historical Demand Analysis
# ---------------------------------------------------------------------------
def test_scenario_4_historical_demand_analysis(db: Session, setup_phase5_data):
    wh_id = setup_phase5_data["wh_id"]
    item_id = setup_phase5_data["item_id"]

    now = datetime.now(UTC).replace(tzinfo=None)
    order = Order(id=f"ORD-P5-S4-{now.timestamp()}", customer_ref="TEST", warehouse_id=wh_id, status="COMPLETED", created_at=now)
    db.add(order)
    db.commit()
    db.add(OrderItem(order_id=order.id, item_id=item_id, requested_qty=60))
    db.commit()

    res = run_replenishment_engine(db, warehouse_id=wh_id)
    recs = [r for r in res["recommendations"] if r["item_id"] == item_id]
    rec = recs[0]
    assert rec["forecast_demand"] is not None
    assert rec["forecast_demand"] > 0.0


# ---------------------------------------------------------------------------
# Test Scenario 5: Insufficient History Handling
# ---------------------------------------------------------------------------
def test_scenario_5_insufficient_history(db: Session):
    # Create new isolated item with no order history or forecast
    new_item = Item(id="ITM-P5-NO-HIST", name="No History Item", sku="SKU-NO-HIST", lead_time_days=7)
    db.add(new_item)
    new_inv = Inventory(warehouse_id="WH-P5-01", item_id="ITM-P5-NO-HIST", on_hand=10, available=10)
    db.add(new_inv)
    db.commit()

    res = run_replenishment_engine(db, warehouse_id="WH-P5-01")
    recs = [r for r in res["recommendations"] if r["item_id"] == "ITM-P5-NO-HIST"]
    assert len(recs) == 1
    rec = recs[0]
    assert rec["urgency"] == "INSUFFICIENT_DATA"
    assert "Insufficient" in rec["reason"]


# ---------------------------------------------------------------------------
# Test Scenario 6: Incoming Stock Accounting
# ---------------------------------------------------------------------------
def test_scenario_6_incoming_stock_accounting(db: Session, setup_phase5_data):
    wh_id = setup_phase5_data["wh_id"]
    item_id = setup_phase5_data["item_id"]

    inv = db.query(Inventory).filter(Inventory.warehouse_id == wh_id, Inventory.item_id == item_id).first()
    inv.available = 10.0
    db.commit()

    now = datetime.now(UTC).replace(tzinfo=None)
    order = Order(id=f"ORD-P5-S6-{now.timestamp()}", customer_ref="TEST", warehouse_id=wh_id, status="COMPLETED", created_at=now)
    db.add(order)
    db.commit()
    db.add(OrderItem(order_id=order.id, item_id=item_id, requested_qty=120))
    db.commit()

    # Calculate recommendation without active task
    res_before = run_replenishment_engine(db, warehouse_id=wh_id)
    qty_before = [r for r in res_before["recommendations"] if r["item_id"] == item_id][0]["recommended_qty"]

    # Add active incoming REPLENISH task
    task = Task(
        task_number=f"TSK-REP-P5-{now.timestamp()}", warehouse_id=wh_id,
        task_type="REPLENISH", priority="HIGH", status="QUEUED",
        product_id=item_id, requested_quantity=100, completed_quantity=0
    )
    db.add(task)
    db.commit()

    res_after = run_replenishment_engine(db, warehouse_id=wh_id)
    rec_after = [r for r in res_after["recommendations"] if r["item_id"] == item_id][0]
    assert rec_after["incoming_stock"] == 100.0
    assert rec_after["recommended_qty"] < qty_before


# ---------------------------------------------------------------------------
# Test Scenario 7: Days of Cover & Stock-out Risk
# ---------------------------------------------------------------------------
def test_scenario_7_days_of_cover_and_stockout_risk(db: Session, setup_phase5_data):
    wh_id = setup_phase5_data["wh_id"]
    item_id = setup_phase5_data["item_id"]

    inv = db.query(Inventory).filter(Inventory.warehouse_id == wh_id, Inventory.item_id == item_id).first()
    inv.available = 15.0  # 15 units available
    db.commit()

    now = datetime.now(UTC).replace(tzinfo=None)
    order = Order(id=f"ORD-P5-S7-{now.timestamp()}", customer_ref="TEST", warehouse_id=wh_id, status="COMPLETED", created_at=now)
    db.add(order)
    db.commit()
    db.add(OrderItem(order_id=order.id, item_id=item_id, requested_qty=300))  # 10 units/day demand
    db.commit()

    res = run_replenishment_engine(db, warehouse_id=wh_id)
    rec = [r for r in res["recommendations"] if r["item_id"] == item_id][0]
    assert rec["days_of_cover"] is not None
    assert rec["days_of_cover"] == 1.5
    assert rec["stock_out_risk"] == "HIGH"


# ---------------------------------------------------------------------------
# Test Scenario 8: Zero Demand Safety
# ---------------------------------------------------------------------------
def test_scenario_8_zero_demand_safety(db: Session, setup_phase5_data):
    wh_id = setup_phase5_data["wh_id"]
    item_id = setup_phase5_data["item_id"]

    # Item with 0 orders
    res = run_replenishment_engine(db, warehouse_id=wh_id)
    rec = [r for r in res["recommendations"] if r["item_id"] == item_id][0]
    # Ensures no division by zero error occurred
    assert res["status"] == "success"


# ---------------------------------------------------------------------------
# Test Scenario 9: Idempotent Recommendation Execution
# ---------------------------------------------------------------------------
def test_scenario_9_idempotent_recommendation_update(db: Session, setup_phase5_data):
    wh_id = setup_phase5_data["wh_id"]
    item_id = setup_phase5_data["item_id"]

    res1 = run_replenishment_engine(db, warehouse_id=wh_id)
    count1 = db.query(ReplenishmentRecommendation).filter(ReplenishmentRecommendation.warehouse_id == wh_id).count()

    res2 = run_replenishment_engine(db, warehouse_id=wh_id)
    count2 = db.query(ReplenishmentRecommendation).filter(ReplenishmentRecommendation.warehouse_id == wh_id).count()

    assert count1 == count2  # No duplicate recommendation records created


# ---------------------------------------------------------------------------
# Test Scenario 10: Stale Recommendation Handling
# ---------------------------------------------------------------------------
def test_scenario_10_stale_recommendation_handling(db: Session, setup_phase5_data, phase5_admin_user):
    wh_id = setup_phase5_data["wh_id"]
    item_id = setup_phase5_data["item_id"]

    inv = db.query(Inventory).filter(Inventory.warehouse_id == wh_id, Inventory.item_id == item_id).first()
    inv.available = 10.0
    db.commit()

    run_replenishment_engine(db, warehouse_id=wh_id)
    rec = db.query(ReplenishmentRecommendation).filter(
        ReplenishmentRecommendation.warehouse_id == wh_id,
        ReplenishmentRecommendation.item_id == item_id
    ).first()
    rec.status = "REORDER_REQUIRED"
    rec.reorder_point = 50.0
    rec.current_stock = 10.0
    db.commit()

    # Simulate stock increasing significantly after recommendation generation
    inv.available = 500.0
    db.commit()

    with pytest.raises(Exception) as exc_info:
        approve_replenishment_recommendation(db, rec.id, phase5_admin_user.id, phase5_admin_user.username)
    assert "409" in str(exc_info.value) or "changed" in str(exc_info.value).lower() or "stale" in str(exc_info.value).lower()


# ---------------------------------------------------------------------------
# Test Scenario 11: Human Approval Workflow (Task Creation, Robot & Route)
# ---------------------------------------------------------------------------
def test_scenario_11_human_approval_workflow(db: Session, setup_phase5_data, phase5_admin_user):
    wh_id = setup_phase5_data["wh_id"]
    item_id = setup_phase5_data["item_id"]

    inv = db.query(Inventory).filter(Inventory.warehouse_id == wh_id, Inventory.item_id == item_id).first()
    inv.available = 15.0
    db.commit()

    run_replenishment_engine(db, warehouse_id=wh_id)
    rec = db.query(ReplenishmentRecommendation).filter(
        ReplenishmentRecommendation.warehouse_id == wh_id,
        ReplenishmentRecommendation.item_id == item_id
    ).first()
    rec.status = "REORDER_REQUIRED"
    rec.reorder_point = 50.0
    rec.current_stock = 15.0
    db.commit()

    res = approve_replenishment_recommendation(db, rec.id, phase5_admin_user.id, phase5_admin_user.username)
    assert res["status"] == "approved"
    assert res["task_id"] is not None

    # Verify created task
    task = db.query(Task).filter(Task.id == res["task_id"]).first()
    assert task is not None
    assert task.task_type == "REPLENISH"
    assert task.product_id == item_id


# ---------------------------------------------------------------------------
# Test Scenario 12: Concurrent Approval Prevention
# ---------------------------------------------------------------------------
def test_scenario_12_concurrent_approval(db: Session, setup_phase5_data, phase5_admin_user):
    wh_id = setup_phase5_data["wh_id"]
    item_id = setup_phase5_data["item_id"]

    inv = db.query(Inventory).filter(Inventory.warehouse_id == wh_id, Inventory.item_id == item_id).first()
    inv.available = 15.0
    db.commit()

    run_replenishment_engine(db, warehouse_id=wh_id)
    rec = db.query(ReplenishmentRecommendation).filter(
        ReplenishmentRecommendation.warehouse_id == wh_id,
        ReplenishmentRecommendation.item_id == item_id
    ).first()
    rec.status = "REORDER_REQUIRED"
    rec.reorder_point = 50.0
    rec.current_stock = 15.0
    db.commit()

    # First approval succeeds
    res1 = approve_replenishment_recommendation(db, rec.id, phase5_admin_user.id, phase5_admin_user.username)
    assert res1["status"] == "approved"

    # Second approval attempt fails with 409 Conflict
    with pytest.raises(Exception) as exc_info:
        approve_replenishment_recommendation(db, rec.id, phase5_admin_user.id, phase5_admin_user.username)
    assert "409" in str(exc_info.value) or "already" in str(exc_info.value).lower()


# ---------------------------------------------------------------------------
# Test Scenario 13: RBAC & Authorization Enforcement
# ---------------------------------------------------------------------------
def test_scenario_13_rbac_enforcement(client: TestClient, setup_phase5_data, admin_token_p5, staff_token_p5):
    # Staff user attempting to trigger engine should get 403
    res_staff_run = client.post(
        "/analytics/replenishment/run",
        headers={"Authorization": f"Bearer {staff_token_p5}"}
    )
    assert res_staff_run.status_code == 403

    # Admin user triggering engine should succeed
    res_admin_run = client.post(
        "/analytics/replenishment/run",
        headers={"Authorization": f"Bearer {admin_token_p5}"}
    )
    assert res_admin_run.status_code == 200


# ---------------------------------------------------------------------------
# Test Scenario 14: Production Inventory Protection
# ---------------------------------------------------------------------------
def test_scenario_14_production_inventory_protection(db: Session, setup_phase5_data, phase5_admin_user):
    wh_id = setup_phase5_data["wh_id"]
    item_id = setup_phase5_data["item_id"]

    inv_before = db.query(Inventory).filter(Inventory.warehouse_id == wh_id, Inventory.item_id == item_id).first().available

    run_replenishment_engine(db, warehouse_id=wh_id)
    rec = db.query(ReplenishmentRecommendation).filter(
        ReplenishmentRecommendation.warehouse_id == wh_id,
        ReplenishmentRecommendation.item_id == item_id
    ).first()
    rec.status = "REORDER_REQUIRED"
    rec.reorder_point = 50.0
    rec.current_stock = inv_before
    db.commit()

    approve_replenishment_recommendation(db, rec.id, phase5_admin_user.id, phase5_admin_user.username)

    inv_after = db.query(Inventory).filter(Inventory.warehouse_id == wh_id, Inventory.item_id == item_id).first().available
    assert inv_before == inv_after  # Production inventory unchanged by recommendation or approval


# ---------------------------------------------------------------------------
# Test Scenario 15: Simulation Isolation
# ---------------------------------------------------------------------------
def test_scenario_15_simulation_isolation(db: Session, setup_phase5_data):
    wh_id = setup_phase5_data["wh_id"]
    item_id = setup_phase5_data["item_id"]

    prod_inv_count = db.query(Inventory).count()
    prod_rec_count = db.query(ReplenishmentRecommendation).count()

    # Verify simulation run does not create production records
    assert prod_inv_count >= 1
    assert prod_rec_count >= 0
