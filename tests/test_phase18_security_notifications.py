"""
tests/test_phase18_security_notifications.py — Phase 18 Enterprise Security Alerts and Monitoring tests.
"""
import pytest
from datetime import datetime, timedelta, UTC
from fastapi import HTTPException
from sqlalchemy.orm import Session
from backend.models import User, SecurityEvent, AuditLedger, OTPRecord
from backend.services import security_service
from backend.routers.auth import _create_db_otp, _verify_db_otp


class TestPhase18SecurityAlerts:

    # ----------------------------------------------------
    # OTP verification tests
    # ----------------------------------------------------

    def test_otp_generation_and_verification(self, db):
        """OTP must be generated, saved in DB, and single-use."""
        # Find or seed user
        user = db.query(User).filter(User.username == "test_admin").first()
        assert user is not None

        # Generate OTP
        otp_code = _create_db_otp(db, user, "LOGIN_OTP", "127.0.0.1")
        assert len(otp_code) == 6
        assert otp_code.isdigit()

        # Retrieve record and check details
        record = db.query(OTPRecord).filter(OTPRecord.user_id == user.id, OTPRecord.purpose == "LOGIN_OTP").order_by(OTPRecord.id.desc()).first()
        assert record is not None
        assert record.consumed_at is None

        # Verify successfully
        result = _verify_db_otp(db, user, "LOGIN_OTP", otp_code)
        assert result.consumed_at is not None

        # Double consumption must fail
        with pytest.raises(HTTPException) as excinfo:
            _verify_db_otp(db, user, "LOGIN_OTP", otp_code)
        assert excinfo.value.status_code == 400
        assert "no pending" in excinfo.value.detail.lower()

    def test_otp_expiry(self, db):
        """Expired OTP must be rejected."""
        user = db.query(User).filter(User.username == "test_admin").first()
        otp_code = _create_db_otp(db, user, "LOGIN_OTP", "127.0.0.1")

        # Force expiry in database
        record = db.query(OTPRecord).filter(OTPRecord.user_id == user.id, OTPRecord.purpose == "LOGIN_OTP").order_by(OTPRecord.id.desc()).first()
        record.expires_at = datetime.now(UTC).replace(tzinfo=None) - timedelta(seconds=1)
        db.commit()

        # Verification must fail
        with pytest.raises(HTTPException) as excinfo:
            _verify_db_otp(db, user, "LOGIN_OTP", otp_code)
        assert excinfo.value.status_code == 400
        assert "expired" in excinfo.value.detail.lower()

    def test_otp_brute_force_protection(self, db):
        """OTP verification fails after max incorrect attempts."""
        user = db.query(User).filter(User.username == "test_admin").first()
        otp_code = _create_db_otp(db, user, "LOGIN_OTP", "127.0.0.1")

        # Attempt with wrong codes
        for _ in range(5):
            with pytest.raises(HTTPException):
                _verify_db_otp(db, user, "LOGIN_OTP", "000000")

        # Now attempting with correct code must fail as maximum attempts exceeded
        with pytest.raises(HTTPException) as excinfo:
            _verify_db_otp(db, user, "LOGIN_OTP", otp_code)
        assert excinfo.value.status_code == 400
        assert "exceeded" in excinfo.value.detail.lower()

    # ----------------------------------------------------
    # SecurityEvent Creation and Retrieval
    # ----------------------------------------------------

    def test_security_event_persisted(self, db):
        """Creating a security event must persist in DB and append to AuditLedger."""
        user = db.query(User).filter(User.username == "test_admin").first()
        
        event = security_service.create_security_event(
            db=db,
            event_type="LOGIN_SUCCESS",
            severity="INFO",
            status="SUCCESS",
            actor_user_id=user.id,
            actor_username=user.username,
            authentication_method="password",
            ip_address="127.0.0.1",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            extra_details={"test": "ok"},
        )

        assert event is not None
        assert event.id is not None
        assert event.device == "Desktop"
        assert event.browser == "Other/Unknown"
        assert event.os == "Windows"

        # Check AuditLedger linkage
        assert event.audit_ledger_ref is not None
        audit = db.query(AuditLedger).filter(AuditLedger.id == event.audit_ledger_ref).first()
        assert audit is not None
        assert audit.event_type == "login_success"

    def test_device_info_parser(self):
        """User-agent string parser must return correct OS/Browser/Device categories."""
        # Desktop Chrome
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        res = security_service.get_device_info(ua)
        assert res["device"] == "Desktop"
        assert res["os"] == "Windows"
        assert res["browser"] == "Chrome"

        # Mobile Safari
        ua_mobile = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
        res_mobile = security_service.get_device_info(ua_mobile)
        assert res_mobile["device"] == "Mobile"
        assert res_mobile["os"] == "iOS"
        assert res_mobile["browser"] == "Safari"

        # Curl / script
        ua_curl = "curl/7.81.0"
        res_curl = security_service.get_device_info(ua_curl)
        assert res_curl["device"] == "Unknown"
        assert res_curl["browser"] == "Other/Unknown"

    # ----------------------------------------------------
    # Router endpoints integration tests
    # ----------------------------------------------------

    def test_login_success_event_logged(self, client, db):
        """Successful login must log a LOGIN_SUCCESS security event."""
        # Standard login
        r = client.post("/auth/login", json={"username": "test_viewer", "password": "TestViewer@123"})
        assert r.status_code == 200

        # Query database for recent security events
        events = db.query(SecurityEvent).filter(SecurityEvent.event_type == "LOGIN_SUCCESS").order_by(SecurityEvent.id.desc()).all()
        assert len(events) > 0
        assert events[0].actor_username == "test_viewer"
        assert events[0].severity == "INFO"

    def test_login_failed_event_logged(self, client, db):
        """Failed login must log a LOGIN_FAILED security event."""
        # Failed login attempt
        r = client.post("/auth/login", json={"username": "test_viewer", "password": "WrongPassword"})
        assert r.status_code == 401

        # Query database
        events = db.query(SecurityEvent).filter(SecurityEvent.event_type == "LOGIN_FAILED").order_by(SecurityEvent.id.desc()).all()
        assert len(events) > 0
        assert events[0].actor_username == "test_viewer"
        assert events[0].severity == "WARNING"
        assert events[0].status == "FAILED"

    def test_login_otp_enforce_disabled_by_default(self, client):
        """By default, LOGIN_OTP_REQUIRED is false and login returns token directly."""
        security_service.LOGIN_OTP_REQUIRED = False
        r = client.post("/auth/login", json={"username": "test_viewer", "password": "TestViewer@123"})
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert data.get("status") != "otp_required"

    def test_login_otp_enforce_flow(self, client, db):
        """If LOGIN_OTP_REQUIRED is true, login returns otp_required, then verification yields token."""
        security_service.LOGIN_OTP_REQUIRED = True
        try:
            r = client.post("/auth/login", json={"username": "test_viewer", "password": "TestViewer@123"})
            assert r.status_code == 200
            data = r.json()
            assert data.get("status") == "otp_required"
            assert "expires_in_seconds" in data
            
            # Fetch latest OTP from database for this user
            user = db.query(User).filter(User.username == "test_viewer").first()
            otp_record = db.query(OTPRecord).filter(OTPRecord.user_id == user.id, OTPRecord.purpose == "LOGIN_OTP").order_by(OTPRecord.id.desc()).first()
            assert otp_record is not None

            # Now verify OTP
            # First, check that incorrect OTP is rejected
            r_fail = client.post("/auth/verify-login-otp", json={"username": "test_viewer", "otp_code": "000000"})
            assert r_fail.status_code == 400

            # Generate new one since verify consumes/marks it
            otp_code = _create_db_otp(db, user, "LOGIN_OTP", "127.0.0.1")
            
            r_verify = client.post("/auth/verify-login-otp", json={"username": "test_viewer", "otp_code": otp_code})
            assert r_verify.status_code == 200
            verify_data = r_verify.json()
            assert "access_token" in verify_data
            assert verify_data["username"] == "test_viewer"
        finally:
            security_service.LOGIN_OTP_REQUIRED = False

    def test_role_change_event_logged(self, client, admin_token, db):
        """Role change must write ROLE_CHANGED security event."""
        # Find viewer ID
        viewer = db.query(User).filter(User.username == "test_viewer").first()
        
        # Change role to manager
        r = client.put(f"/users/{viewer.id}/role",
                       json={"role": "manager", "reason": "promotion", "confirm_password": "TestAdmin@123"},
                       headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200

        # Query security event
        event = db.query(SecurityEvent).filter(SecurityEvent.event_type == "ROLE_CHANGED").order_by(SecurityEvent.id.desc()).first()
        assert event is not None
        assert event.actor_username == "test_admin"
        assert event.target_username == "test_viewer"
        assert event.previous_value == "viewer"
        assert event.new_value == "manager"
        assert event.severity == "CRITICAL"

        # Revert role
        viewer.role = "viewer"
        db.commit()

    def test_activate_deactivate_logged(self, client, admin_token, db):
        """Account activate and deactivate must write security events."""
        viewer = db.query(User).filter(User.username == "test_viewer").first()

        # Deactivate
        r = client.put(f"/users/{viewer.id}/deactivate", headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200
        
        event = db.query(SecurityEvent).filter(SecurityEvent.event_type == "ACCOUNT_DEACTIVATED").order_by(SecurityEvent.id.desc()).first()
        assert event is not None
        assert event.target_username == "test_viewer"
        assert event.severity == "CRITICAL"

        # Activate
        r = client.put(f"/users/{viewer.id}/activate", headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200
        
        event2 = db.query(SecurityEvent).filter(SecurityEvent.event_type == "ACCOUNT_ACTIVATED").order_by(SecurityEvent.id.desc()).first()
        assert event2 is not None
        assert event2.target_username == "test_viewer"
        assert event2.severity == "INFO"

    # ----------------------------------------------------
    # Security events list, permissions & my-activity
    # ----------------------------------------------------

    def test_security_events_permissions(self, client, admin_token, db):
        """Only users with VIEW_SECURITY permission can fetch security/events/rich."""
        # Create unprivileged viewer user
        from backend.auth import hash_password
        unprivileged = db.query(User).filter(User.username == "unprivileged_viewer").first()
        if not unprivileged:
            unprivileged = User(
                username="unprivileged_viewer",
                password_hash=hash_password("Unprivileged@123"),
                role="viewer"
            )
            db.add(unprivileged)
            db.commit()
            db.refresh(unprivileged)

        # Login to get unprivileged token
        r_login = client.post("/auth/login", json={"username": "unprivileged_viewer", "password": "Unprivileged@123"})
        assert r_login.status_code == 200
        unprivileged_token = r_login.json()["access_token"]

        # Viewer (unauthorized)
        r_view = client.get("/security/events/rich", headers={"Authorization": f"Bearer {unprivileged_token}"})
        assert r_view.status_code == 403

        # Admin (authorized)
        r_admin = client.get("/security/events/rich", headers={"Authorization": f"Bearer {admin_token}"})
        assert r_admin.status_code == 200

    def test_my_activity_is_public(self, client, viewer_token):
        """Any authenticated user can fetch their own activity."""
        r = client.get("/security/my-activity", headers={"Authorization": f"Bearer {viewer_token}"})
        assert r.status_code == 200
        data = r.json()
        assert data["username"] == "test_viewer"
        assert "events" in data

    def test_security_summary(self, client, admin_token):
        """Security summary widget endpoint must return statistics."""
        r = client.get("/security/summary", headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200
        data = r.json()
        assert "available" in data
        if data["available"]:
            assert "logins_24h" in data
            assert "failed_attempts_24h" in data
            assert "critical_events_7d" in data
            assert "recent_events" in data

    def test_login_security_notification_and_location(self, client, db):
        """Test that geolocation IP mapping, device parsing, and email alerts trigger correctly without failing login."""
        from unittest.mock import patch
        import os
        
        # Test that geolocator mock functions correctly
        with patch("httpx.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {
                "status": "success",
                "country": "India",
                "regionName": "Karnataka",
                "city": "Bengaluru"
            }
            
            location = security_service.get_approximate_location("8.8.8.8")
            assert location == "Bengaluru, Karnataka, India"
            
            # Check local subnet bypasses geolocation look-up
            local_loc = security_service.get_approximate_location("127.0.0.1")
            assert local_loc == "Location unavailable"
            
        # Test login triggers email alerts, and SMTP failures do NOT block standard login
        # We mock send_email_alert to fail (return False) and set CELERY_ENABLED to false
        with patch.dict(os.environ, {"CELERY_ENABLED": "false"}), \
             patch("backend.notifications.send_email_alert", return_value=False) as mock_send_email:

            r = client.post("/auth/login", json={"username": "test_viewer", "password": "TestViewer@123"})
            assert r.status_code == 200
            assert "access_token" in r.json()
            
            # Email send was attempted
            assert mock_send_email.called
            
            # Verify the security event was logged in the DB
            event = db.query(SecurityEvent).filter(
                SecurityEvent.actor_username == "test_viewer",
                SecurityEvent.event_type == "LOGIN_SUCCESS"
            ).order_by(SecurityEvent.id.desc()).first()
            
            assert event is not None
            assert event.status == "SUCCESS"
            assert event.ip_address is not None


