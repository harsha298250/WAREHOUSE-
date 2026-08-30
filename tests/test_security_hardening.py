import pytest
import time
from backend.main import _login_attempts
from backend.models import User
from backend.auth import hash_password

def test_login_security(client, db):
    # Clear rate limiter to avoid 429
    _login_attempts.clear()

    # Seed admin user if not exists
    existing = db.query(User).filter(User.username == "test_admin_hardened").first()
    if not existing:
        admin = User(
            username="test_admin_hardened",
            password_hash=hash_password("AdminHardened@123"),
            role="admin"
        )
        db.add(admin)
        db.commit()

    # Valid admin login
    res = client.post("/auth/login", json={"username": "test_admin_hardened", "password": "AdminHardened@123"})
    assert res.status_code == 200
    assert "access_token" in res.json()

    # Invalid password login
    res_bad = client.post("/auth/login", json={"username": "test_admin_hardened", "password": "WrongPassword"})
    assert res_bad.status_code == 401


def test_otp_security_and_zero_leakage(client, db):
    # Clear rate limiter
    _login_attempts.clear()

    # Seed admin user if not exists
    existing = db.query(User).filter(User.username == "test_admin_hardened").first()
    if not existing:
        admin = User(
            username="test_admin_hardened",
            password_hash=hash_password("AdminHardened@123"),
            role="admin"
        )
        db.add(admin)
        db.commit()

    login_res = client.post("/auth/login", json={"username": "test_admin_hardened", "password": "AdminHardened@123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Request OTP for new admin creation
    req_res = client.post("/admin/request-add-admin", json={
        "username": f"testadmin_{int(time.time())}",
        "full_name": "Test Security Admin",
        "email": "testadmin.security@gmail.com",
        "password": "SecurePassword@2026"
    }, headers=headers)

    assert req_res.status_code == 200
    data = req_res.json()
    assert data["status"] == "otp_sent"
    # Zero OTP leakage verification
    assert "passkey_dev" not in data
    assert "otp_code" not in data

    # Attempt incorrect OTP
    confirm_bad = client.post("/admin/confirm-add-admin", json={"passkey": "000000"}, headers=headers)
    assert confirm_bad.status_code == 400
    assert "attempts remaining" in confirm_bad.json()["detail"].lower()


def test_google_token_verification_rejection(client):
    # Unverified / fake Google token must be rejected
    res = client.post("/auth/google-signin", json={"id_token": "fake_unverified_token_123"})
    assert res.status_code == 401
    assert "Invalid or expired Google ID Token" in res.json()["detail"]


def test_health_endpoints_no_secrets(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert "password" not in str(data).lower()
    assert "secret" not in str(data).lower()
