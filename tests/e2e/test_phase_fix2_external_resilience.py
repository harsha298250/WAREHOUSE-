import time
import json
import urllib.request
import pytest
import redis
import pika
import httpx
import asyncio
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from botocore.config import Config

from backend.models import (
    Warehouse, Item, Inventory, Order, User, AuditLedger, Notification, WarehouseLocation
)
from backend import redis_client
from backend import mq_client
from backend import weather_service
from backend.services.ai_service import GeminiService
from backend import cloud_storage
from backend.routers import health
from backend.timeout_policy import HEALTH_CHECK_TIMEOUT, OAUTH_TIMEOUT, WEATHER_TIMEOUT, S3_CONNECT_TIMEOUT, S3_READ_TIMEOUT

# ---------------------------------------------------------------------------
# Helpers & Fixtures
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Redis Resilience Tests
# ---------------------------------------------------------------------------

def test_redis_timeout(db):
    """Test that Redis timeout logs warning and fails open/safe."""
    redis_client.redis_available = True
    mock_client = MagicMock()
    mock_client.get.side_effect = redis.exceptions.TimeoutError("Redis socket timeout")
    redis_client._client = mock_client
    
    try:
        val = redis_client.get_cache("test_key_timeout")
        assert val is None
        assert redis_client.redis_available is False
    finally:
        redis_client._client = None
        redis_client.redis_available = False


def test_redis_unavailable(db):
    """Test that Redis connection failure behaves safely and bypasses caching."""
    redis_client.redis_available = True
    mock_client = MagicMock()
    mock_client.setex.side_effect = redis.exceptions.ConnectionError("Redis connection refused")
    redis_client._client = mock_client
    
    try:
        success = redis_client.set_cache("test_key_conn", "value", ttl_seconds=10)
        assert success is False
        assert redis_client.redis_available is False
    finally:
        redis_client._client = None
        redis_client.redis_available = False


# ---------------------------------------------------------------------------
# RabbitMQ & Celery Resilience Tests
# ---------------------------------------------------------------------------

def test_rabbitmq_timeout(db):
    """Test that RabbitMQ timeout fails safely and does not block."""
    mq_client.mq_available = True
    
    with patch("pika.BlockingConnection", side_effect=pika.exceptions.AMQPConnectionError("Timeout connecting")):
        # Should fallback to fast reconnect, fail and log event locally
        success = mq_client.publish_event("ORDER_CREATED", "orders", {"order_id": "ORD-123"})
        assert success is False
        assert mq_client.mq_available is False


def test_rabbitmq_unavailable(db):
    """Test that RabbitMQ connection refusal fails safely and records bypass."""
    mq_client.mq_available = True
    
    with patch("backend.mq_client.get_channel", return_value=None):
        success = mq_client.publish_event("INVENTORY_CHANGED", "inventory", {"item_id": "ITM-01"})
        assert success is False


