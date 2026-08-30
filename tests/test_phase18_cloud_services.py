"""
tests/test_phase18_cloud_services.py — Phase 18 Cloud Services, Infrastructure & Celery verification tests.
"""
import os
import json
import pytest
from datetime import datetime, UTC
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from sqlalchemy.orm import Session
from backend.models import BackupRecord, User, SecurityEvent
from backend import redis_client
from backend.services import security_service
from backend.routers.auth import check_login_rate_limit, check_recovery_rate_limit
from backend.sentry import sanitize_event_data
from backend import cloud_storage


class TestPhase18CloudServices:

    # ----------------------------------------------------
    # Redis Integration & Rate Limiting
    # ----------------------------------------------------

    def test_redis_offline_graceful_bypass(self, monkeypatch):
        """Test 21: Redis client can connect when offline gracefully bypasses."""
        # Force get_redis_client to return None
        monkeypatch.setattr(redis_client, "get_redis_client", lambda: None)
        
        # Operations must not crash, must return safe fallbacks
        assert redis_client.get_cache("test_key") is None
        assert redis_client.set_cache("test_key", "val") is False
        assert redis_client.delete_cache("test_key") is False

    def test_redis_otp_temporary_state(self, monkeypatch):
        """Test 22: Redis OTP temporary state uses correct TTL and namespaces."""
        mock_redis = MagicMock()
        mock_pipeline = MagicMock()
        mock_redis.pipeline.return_value = mock_pipeline
        mock_redis.get.return_value = None
        
        monkeypatch.setattr(redis_client, "get_redis_client", lambda: mock_redis)
        
        # Verify check_otp_rate_limit sets correct keys and TTL
        res = security_service.check_otp_rate_limit(user_id=123)
        assert res is True
        
        mock_redis.get.assert_called_with("otp:ratelimit:123")
        mock_pipeline.incr.assert_called_with("otp:ratelimit:123")
        mock_pipeline.expire.assert_called_with("otp:ratelimit:123", 3600)
        mock_pipeline.execute.assert_called_once()

    def test_login_rate_limiting_redis(self, monkeypatch):
        """Test 23: Login rate limiting (Redis increment and fallback)."""
        mock_redis = MagicMock()
        mock_redis.get.return_value = "5" # LOGIN_RATE_LIMIT is usually 5
        
        monkeypatch.setattr(redis_client, "get_redis_client", lambda: mock_redis)
        monkeypatch.setenv("ENVIRONMENT", "production")
        
        with pytest.raises(HTTPException) as excinfo:
            check_login_rate_limit("192.168.1.100")
        assert excinfo.value.status_code == 429
        assert "too many login attempts" in excinfo.value.detail.lower()

    def test_otp_rate_limiting(self, monkeypatch):
        """Test 24: OTP rate limiting triggers when limit exceeded."""
        mock_redis = MagicMock()
        # Mocking exceeding hourly limit
        mock_redis.get.return_value = str(security_service.OTP_RATE_LIMIT_PER_HOUR + 1)
        
        monkeypatch.setattr(redis_client, "get_redis_client", lambda: mock_redis)
        
        res = security_service.check_otp_rate_limit(user_id=123)
        assert res is False

    def test_api_rate_limiting_recovery(self, monkeypatch):
        """Test 25: API rate limiting recovery checks."""
        mock_redis = MagicMock()
        mock_redis.get.return_value = "10" # EXCEEDS LIMIT
        
        monkeypatch.setattr(redis_client, "get_redis_client", lambda: mock_redis)
        monkeypatch.setenv("ENVIRONMENT", "production")
        
        with pytest.raises(HTTPException) as excinfo:
            check_recovery_rate_limit("192.168.1.100")
        assert excinfo.value.status_code == 429
        assert "too many recovery login attempts" in excinfo.value.detail.lower()

    # ----------------------------------------------------
    # RabbitMQ & Celery Configuration
    # ----------------------------------------------------

    def test_rabbitmq_broker_setup(self):
        """Test 27: Verify RabbitMQ Connection string and initialization parameters."""
        from backend import mq_client
        assert mq_client.RABBITMQ_URL is not None
        # Should not crash on status checking
        status = mq_client.check_rabbitmq_health()
        assert "status" in status

    def test_celery_background_worker_config(self):
        """Test 28: Celery background worker configuration and task execution."""
        from backend.celery_app import celery
        assert celery.conf.task_serializer == "json"
        assert celery.conf.result_serializer == "json"
        assert "json" in celery.conf.accept_content
        assert celery.conf.timezone == "UTC"

    # ----------------------------------------------------
    # Sentry Sanitization & Monitoring
    # ----------------------------------------------------

    def test_sentry_fastapi_integration(self):
        """Test 29: Sentry FastAPI integration config presence."""
        from backend.sentry import init_sentry
        # Initialization shouldn't raise exception
        init_sentry()

    def test_sentry_sensitive_scrub_mask(self):
        """Test 31: Sentry sensitive scrub mask (passwords/tokens/OTPs/keys)."""
        # Formulate mock sentry event dict containing sensitive values
        event = {
            "request": {
                "headers": {
                    "authorization": "Bearer secret_jwt_token_123",
                    "cookie": "session=xyz123",
                    "content-type": "application/json"
                },
                "data": {
                    "username": "user1",
                    "password": "my_super_secret_password",
                    "otp_code": "123456",
                    "secret_key": "somekey"
                }
            },
            "exception": {
                "values": [
                    {
                        "stacktrace": {
                            "frames": [
                                {
                                    "vars": {
                                        "user_password": "sensitive_password_local_variable",
                                        "my_token": "tokeninfo",
                                        "safe_var": 42
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }
        
        scrubbed_event = sanitize_event_data(event, hint=None)
        
        # Verify request headers are scrubbed
        headers = scrubbed_event["request"]["headers"]
        assert headers["authorization"] == "[SCRUBBED]"
        assert headers["cookie"] == "[SCRUBBED]"
        assert headers["content-type"] == "application/json"
        
        # Verify request body values are scrubbed
        data = scrubbed_event["request"]["data"]
        assert data["username"] == "user1"
        assert data["password"] == "[SCRUBBED]"
        assert data["otp_code"] == "[SCRUBBED]"
        assert data["secret_key"] == "[SCRUBBED]"
        
        # Verify stacktrace local variables are scrubbed
        vars_dict = scrubbed_event["exception"]["values"][0]["stacktrace"]["frames"][0]["vars"]
        assert vars_dict["user_password"] == "[SCRUBBED]"
        assert vars_dict["my_token"] == "[SCRUBBED]"
        assert vars_dict["safe_var"] == 42

    # ----------------------------------------------------
    # Backblaze B2 & Backup Workflows
    # ----------------------------------------------------

    def test_b2_cloud_backup_routine(self, db):
        """Test 32: B2 cloud backup routine gracefully executes/falls back."""
        # Execute disaster recovery backup
        res = cloud_storage.run_disaster_recovery_backup(db, backup_type="TEST_RUN", initiated_by="test_admin")
        
        # Backup must register in database and return correct keys
        assert res["status"] in ("UPLOADED", "SUCCESS", "FAILED")
        assert res["backup_id"].startswith("BK-")
        
        # Check record in database
        rec = db.query(BackupRecord).filter(BackupRecord.backup_id == res["backup_id"]).first()
        assert rec is not None
        assert rec.backup_type == "TEST_RUN"
        assert rec.initiated_by == "test_admin"

    def test_b2_backup_verification_job(self, db):
        """Test 33: B2 backup verification job verification."""
        # Create a mock database record
        rec = BackupRecord(
            backup_id="BK-MOCK-VERIFY",
            filename="mock_backup.sql.gz",
            status="SUCCESS",
            sha256="810ff2fb242a5dee4220f2cb0e6a519891fb67f2f828a6cab4ef8894633b1f50", # sha256 for b"testdata"
            storage_provider="Local Fallback",
            storage_key="data/backups/mock_backup.sql.gz",
            bucket="local-backups"
        )
        db.add(rec)
        db.commit()

        # Write dummy file to backups directory to verify
        backup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "backups")
        os.makedirs(backup_dir, exist_ok=True)
        file_path = os.path.join(backup_dir, "mock_backup.sql.gz")
        with open(file_path, "wb") as f:
            f.write(b"testdata")

        try:
            res = cloud_storage.verify_backup_integrity(db, "BK-MOCK-VERIFY")
            assert res["status"] == "SUCCESS"
            
            # Check DB updated status
            db.refresh(rec)
            assert rec.verification_status == "VERIFIED"
            assert rec.status == "VERIFIED"
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    def test_isolated_sqlite_restore_test_dryrun(self, db):
        """Test 34: Isolated SQLite restore test dry-run."""
        import gzip
        
        # Mock gzip SQL dump contents
        sql_content = """
        CREATE TABLE dummy_restore (id INTEGER PRIMARY KEY, val TEXT);
        INSERT INTO dummy_restore (id, val) VALUES (1, 'hello');
        """
        compressed = gzip.compress(sql_content.encode("utf-8"))
        import hashlib
        checksum = hashlib.sha256(compressed).hexdigest()

        rec = BackupRecord(
            backup_id="BK-MOCK-RESTORE",
            filename="mock_restore.sql.gz",
            status="SUCCESS",
            sha256=checksum,
            storage_provider="Local Fallback",
            storage_key="data/backups/mock_restore.sql.gz",
            bucket="local-backups"
        )
        db.add(rec)
        db.commit()

        backup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "backups")
        os.makedirs(backup_dir, exist_ok=True)
        file_path = os.path.join(backup_dir, "mock_restore.sql.gz")
        with open(file_path, "wb") as f:
            f.write(compressed)

        try:
            res = cloud_storage.run_backup_restore_test(db, "BK-MOCK-RESTORE")
            assert res["status"] == "SUCCESS"
            
            db.refresh(rec)
            assert rec.restore_test_status == "SUCCESS"
            assert rec.status == "RESTORE_TESTED"
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    # ----------------------------------------------------
    # Health Integrations Endpoint
    # ----------------------------------------------------

    def test_system_health_integrations_endpoint(self, client, admin_token):
        """Test 35: System health integrations endpoint matches expected components."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        r = client.get("/health/integrations", headers=headers)
        assert r.status_code == 200
        
        data = r.json()
        assert "integrations" in data
        integrations = data["integrations"]
        
        assert "redis" in integrations
        assert "rabbitmq" in integrations
        assert "celery" in integrations
        assert "resend" in integrations
        assert "sentry" in integrations
        assert "gemini" in integrations
        assert "backups" in integrations
        assert "oauth" in integrations
        assert "render" in integrations
