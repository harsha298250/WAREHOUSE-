"""
Phase 11 — Backup, Disaster Recovery & Reliability Tests.

Validates:
- BackupRecord model creation with extended metadata columns
- SHA-256 checksum generation and verification logic
- Isolated restore-test dry-run in temporary SQLite database
- RBAC enforcement on backup API endpoints
"""
import pytest
import os
import secrets
import hashlib
from datetime import datetime, UTC

from backend.models import BackupRecord, User
from backend import cloud_storage


def test_backup_metadata_creation(db):
    """Test that a backup record is properly initialized in database with extended columns."""
    backup_id = f"TEST-{secrets.token_hex(4).upper()}"
    rec = BackupRecord(
        backup_id=backup_id,
        filename=f"backup_{backup_id}.sql.gz",
        status="RUNNING",
        started_at=datetime.now(UTC).replace(tzinfo=None),
        backup_type="MANUAL",
        initiated_by="admin_test",
        storage_provider="Local Fallback",
        bucket="test-bucket"
    )
    db.add(rec)
    db.commit()

    # Query database
    retrieved = db.query(BackupRecord).filter(BackupRecord.backup_id == backup_id).first()
    assert retrieved is not None
    assert retrieved.status == "RUNNING"
    assert retrieved.backup_type == "MANUAL"
    assert retrieved.initiated_by == "admin_test"
    assert retrieved.checksum_algorithm == "SHA-256"


def test_checksum_generation_and_verification(db):
    """Verify integrity check calculates correct SHA-256 values and handles matching/mismatched states."""
    # Write a temporary mock file
    backup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "backups")
    os.makedirs(backup_dir, exist_ok=True)
    filename = "test_mock_archive.sql.gz"
    filepath = os.path.join(backup_dir, filename)

    payload = b"intact backup payload data string"
    with open(filepath, "wb") as f:
        f.write(payload)

    expected_hash = hashlib.sha256(payload).hexdigest()

    backup_id = f"TEST-{secrets.token_hex(4).upper()}"
    rec = BackupRecord(
        backup_id=backup_id,
        filename=filename,
        created_at=datetime.now(UTC).replace(tzinfo=None),
        size_bytes=len(payload),
        sha256=expected_hash,
        status="SUCCESS",
        storage_key=f"data/backups/{filename}",
        storage_provider="Local Fallback",
        bucket="local-backups"
    )
    db.add(rec)
    db.commit()

    try:
        # 1. Verification with matching checksum
        res = cloud_storage.verify_backup_integrity(db, backup_id)
        assert res["status"] == "SUCCESS"

        db.refresh(rec)
        assert rec.verification_status == "VERIFIED"
        assert rec.status == "VERIFIED"

        # 2. Reset and test with mismatched checksum
        rec.sha256 = "invalid_expected_checksum"
        rec.status = "SUCCESS"
        rec.verification_status = None
        db.commit()

        res_fail = cloud_storage.verify_backup_integrity(db, backup_id)
        assert res_fail["status"] == "FAILED"

        db.refresh(rec)
        assert rec.verification_status == "FAILED"
        assert rec.status == "FAILED"

    finally:
        # Cleanup mock file
        if os.path.exists(filepath):
            os.remove(filepath)


def test_safe_restore_validation(db):
    """Test that restore test runs successfully in isolation without affecting the live DB."""
    import gzip as gzip_mod

    # Create mock SQLite backup file
    backup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "backups")
    os.makedirs(backup_dir, exist_ok=True)
    filename = "test_restore_archive.sql.gz"
    filepath = os.path.join(backup_dir, filename)

    # SQLite schema query statements
    sql_dump = (
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username VARCHAR(50), role VARCHAR(20));\n"
        "CREATE TABLE IF NOT EXISTS warehouses (id VARCHAR(20) PRIMARY KEY);\n"
        "CREATE TABLE IF NOT EXISTS items (id VARCHAR(20) PRIMARY KEY);\n"
        "INSERT INTO users (id, username, role) VALUES (1, 'admin_restore', 'admin');\n"
        "INSERT INTO warehouses (id) VALUES ('WH-BLR-01');\n"
        "INSERT INTO items (id) VALUES ('ITM-01');\n"
    )

    with gzip_mod.open(filepath, "wb") as f:
        f.write(sql_dump.encode("utf-8"))

    with open(filepath, "rb") as f:
        raw_data = f.read()
    expected_hash = hashlib.sha256(raw_data).hexdigest()

    backup_id = f"TEST-{secrets.token_hex(4).upper()}"
    rec = BackupRecord(
        backup_id=backup_id,
        filename=filename,
        created_at=datetime.now(UTC).replace(tzinfo=None),
        size_bytes=len(raw_data),
        sha256=expected_hash,
        status="VERIFIED",
        verification_status="VERIFIED",
        storage_key=f"data/backups/{filename}",
        storage_provider="Local Fallback",
        bucket="local-backups"
    )
    db.add(rec)
    db.commit()

    try:
        # Execute isolated restore test
        res = cloud_storage.run_backup_restore_test(db, backup_id)
        assert res["status"] == "SUCCESS"

        db.refresh(rec)
        assert rec.restore_test_status == "SUCCESS"
        assert rec.status == "RESTORE_TESTED"

        # Verify production schema remains unaffected (live users table not overwritten)
        live_users = db.query(User).filter(User.username == "admin_restore").first()
        assert live_users is None

    finally:
        # Cleanup mock file
        if os.path.exists(filepath):
            os.remove(filepath)


def test_rbac_backup_trigger_admin_only(client, admin_token, viewer_token):
    """Verify that only Admin role can trigger backups; viewers get 403."""
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    headers_viewer = {"Authorization": f"Bearer {viewer_token}"}

    # Viewer should be rejected
    res_viewer = client.post("/api/backups", headers=headers_viewer)
    assert res_viewer.status_code == 403

    # Admin should be allowed
    res_admin = client.post("/api/backups", headers=headers_admin)
    assert res_admin.status_code == 200


def test_rbac_verify_restricted_to_admin(client, viewer_token):
    """Verify that viewers cannot trigger verification."""
    headers_viewer = {"Authorization": f"Bearer {viewer_token}"}
    res = client.post("/api/backups/BK-NONEXISTENT/verify", headers=headers_viewer)
    assert res.status_code == 403


def test_rbac_restore_test_restricted_to_admin(client, viewer_token):
    """Verify that viewers cannot trigger restore tests."""
    headers_viewer = {"Authorization": f"Bearer {viewer_token}"}
    res = client.post("/api/backups/BK-NONEXISTENT/restore-test", headers=headers_viewer)
    assert res.status_code == 403


def test_list_backups_authenticated(client, admin_token):
    """Verify that listing backups works for authenticated users."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/api/backups", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)


def test_get_nonexistent_backup_returns_404(client, admin_token):
    """Verify that fetching a non-existent backup returns 404."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/api/backups/BK-DOESNOTEXIST", headers=headers)
    assert res.status_code == 404
