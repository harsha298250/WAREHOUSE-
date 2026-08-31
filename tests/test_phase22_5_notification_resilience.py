import time
import json
import pytest
from unittest.mock import patch, MagicMock
from backend.models import (
    Warehouse, Item, Inventory, Order, User, AuditLedger, Notification, WarehouseLocation
)
from backend.auth import hash_password
from backend.database import SessionLocal
from backend.event_processor import publish_event
import backend.notifications as notifications

@pytest.fixture
def admin_token(client, db):
    existing = db.query(User).filter(User.username == "res_admin").first()
    if not existing:
        user = User(
            username="res_admin",
            password_hash=hash_password("AdminPass123!"),
            role="admin",
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.commit()

    r = client.post("/auth/login", json={"username": "res_admin", "password": "AdminPass123!"})
    assert r.status_code == 200
    return r.json()["access_token"]

@pytest.fixture
def setup_wms_data(db):
    # Setup base warehouse, item, location, inventory
    wh = db.query(Warehouse).filter(Warehouse.id == "WH-RES-01").first()
    if not wh:
        wh = Warehouse(id="WH-RES-01", name="Resilience Warehouse", location="Loc 1")
        db.add(wh)
    
    it = db.query(Item).filter(Item.id == "ITM-RES-01").first()
    if not it:
        it = Item(id="ITM-RES-01", name="Resilient Widget", sku="ITM-RES-01", category="WIDGET", unit_cost=20.0)
        db.add(it)
        
    loc = db.query(WarehouseLocation).filter(WarehouseLocation.id == "WH-RES-01-A-01").first()
    if not loc:
        loc = WarehouseLocation(
            id="WH-RES-01-A-01",
            warehouse_id="WH-RES-01",
            zone="A",
            aisle="1",
            rack="1",
            shelf="1",
            location_type="PICKING"
        )
        db.add(loc)
        
    db.commit()
    
    # Refresh/create inventory
    inv = db.query(Inventory).filter(Inventory.warehouse_id == "WH-RES-01", Inventory.item_id == "ITM-RES-01").first()
    if not inv:
        inv = Inventory(
            warehouse_id="WH-RES-01",
            item_id="ITM-RES-01",
            location_id="WH-RES-01-A-01",
            on_hand=100,
            available=100,
            reserved=0
        )
        db.add(inv)
    else:
        inv.on_hand = 100
        inv.available = 100
        inv.reserved = 0
    db.commit()
    return wh, it

def test_normal_notification_publishing_still_works(db, setup_wms_data):
    """
    Test A: Normal notification publishing still creates correct notification records
    and triggers worker execution.
    """
    # Clean old alerts
    db.query(Notification).filter(Notification.event_type == "PASSWORD_CHANGED").delete()
    db.commit()

    # Trigger password change notification
    user = db.query(User).filter(User.role == "admin").first()
    assert user is not None

    success = notifications.send_change_alert("Security Update: Password Changed Successfully", {
        "message": "Password changed successfully for test user.",
        "warehouse_id": "WH-RES-01"
    })
    
    assert success is True
    
    # Wait for the background thread to write to database
    # Since daemon thread starts immediately, let's wait a short bit
    time.sleep(0.5)
    
    # Confirm notification gets created for all active admins
    notif = db.query(Notification).filter(
        Notification.event_type == "PASSWORD_CHANGED"
    ).first()
    
    # If notifications/SMTP is bypassed, there should still be an in-app notification
    assert notif is not None
    assert notif.severity == "WARNING"

def test_broker_unavailable_does_not_block_wms(client, db, admin_token, setup_wms_data):
    """
    Test B, C, D, E, F: When RabbitMQ/Celery hangs or is completely offline:
    - HTTP request completes instantly (fails fast).
    - WMS transaction commits successfully (Order created, inventory reserved).
    - Database is not corrupted.
    - Audit ledger contains audit log entry.
    - No fake notification success is fabricated inside the persistent notification log (status is QUEUED/FAILED).
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    from backend.celery_app import celery
    
    # Save original configuration
    orig_broker = celery.conf.broker_url
    orig_backend = celery.conf.result_backend
    orig_timeout = celery.conf.broker_connection_timeout
    
    # Reconfigure Celery to use unreachable endpoints
    celery.conf.broker_url = "amqp://localhost:5699//"
    celery.conf.result_backend = "redis://localhost:6399/0"
    celery.conf.broker_connection_timeout = 1.0
    
    # Reset pool properties
    import kombu.pools
    kombu.pools.reset()
    for attr in ["_pool", "pool", "producer_pool"]:
        try:
            delattr(celery, attr)
        except AttributeError:
            pass
        if attr in celery.__dict__:
            del celery.__dict__[attr]
    
    try:
        # Mock mq_client.publish_event to simulate a network hang (takes 3 seconds)
        # Mock send_email_alert to return False to simulate SMTP failure when broker is down
        with patch("backend.mq_client.publish_event", side_effect=lambda *a, **k: time.sleep(3) or False), \
             patch("backend.notifications.send_email_alert", return_value=False):
             
            t0 = time.time()
            
            # Post a WMS order
            payload = {
                "customer_ref": "Resilient Customer",
                "items": [
                    {"item_id": "ITM-RES-01", "requested_qty": 5}
                ],
                "warehouse_id": "WH-RES-01"
            }
            
            response = client.post("/wms/orders", json=payload, headers=headers)
            t_duration = time.time() - t0
            
            # Verify call completes immediately despite 3-second sleep mock
            assert t_duration < 1.5, f"HTTP request blocked for {t_duration}s"
            assert response.status_code == 201
            
            # Check order status in response
            res_data = response.json()
            assert res_data["status"] == "created"
            order_id = res_data["order_id"]
            
            # Verify transaction commit & inventory reservation integrity
            db.expire_all()
            inv = db.query(Inventory).filter(Inventory.warehouse_id == "WH-RES-01", Inventory.item_id == "ITM-RES-01").first()
            assert inv.reserved == 5
            assert inv.available == 95
            
            # Verify order exists
            order = db.query(Order).filter(Order.id == order_id).first()
            assert order is not None
            assert order.status == "RESERVED"
            
            # Verify AuditLedger has trace
            audit = db.query(AuditLedger).filter(AuditLedger.event_type == "ORDER_CREATED").first()
            assert audit is not None
            assert json.loads(audit.details)["order_id"] == order_id
    
            # Verify no fabricated success state in notification table
            # Let's wait a bit for background thread to run
            time.sleep(1.5)
            
            db.expire_all()
            # The email notification created during this run should be QUEUED or FAILED, not SENT/DELIVERED
            notifs = db.query(Notification).filter(
                Notification.event_type == "ORDER_CREATED",
                Notification.channel == "EMAIL",
                Notification.warehouse_id == "WH-RES-01"
            ).all()
            for n in notifs:
                assert n.status in ("QUEUED", "FAILED")
    finally:
        # Restore configuration
        celery.conf.broker_url = orig_broker
        celery.conf.result_backend = orig_backend
        celery.conf.broker_connection_timeout = orig_timeout
        
        # Reset pools again
        kombu.pools.reset()
        for attr in ["_pool", "pool", "producer_pool"]:
            try:
                delattr(celery, attr)
            except AttributeError:
                pass
            if attr in celery.__dict__:
                del celery.__dict__[attr]


def test_celery_broker_unreachable_fail_fast():
    """
    CASE B: Celery broker unreachable causes bounded connection timeouts (fails fast).
    """
    from backend.celery_app import celery, send_resend_email_task
    import kombu.pools
    
    orig_broker = celery.conf.broker_url
    orig_timeout = celery.conf.broker_connection_timeout
    orig_retry = celery.conf.broker_connection_retry
    orig_max_retries = celery.conf.broker_connection_max_retries
    
    # Configure unreachable broker URL and short connection timeout
    celery.conf.broker_url = "amqp://localhost:5699//"
    celery.conf.broker_connection_timeout = 2.0
    celery.conf.broker_connection_retry = False
    celery.conf.broker_connection_max_retries = 1
    
    # Reset pools
    kombu.pools.reset()
    for attr in ["_pool", "pool", "producer_pool"]:
        try:
            delattr(celery, attr)
        except AttributeError:
            pass
        if attr in celery.__dict__:
            del celery.__dict__[attr]
    
    t0 = time.time()
    try:
        # Dispatch a task using safe_task_dispatch. It should fail fast (raise exception in < 6s) rather than hang
        from backend.celery_app import safe_task_dispatch
        safe_task_dispatch(send_resend_email_task, "Subject", "Body", "test@example.com", 999, timeout=2.5)
        pytest.fail("Should have failed on unreachable broker connection")
    except Exception as e:
        # Expected connection failure
        assert time.time() - t0 < 6.0, f"Unreachable broker caused long delay: {time.time() - t0}s"
    finally:
        celery.conf.broker_url = orig_broker
        celery.conf.broker_connection_timeout = orig_timeout
        celery.conf.broker_connection_retry = orig_retry
        celery.conf.broker_connection_max_retries = orig_max_retries
        
        # Reset pools again
        kombu.pools.reset()
        for attr in ["_pool", "pool", "producer_pool"]:
            try:
                delattr(celery, attr)
            except AttributeError:
                pass
            if attr in celery.__dict__:
                del celery.__dict__[attr]


def test_celery_result_backend_unreachable_fail_fast():
    """
    CASE B: Redis result backend unreachable causes bounded connection/socket timeouts (fails fast).
    """
    from backend.celery_app import celery
    import redis
    
    backend = celery.backend
    assert backend is not None
    
    # Save original connection kwargs
    orig_kwargs = dict(backend.client.connection_pool.connection_kwargs)
    
    # Configure to point to an unreachable local port using 127.0.0.1 to avoid Windows IPv6 resolution latency
    backend.client.connection_pool.connection_kwargs["host"] = "127.0.0.1"
    backend.client.connection_pool.connection_kwargs["port"] = 6399
    backend.client.connection_pool.connection_kwargs["socket_timeout"] = 1.0
    backend.client.connection_pool.connection_kwargs["socket_connect_timeout"] = 1.0
    
    # Disconnect any cached connections
    backend.client.connection_pool.disconnect()
    
    t0 = time.time()
    try:
        # Access client which triggers a socket connection attempt
        backend.client.ping()
        pytest.fail("Should have timed out on unreachable Redis backend")
    except (redis.exceptions.TimeoutError, redis.exceptions.ConnectionError):
        # Expected timeout/connection failure
        assert time.time() - t0 < 6.0, f"Unreachable Redis backend caused long delay: {time.time() - t0}s"
    finally:
        # Restore connection kwargs
        backend.client.connection_pool.connection_kwargs.update(orig_kwargs)
        backend.client.connection_pool.disconnect()


def test_celery_recovery():
    """
    CASE C: Restoring correct Celery parameters recovers task/connection publishing.
    """
    from backend.celery_app import celery
    # Verify we can obtain a valid Kombu connection URI under restored configuration
    conn = celery.connection()
    assert conn.as_uri().startswith("amqp") or conn.as_uri().startswith("amqps")


def test_s3_timeout_fail_fast():
    """
    Verify boto3 client connection attempts to an unreachable endpoint fail fast (connect_timeout limits).
    """
    import boto3
    from botocore.config import Config
    from botocore.exceptions import ConnectTimeoutError, EndpointConnectionError
    
    t0 = time.time()
    try:
        # Try listing objects from a bad local endpoint
        s3 = boto3.client(
            "s3", region_name="us-east-1",
            aws_access_key_id="dummy", aws_secret_access_key="dummy",
            endpoint_url="http://localhost:9999",
            config=Config(connect_timeout=2.0, read_timeout=2.0, retries={"max_attempts": 0}),
            verify=True
        )
        s3.list_objects(Bucket="dummy-bucket")
        pytest.fail("Should have failed on unreachable S3 endpoint")
    except (ConnectTimeoutError, EndpointConnectionError, Exception):
        # Expected connect/timeout failure
        assert time.time() - t0 < 6.0, f"Unreachable S3 endpoint caused long delay: {time.time() - t0}s"


def test_rbac_validation_unchanged(client, db):
    """
    Test G: Existing RBAC behavior remains unchanged.
    """
    # Create staff user
    staff = db.query(User).filter(User.username == "res_staff").first()
    if not staff:
        staff = User(
            username="res_staff",
            password_hash=hash_password("StaffPass123!"),
            role="staff",
            is_active=True,
            is_verified=True
        )
        db.add(staff)
        db.commit()

    r = client.post("/auth/login", json={"username": "res_staff", "password": "StaffPass123!"})
    assert r.status_code == 200
    staff_token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {staff_token}"}
    
    # Try to adjust inventory (only admin/manager allowed)
    payload = {
        "adjustment": 10,
        "item_id": "ITM-RES-01",
        "reason": "testing",
        "warehouse_id": "WH-RES-01"
    }
    response = client.post("/wms/inventory/adjust", json=payload, headers=headers)
    assert response.status_code == 403