def test_celery_unavailable(client, db, admin_token, setup_wms_data):
    """Test that WMS operations succeed even if Celery task queuing fails."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Mock celery delay call to raise exception (broker offline)
    with patch("backend.celery_app.send_resend_email_task.delay", side_effect=Exception("Celery broker connection refused")), \
         patch("backend.mq_client.publish_event", return_value=True), \
         patch("backend.notifications.send_email_alert", return_value=False):
         
        payload = {
            "warehouse_id": "WH-RES-01",
            "customer_ref": "Resilient Cust Celery",
            "items": [
                {"item_id": "ITM-RES-01", "requested_qty": 2}
            ]
        }
        
        response = client.post("/wms/orders", json=payload, headers=headers)
        assert response.status_code == 201
        
        # Verify transaction succeeded despite celery failure
        res_data = response.json()
        assert res_data["status"] == "created"
        
        db.expire_all()
        order = db.query(Order).filter(Order.id == res_data["order_id"]).first()
        assert order is not None
        assert order.status == "RESERVED"


# ---------------------------------------------------------------------------
# Gemini AI Assistant Resilience Tests
# ---------------------------------------------------------------------------

def test_gemini_timeout(db, setup_wms_data):
    """Test that Gemini API timeout falls back safely to offline assistant."""
    async def run():
        user = User(username="test_ai_user", role="admin")
        with patch("httpx.AsyncClient.post", side_effect=httpx.TimeoutException("Gemini connection timed out")):
            res = await GeminiService.run_ai_chat(db, "What is my inventory?", "WH-RES-01", user)
            assert res["status"] == "success"
            assert "Fallback mode" in res["response"]
            assert res["engine"] == "Fallback Rule-Based (Database Grounded)"
    run_async(run)


def test_gemini_unavailable_malformed(db, setup_wms_data):
    """Test that Gemini empty candidates response does not raise IndexError."""
    async def run():
        user = User(username="test_ai_user", role="admin")
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Malformed candidates dictionary (empty candidates list)
        mock_response.json.return_value = {"candidates": []}
        
        with patch("httpx.AsyncClient.post", return_value=mock_response):
            res = await GeminiService.run_ai_chat(db, "Hello?", "WH-RES-01", user)
            assert res["status"] == "success"
            assert "Fallback" in res["engine"] or "Fallback" in res["response"]
    run_async(run)


# ---------------------------------------------------------------------------
# Open-Meteo Weather Resilience Tests
# ---------------------------------------------------------------------------

def test_open_meteo_timeout():
    """Test that weather provider timeout raises predictable exception."""
    with patch("httpx.Client.get", side_effect=httpx.TimeoutException("Connection timed out")):
        with pytest.raises(Exception):
            weather_service.fetch_weather_from_provider(12.97, 77.59)


def test_open_meteo_malformed_response():
    """Test that malformed Open-Meteo JSON raises ValueError."""
    mock_res = MagicMock()
    mock_res.status_code = 200
    mock_res.json.return_value = {"invalid_key": {}}
    
    with patch("httpx.Client.get", return_value=mock_res):
        with pytest.raises(ValueError, match="Malformed response"):
            weather_service.fetch_weather_from_provider(12.97, 77.59)


# ---------------------------------------------------------------------------
# Resend Email & B2 Resilience Tests
# ---------------------------------------------------------------------------

def test_resend_timeout():
    """Test that email failure does not block and fails safely.

    resend_client.send_html_email() delegates to notifications.send_email_alert() (Gmail SMTP).
    We patch the delegate function to return False to simulate connection/SMTP failure.
    """
    from backend import resend_client

    with patch("backend.notifications.send_email_alert", return_value=False):
        success = resend_client.send_html_email("Alert", "Body", "test@test.com")
        assert success is False


def test_b2_upload_failure(db):
    """Test that cloud storage upload failure falls back cleanly to local storage backup."""
    # Ensure is_configured returns True to trigger cloud path
    with patch("backend.cloud_storage.is_configured", return_value=True), \
         patch("boto3.client") as mock_boto:
         
        # Simulate upload error
        mock_client = MagicMock()
        mock_client.upload_fileobj.side_effect = Exception("Backblaze B2 connection refused")
        mock_boto.return_value = mock_client
        
        result = cloud_storage.run_backup()
        # Verify it fallback successfully and saved locally
        assert "Local storage" in result["bucket"]
        assert "Local Fallback" in result["mode"]


# ---------------------------------------------------------------------------
# OAuth Provider Resilience Tests
# ---------------------------------------------------------------------------

def test_oauth_provider_timeout(client, db):
    """Test that Google OAuth connection timeout fails safely without authenticating."""
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("Connection timed out")):
        payload = {"id_token": "mock_id_token_123"}
        response = client.post("/auth/google-signin", json=payload)
        assert response.status_code == 401
        assert "Invalid or expired Google ID Token" in response.json()["detail"]


# ---------------------------------------------------------------------------
# Health Check Timeout Isolation & Multiple Dependency Failures
# ---------------------------------------------------------------------------

def test_health_check_timeout_isolation(client, db, admin_token):
    """Test that health checks enforce HEALTH_CHECK_TIMEOUT and do not block."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Mock urllib.request.urlopen to verify Google OAuth check parameters
    # Mock boto3.client to verify S3 config parameters
    # Mock Redis and RabbitMQ to return immediately
    with patch("urllib.request.urlopen") as mock_urlopen, \
         patch("boto3.client") as mock_boto, \
         patch("backend.redis_client.get_redis_client", return_value=None), \
         patch("backend.mq_client.get_channel", return_value=None):
         
        # Setup mock return values to prevent crashes in subsequent lines
        mock_urlopen.return_value.__enter__.return_value.read.return_value = b""
        
        response = client.get("/api/system/health", headers=headers)
        assert response.status_code == 200
        
        # Verify OAuth urlopen was called with HEALTH_CHECK_TIMEOUT
        mock_urlopen.assert_any_call("https://accounts.google.com", timeout=HEALTH_CHECK_TIMEOUT)
        
        # Verify S3 client was created with Config connect_timeout/read_timeout = HEALTH_CHECK_TIMEOUT
        # and verify=True
        boto_calls = mock_boto.call_args_list
        assert len(boto_calls) > 0
        config_arg = boto_calls[0][1].get("config")
        verify_arg = boto_calls[0][1].get("verify")
        
        assert config_arg is not None
        # Health.py uses centralized S3_CONNECT_TIMEOUT / S3_READ_TIMEOUT for boto3 clients
        # (not HEALTH_CHECK_TIMEOUT, which is for lightweight OAuth/HTTP probes only).
        assert config_arg.connect_timeout == S3_CONNECT_TIMEOUT
        assert config_arg.read_timeout == S3_READ_TIMEOUT
        assert verify_arg is True


