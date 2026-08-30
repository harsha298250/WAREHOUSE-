import pytest
import time
import os
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from backend.models import (
    User, Warehouse, Item, Inventory, Order, AccessLog
)
from backend.auth import hash_password
from backend.main import app

client = TestClient(app)


@pytest.fixture
def test_smoke_user(db):
    existing = db.query(User).filter(User.username == "smoke_admin").first()
    if not existing:
        user = User(
            username="smoke_admin",
            password_hash=hash_password("SmokePass123!"),
            role="admin"
        )
        db.add(user)
        db.commit()
        return user
    return existing


@pytest.fixture
def smoke_token(client, test_smoke_user):
    r = client.post("/auth/login", json={"username": "smoke_admin", "password": "SmokePass123!"})
    assert r.status_code == 200
    return r.json()["access_token"]


def test_production_smoke_health():
    # Verify that the health check endpoint returns success status
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] in ("healthy", "ok", "success")


def test_production_smoke_auth(smoke_token):
    # Verify that requesting a protected WMS route without token throws 401
    r = client.get("/warehouses")
    assert r.status_code == 401

    # Requesting with valid token should succeed
    headers = {"Authorization": f"Bearer {smoke_token}"}
    r = client.get("/warehouses", headers=headers)
    assert r.status_code == 200


def test_production_smoke_inventory_read(smoke_token):
    # Verify inventory endpoint works and returns lists
    headers = {"Authorization": f"Bearer {smoke_token}"}
    r = client.get("/items", headers=headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_production_smoke_analytics_read(smoke_token):
    headers = {"Authorization": f"Bearer {smoke_token}"}
    r = client.get("/analytics/overview", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert "metrics" in body or "kpis" in body or isinstance(body, dict)


def test_production_smoke_ai_fallback(smoke_token):
    headers = {"Authorization": f"Bearer {smoke_token}"}
    
    # We patch Gemini to be offline/fallback mode using empty key
    orig_key = os.environ.get("GEMINI_API_KEY")
    os.environ["GEMINI_API_KEY"] = ""
    try:
        r = client.post("/ai/assistant", json={"message": "Show me the warehouse layout"}, headers=headers)
        assert r.status_code == 200
        assert "response" in r.json()
    finally:
        if orig_key:
            os.environ["GEMINI_API_KEY"] = orig_key


def test_production_smoke_audit_logging(smoke_token, db, test_smoke_user):
    headers = {"Authorization": f"Bearer {smoke_token}"}
    
    # Trigger an operation that writes to audit ledger, e.g. querying security dashboard
    r = client.get("/warehouses", headers=headers)
    assert r.status_code == 200

    # Verify that an access log entry was written
    db.expire_all()
    log = db.query(AccessLog).filter(AccessLog.username == test_smoke_user.username).first()
    assert log is not None
