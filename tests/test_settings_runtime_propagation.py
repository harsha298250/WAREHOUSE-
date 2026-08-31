"""
tests/test_settings_runtime_propagation.py

Automated regression test suite for Phase 1: Settings -> Runtime Propagation.
Verifies all 7 required scenarios:
1. test_low_stock_threshold_runtime_propagation
2. test_reorder_point_runtime_propagation
3. test_robot_speed_runtime_propagation
4. test_settings_persistence_across_sessions
5. test_non_admin_settings_access_blocked
6. test_settings_api_returns_db_backed_values
7. test_settings_no_silent_default_overrides
"""
import pytest
from backend.settings import get_settings, get_setting_value, save_settings, reset_to_defaults, DEFAULT_SETTINGS
from backend.models import Item, Inventory, Warehouse, AppSetting, Robot
from ml.replenishment.engine import run_replenishment_engine
from backend.simulation.engine import SimulationEngine


def test_low_stock_threshold_runtime_propagation(client, admin_token, db):
    """1. Admin changes low_stock_thresh from 10 to 5 -> Item with stock 8 moves from LOW_STOCK to HEALTHY."""
    # Ensure baseline settings reset
    reset_to_defaults(db)

    # Create a warehouse and item with available stock = 8 (no custom reorder_threshold)
    wh = db.query(Warehouse).filter(Warehouse.id == "WH-SET-01").first()
    if not wh:
        wh = Warehouse(id="WH-SET-01", name="Settings Test Wh", location="Test")
        db.add(wh)

    item = db.query(Item).filter(Item.id == "ITM-SET-01").first()
    if not item:
        item = Item(id="ITM-SET-01", name="Settings Test Item", category="Test", safety_stock=2, reorder_threshold=None)
        db.add(item)
    else:
        item.reorder_threshold = None
        item.safety_stock = 2

    inv = db.query(Inventory).filter(Inventory.warehouse_id == "WH-SET-01", Inventory.item_id == "ITM-SET-01").first()
    if not inv:
        inv = Inventory(warehouse_id="WH-SET-01", item_id="ITM-SET-01", on_hand=8, reserved=0, available=8)
        db.add(inv)
    else:
        inv.on_hand = 8
        inv.reserved = 0
        inv.available = 8
    db.commit()

    # Step 1: Set low_stock_thresh = 10 -> item available stock 8 is LOW_STOCK
    save_settings(db, {"low_stock_thresh": 10})
    res1 = client.get("/wms/inventory?warehouse_id=WH-SET-01", headers={"Authorization": f"Bearer {admin_token}"})
    assert res1.status_code == 200
    items1 = res1.json().get("items", [])
    target_item1 = next((i for i in items1 if i["item_id"] == "ITM-SET-01"), None)
    assert target_item1 is not None
    assert target_item1["status"] == "LOW_STOCK"

    # Step 2: Admin changes low_stock_thresh to 5 -> item available stock 8 moves to HEALTHY
    save_settings(db, {"low_stock_thresh": 5})
    res2 = client.get("/wms/inventory?warehouse_id=WH-SET-01", headers={"Authorization": f"Bearer {admin_token}"})
    assert res2.status_code == 200
    items2 = res2.json().get("items", [])
    target_item2 = next((i for i in items2 if i["item_id"] == "ITM-SET-01"), None)
    assert target_item2 is not None
    assert target_item2["status"] == "HEALTHY"


