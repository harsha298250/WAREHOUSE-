import pytest
import time
import os
import shutil
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime, timezone

from backend.database import SessionLocal, engine
from backend.models import User, RecoveryCredential, RecoveryCode, BackupRecord
from backend.cloud_storage import run_disaster_recovery_backup
from backend.routers.auth import _recovery_attempts


def test_recovery_setup_and_login(client, db, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Clear recovery tables for test_admin
    user = db.query(User).filter(User.username == "test_admin").first()
    db.query(RecoveryCredential).filter(RecoveryCredential.user_id == user.id).delete()
    db.query(RecoveryCode).filter(RecoveryCode.user_id == user.id).delete()
    db.commit()

    # 1. Recovery setup
    setup_payload = {
        "password": "my_recovery_password_123",
        "generate_codes": True
    }
    r = client.post("/auth/recovery-setup", json=setup_payload, headers=headers)
    assert r.status_code == 200
    res = r.json()
    assert res["status"] == "success"
    codes = res["recovery_codes"]
    assert len(codes) == 8

    # 2. Login with recovery password
    login_payload = {
        "username": "test_admin",
        "password_or_code": "my_recovery_password_123"
    }
    r_login = client.post("/auth/recovery-login", json=login_payload)
    assert r_login.status_code == 200
    assert "access_token" in r_login.json()
    assert r_login.json()["auth_mode"] == "account_recovery"

    # 3. Login with recovery code
    code_to_use = codes[0]
    login_payload_code = {
        "username": "test_admin",
        "password_or_code": code_to_use
    }
    r_login_code = client.post("/auth/recovery-login", json=login_payload_code)
    assert r_login_code.status_code == 200
    assert "access_token" in r_login_code.json()

    # 4. Try using the same code again (must fail)
    r_login_code_second = client.post("/auth/recovery-login", json=login_payload_code)
    assert r_login_code_second.status_code == 401
    assert "Invalid recovery credentials" in r_login_code_second.json()["detail"]


def test_recovery_login_invalid_credentials(client):
    login_payload = {
        "username": "test_admin",
        "password_or_code": "wrong_recovery_code_or_pass"
    }
    r = client.post("/auth/recovery-login", json=login_payload)
    assert r.status_code == 401


def test_recovery_rate_limiting(client):
    from unittest.mock import patch
    _recovery_attempts.clear()
    login_payload = {
        "username": "test_admin",
        "password_or_code": "invalid_attempt"
    }
    
    with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
        # Trigger 5 failed attempts
        for _ in range(5):
            r = client.post("/auth/recovery-login", json=login_payload)
            assert r.status_code in [401, 429]

        # 6th attempt must be blocked by rate limiter
        r_blocked = client.post("/auth/recovery-login", json=login_payload)
        assert r_blocked.status_code == 429
        assert "Too many recovery login attempts" in r_blocked.json()["detail"]
        _recovery_attempts.clear()


@patch("backend.cloud_storage.is_configured", return_value=True)
def test_backup_success_flow(mock_is_configured, db):
    # Set dummy backup key (must be a valid base64 key for Fernet)
    os.environ["BACKUP_ENCRYPTION_KEY"] = "VDFDVkRVVkRVVkRVVkRVVkRVVkRVVkRVVkRVVkRVVkQ="

    # Clean existing records
    db.query(BackupRecord).delete()
    db.commit()

    with patch("boto3.client") as mock_boto:
        mock_s3 = MagicMock()
        mock_boto.return_value = mock_s3
        # Mock head check size metadata
        mock_s3.head_object.return_value = {"ContentLength": 100}

        # Run backup (SQLite format as active during testing)
        with patch("os.path.getsize", return_value=100):
            res = run_disaster_recovery_backup(db)
            assert res["status"] in ("SUCCESS", "UPLOADED")
            assert "backup_id" in res
            assert "sha256" in res
            
            # Check DB metadata registry
            db_record = db.query(BackupRecord).filter(BackupRecord.backup_id == res["backup_id"]).first()
            assert db_record is not None
            assert db_record.status in ("SUCCESS", "UPLOADED")
            assert db_record.sha256 == res["sha256"]
            assert db_record.size_bytes == 100


@patch("backend.cloud_storage.is_configured", return_value=True)
def test_backup_upload_failure_handling(mock_is_configured, db):
    os.environ["BACKUP_ENCRYPTION_KEY"] = "VDFDVkRVVkRVVkRVVkRVVkRVVkRVVkRVVkRVVkRVVkQ="

    db.query(BackupRecord).delete()
    db.commit()

    with patch("boto3.client") as mock_boto:
        mock_s3 = MagicMock()
        mock_boto.return_value = mock_s3
        # Simulate upload error
        mock_s3.upload_fileobj.side_effect = Exception("Backblaze authentication timeout")

        with patch("os.path.getsize", return_value=120):
            res = run_disaster_recovery_backup(db)
            assert res["status"] == "FAILED"
            assert "B2 Upload failed" in res["message"]

            db_record = db.query(BackupRecord).filter(BackupRecord.backup_id == res["backup_id"]).first()
            assert db_record is not None
            assert db_record.status == "FAILED"
            assert "B2 Upload failed" in db_record.error_message


def test_scheduler_resilience_on_exception(db):
    # Verify that calling backup triggers error inside loop cleanly
    from backend.main import schedule_backups_worker
    from backend.models import AuditLedger
    
    # Clean any pre-existing auto-backup ledger entries to prevent cross-test contamination
    db.query(AuditLedger).filter(AuditLedger.event_type == "auto_cloud_backup").delete()
    db.commit()
    
    with patch.dict(os.environ, {"CELERY_ENABLED": "false"}):
        with patch("backend.cloud_storage.run_disaster_recovery_backup", side_effect=Exception("Database lock error")) as mock_run:
            with patch("backend.main.BACKUP_WORKER_STOP_EVENT.wait", side_effect=[False, True]) as mock_wait:
                schedule_backups_worker()
                
                # Ensure the worker attempted to trigger backup
                assert mock_run.called

