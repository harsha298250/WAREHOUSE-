import pytest
import secrets
from datetime import datetime, date, timedelta, UTC
from fastapi.testclient import TestClient

from backend.main import app
from backend.models import (
    Order, OrderItem, OrderEvent, Inventory, Item, StockMovement,
    Task, Robot, AIRecommendation, ShrinkageFlag, RobotRoute, Warehouse
)
from backend import analytics_engine as engine

client = TestClient(app)

@pytest.fixture(autouse=True)
def seed_warehouse_blr(db):
    """Ensure the target warehouse WH-BLR-01 exists for foreign key constraints."""
    wh = db.query(Warehouse).filter(Warehouse.id == "WH-BLR-01").first()
    if not wh:
        wh = Warehouse(id="WH-BLR-01", name="Bangalore Hub")
        db.add(wh)
        db.commit()
    return wh


def test_date_range_helper():
    """Verify that get_date_range correctly splits and parses periods."""
    # 1. Standard periods
    start_30d, end_30d = engine.get_date_range("30d")
    assert (end_30d - start_30d).days >= 29
    
    start_7d, end_7d = engine.get_date_range("7d")
    assert (end_7d - start_7d).days >= 6
    
    # 2. Custom period
    start_str = "2026-08-01T00:00:00"
    end_str = "2026-08-15T23:59:59"
    start_cust, end_cust = engine.get_date_range("custom", start_str, end_str)
    assert start_cust == datetime.fromisoformat(start_str)
    assert end_cust == datetime.fromisoformat(end_str)


def test_order_analytics_formulas(db):
    """Test order cycle time, completion rate and throughput calculations."""
    db.query(OrderEvent).delete()
    db.query(Order).delete()
    db.commit()

    wh_id = "WH-BLR-01"
    start = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=2)
    end = datetime.now(UTC).replace(tzinfo=None) + timedelta(days=1)
    
    # Seed 3 orders: 1 completed, 1 cancelled, 1 failed (exception)
    o1 = Order(id="ORD-T1", customer_ref="Cust 1", warehouse_id=wh_id, created_at=start + timedelta(hours=1), status="DELIVERED")
    o2 = Order(id="ORD-T2", customer_ref="Cust 2", warehouse_id=wh_id, created_at=start + timedelta(hours=2), status="CANCELLED")
    o3 = Order(id="ORD-T3", customer_ref="Cust 3", warehouse_id=wh_id, created_at=start + timedelta(hours=3), status="FAILED")
    db.add_all([o1, o2, o3])
    db.commit()
    
    # Seed order event for completed o1 (takes 5 hours)
    e1 = OrderEvent(order_id="ORD-T1", timestamp=o1.created_at + timedelta(hours=5), status="DELIVERED", event_type="DELIVERED")
    db.add(e1)
    db.commit()
    
    res = engine.compute_order_analytics(db, wh_id, start, end)
    
    assert res["throughput"]["value"] == 1
    # denominator = total (3) - cancelled (1) = 2. completed = 1. completion = 1/2 = 50.0%
    assert res["completion_rate"]["value"] == 50.0
    assert res["cancellation_rate"]["value"] == 33.3  # 1/3
    assert res["exception_rate"]["value"] == 33.3     # 1/3
    assert res["avg_cycle_time_hours"]["value"] == 5.0


def test_inventory_kpis_and_abc(db):
    """Verify stock summaries, low-stock flags, and turnover values."""
    db.query(Inventory).delete()
    db.query(StockMovement).delete()
    db.commit()

    wh_id = "WH-BLR-01"
    item1 = db.query(Item).filter(Item.id == "ITM-T1").first()
    if not item1:
        item1 = Item(id="ITM-T1", name="Test Item A", unit_cost=100.0, safety_stock=5, reorder_threshold=5)
        db.add(item1)
    else:
        item1.unit_cost = 100.0
        item1.safety_stock = 5
        item1.reorder_threshold = 5
        
    item2 = db.query(Item).filter(Item.id == "ITM-T2").first()
    if not item2:
        item2 = Item(id="ITM-T2", name="Test Item B", unit_cost=50.0, safety_stock=20, reorder_threshold=20)
        db.add(item2)
    else:
        item2.unit_cost = 50.0
        item2.safety_stock = 20
        item2.reorder_threshold = 20
        
    db.commit()
    
    inv1 = Inventory(warehouse_id=wh_id, item_id=item1.id, on_hand=10, reserved=2, available=8, damaged=1)
    inv2 = Inventory(warehouse_id=wh_id, item_id=item2.id, on_hand=5, reserved=0, available=5, damaged=0)
    db.add_all([inv1, inv2])
    db.commit()
    
    start = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=5)
    end = datetime.now(UTC).replace(tzinfo=None) + timedelta(days=1)
    
    # Stock out-bound movement for turnover
    mov = StockMovement(date=start.date(), warehouse_id=wh_id, item_id=item1.id, stock_in=0, stock_out=2, closing_stock=10)
    db.add(mov)
    db.commit()
    
    res = engine.compute_inventory_analytics(db, wh_id, start, end)
    
    assert res["on_hand"]["value"] == 15
    assert res["reserved"]["value"] == 2
    assert res["available"]["value"] == 13
    assert res["damaged"]["value"] == 1
    assert res["inventory_value"]["value"] == 1250.0  # (10 * 100) + (5 * 50)
    assert res["low_stock_count"]["value"] == 1      # ITM-T2 (available 5 < safety_stock 20)
    assert res["stockout_rate"]["value"] == 0.0


