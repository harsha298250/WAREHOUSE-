import pytest
from sqlalchemy.orm import Session
from backend.models import Item, Inventory, Warehouse, StockMovement, Order, OrderItem, Task, User
from backend.auth import hash_password


@pytest.fixture
def admin_token(client, db):
    user = db.query(User).filter(User.username == "inv_admin").first()
    if not user:
        user = User(
            username="inv_admin",
            password_hash=hash_password("AdminPass123!"),
            role="admin",
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.commit()

    r = client.post("/auth/login", json={"username": "inv_admin", "password": "AdminPass123!"})
    assert r.status_code == 200
    return r.json()["access_token"]


@pytest.fixture
def setup_warehouses(db):
    w1 = db.query(Warehouse).filter(Warehouse.id == "WH-BLR-01").first()
    if not w1:
        w1 = Warehouse(id="WH-BLR-01", name="Bangalore Fulfillment Center", location="Zone A")
        db.add(w1)

    w2 = db.query(Warehouse).filter(Warehouse.id == "WH-CHN-01").first()
    if not w2:
        w2 = Warehouse(id="WH-CHN-01", name="Chennai Distribution Hub", location="Zone B")
        db.add(w2)

    db.commit()
    return w1, w2


def test_1_create_item_single_source_of_truth(client, admin_token, setup_warehouses, db: Session):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "id": "ITM-TEST-E2E-01",
        "name": "Test GPU Card",
        "category": "Electronics",
        "unit_cost": 1000.0,
        "safety_stock": 20,
        "reorder_threshold": 25,
        "warehouse_id": "WH-BLR-01",
        "initial_stock": 100,
        "sku": "SKU-GPU-E2E"
    }

    r = client.post("/items", json=payload, headers=headers)
    assert r.status_code == 200
    res = r.json()
    assert res["status"] == "created"
    assert res["id"] == "ITM-TEST-E2E-01"

    # Verify DB state
    db.expire_all()
    item_db = db.query(Item).filter(Item.id == "ITM-TEST-E2E-01").first()
    assert item_db is not None
    assert item_db.name == "Test GPU Card"
    assert item_db.unit_cost == 1000.0

    inv_db = db.query(Inventory).filter(Inventory.warehouse_id == "WH-BLR-01", Inventory.item_id == "ITM-TEST-E2E-01").first()
    assert inv_db is not None
    assert inv_db.on_hand == 100
    assert inv_db.available == 100

    # Verify GET /inventory/WH-BLR-01 returns item
    r_inv = client.get("/inventory/WH-BLR-01", headers=headers)
    assert r_inv.status_code == 200
    items_list = r_inv.json()
    matching = [i for i in items_list if i["item_id"] == "ITM-TEST-E2E-01"]
    assert len(matching) == 1
    assert matching[0]["current_stock"] == 100
    assert matching[0]["unit_cost"] == 1000.0

    # Verify GET /wms/inventory returns item
    r_wms = client.get("/wms/inventory?warehouse_id=WH-BLR-01", headers=headers)
    assert r_wms.status_code == 200
    wms_items = r_wms.json()["items"]
    matching_wms = [i for i in wms_items if i["item_id"] == "ITM-TEST-E2E-01"]
    assert len(matching_wms) == 1
    assert matching_wms[0]["on_hand"] == 100


def test_2_update_item_single_source(client, admin_token, setup_warehouses, db: Session):
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Create item first
    client.post("/items", json={
        "id": "ITM-TEST-E2E-02",
        "name": "Test Monitor",
        "category": "Electronics",
        "unit_cost": 500.0,
        "warehouse_id": "WH-BLR-01",
        "initial_stock": 50
    }, headers=headers)

    patch_payload = {
        "unit_cost": 1200.0,
        "current_stock": 25,
        "warehouse_id": "WH-BLR-01"
    }

    r_patch = client.patch("/items/ITM-TEST-E2E-02", json=patch_payload, headers=headers)
    assert r_patch.status_code == 200

    # Verify GET /inventory/WH-BLR-01 reflects updated values
    r_inv = client.get("/inventory/WH-BLR-01", headers=headers)
    assert r_inv.status_code == 200
    matching = [i for i in r_inv.json() if i["item_id"] == "ITM-TEST-E2E-02"][0]
    assert matching["current_stock"] == 25
    assert matching["unit_cost"] == 1200.0


def test_3_stock_movement_synchronization(client, admin_token, setup_warehouses, db: Session):
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Create item first
    client.post("/items", json={
        "id": "ITM-TEST-E2E-03",
        "name": "Test Keyboard",
        "category": "Electronics",
        "unit_cost": 80.0,
        "warehouse_id": "WH-BLR-01",
        "initial_stock": 25
    }, headers=headers)

    sm_payload = {
        "date": "2026-08-31",
        "warehouse_id": "WH-BLR-01",
        "item_id": "ITM-TEST-E2E-03",
        "stock_in": 0,
        "stock_out": 10
    }

    r_sm = client.post("/stock-movements", json=sm_payload, headers=headers)
    assert r_sm.status_code == 200

    # Verify inventory is updated to 15 (25 - 10)
    db.expire_all()
    inv_db = db.query(Inventory).filter(Inventory.warehouse_id == "WH-BLR-01", Inventory.item_id == "ITM-TEST-E2E-03").first()
    assert inv_db is not None
    assert inv_db.on_hand == 15


def test_4_warehouse_isolation(client, admin_token, setup_warehouses, db: Session):
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Create item specifically in Chennai
    chn_payload = {
        "id": "ITM-CHN-ONLY",
        "name": "Chennai Special Cable",
        "category": "General",
        "unit_cost": 50.0,
        "warehouse_id": "WH-CHN-01",
        "initial_stock": 50
    }
    r = client.post("/items", json=chn_payload, headers=headers)
    assert r.status_code == 200

    # Verify Bangalore inventory does NOT list ITM-CHN-ONLY as having stock in Bangalore
    r_blr = client.get("/inventory/WH-BLR-01", headers=headers)
    assert r_blr.status_code == 200
    matching_blr = [i for i in r_blr.json() if i["item_id"] == "ITM-CHN-ONLY"]
    if matching_blr:
        assert matching_blr[0]["current_stock"] == 0


def test_5_delete_archive_item_guard(client, admin_token, setup_warehouses, db: Session):
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Create item and log stock movement
    client.post("/items", json={
        "id": "ITM-TEST-E2E-05",
        "name": "Test Mouse",
        "category": "Electronics",
        "unit_cost": 30.0,
        "warehouse_id": "WH-BLR-01",
        "initial_stock": 10
    }, headers=headers)

    client.post("/stock-movements", json={
        "date": "2026-08-31",
        "warehouse_id": "WH-BLR-01",
        "item_id": "ITM-TEST-E2E-05",
        "stock_in": 5,
        "stock_out": 0
    }, headers=headers)

    # ITM-TEST-E2E-05 has stock movements, so delete should trigger safe soft archive
    r_del = client.delete("/items/ITM-TEST-E2E-05", headers=headers)
    assert r_del.status_code == 200
    res = r_del.json()
    assert res["status"] in ("archived", "deleted")

    db.expire_all()
    item_db = db.query(Item).filter(Item.id == "ITM-TEST-E2E-05").first()
    if item_db:
        assert item_db.is_active is False
