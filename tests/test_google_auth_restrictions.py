"""
tests/test_google_auth_restrictions.py

Automated Security Verification Suite:
Enforces that Google Sign-In works ONLY for users who are pre-registered
and active in the PostgreSQL Users table. Unregistered emails must be
strictly rejected with HTTP 403 Forbidden and zero database side-effects.
"""

import os
import json
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from backend.main import app
from backend.database import get_db
from backend.models import User
from backend.auth import hash_password

client = TestClient(app)

# Helper function to mock google verification
def mock_google_token_info(email: str, email_verified: bool = True, sub: str = "mock-google-sub-id"):
    return {
        "iss": "https://accounts.google.com",
        "aud": "mock-test-client-id",
        "email": email,
        "email_verified": email_verified,
        "sub": sub,
        "name": email.split("@")[0].title()
    }


@pytest.fixture(autouse=True)
def setup_google_oauth_env():
    """Ensure GOOGLE_CLIENT_ID is set for these tests."""
    orig = os.environ.get("GOOGLE_CLIENT_ID")
    os.environ["GOOGLE_CLIENT_ID"] = "mock-test-client-id"
    yield
    if orig is None:
        os.environ.pop("GOOGLE_CLIENT_ID", None)
    else:
        os.environ["GOOGLE_CLIENT_ID"] = orig


@pytest.fixture
def db_session():
    """Provides a database session for test setup and assertions."""
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()


def test_1_registered_admin_google_login_succeeds(db_session):
    """TEST 1: Registered ADMIN Google email -> login succeeds, role = ADMIN"""
    email = "test_admin_google@example.com"
    # Seed user in DB
    existing = db_session.query(User).filter(User.email == email).first()
    if not existing:
        user = User(
            username=email,
            email=email,
            password_hash=hash_password("Password123!"),
            role="admin",
            full_name="Test Admin User",
            is_active=True
        )
        db_session.add(user)
        db_session.commit()

    token_info = mock_google_token_info(email, sub="admin-sub-123")
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(token_info).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        res = client.post("/auth/google-signin", json={"id_token": "valid-admin-google-token"})
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        assert "access_token" in data
        assert data["user"]["role"] == "admin"


def test_2_registered_manager_google_login_succeeds(db_session):
    """TEST 2: Registered MANAGER Google email -> login succeeds, role = MANAGER"""
    email = "test_manager_google@example.com"
    existing = db_session.query(User).filter(User.email == email).first()
    if not existing:
        user = User(
            username=email,
            email=email,
            password_hash=hash_password("Password123!"),
            role="manager",
            full_name="Test Manager User",
            is_active=True
        )
        db_session.add(user)
        db_session.commit()

    token_info = mock_google_token_info(email, sub="manager-sub-456")
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(token_info).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        res = client.post("/auth/google-signin", json={"id_token": "valid-manager-google-token"})
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        assert "access_token" in data
        assert data["user"]["role"] == "manager"


def test_3_registered_operator_google_login_succeeds(db_session):
    """TEST 3: Registered OPERATOR Google email -> login succeeds, role = OPERATOR"""
    email = "test_operator_google@example.com"
    existing = db_session.query(User).filter(User.email == email).first()
    if not existing:
        user = User(
            username=email,
            email=email,
            password_hash=hash_password("Password123!"),
            role="operator",
            full_name="Test Operator User",
            is_active=True
        )
        db_session.add(user)
        db_session.commit()

    token_info = mock_google_token_info(email, sub="operator-sub-789")
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(token_info).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        res = client.post("/auth/google-signin", json={"id_token": "valid-operator-google-token"})
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        assert "access_token" in data
        assert data["user"]["role"] == "operator"


def test_4_registered_viewer_google_login_succeeds(db_session):
    """TEST 4: Registered VIEWER Google email -> login succeeds, role = VIEWER"""
    email = "test_viewer_google@example.com"
    existing = db_session.query(User).filter(User.email == email).first()
    if not existing:
        user = User(
            username=email,
            email=email,
            password_hash=hash_password("Password123!"),
            role="viewer",
            full_name="Test Viewer User",
            is_active=True
        )
        db_session.add(user)
        db_session.commit()

    token_info = mock_google_token_info(email, sub="viewer-sub-101")
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(token_info).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        res = client.post("/auth/google-signin", json={"id_token": "valid-viewer-google-token"})
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        assert "access_token" in data
        assert data["user"]["role"] == "viewer"


