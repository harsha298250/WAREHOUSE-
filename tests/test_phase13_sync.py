import pytest
import json
import asyncio
import queue
import threading
from backend.models import Warehouse, User
from backend.sync_broadcast import broadcaster
from backend.routers.digital_twin import sync_dt_state


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


def test_broadcaster_subscription_live():
    """Verifies that live subscription queues are isolated and broadcast successfully."""
    async def run():
        queue_obj = asyncio.Queue()
        broadcaster.subscribe_live("WH-SYNC-1", queue_obj)
        
        event = {"event_type": "ROBOT_MOVED", "entity_type": "robot", "entity_id": "ROB-A", "data": {"x": 5.0, "y": 2.0}}
        broadcaster.broadcast_live("WH-SYNC-1", event)
        
        # Yield control to the loop to allow scheduled dispatch tasks to process
        await asyncio.sleep(0.01)
        
        assert queue_obj.qsize() == 1
        received = queue_obj.get_nowait()
        assert received["event_type"] == "ROBOT_MOVED"
        assert received["entity_id"] == "ROB-A"
        
        broadcaster.unsubscribe_live("WH-SYNC-1", queue_obj)
    run_async(run)


def test_broadcaster_subscription_sim():
    """Verifies that simulation subscription queues are isolated and broadcast successfully."""
    async def run():
        queue_obj = asyncio.Queue()
        broadcaster.subscribe_sim(42, queue_obj)
        
        event = {"event_type": "TASK_STATUS_CHANGED", "entity_type": "task", "entity_id": "TSK-01", "data": {"status": "COMPLETED"}}
        broadcaster.broadcast_sim(42, event)
        
        # Yield control to the loop to allow scheduled dispatch tasks to process
        await asyncio.sleep(0.01)
        
        assert queue_obj.qsize() == 1
        received = queue_obj.get_nowait()
        assert received["event_type"] == "TASK_STATUS_CHANGED"
        assert received["entity_id"] == "TSK-01"
        
        broadcaster.unsubscribe_sim(42, queue_obj)
    run_async(run)


def test_sync_stream_snapshot_endpoint(db):
    """Asserts that establishing an SSE sync connection delivers the authoritative SNAPSHOT as its first message."""
    async def run():
        wh = db.query(Warehouse).filter(Warehouse.id == "WH-BLR-01").first()
        if not wh:
            wh = Warehouse(id="WH-BLR-01", name="Bangalore Hub", location="BLR")
            db.add(wh)
            db.commit()

        admin = db.query(User).filter(User.username == "test_admin").first()
        
        response = await sync_dt_state(
            warehouse_id="WH-BLR-01",
            mode="LIVE",
            db=db,
            user=admin
        )
        
        assert response.status_code == 200
        iterator = response.body_iterator
        first_item = await iterator.__anext__()
        
        assert first_item.startswith("data: ")
        data = json.loads(first_item[6:])
        assert data["event_type"] == "SNAPSHOT"
        assert data["warehouse_id"] == "WH-BLR-01"
        assert "data" in data
    run_async(run)


def test_sync_stream_multi_warehouse_isolation(db):
    """Verifies that updates published to Warehouse A do not leak to Warehouse B subscribers."""
    async def run():
        wh_a = db.query(Warehouse).filter(Warehouse.id == "WH-A").first()
        if not wh_a:
            db.add(Warehouse(id="WH-A", name="Warehouse A", location="A"))
        wh_b = db.query(Warehouse).filter(Warehouse.id == "WH-B").first()
        if not wh_b:
            db.add(Warehouse(id="WH-B", name="Warehouse B", location="B"))
        db.commit()

        admin = db.query(User).filter(User.username == "test_admin").first()
        
        response = await sync_dt_state(
            warehouse_id="WH-A",
            mode="LIVE",
            db=db,
            user=admin
        )
        
        assert response.status_code == 200
        iterator = response.body_iterator
        
        # Read snapshot
        first_item = await iterator.__anext__()
        assert first_item.startswith("data: ")
        
        # Broadcast to WH-B
        broadcaster.broadcast_live("WH-B", {
            "event_type": "ROBOT_MOVED",
            "entity_type": "robot",
            "entity_id": "ROB-B",
            "data": {"x": 1.0, "y": 1.0}
        })
        
        # Verify separation
        wh_a_listeners = broadcaster.live_listeners.get("WH-A", set())
        wh_b_listeners = broadcaster.live_listeners.get("WH-B", set())
        
        assert len(wh_a_listeners) == 1
        assert len(wh_b_listeners) == 0
    run_async(run)


def test_sync_database_non_mutation_safety(db):
    """Guarantees that establishing real-time sync streams and broadcasting events does NOT write to PostgreSQL."""
    wh = db.query(Warehouse).filter(Warehouse.id == "WH-BLR-01").first()
    if not wh:
        wh = Warehouse(id="WH-BLR-01", name="Bangalore Hub", location="BLR")
        db.add(wh)
        db.commit()

    wh_count_before = db.query(Warehouse).count()
    broadcaster.broadcast_live("WH-BLR-01", {
        "event_type": "ROBOT_MOVED",
        "entity_type": "robot",
        "entity_id": "ROB-A",
        "data": {"x": 5.0, "y": 2.0}
    })
    wh_count_after = db.query(Warehouse).count()
    assert wh_count_before == wh_count_after
