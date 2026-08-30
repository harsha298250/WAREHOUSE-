import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from sqlalchemy.orm import Session

import queue
import threading
import asyncio
from backend.models import User, Warehouse, UserWarehouseAccess, FinancialTransaction, Inventory, Robot, Task, ShrinkageFlag, Order, Item
from backend.services.ai_service import GeminiService

def run_async(coro_creator):
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
def test_user(db):
    return db.query(User).filter(User.id == 999).first()

@pytest.fixture
def test_admin(db):
    return db.query(User).filter(User.id == 888).first()

@pytest.fixture
def setup_test_db(db):
    # Purge existing data
    db.query(UserWarehouseAccess).delete()
    db.query(FinancialTransaction).delete()
    db.query(Order).delete()
    db.query(Inventory).delete()
    db.query(ShrinkageFlag).delete()
    db.query(Warehouse).delete()
    db.query(Item).filter(Item.id == "ITM-CPU-01").delete()
    db.query(User).filter((User.id.in_([999, 888])) | (User.username.in_(["test_operator", "test_admin"]))).delete()
    db.commit()

    # Seed users
    u_op = User(id=999, username="test_operator", role="operator", password_hash="dummyhash")
    u_ad = User(id=888, username="test_admin", role="admin", password_hash="dummyhash")
    db.add_all([u_op, u_ad])
    db.commit()

    # Seed isolated warehouse
    wh = Warehouse(id="WH-BLR-01", name="Bangalore Hub", location="Bangalore")
    wh_unauth = Warehouse(id="WH-DEL-01", name="Delhi Hub", location="Delhi")
    db.add_all([wh, wh_unauth])
    db.commit()

    # Seed User Access: operator has access only to WH-BLR-01
    access = UserWarehouseAccess(user_id=999, warehouse_id="WH-BLR-01")
    db.add(access)
    db.commit()

    # Seed Item
    i1 = Item(id="ITM-CPU-01", name="CPU Core", safety_stock=20, unit_cost=100.0)
    db.add(i1)
    db.commit()

    # Seed Order
    o1 = Order(id="ORD-TEST-01", customer_ref="Customer Test", warehouse_id="WH-BLR-01", status="COMPLETED")
    db.add(o1)
    db.commit()

    # Seed financial transactions
    t1 = FinancialTransaction(
        transaction_id="TXN-001",
        order_id="ORD-TEST-01",
        warehouse_id="WH-BLR-01",
        amount=12500.0,
        transaction_type="SALE",
        created_at=datetime.utcnow()
    )
    t2 = FinancialTransaction(
        transaction_id="TXN-002",
        order_id="ORD-TEST-01",
        warehouse_id="WH-BLR-01",
        amount=1500.0,
        transaction_type="REFUND",
        created_at=datetime.utcnow()
    )
    db.add_all([t1, t2])
    db.commit()

    # Seed robots
    r = Robot(robot_code="ROB-TEST-01", name="Test Bot", status="AVAILABLE", battery_level=90.0, warehouse_id="WH-BLR-01")
    db.add(r)
    db.commit()

    # Seed inventory
    inv = Inventory(warehouse_id="WH-BLR-01", item_id="ITM-CPU-01", on_hand=100, reserved=10, available=90, damaged=0)
    db.add(inv)
    db.commit()

    yield db

def test_rbac_unauthorized_warehouse_check(db, setup_test_db, test_user):
    """Verify that a user is prevented from querying a warehouse they don't have access to."""
    async def run():
        # Case 1: Direct warehouse parameter check should raise 403
        with pytest.raises(HTTPException) as exc:
            await GeminiService.run_ai_chat(db, "What is the inventory?", "WH-DEL-01", test_user)
        assert exc.value.status_code == 403

        # Case 2: Mentioning unauthorized warehouse in message with active authorized session should return access denied response
        res = await GeminiService.run_ai_chat(db, "What is the inventory of WH-DEL-01?", "WH-BLR-01", test_user)
        assert res["status"] == "success"
        assert any(word in res["response"].lower() for word in ["denied", "restricted", "permission"])
        # Tool call is attempted by model and blocked by service authorization
        assert len(res["tool_calls"]) == 1
    run_async(run)

def test_admin_unrestricted_warehouse_check(db, setup_test_db, test_admin):
    """Verify that an admin can query any warehouse without restrictions."""
    async def run():
        res = await GeminiService.run_ai_chat(db, "What is the inventory of WH-DEL-01?", "WH-DEL-01", test_admin)
        assert res["status"] == "success"
        assert not any(word in res["response"].lower() for word in ["denied", "restricted", "permission"])
    run_async(run)

def test_kpi_revenue_grounded_routing(db, setup_test_db, test_user):
    """Verify that KPIs and revenue questions correctly trigger get_executive_kpis and query real database numbers."""
    async def run():
        res = await GeminiService.run_ai_chat(db, "What is the total gross revenue of WH-BLR-01?", "WH-BLR-01", test_user)
        assert res["status"] == "success"
        assert any(val in res["response"] for val in ["12,500", "12500", "12.500"])
        assert any(tc["name"] == "get_executive_kpis" for tc in res["tool_calls"])
    run_async(run)

def test_inventory_grounded_routing(db, setup_test_db, test_user):
    """Verify inventory status queries match get_inventory_analytics and return database stock counts."""
    async def run():
        res = await GeminiService.run_ai_chat(db, "How much inventory do we have in WH-BLR-01?", "WH-BLR-01", test_user)
        assert res["status"] == "success"
        assert any(val in res["response"] for val in ["100", "90"])
        assert any(tc["name"] in ("get_inventory_levels", "get_inventory_analytics") for tc in res["tool_calls"])
    run_async(run)

def test_robot_fleet_grounded_routing(db, setup_test_db, test_user):
    """Verify robot queries match get_robot_analytics and return active robot status details."""
    async def run():
        res = await GeminiService.run_ai_chat(db, "Show me robot status for WH-BLR-01.", "WH-BLR-01", test_user)
        assert res["status"] == "success"
        assert "ROB-TEST-01" in res["response"]
        assert any(tc["name"] in ("get_robot_telemetry", "get_robot_analytics") for tc in res["tool_calls"])
    run_async(run)

def test_multi_part_operational_query(db, setup_test_db, test_user):
    """Verify that queries containing both inventory and robot requests execute both tools and combine their outputs."""
    async def run():
        res = await GeminiService.run_ai_chat(db, "Give me inventory and robot status for WH-BLR-01.", "WH-BLR-01", test_user)
        assert res["status"] == "success"
        assert any(tc["name"] in ("get_inventory_levels", "get_inventory_analytics") for tc in res["tool_calls"])
        assert any(tc["name"] in ("get_robot_telemetry", "get_robot_analytics") for tc in res["tool_calls"])
    run_async(run)
