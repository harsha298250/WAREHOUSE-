import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend import redis_client
from backend import mq_client
from backend import resend_client

client = TestClient(app)

def test_prometheus_metrics_endpoint():
    """Verify that the /metrics endpoint is exposed and returns Prometheus metric formats."""
    res = client.get("/metrics")
    assert res.status_code == 200
    assert "http_requests_total" in res.text
    assert "database_pool_size" in res.text


def test_health_integrations_endpoint():
    """Verify that `/health/integrations` runs and returns structured JSON connectivity details."""
    res = client.get("/health/integrations")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ("healthy", "degraded", "unavailable", "not_configured")
    assert "integrations" in data
    
    integs = data["integrations"]
    for key in ("redis", "rabbitmq", "celery", "resend", "sentry", "gemini"):
        assert key in integs
        assert "status" in integs[key]
        assert "connected" in integs[key]


def test_redis_graceful_fallback():
    """Test that Redis client wrapper returns None and skips operations when offline without throwing exceptions."""
    # Force client to None
    original_client = redis_client._client
    original_state = redis_client.redis_available
    
    redis_client._client = None
    redis_client.redis_available = False
    
    try:
        # Should gracefully return None and not raise exceptions
        assert redis_client.get_cache("some_test_key") is None
        assert redis_client.set_cache("some_test_key", "value") is False
        assert redis_client.delete_cache("some_test_key") is False
    finally:
        redis_client._client = original_client
        redis_client.redis_available = original_state


def test_rabbitmq_graceful_fallback():
    """Test that RabbitMQ event publisher logs warning and returns False when offline instead of crashing."""
    original_channel = mq_client._channel
    original_conn = mq_client._connection
    original_state = mq_client.mq_available
    
    mq_client._channel = None
    mq_client._connection = None
    mq_client.mq_available = False
    
    try:
        # Should return False and degrade gracefully
        res = mq_client.publish_event(
            event_type="TEST_EVENT", 
            category="system", 
            payload={"test": "data"}
        )
        assert res is False
    finally:
        mq_client._channel = original_channel
        mq_client._connection = original_conn
        mq_client.mq_available = original_state


def test_resend_email_client_mock():
    """Verify that Resend email client falls back to logging mock delivery if API key is not present."""
    original_key = resend_client.RESEND_API_KEY
    resend_client.RESEND_API_KEY = ""
    
    try:
        res = resend_client.send_html_email(
            subject="Test Alert OTP [123456]", 
            body="Your code is 123456", 
            recipient="test@example.com"
        )
        assert res is True  # Mock delivery returns True
    finally:
        resend_client.RESEND_API_KEY = original_key


def test_ai_assistant_offline_mode(db, admin_token):
    """Test that AI Assistant route resolves requests successfully even in offline mode (using mock responses)."""
    from unittest.mock import patch
    from backend.models import Warehouse
    
    # Ensure warehouse exists
    wh = db.query(Warehouse).filter(Warehouse.id == "WH-BLR-01").first()
    if not wh:
        wh = Warehouse(id="WH-BLR-01", name="Bangalore Hub", location="BLR")
        db.add(wh)
        db.commit()

    headers = {"Authorization": f"Bearer {admin_token}"}
    
    with patch("backend.services.ai_service.GEMINI_API_KEY", ""):
        # Test stockout query
        res = client.post("/ai/assistant", json={
            "message": "Is there any stockout risk for ITM-CPU-01?",
            "warehouse_id": "WH-BLR-01"
        }, headers=headers)
        assert res.status_code == 200
        assert "ITM-CPU-01" in res.json()["response"]
        
        # Test fleet query
        res_robot = client.post("/ai/assistant", json={
            "message": "Tell me about the robot fleet",
            "warehouse_id": "WH-BLR-01"
        }, headers=headers)
        assert res_robot.status_code == 200
        assert "robot" in res_robot.json()["response"].lower()


def test_ortools_scheduler_route(db, admin_token):
    """Test that OR-Tools route operates and outputs heuristics and solver latency details."""
    from backend.models import Warehouse
    
    # Ensure warehouse exists
    wh = db.query(Warehouse).filter(Warehouse.id == "WH-BLR-01").first()
    if not wh:
        wh = Warehouse(id="WH-BLR-01", name="Bangalore Hub", location="BLR")
        db.add(wh)
        db.commit()

    headers = {"Authorization": f"Bearer {admin_token}"}
    
    res = client.get("/ai/optimize-scheduler?warehouse_id=WH-BLR-01", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ("success", "skipped")
    if data["status"] == "success":
        assert "metrics" in data
        metrics = data["metrics"]

        assert "heuristic" in metrics
        assert "ortools_optimized" in metrics
        assert "improvement_pct" in metrics