# ---------------------------------------------------------------------------
# Security & Secret Exposure Checks
# ---------------------------------------------------------------------------

def test_no_secrets_in_error_responses(client, db):
    """Test that database credentials and S3 keys do not appear in error messages."""
    with patch("backend.cloud_storage._get_secret", return_value="super_secret_b2_key_12345"), \
         patch("backend.cloud_storage._get_key_id", return_value="b2_app_key_id_9876"), \
         patch("boto3.client", side_effect=Exception("B2 failed with secret_key super_secret_b2_key_12345")):
         
        # Trigger cloud backup manually which will fail
        with patch("backend.cloud_storage.is_configured", return_value=True):
            res = cloud_storage.run_backup()
            # Local fallback is expected, verify no keys are leaked
            assert "super_secret_b2_key" not in res["message"]


# ---------------------------------------------------------------------------
# Business Transactions & Integrity checks
# ---------------------------------------------------------------------------

def test_wms_transaction_and_reservations_remain_correct(client, db, admin_token, setup_wms_data):
    """Test that WMS transaction commits and inventory reservations remain 100% accurate."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Mock all external notifications to fail/timeout
    with patch("backend.mq_client.publish_event", return_value=False), \
         patch("backend.celery_app.send_resend_email_task.delay", side_effect=Exception("Broker offline")), \
         patch("backend.notifications.send_email_alert", return_value=False):
         
        db.expire_all()
        inv_before = db.query(Inventory).filter(Inventory.warehouse_id == "WH-RES-01", Inventory.item_id == "ITM-RES-01").first()
        initial_avail = inv_before.available
        initial_res = inv_before.reserved
        
        payload = {
            "warehouse_id": "WH-RES-01",
            "customer_ref": "Integrity Cust",
            "items": [
                {"item_id": "ITM-RES-01", "requested_qty": 3}
            ]
        }
        
        response = client.post("/wms/orders", json=payload, headers=headers)
        assert response.status_code == 201
        
        db.expire_all()
        inv_after = db.query(Inventory).filter(Inventory.warehouse_id == "WH-RES-01", Inventory.item_id == "ITM-RES-01").first()
        assert inv_after.reserved == initial_res + 3
        assert inv_after.available == initial_avail - 3
        
        # Verify AuditLedger recorded the order creation successfully
        audit = db.query(AuditLedger).filter(AuditLedger.event_type == "ORDER_CREATED").order_by(AuditLedger.id.desc()).first()
        assert audit is not None
        assert json.loads(audit.details)["order_id"] == response.json()["order_id"]
