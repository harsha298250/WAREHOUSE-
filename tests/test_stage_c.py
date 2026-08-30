import pytest
import os
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_google_oauth_disabled_by_default():
    """Verify that Google Sign-in returns 400 when GOOGLE_CLIENT_ID is not configured."""
    original_client_id = os.getenv("GOOGLE_CLIENT_ID")
    os.environ["GOOGLE_CLIENT_ID"] = ""
    
    try:
        res = client.post("/auth/google-signin", json={"id_token": "some-token"})
        assert res.status_code == 400
        assert "not configured" in res.json()["detail"]
    finally:
        if original_client_id is not None:
            os.environ["GOOGLE_CLIENT_ID"] = original_client_id
        else:
            os.environ.pop("GOOGLE_CLIENT_ID", None)


def test_google_oauth_invalid_token():
    """Verify that an invalid token returns 401 Unauthorized."""
    original_client_id = os.getenv("GOOGLE_CLIENT_ID")
    os.environ["GOOGLE_CLIENT_ID"] = "dummy-client-id"
    
    try:
        res = client.post("/auth/google-signin", json={"id_token": "invalid-token-value"})
        assert res.status_code == 401
        assert "Invalid or expired Google ID Token" in res.json()["detail"]
    finally:
        if original_client_id is not None:
            os.environ["GOOGLE_CLIENT_ID"] = original_client_id
        else:
            os.environ.pop("GOOGLE_CLIENT_ID", None)


def test_gemini_diagnostics():
    """Verify that `/health/integrations` reports Google Gemini status correctly."""
    res = client.get("/health/integrations")
    assert res.status_code == 200
    data = res.json()
    assert "gemini" in data["integrations"]
    assert data["integrations"]["gemini"]["provider"] == "Google Gemini"
