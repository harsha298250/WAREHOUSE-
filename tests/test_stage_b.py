import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_sentry_test_endpoint_rbac(db, viewer_token, admin_token):
    """Verify `/health/sentry-test` checks role permissions correctly."""
    # 1. Access by viewer (Forbidden)
    res = client.post("/health/sentry-test", headers={"Authorization": f"Bearer {viewer_token}"})
    assert res.status_code == 403
    assert "Only administrators" in res.json()["detail"]

    # 2. Access by administrator (should trigger ZeroDivisionError)
    with pytest.raises(ZeroDivisionError):
        client.post("/health/sentry-test", headers={"Authorization": f"Bearer {admin_token}"})


def test_sentry_diagnostics():
    """Verify that `/health/integrations` reports Sentry correctly when unconfigured/configured."""
    res = client.get("/health/integrations")
    assert res.status_code == 200
    data = res.json()
    assert "sentry" in data["integrations"]
