import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import sqlalchemy as sa

from backend.main import app
from backend.models import (
    User, Warehouse, Item, Inventory, WarehouseLocation,
    StockMovement, ABCClassification, AnomalyResult,
    ReplenishmentRecommendation, ForecastRun, ForecastResult
)
from backend.auth import hash_password

client = TestClient(app)


def run_async(coro_creator):
    import queue
    import threading
    q = queue.Queue()
    
    def worker():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            res = loop.run_until_complete(coro_creator())
            q.put((True, res))
        except Exception as e:
            q.put((False, e))
        finally:
            loop.close()
            
    t = threading.Thread(target=worker)
    t.start()
    t.join()
    
    success, val = q.get()
    if success:
        return val
    else:
        raise val


@pytest.fixture
def p2_manager(db):
    user = db.query(User).filter(User.username == "p2_manager").first()
    if not user:
        user = User(
            username="p2_manager",
            password_hash=hash_password("ManagerPass123!"),
            role="manager"
        )
        db.add(user)
        db.commit()
    return user


@pytest.fixture
def p2_viewer(db):
    user = db.query(User).filter(User.username == "p2_viewer").first()
    if not user:
        user = User(
            username="p2_viewer",
            password_hash=hash_password("ViewerPass123!"),
            role="viewer"
        )
        db.add(user)
        db.commit()
    return user


@pytest.fixture
def manager_token(client, p2_manager):
    r = client.post("/auth/login", json={"username": "p2_manager", "password": "ManagerPass123!"})
    assert r.status_code == 200
    return r.json()["access_token"]


@pytest.fixture
def viewer_token(client, p2_viewer):
    r = client.post("/auth/login", json={"username": "p2_viewer", "password": "ViewerPass123!"})
    assert r.status_code == 200
    return r.json()["access_token"]


def setup_p2_data(db, p2_manager, p2_viewer):
    # Setup test warehouses, items, locations
    db.query(ReplenishmentRecommendation).delete()
    db.query(AnomalyResult).delete()
    db.query(ABCClassification).delete()
    db.query(ForecastResult).delete()
    db.query(ForecastRun).delete()
    db.query(StockMovement).delete()
    db.query(Inventory).delete()
    db.query(WarehouseLocation).filter(WarehouseLocation.warehouse_id.in_(["WH-P2-01", "WH-P2-02"])).delete()
    db.query(Warehouse).filter(Warehouse.id.in_(["WH-P2-01", "WH-P2-02"])).delete()
    db.query(Item).filter(Item.id.in_(["ITM-P2-A", "ITM-P2-B", "ITM-P2-C"])).delete()
    db.commit()

    db.add(Warehouse(id="WH-P2-01", name="P2 Wh 1", location="Source City"))
    db.add(Warehouse(id="WH-P2-02", name="P2 Wh 2", location="Dest City"))
    
    # Lead time & safety stock set for replenishment calculations
    db.add(Item(id="ITM-P2-A", name="P2 Widget A", category="Widgets", sku="SKU-P2-A", unit_cost=100.0, lead_time_days=5, safety_stock=10))
    db.add(Item(id="ITM-P2-B", name="P2 Widget B", category="Widgets", sku="SKU-P2-B", unit_cost=10.0, lead_time_days=10, safety_stock=20))
    db.add(Item(id="ITM-P2-C", name="P2 Widget C", category="Widgets", sku="SKU-P2-C", unit_cost=1.0, lead_time_days=15, safety_stock=30))
    
    # Active locations
    db.add(WarehouseLocation(id="LOC-P2-01", warehouse_id="WH-P2-01", zone="storage", aisle="A", rack="1", shelf="1", capacity=1000, location_type="STORAGE", status="ACTIVE"))
    db.add(WarehouseLocation(id="LOC-P2-02", warehouse_id="WH-P2-02", zone="storage", aisle="A", rack="1", shelf="1", capacity=1000, location_type="STORAGE", status="ACTIVE"))
    
    # Seed inventory stock levels
    db.add(Inventory(warehouse_id="WH-P2-01", item_id="ITM-P2-A", location_id="LOC-P2-01", on_hand=15, reserved=0, available=15))
    db.add(Inventory(warehouse_id="WH-P2-01", item_id="ITM-P2-B", location_id="LOC-P2-01", on_hand=200, reserved=0, available=200))
    db.add(Inventory(warehouse_id="WH-P2-01", item_id="ITM-P2-C", location_id="LOC-P2-01", on_hand=500, reserved=0, available=500))
    
    db.commit()

    # Map user warehouse access (p2_manager has access only to WH-P2-01, p2_viewer has access only to WH-P2-01)
    from backend.models import UserWarehouseAccess
    db.query(UserWarehouseAccess).filter(UserWarehouseAccess.user_id.in_([p2_manager.id, p2_viewer.id])).delete()
    db.add(UserWarehouseAccess(user_id=p2_manager.id, warehouse_id="WH-P2-01"))
    db.add(UserWarehouseAccess(user_id=p2_viewer.id, warehouse_id="WH-P2-01"))
    db.commit()


