import pytest
from backend.models import User
from backend.auth import hash_password


def get_token(client, username, password):
    r = client.post("/auth/login", json={"username": username, "password": password})
    assert r.status_code == 200
    return r.json()["access_token"]


def test_unauthenticated_requests(client):
    """Verifies that all Phase 9 API routes reject unauthenticated requests with 401."""
    routes = [
        ("POST", "/analytics/forecasting/run"),
        ("GET", "/analytics/forecasting/runs"),
        ("GET", "/analytics/forecasting/results"),
        ("POST", "/analytics/abc/run"),
        ("GET", "/analytics/abc"),
        ("POST", "/analytics/anomalies/run"),
        ("GET", "/analytics/anomalies/demand"),
        ("POST", "/analytics/replenishment/run"),
        ("GET", "/analytics/replenishment"),
    ]

    for method, path in routes:
        if method == "POST":
            r = client.post(path)
        else:
            r = client.get(path)
        assert r.status_code == 401, f"{method} {path} should require authentication."


def test_viewer_rbac_restrictions(client, db):
    """Verifies that viewer role is forbidden from triggering ML pipeline calculations (POST runs)."""
    token = get_token(client, "test_viewer", "TestViewer@123")
    headers = {"Authorization": f"Bearer {token}"}

    post_routes = [
        "/analytics/forecasting/run",
        "/analytics/abc/run",
        "/analytics/anomalies/run",
        "/analytics/replenishment/run",
    ]

    for path in post_routes:
        r = client.post(path, headers=headers)
        assert r.status_code == 403, f"Viewer should not be authorized to POST to {path}."


def test_manager_authorized(client, db):
    """Verifies that manager and admin roles can fetch GET endpoints successfully."""
    token = get_token(client, "test_manager", "TestManager@123")
    headers = {"Authorization": f"Bearer {token}"}

    get_routes = [
        "/analytics/forecasting/runs",
        "/analytics/forecasting/results",
        "/analytics/abc?source=wms",
        "/analytics/anomalies/demand",
        "/analytics/replenishment",
    ]

    for path in get_routes:
        r = client.get(path, headers=headers)
        # Should be authorized and succeed (200) or find no data (200 with empty list/results)
        assert r.status_code == 200, f"Manager should be able to query GET {path}."
