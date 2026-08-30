import pytest
import time
import os
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from backend.models import (
    User, Item, Warehouse, Inventory, Order, AccessLog,
    UserWarehouseAccess, ForecastRun, ABCClassification, AnomalyResult
)
from backend.auth import hash_password
from backend.services.ai_service import GeminiService, TOOL_REGISTRY
from backend.main import app

client = TestClient(app)


def run_async(coro_creator):
    import queue
    import asyncio
    import threading
    q = queue.Queue()
    
    def worker():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            res = loop.run_until_complete(coro_creator())
            q.put((True, res))
        except Exception as e:
            q.put((False, e))
        finally:
            loop.close()
            
    t = threading.Thread(target=worker)
    t.start()
    t.join()
    
    success, val = q.get()
    if success:
        return val
    else:
        raise val


@pytest.fixture
def test_user(db):
    existing = db.query(User).filter(User.username == "final_admin").first()
    if not existing:
        user = User(
            username="final_admin",
            password_hash=hash_password("AdminPass123!"),
            role="admin"
        )
        db.add(user)
        db.commit()
        return user
    return existing


@pytest.fixture
def token(client, test_user):
    r = client.post("/auth/login", json={"username": "final_admin", "password": "AdminPass123!"})
    assert r.status_code == 200
    return r.json()["access_token"]


def test_final_verification_startup():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] in ("healthy", "ok", "success")


def test_final_verification_auth_isolation(token, db):
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Accessing without token should be 401
    r = client.get("/warehouses")
    assert r.status_code == 401

    # 2. Accessing with token should succeed
    r = client.get("/warehouses", headers=headers)
    assert r.status_code == 200


def test_final_verification_ai_assistant_fallback(token):
    headers = {"Authorization": f"Bearer {token}"}
    
    # Check that Gemini assistant falls back gracefully on outage
    orig_key = os.environ.get("GEMINI_API_KEY")
    os.environ["GEMINI_API_KEY"] = ""
    try:
        r = client.post("/ai/assistant", json={"message": "What is our low stock count?"}, headers=headers)
        assert r.status_code == 200
        assert "response" in r.json()
    finally:
        if orig_key:
            os.environ["GEMINI_API_KEY"] = orig_key


def test_final_verification_forecasting_and_abc(db):
    # Verify that ABC analysis classification tool runs safely and returns classifications
    # (Check model registry tool is mapped and checks permissions)
    res = TOOL_REGISTRY["get_abc_analytics"](db, "admin", source="wms")
    assert "total_classified_items" in res
    assert "summary" in res


def test_final_verification_audit_logging(token, db, test_user):
    headers = {"Authorization": f"Bearer {token}"}
    
    # Call a protected endpoint that triggers access logging
    r = client.get("/warehouses", headers=headers)
    assert r.status_code == 200

    # Assert that an access log is successfully persisted
    db.expire_all()
    log = db.query(AccessLog).filter(AccessLog.username == test_user.username).first()
    assert log is not None