def test_rbac_write_restrictions(db, manager_token, viewer_token, p2_manager, p2_viewer):
    setup_p2_data(db, p2_manager, p2_viewer)
    
    headers_viw = {"Authorization": f"Bearer {viewer_token}"}

    # Viewer tries to run ABC - should return 403
    r = client.post("/analytics/abc/run?source=wms&warehouse_id=WH-P2-01", headers=headers_viw)
    assert r.status_code == 403


def test_abc_warehouse_isolation(db, manager_token, p2_manager, p2_viewer):
    setup_p2_data(db, p2_manager, p2_viewer)
    headers = {"Authorization": f"Bearer {manager_token}"}

    # Seed stock movements in WH-P2-01 to give A/B classifications value contribution
    # ITM-P2-A: 5 * 100 = 500 (62.5% contribution) -> A
    # ITM-P2-B: 20 * 10 = 200 (25.0% contribution) -> B
    # ITM-P2-C: 100 * 1 = 100 (12.5% contribution) -> C
    from datetime import date
    db.add(StockMovement(date=date.today(), warehouse_id="WH-P2-01", item_id="ITM-P2-A", stock_in=0, stock_out=5, closing_stock=15, entry_source="manual", entered_by="test"))
    db.add(StockMovement(date=date.today(), warehouse_id="WH-P2-01", item_id="ITM-P2-B", stock_in=0, stock_out=20, closing_stock=200, entry_source="manual", entered_by="test"))
    db.add(StockMovement(date=date.today(), warehouse_id="WH-P2-01", item_id="ITM-P2-C", stock_in=0, stock_out=100, closing_stock=500, entry_source="manual", entered_by="test"))
    db.commit()

    # Run ABC for WH-P2-01
    r = client.post("/analytics/abc/run?source=wms&warehouse_id=WH-P2-01", headers=headers)
    assert r.status_code == 200

    # Query ABC classification for authorized warehouse WH-P2-01
    r = client.get("/analytics/abc?source=wms&warehouse_id=WH-P2-01", headers=headers)
    assert r.status_code == 200
    res = r.json()
    assert res["total"] > 0
    
    # Check individual assignments
    class_a = next(x for x in res["results"] if x["item_id"] == "ITM-P2-A")
    assert class_a["abc_class"] == "A"

    # Manager queries unauthorized warehouse WH-P2-02 - should return 403
    r = client.get("/analytics/abc?source=wms&warehouse_id=WH-P2-02", headers=headers)
    assert r.status_code == 403


def test_replenishment_and_stockout_risk(db, manager_token, p2_manager, p2_viewer):
    setup_p2_data(db, p2_manager, p2_viewer)
    headers = {"Authorization": f"Bearer {manager_token}"}

    # Run replenishment recommendations for WH-P2-01
    r = client.post("/analytics/replenishment/run?warehouse_id=WH-P2-01", headers=headers)
    assert r.status_code == 200
    assert r.json()["status"] == "success"

    # Query replenishment recommendations for authorized warehouse WH-P2-01
    r = client.get("/analytics/replenishment?warehouse_id=WH-P2-01", headers=headers)
    assert r.status_code == 200
    res = r.json()
    
    # We should have safety stock recommendations
    assert len(res["results"]) > 0
    
    # Query unauthorized warehouse WH-P2-02 - should return 403
    r = client.get("/analytics/replenishment?warehouse_id=WH-P2-02", headers=headers)
    assert r.status_code == 403


def test_anomalies_and_forecasting_warehouse_isolation(db, manager_token, p2_manager, p2_viewer):
    setup_p2_data(db, p2_manager, p2_viewer)
    headers = {"Authorization": f"Bearer {manager_token}"}

    # Run anomalies with warehouse_id WH-P2-01
    r = client.post("/analytics/anomalies/run?warehouse_id=WH-P2-01", headers=headers)
    # The anomaly engine may return 400 if there's insufficient historical data on NeuroCipher
    # But let's check that if we query anomalies with warehouse_id WH-P2-02, it raises 403!
    r = client.get("/analytics/anomalies/demand?warehouse_id=WH-P2-02", headers=headers)
    assert r.status_code == 403

    # Query forecast runs for unauthorized warehouse WH-P2-02 - should return 403
    r = client.get("/analytics/forecasting/runs?warehouse_id=WH-P2-02", headers=headers)
    assert r.status_code == 403

    # Query forecast results for unauthorized warehouse WH-P2-02 - should return 403
    r = client.get("/analytics/forecasting/results?warehouse_id=WH-P2-02", headers=headers)
    assert r.status_code == 403


def test_gemini_tools_warehouse_isolation(db, manager_token, p2_manager, p2_viewer):
    setup_p2_data(db, p2_manager, p2_viewer)
    
    from backend.services.ai_service import GeminiService
    
    async def run():
        # Verify that run_ai_chat checks warehouse isolation at start
        with pytest.raises(Exception) as excinfo:
            await GeminiService.run_ai_chat(db, "Give me inventory status", "WH-P2-02", p2_manager)
        assert "restricted" in str(excinfo.value).lower()
        
    run_async(run)
