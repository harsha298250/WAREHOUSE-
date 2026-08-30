import pytest
import time
import os
import concurrent.futures
import numpy as np
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock

from backend.models import (
    User, Item, Warehouse, Inventory, Order, OrderItem,
    WarehouseLocation, UserWarehouseAccess
)
from backend.auth import hash_password
from backend.services.ai_service import GeminiService, TOOL_REGISTRY
from backend.routers.pathfinding import run_a_star
from backend.routers.or_tools_scheduler import benchmark_ortools_assignment
from backend.main import app

client = TestClient(app)


def run_async(coro_creator):
    import queue
    import asyncio
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
def test_admin_user(db):
    existing = db.query(User).filter(User.username == "stress_admin").first()
    if not existing:
        user = User(
            username="stress_admin",
            password_hash=hash_password("AdminPass123!"),
            role="admin"
        )
        db.add(user)
        db.commit()
        return user
    return existing


@pytest.fixture
def admin_token(client, test_admin_user):
    r = client.post("/auth/login", json={"username": "stress_admin", "password": "AdminPass123!"})
    assert r.status_code == 200
    return r.json()["access_token"]


def setup_stress_e2e_data(db):
    db.query(UserWarehouseAccess).delete()
    db.query(Inventory).delete()
    db.query(WarehouseLocation).filter(WarehouseLocation.warehouse_id == "WH-STRESS-01").delete()
    db.query(Warehouse).filter(Warehouse.id == "WH-STRESS-01").delete()
    db.query(Item).filter(Item.id == "ITM-STRESS-01").delete()
    db.commit()

    wh = Warehouse(id="WH-STRESS-01", name="Stress Wh", location="Zone Z")
    db.add(wh)
    db.commit()

    itm = Item(id="ITM-STRESS-01", name="Stress Item", unit_cost=10.0, safety_stock=5)
    db.add(itm)
    db.commit()

    loc = WarehouseLocation(
        id="LOC-STRESS-A01", warehouse_id="WH-STRESS-01",
        zone="A", aisle="01", rack="01", shelf="01", capacity=100
    )
    db.add(loc)
    db.commit()

    db.add(Inventory(
        warehouse_id="WH-STRESS-01", item_id="ITM-STRESS-01", location_id="LOC-STRESS-A01",
        on_hand=100, reserved=0, available=100
    ))
    db.commit()


def calculate_latencies(durations):
    dur_arr = np.array(durations)
    return {
        "avg": float(np.mean(dur_arr)) * 1000,
        "median": float(np.median(dur_arr)) * 1000,
        "p95": float(np.percentile(dur_arr, 95)) * 1000,
        "min": float(np.min(dur_arr)) * 1000,
        "max": float(np.max(dur_arr)) * 1000,
    }


def test_baseline_api_latencies(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    endpoints = [
        "/wms/warehouses",
        "/wms/items",
        "/analytics/overview"
    ]
    
    for ep in endpoints:
        durations = []
        for _ in range(5):
            start = time.perf_counter()
            r = client.get(ep, headers=headers)
            durations.append(time.perf_counter() - start)
            assert r.status_code in [200, 404]
            
        stats = calculate_latencies(durations)
        print(f"\nEndpoint {ep} baseline: Avg={stats['avg']:.2f}ms, Median={stats['median']:.2f}ms, P95={stats['p95']:.2f}ms")


def test_astar_pathfinding_complexity():
    grid_sizes = [6, 10, 20]
    for size in grid_sizes:
        grid = {
            (x, y): {"traversable": True, "cost": 1.0, "type": "FLOOR"}
            for x in range(1, size+1) for y in range(1, size+1)
        }
        
        durations = []
        for _ in range(10):
            start = time.perf_counter()
            path, cost, duration, msg, expanded = run_a_star((1, 1), (size, size), grid)
            durations.append(time.perf_counter() - start)
            assert path is not None
            
        stats = calculate_latencies(durations)
        print(f"\nA* Route {size}x{size}: Avg={stats['avg']:.2f}ms, Median={stats['median']:.2f}ms, P95={stats['p95']:.2f}ms")


def test_or_tools_assignment_fallback(db):
    start = time.perf_counter()
    benchmark_ortools_assignment(db, "WH-STRESS-01")
    duration = time.perf_counter() - start
    print(f"\nOR-Tools scheduling run duration: {duration*1000:.2f}ms")


def test_offline_resilience_outages():
    with patch("backend.redis_client.get_redis_client", return_value=None):
        from backend.redis_client import get_cache, set_cache
        assert get_cache("any_key") is None
        assert set_cache("any_key", "value") is False

    with patch("backend.mq_client.get_channel", return_value=None):
        from backend.mq_client import publish_event
        assert publish_event("ORDER_COMPLETED", "orders", {"id": 1}) is False


def test_database_concurrency_conflict(db, admin_token):
    setup_stress_e2e_data(db)
    
    import os
    db_url = os.getenv("DATABASE_URL", "sqlite")
    use_sqlite = "sqlite" in db_url

    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "customer_ref": "Stress Concurrency",
        "warehouse_id": "WH-STRESS-01",
        "items": [{"item_id": "ITM-STRESS-01", "requested_qty": 6}]
    }

    results = []

    def run_order_creation():
        with TestClient(app) as local_client:
            return local_client.post("/wms/orders", json=payload, headers=headers)

    if use_sqlite:
        for _ in range(20):
            results.append(run_order_creation())
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(run_order_creation) for _ in range(20)]
            for f in concurrent.futures.as_completed(futures):
                results.append(f.result())

    # Count successful reserved orders (HTTP 201 with RESERVED order_status)
    reserved_orders = [
        r for r in results 
        if r.status_code == 201 and r.json().get("order_status") == "RESERVED"
    ]
    print(f"\nConcurrency test results: Total orders={len(results)}, Reserved={len(reserved_orders)}")
    
    db.expire_all()
    inv = db.query(Inventory).filter(Inventory.item_id == "ITM-STRESS-01").first()
    assert inv.available >= 0
    # 16 orders fully reserved 96 units, and the 17th order partially reserved the remaining 4 units
    assert inv.reserved == 100
    assert inv.available == 0


def test_multi_warehouse_stress_isolation(db):
    db.query(UserWarehouseAccess).delete()
    db.query(Inventory).delete()
    db.query(WarehouseLocation).filter(WarehouseLocation.warehouse_id.in_(["WH-STRESS-01", "WH-STRESS-02"])).delete()
    db.query(Warehouse).filter(Warehouse.id.in_(["WH-STRESS-01", "WH-STRESS-02"])).delete()
    db.commit()

    db.add(Warehouse(id="WH-STRESS-01", name="Wh 1", location="Zone A"))
    db.add(Warehouse(id="WH-STRESS-02", name="Wh 2", location="Zone B"))
    db.commit()

    user1 = db.query(User).filter(User.username == "sec_viewer").first()
    if not user1:
        user1 = User(username="sec_viewer", role="viewer", password_hash=hash_password("Pass123!"))
        db.add(user1)
        db.commit()

    db.add(UserWarehouseAccess(user_id=user1.id, warehouse_id="WH-STRESS-01"))
    db.commit()

    orig_key = os.environ.get("GEMINI_API_KEY")
    os.environ["GEMINI_API_KEY"] = ""
    try:
        with pytest.raises(Exception) as exc_info:
            run_async(lambda: GeminiService.run_ai_chat(db, "telemetry status", "WH-STRESS-02", user1))
        assert "Access to warehouse" in str(exc_info.value)
    finally:
        if orig_key:
            os.environ["GEMINI_API_KEY"] = orig_key