def test_reorder_point_runtime_propagation(client, admin_token, db):
    """2. Admin changes reorder_point from 20 to 50 -> Replenishment calculation updates reorder status."""
    # Reset settings
    reset_to_defaults(db)

    # Setup inventory item with current_stock = 35
    wh = db.query(Warehouse).filter(Warehouse.id == "WH-SET-02").first()
    if not wh:
        wh = Warehouse(id="WH-SET-02", name="Replenish Test Wh", location="Test")
        db.add(wh)

    item = db.query(Item).filter(Item.id == "ITM-SET-02").first()
    if not item:
        item = Item(id="ITM-SET-02", name="Replenish Test Item", category="Test", reorder_threshold=0)
        db.add(item)
    else:
        item.reorder_threshold = 0

    inv = db.query(Inventory).filter(Inventory.warehouse_id == "WH-SET-02", Inventory.item_id == "ITM-SET-02").first()
    if not inv:
        inv = Inventory(warehouse_id="WH-SET-02", item_id="ITM-SET-02", on_hand=35, reserved=0, available=35)
        db.add(inv)
    else:
        inv.on_hand = 35
        inv.reserved = 0
        inv.available = 35
    db.commit()

    # Step 1: Default reorder_point = 20 -> stock 35 > 20 * 1.5 (30) is HEALTHY / NO_ACTION
    save_settings(db, {"reorder_point": 20})
    result1 = run_replenishment_engine(db, warehouse_id="WH-SET-02")
    rec1 = next((r for r in result1.get("recommendations", []) if r["item_id"] == "ITM-SET-02"), None)
    assert rec1 is not None
    assert rec1["urgency"] == "NO_ACTION"

    # Step 2: Admin changes reorder_point to 50 -> stock 35 <= 50, urgency becomes REORDER_RECOMMENDED
    save_settings(db, {"reorder_point": 50})
    result2 = run_replenishment_engine(db, warehouse_id="WH-SET-02")
    rec2 = next((r for r in result2.get("recommendations", []) if r["item_id"] == "ITM-SET-02"), None)
    assert rec2 is not None
    assert rec2["urgency"] == "REORDER_RECOMMENDED"
    assert rec2["reorder_point"] == 50.0


def test_robot_speed_runtime_propagation(client, admin_token, db):
    """3. Admin changes robot_speed -> Simulation engine loads and uses new speed."""
    reset_to_defaults(db)

    # Save custom robot_speed = 3.5
    save_settings(db, {"robot_speed": 3.5})

    wh = db.query(Warehouse).filter(Warehouse.id == "WH-SET-03").first()
    if not wh:
        wh = Warehouse(id="WH-SET-03", name="Sim Test Wh", location="Test")
        db.add(wh)
        db.commit()

    sim_engine = SimulationEngine(
        db=db,
        warehouse_id="WH-SET-03",
        mode="NORMAL",
        duration=10.0,
        random_seed=42,
        config={}
    )
    sim_engine.load_snapshot()
    assert sim_engine.effective_robot_speed == 3.5

    app_settings = get_settings(db)
    assert app_settings["robot_speed"] == 3.5


def test_settings_persistence_across_sessions(client, admin_token, db):
    """4. Saved settings persist in DB across requests and logins."""
    # Update settings via REST API
    payload = {"system_name": "Custom Warehouse OS v2", "low_stock_thresh": 12, "robot_speed": 2.4}
    res = client.post("/api/settings", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code in (200, 201)

    # Query GET endpoint to verify persistence
    get_res = client.get("/api/settings", headers={"Authorization": f"Bearer {admin_token}"})
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["system_name"] == "Custom Warehouse OS v2"
    assert data["low_stock_thresh"] == 12
    assert data["robot_speed"] == 2.4

    # Verify directly in DB
    db_val = get_setting_value(db, "system_name")
    assert db_val == "Custom Warehouse OS v2"


def test_non_admin_settings_access_blocked(client, viewer_token):
    """5. Non-admin users attempting settings update receive HTTP 403 Forbidden."""
    res = client.post("/api/settings", json={"low_stock_thresh": 99}, headers={"Authorization": f"Bearer {viewer_token}"})
    assert res.status_code == 403
    assert "Forbidden" in res.json().get("detail", "") or "permissions" in res.json().get("detail", "").lower() or "admin" in res.json().get("detail", "").lower()


def test_settings_api_returns_db_backed_values(client, admin_token, db):
    """6. Settings GET endpoint returns values saved in PostgreSQL AppSetting."""
    save_settings(db, {"order_num_prefix": "ORD-TEST-", "auto_assign_orders": False})

    res = client.get("/api/settings", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["order_num_prefix"] == "ORD-TEST-"
    assert data["auto_assign_orders"] is False


def test_settings_no_silent_default_overrides(db):
    """7. Changing a setting takes precedence over default fallbacks."""
    reset_to_defaults(db)

    # Default value for low_stock_thresh is 10
    default_val = get_setting_value(db, "low_stock_thresh", default=99)
    assert default_val == 10

    # Override setting to 18
    save_settings(db, {"low_stock_thresh": 18})
    updated_val = get_setting_value(db, "low_stock_thresh", default=99)
    assert updated_val == 18
    assert updated_val != 10
