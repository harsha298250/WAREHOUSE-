import pytest
from datetime import datetime, UTC, timedelta
from jose import jwt
from sqlalchemy import text
from backend.auth import (
    hash_password,
    verify_password,
    SECRET_KEY,
    ALGORITHM,
    Permissions,
)
from backend.models import User, AuditLedger, OTPRecord, FinancialTransaction, Item, Warehouse, Inventory
from backend.database import SessionLocal

@pytest.fixture(scope="function")
def local_admin(db):
    username = "local_sec_admin"
    password = "SecAdminPassword@123"
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        db.delete(existing)
        db.commit()

    u = User(
        username=username,
        password_hash=hash_password(password),
        role="admin",
        is_active=True
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    yield u, password
    db.delete(u)
    db.commit()

@pytest.fixture(scope="function")
def local_admin_token(client, local_admin):
    u, password = local_admin
    r = client.post("/auth/login", json={"username": u.username, "password": password})
    assert r.status_code == 200
    return r.json()["access_token"]

# 1. Valid login
def test_valid_login(client, db):
    username = "login_success_user"
    password = "SuccessPassword@123"
    u = User(username=username, password_hash=hash_password(password), role="viewer", is_active=True)
    db.add(u)
    db.commit()

    r = client.post("/auth/login", json={"username": username, "password": password})
    assert r.status_code == 200
    assert "access_token" in r.json()

    # cleanup
    db.delete(u)
    db.commit()

# 2. Invalid login
def test_invalid_login(client):
    r = client.post("/auth/login", json={"username": "non_existent_user_xyz", "password": "WrongPassword@123"})
    assert r.status_code == 401

# 3. Password hashing
def test_password_hashing():
    pw = "SecretPassword123!"
    h = hash_password(pw)
    assert h != pw
    assert verify_password(pw, h) is True
    assert verify_password("WrongPassword123!", h) is False

# 4. Expired JWT rejection
def test_expired_jwt_rejection(client):
    payload = {"sub": "test_admin", "role": "admin", "exp": datetime.now(UTC).replace(tzinfo=None) - timedelta(hours=1)}
    expired_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    r = client.get("/users", headers={"Authorization": f"Bearer {expired_token}"})
    assert r.status_code == 401

# 5. Invalid JWT rejection
def test_invalid_jwt_rejection(client):
    invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalidpayload.invalidsignature"
    r = client.get("/users", headers={"Authorization": f"Bearer {invalid_token}"})
    assert r.status_code == 401

# 6. Protected endpoint without authentication
def test_protected_endpoint_no_auth(client):
    r = client.get("/users")
    assert r.status_code == 401

# 7. Unauthorized role access
def test_unauthorized_role_access(client, viewer_token):
    r = client.get("/users", headers={"Authorization": f"Bearer {viewer_token}"})
    assert r.status_code == 403

# 8. Authorized role access
def test_authorized_role_access(client, admin_token):
    r = client.get("/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200

# 9. Admin role change with correct ADMIN password
def test_admin_role_change_correct_password(client, db, local_admin, local_admin_token):
    target = User(username="target_role_change_1", password_hash=hash_password("TargetPass@123"), role="viewer")
    db.add(target)
    db.commit()

    u, password = local_admin
    r = client.put(
        f"/users/{target.id}/role",
        json={"role": "operator", "confirm_password": password},
        headers={"Authorization": f"Bearer {local_admin_token}"}
    )
    assert r.status_code == 200
    db.refresh(target)
    assert target.role == "operator"

    db.delete(target)
    db.commit()

# 10. Admin role change with incorrect ADMIN password
def test_admin_role_change_incorrect_password(client, db, local_admin_token):
    target = User(username="target_role_change_2", password_hash=hash_password("TargetPass@123"), role="viewer")
    db.add(target)
    db.commit()

    r = client.put(
        f"/users/{target.id}/role",
        json={"role": "operator", "confirm_password": "WrongAdminPassword@123"},
        headers={"Authorization": f"Bearer {local_admin_token}"}
    )
    assert r.status_code == 403
    db.refresh(target)
    assert target.role == "viewer"

    db.delete(target)
    db.commit()

# 11. Attempt to use TARGET USER password for admin role change
def test_admin_role_change_target_user_password_rejected(client, db, local_admin_token):
    target = User(username="target_role_change_3", password_hash=hash_password("TargetPass@123"), role="viewer")
    db.add(target)
    db.commit()

    r = client.put(
        f"/users/{target.id}/role",
        json={"role": "operator", "confirm_password": "TargetPass@123"},
        headers={"Authorization": f"Bearer {local_admin_token}"}
    )
    assert r.status_code == 403
    db.refresh(target)
    assert target.role == "viewer"

    db.delete(target)
    db.commit()

# 12. Role change audit entry
def test_role_change_audit_entry(client, db, local_admin, local_admin_token):
    target = User(username="target_role_change_4", password_hash=hash_password("TargetPass@123"), role="viewer")
    db.add(target)
    db.commit()

    u, password = local_admin
    r = client.put(
        f"/users/{target.id}/role",
        json={"role": "operator", "confirm_password": password},
        headers={"Authorization": f"Bearer {local_admin_token}"}
    )
    assert r.status_code == 200

    audit = db.query(AuditLedger).filter(AuditLedger.event_type == "role_changed").order_by(AuditLedger.id.desc()).first()
    assert audit is not None
    assert "target_username" in audit.details
    assert target.username in audit.details

    db.delete(target)
    db.commit()

# 13. Self-role escalation protection
def test_self_role_escalation_protection(client, db, local_admin, local_admin_token):
    u, password = local_admin
    r = client.put(
        f"/users/{u.id}/role",
        json={"role": "viewer", "confirm_password": password},
        headers={"Authorization": f"Bearer {local_admin_token}"}
    )
    assert r.status_code == 400
    db.refresh(u)
    assert u.role == "admin"

# 14. Financial permission enforcement
def test_financial_permission_enforcement(client, viewer_token, admin_token):
    r = client.get("/wms/financial/revenue", headers={"Authorization": f"Bearer {viewer_token}"})
    assert r.status_code == 403

    r = client.get("/wms/financial/revenue", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200

# 15. Inventory permission enforcement
def test_inventory_permission_enforcement(client, viewer_token, admin_token, db):
    wh = Warehouse(id="WH-SEC-01", name="Security WH", location="City Sec")
    item = Item(id="ITM-SEC-01", name="Security Item", category="Sec", unit_cost=10.0, safety_stock=5, lead_time_days=3)
    db.add(wh)
    db.add(item)
    db.commit()

    inv = Inventory(warehouse_id="WH-SEC-01", item_id="ITM-SEC-01", on_hand=100, reserved=0)
    db.add(inv)
    db.commit()

    payload = {
        "warehouse_id": "WH-SEC-01",
        "item_id": "ITM-SEC-01",
        "adjustment": 10,
        "reason": "Test adjustment permissions"
    }

    r = client.post("/wms/inventory/adjust", json=payload, headers={"Authorization": f"Bearer {viewer_token}"})
    assert r.status_code == 403

    r = client.post("/wms/inventory/adjust", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200

    db.delete(inv)
    db.delete(item)
    db.delete(wh)
    db.commit()

# 16. User-management permission enforcement
def test_user_management_permission_enforcement(client, viewer_token, admin_token):
    r = client.get("/users", headers={"Authorization": f"Bearer {viewer_token}"})
    assert r.status_code == 403

    r = client.get("/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200

# 17. OTP success
def test_otp_success(client, db, local_admin, local_admin_token):
    u, password = local_admin
    r = client.post(
        "/auth/request-change-password",
        json={"current_password": password, "new_password": "NewAdminPass@123"},
        headers={"Authorization": f"Bearer {local_admin_token}"}
    )
    assert r.status_code == 200
    assert r.json()["status"] == "otp_sent"

    otp_record = db.query(OTPRecord).filter(OTPRecord.user_id == u.id, OTPRecord.purpose == "PASSWORD_CHANGE").first()
    assert otp_record is not None

    otp_record.code_hash = hash_password("654321")
    db.commit()

    r = client.post(
        "/auth/confirm-change-password",
        json={"passkey": "654321"},
        headers={"Authorization": f"Bearer {local_admin_token}"}
    )
    assert r.status_code == 200
    assert r.json()["status"] == "success"

# 18. OTP failure
def test_otp_failure(client, db, local_admin, local_admin_token):
    u, password = local_admin
    r = client.post(
        "/auth/request-change-password",
        json={"current_password": password, "new_password": "NewAdminPass@123"},
        headers={"Authorization": f"Bearer {local_admin_token}"}
    )
    assert r.status_code == 200

    r = client.post(
        "/auth/confirm-change-password",
        json={"passkey": "incorrect_otp_code"},
        headers={"Authorization": f"Bearer {local_admin_token}"}
    )
    assert r.status_code == 400

# 19. OTP expiration
def test_otp_expiration(client, db, local_admin, local_admin_token):
    u, password = local_admin
    r = client.post(
        "/auth/request-change-password",
        json={"current_password": password, "new_password": "NewAdminPass@123"},
        headers={"Authorization": f"Bearer {local_admin_token}"}
    )
    assert r.status_code == 200

    otp_record = db.query(OTPRecord).filter(OTPRecord.user_id == u.id, OTPRecord.purpose == "PASSWORD_CHANGE").first()
    assert otp_record is not None

    otp_record.expires_at = datetime.now(UTC).replace(tzinfo=None) - timedelta(seconds=1)
    db.commit()

    r = client.post(
        "/auth/confirm-change-password",
        json={"passkey": "any_code"},
        headers={"Authorization": f"Bearer {local_admin_token}"}
    )
    assert r.status_code == 400
    assert "expired" in r.json()["detail"].lower()

# 20. Lockout/failed-attempt behavior
def test_lockout_behavior(client, db):
    username = "lockout_test_user_unique"
    password = "CorrectPass@123"
    u = User(username=username, password_hash=hash_password(password), role="viewer", is_active=True, failed_login_count=0)
    db.add(u)
    db.commit()

    for _ in range(4):
        r = client.post("/auth/login", json={"username": username, "password": "WrongPassword"})
        assert r.status_code == 401

    db.refresh(u)
    assert u.failed_login_count == 4
    assert u.locked_until is None

    r = client.post("/auth/login", json={"username": username, "password": "WrongPassword"})
    assert r.status_code == 401

    db.refresh(u)
    assert u.failed_login_count == 5
    assert u.locked_until is not None

    r = client.post("/auth/login", json={"username": username, "password": password})
    assert r.status_code == 403
    assert "locked" in r.json()["detail"].lower()

    db.delete(u)
    db.commit()
