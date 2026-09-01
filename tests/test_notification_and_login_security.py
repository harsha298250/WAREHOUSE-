"""
test_notification_and_login_security.py — Unit and integration tests for
Notification UI solid background, Login Security Audit Metadata, IP/Device parsing,
and Audit Ledger event generation.
"""
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services import security_service
from backend.database import get_db

client = TestClient(app)


def test_device_info_parsing():
    """Verify User-Agent parsing extracts device, OS, browser, and version."""
    ua_windows_chrome = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    info = security_service.get_device_info(ua_windows_chrome)
    assert info["device"] == "Desktop"
    assert info["os"] == "Windows"
    assert info["browser"] == "Chrome"
    assert info["version"] == "128.0.0.0"

    ua_mobile_safari = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1"
    info2 = security_service.get_device_info(ua_mobile_safari)
    assert info2["device"] == "Mobile"
    assert info2["os"] == "iOS"
    assert info2["browser"] == "Safari"


def test_ip_extraction_and_geolocation():
    """Verify trusted client IP extraction behind reverse proxy and non-blocking geolocation."""
    class DummyRequest:
        headers = {"x-forwarded-for": "203.0.113.195, 10.0.0.1", "user-agent": "TestAgent"}
    
    ip = security_service.get_client_ip(DummyRequest())
    assert ip == "203.0.113.195"

    loc = security_service.get_approximate_location_details("127.0.0.1")
    assert loc["formatted"] == "Location unavailable"


def test_login_audit_and_notification_generation(db):
    """Verify login creates structured USER_LOGIN_SUCCESS event & notification without exposing secrets."""
    response = client.post("/auth/login", json={"username": "admin", "password": "AdminPassword123!"})
    assert response.status_code == 200
    assert "access_token" in response.json()

    # Query Audit Ledger for USER_LOGIN_SUCCESS
    from backend.models import AuditLedger, Notification
    entry = db.query(AuditLedger).filter(AuditLedger.event_type == "USER_LOGIN_SUCCESS").order_by(AuditLedger.id.desc()).first()
    assert entry is not None
    assert "admin" in entry.details
    assert "password" not in entry.details.lower() or '"auth_method": "password"' in entry.details
    assert "AdminPassword123!" not in entry.details

    # Query Notification
    notif = db.query(Notification).filter(Notification.event_type == "USER_LOGIN_SUCCESS").order_by(Notification.id.desc()).first()
    assert notif is not None
    assert notif.notification_type == "SECURITY_ALERT"
    assert "logged in successfully" in notif.message


def test_failed_login_audit(db):
    """Verify failed login generates USER_LOGIN_FAILED event without logging invalid password."""
    response = client.post("/auth/login", json={"username": "admin", "password": "WrongPassword123!"})
    assert response.status_code == 401

    from backend.models import AuditLedger
    entry = db.query(AuditLedger).filter(AuditLedger.event_type == "USER_LOGIN_FAILED").order_by(AuditLedger.id.desc()).first()
    assert entry is not None
    assert "WrongPassword123!" not in entry.details
    assert "invalid_credentials" in entry.details
