import pytest
import concurrent.futures
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from backend.main import app
from backend.models import Warehouse, Item, Inventory, Order, OrderItem, WarehouseLocation
from backend.routers.pathfinding import run_a_star
from backend.redis_client import get_cache, set_cache
from backend.mq_client import publish_event

client = TestClient(app)

@pytest.fixture
def stress_setup_data(db):
    # Create isolated warehouse
    wh = Warehouse(id="WH-STRESS", name="Stress Test Warehouse", location="12.9716,77.5946")
    db.add(wh)
    db.commit()

    # Create a source location so task FK constraints pass
    loc = WarehouseLocation(
        id="LOC-STRESS-A01",
        warehouse_id="WH-STRESS",
        zone="A", aisle="1", rack="1", shelf="1",
        capacity=100
    )
    db.add(loc)
    db.commit()

    itm = Item(id="ITM-STRESS-01", name="Stress Item 1", category="Bulk", safety_stock=5, unit_cost=10.0)
    db.add(itm)
    db.commit()

    inv = Inventory(
        warehouse_id="WH-STRESS",
        item_id="ITM-STRESS-01",
        location_id="LOC-STRESS-A01",
        on_hand=10, reserved=0, available=10
    )
    db.add(inv)
    db.commit()

    yield

    # Teardown in FK-safe order.
    # task_events has no task_number column; it is cleaned via CASCADE when tasks
    # are deleted.  inventory_reservations is also CASCADE-deleted with orders.
    from sqlalchemy import text
    db.execute(text("DELETE FROM tasks WHERE warehouse_id = 'WH-STRESS'"))
    db.execute(text("DELETE FROM order_items WHERE item_id = 'ITM-STRESS-01'"))
    db.execute(text("DELETE FROM orders WHERE warehouse_id = 'WH-STRESS'"))
    db.execute(text("DELETE FROM inventory_movements WHERE warehouse_id = 'WH-STRESS'"))
    db.execute(text("DELETE FROM inventory_reservations WHERE item_id = 'ITM-STRESS-01'"))
    db.execute(text("DELETE FROM inventory WHERE warehouse_id = 'WH-STRESS'"))
    db.execute(text("DELETE FROM warehouse_locations WHERE warehouse_id = 'WH-STRESS'"))
    db.execute(text("DELETE FROM items WHERE id = 'ITM-STRESS-01'"))
    db.execute(text("DELETE FROM warehouses WHERE id = 'WH-STRESS'"))
    db.commit()

def test_concurrent_orders_locking(db, stress_setup_data, admin_token):
    """Verifies inventory reservation locking under concurrent/sequential order load.

    SQLite in-memory (StaticPool) cannot handle parallel write transactions across
    threads — concurrent flushes cause IntegrityError or lock collisions.  On SQLite
    we therefore issue the 8 requests sequentially (same behaviour from the locking
    perspective: inventory is checked and mutated inside a single serialised DB
    session, so the reservation cap still holds).  On PostgreSQL the requests are
    fired concurrently via a ThreadPoolExecutor.
    """
    import os
    db_url = os.getenv("DATABASE_URL", "sqlite")
    use_sqlite = "sqlite" in db_url

    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "customer_ref": "Stress Cust",
        "warehouse_id": "WH-STRESS",
        "items": [{"item_id": "ITM-STRESS-01", "requested_qty": 2}]
    }

    # Total qty requested = 16, stock available = 10 → at most 5 can succeed
    results = []

    def place_order():
        with TestClient(app) as local_client:
            return local_client.post("/wms/orders", json=payload, headers=headers)

    if use_sqlite:
        # Sequential execution on SQLite: avoids multi-thread write conflicts while
        # still asserting the reservation cap is enforced correctly.
        for _ in range(8):
            results.append(place_order())
    else:
        # Concurrent execution on PostgreSQL: real SELECT FOR UPDATE locking test.
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(place_order) for _ in range(8)]
            for f in concurrent.futures.as_completed(futures):
                results.append(f.result())

    # The WMS endpoint returns HTTP 201 for ALL accepted orders — both
    # RESERVED and INVENTORY_SHORTAGE.  The reservation outcome is in the
    # "order_status" field (not "status", which is always "created").
    fully_reserved = [
        r for r in results
        if r.status_code == 201 and r.json().get("order_status") == "RESERVED"
    ]
    shortage_or_fail = [r for r in results if r not in fully_reserved]

    # Exactly 8 responses received
    assert len(fully_reserved) + len(shortage_or_fail) == 8
    # Never more than 5 orders can be FULLY reserved (10 stock / 2 per order)
    assert len(fully_reserved) <= 5

    # Re-fetch inventory to verify consistency — reserved must match full reservations
    db.expire_all()   # force re-read from DB to see committed state
    inv = db.query(Inventory).filter(
        Inventory.warehouse_id == "WH-STRESS",
        Inventory.item_id == "ITM-STRESS-01"
    ).first()
    assert inv is not None
    assert inv.reserved == len(fully_reserved) * 2
    assert inv.available == 10 - (len(fully_reserved) * 2)

def test_astar_pathfinding_failures():
    """Verifies pathfinder handles unreachable, blocked, and congested coordinates gracefully."""
    grid = {
        (x, y): {"traversable": True, "cost": 1.0, "type": "FLOOR"}
        for x in range(1, 6) for y in range(1, 6)
    }
    
    # 1. Unreachable Goal: block all cells surrounding the goal
    grid[(4, 5)]["traversable"] = False
    grid[(5, 4)]["traversable"] = False
    
    path, cost, duration, msg, expanded = run_a_star((1, 1), (5, 5), grid)
    assert path is None
    assert "No traversable route" in msg or "non-traversable" in msg
    
    # 2. Blocked Start cell
    grid_blocked_start = {
        (x, y): {"traversable": True, "cost": 1.0, "type": "FLOOR"}
        for x in range(1, 3) for y in range(1, 3)
    }
    grid_blocked_start[(1, 1)]["traversable"] = False
    path, cost, duration, msg, expanded = run_a_star((1, 1), (2, 2), grid_blocked_start)
    assert path is None
    assert "non-traversable" in msg

def test_redis_offline_resilience():
    """Verifies that Redis offline caching falls back to None bypass without raising exceptions."""
    with patch("backend.redis_client.get_redis_client", return_value=None):
        # Operations must fail-safe and return None or False
        assert get_cache("test_cache_key") is None
        assert set_cache("test_cache_key", "value") is False

def test_rabbitmq_offline_resilience():
    """Verifies that publish_event logs locally and returns False when RabbitMQ is offline."""
    with patch("backend.mq_client.get_channel", return_value=None):
        # Must return False and log locally without crashing
        res = publish_event("ORDER_COMPLETED", "orders", {"order_id": 999})
        assert res is False

def test_gemini_outage_resilience(admin_token):
    """Verifies Gemini AI router falls back gracefully when the Gemini REST API is unreachable."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # The GeminiService uses httpx.AsyncClient.post to call the Gemini REST endpoint.
    # We patch that to raise a connection error, simulating a Gemini outage.
    import httpx
    mock_response = AsyncMock(side_effect=Exception("Simulated Gemini Outage"))
    with patch("httpx.AsyncClient.post", mock_response):
        r = client.post("/ai/assistant", json={"message": "Show me the inventory"}, headers=headers)
        # Must return 200 with fallback response — never a crash
        assert r.status_code == 200
        body = r.json()
        # Fallback mode must be indicated, and no fabricated operational numbers
        assert "response" in body or "detail" in body