def test_task_analytics_formulas(db):
    """Test task priority counts and timing aggregates."""
    db.query(Task).delete()
    db.commit()

    wh_id = "WH-BLR-01"
    start = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=5)
    end = datetime.now(UTC).replace(tzinfo=None) + timedelta(days=1)
    
    # Seed items explicitly
    itm1 = db.query(Item).filter(Item.id == "ITM-GPU-01").first()
    if not itm1:
        itm1 = Item(id="ITM-GPU-01", name="GPU", safety_stock=5)
        db.add(itm1)
    itm2 = db.query(Item).filter(Item.id == "ITM-CPU-01").first()
    if not itm2:
        itm2 = Item(id="ITM-CPU-01", name="CPU", safety_stock=5)
        db.add(itm2)
    db.commit()
    
    t1 = Task(task_number="TSK-T1", warehouse_id=wh_id, task_type="PICK", priority="HIGH", status="COMPLETED",
              created_at=start, started_at=start + timedelta(minutes=10), completed_at=start + timedelta(minutes=25), 
              product_id="ITM-GPU-01", requested_quantity=10)
    t2 = Task(task_number="TSK-T2", warehouse_id=wh_id, task_type="PACK", priority="LOW", status="QUEUED",
              created_at=start, product_id="ITM-CPU-01", requested_quantity=5)
    db.add_all([t1, t2])
    db.commit()
    
    res = engine.compute_task_analytics(db, wh_id, start, end)
    
    assert res["tasks_created"]["value"] == 2
    assert res["tasks_completed"]["value"] == 1
    assert res["tasks_pending"]["value"] == 1
    assert res["avg_queue_time_minutes"]["value"] == 10.0
    assert res["avg_duration_minutes"]["value"] == 15.0


def test_robot_fleet_metrics(db):
    """Test robot fleet utilization percentages and list comparisons."""
    db.query(Robot).delete()
    db.commit()

    wh_id = "WH-BLR-01"
    start = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=5)
    end = datetime.now(UTC).replace(tzinfo=None) + timedelta(days=1)
    
    r1 = Robot(robot_code="ROB-T1", name="Robot 1", warehouse_id=wh_id, status="MOVING", utilization_percent=75.5,
               total_tasks_completed=10, total_distance=100.0, failure_count=1)
    db.add(r1)
    db.commit()
    
    res = engine.compute_robot_analytics(db, wh_id, start, end)
    
    assert res["fleet_size"]["value"] == 1
    assert res["avg_utilization"]["value"] == 75.5
    assert len(res["comparison"]) == 1
    assert res["comparison"][0]["robot_code"] == "ROB-T1"


def test_routing_and_congestion(db):
    """Verify route counts, replans and collision flags."""
    db.query(RobotRoute).delete()
    db.query(Robot).delete()
    db.commit()

    wh_id = "WH-BLR-01"
    start = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=5)
    end = datetime.now(UTC).replace(tzinfo=None) + timedelta(days=1)
    
    rob = Robot(robot_code="ROB-R1", name="Routing Bot", warehouse_id=wh_id, status="IDLE")
    db.add(rob)
    db.commit()
    
    r1 = RobotRoute(robot_id=rob.id, warehouse_id=wh_id, start_x=1, start_y=1, goal_x=5, goal_y=5, distance=10.0, cost=10.0,
                    status="REPLANNED", created_at=start)
    db.add(r1)
    db.commit()
    
    res = engine.compute_routing_analytics(db, wh_id, start, end)
    assert res["route_count"]["value"] == 1
    assert res["replanning_count"]["value"] == 1


def test_empty_period_zero_records(db):
    """Ensure calculations don't throw ZeroDivisionError or crash when DB is empty."""
    wh_id = "WH-EMPTY"
    start = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=5)
    end = datetime.now(UTC).replace(tzinfo=None) + timedelta(days=1)
    
    res_orders = engine.compute_order_analytics(db, wh_id, start, end)
    assert res_orders["throughput"]["value"] == 0
    assert res_orders["completion_rate"]["value"] == 100.0
    assert res_orders["avg_cycle_time_hours"]["value"] is None
    
    res_inv = engine.compute_inventory_analytics(db, wh_id, start, end)
    assert res_inv["on_hand"]["value"] == 0
    assert res_inv["inventory_value"]["value"] is None
    
    res_tasks = engine.compute_task_analytics(db, wh_id, start, end)
    assert res_tasks["tasks_created"]["value"] == 0
    assert res_tasks["avg_duration_minutes"]["value"] is None


def test_rbac_analytics_endpoints(client, admin_token, viewer_token):
    """Assert restricted endpoints (system/AI recommendations) reject non-privilege views."""
    headers_adm = {"Authorization": f"Bearer {admin_token}"}
    headers_view = {"Authorization": f"Bearer {viewer_token}"}
    
    # 1. Public overview (authenticated)
    res_over_view = client.get("/analytics/overview", headers=headers_view)
    assert res_over_view.status_code == 200
    
    # 2. Restrict AI endpoints to admin/manager
    res_ai_view = client.get("/analytics/ai", headers=headers_view)
    assert res_ai_view.status_code == 403
    
    res_ai_adm = client.get("/analytics/ai", headers=headers_adm)
    assert res_ai_adm.status_code == 200
    
    # 3. Restrict System logs to admin/auditor
    res_sys_view = client.get("/analytics/system", headers=headers_view)
    assert res_sys_view.status_code == 403
    
    res_sys_adm = client.get("/analytics/system", headers=headers_adm)
    assert res_sys_adm.status_code == 200


def test_csv_export_endpoint(client, admin_token):
    """Test format=csv queries deliver downloadable text/csv files with headers."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/analytics/orders?format=csv", headers=headers)
    assert res.status_code == 200
    assert res.headers["Content-Type"].startswith("text/csv")
    assert "Content-Disposition" in res.headers
    
    content = res.text
    assert "Metric" in content
    assert "Value" in content