def test_5_unregistered_google_email_rejected_with_403(db_session):
    """TEST 5: Unregistered Google email -> HTTP 403, no token, no session, no user created"""
    email = "unregistered_stranger_999@gmail.com"
    # Ensure not in DB
    db_session.query(User).filter(User.email == email).delete()
    db_session.commit()

    token_info = mock_google_token_info(email, sub="stranger-sub-999")
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(token_info).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        res = client.post("/auth/google-signin", json={"id_token": "unregistered-google-token"})
        assert res.status_code == 403, f"Expected 403, got {res.status_code}: {res.text}"
        assert "not authorized" in res.json()["detail"].lower()

    # Verify no user was created in DB
    created = db_session.query(User).filter(User.email == email).first()
    assert created is None, "Unregistered email MUST NOT be auto-created in database!"


def test_6_unregistered_email_never_falls_back_to_viewer(db_session):
    """TEST 6: Unregistered email must NEVER fall back to Viewer role or auto-create account"""
    email = "fallback_check_unregistered@gmail.com"
    db_session.query(User).filter(User.email == email).delete()
    db_session.commit()

    users_before = db_session.query(User).count()

    token_info = mock_google_token_info(email, sub="sub-fallback-check")
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(token_info).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        res = client.post("/auth/google-signin", json={"id_token": "fallback-check-token"})
        assert res.status_code == 403

    users_after = db_session.query(User).count()
    assert users_before == users_after, f"User count changed from {users_before} to {users_after}! Auto-creation occurred!"


def test_7_deactivated_registered_user_rejected_with_403(db_session):
    """TEST 7: Disabled/inactive user cannot log in via Google Sign-In"""
    email = "deactivated_user_google@example.com"
    existing = db_session.query(User).filter(User.email == email).first()
    if not existing:
        user = User(
            username=email,
            email=email,
            password_hash=hash_password("Password123!"),
            role="manager",
            full_name="Deactivated User",
            is_active=False
        )
        db_session.add(user)
    else:
        existing.is_active = False
    db_session.commit()

    token_info = mock_google_token_info(email, sub="deactivated-sub-123")
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(token_info).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        res = client.post("/auth/google-signin", json={"id_token": "deactivated-user-token"})
        assert res.status_code == 403, f"Expected 403, got {res.status_code}: {res.text}"
        assert "deactivated" in res.json()["detail"].lower() or "disabled" in res.json()["detail"].lower()


def test_8_email_case_normalization_matches_user(db_session):
    """TEST 8: Email case normalization works correctly (John.Doe@Gmail.COM == john.doe@gmail.com)"""
    db_email = "John.Doe.Normalized@Example.COM"
    lookup_email = "john.doe.normalized@example.com"

    existing = db_session.query(User).filter(User.email == db_email).first()
    if not existing:
        user = User(
            username=db_email,
            email=db_email,
            password_hash=hash_password("Password123!"),
            role="manager",
            full_name="Case Sensitive User",
            is_active=True
        )
        db_session.add(user)
        db_session.commit()

    token_info = mock_google_token_info(lookup_email, sub="case-norm-sub-999")
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(token_info).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        res = client.post("/auth/google-signin", json={"id_token": "case-normalization-token"})
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        assert res.json()["user"]["role"] == "manager"


def test_9_direct_api_attempt_with_unauthorized_google_identity_is_rejected(db_session):
    """TEST 9: Direct API attempt with unauthorized Google identity is rejected with 403"""
    unauthorized_email = "hacker_direct_api@attacker.com"
    token_info = mock_google_token_info(unauthorized_email, sub="hacker-sub-666")
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(token_info).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        res = client.post("/auth/google-signin", json={"id_token": "direct-api-hacker-token"})
        assert res.status_code == 403
        assert "not authorized" in res.json()["detail"].lower()


def test_10_existing_database_role_is_preserved_exactly(db_session):
    """TEST 10: Existing user's database role is preserved exactly and NEVER changed to viewer"""
    email = "admin_preserve_role@example.com"
    existing = db_session.query(User).filter(User.email == email).first()
    if not existing:
        user = User(
            username=email,
            email=email,
            password_hash=hash_password("Password123!"),
            role="admin",
            full_name="Preserve Role Admin",
            is_active=True
        )
        db_session.add(user)
        db_session.commit()

    token_info = mock_google_token_info(email, sub="preserve-role-sub")
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(token_info).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        res = client.post("/auth/google-signin", json={"id_token": "preserve-role-token"})
        assert res.status_code == 200
        assert res.json()["user"]["role"] == "admin"

    # Verify DB record role is STILL admin
    db_user = db_session.query(User).filter(User.email == email).first()
    assert db_user.role == "admin", f"Database role changed to {db_user.role}! MUST remain admin!"
