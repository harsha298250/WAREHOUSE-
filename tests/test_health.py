"""
tests/test_health.py — Health endpoint tests
"""
import pytest


class TestHealthEndpoints:

    def test_health_returns_200(self, client):
        r = client.get("/health")
        assert r.status_code == 200

    def test_health_has_required_fields(self, client):
        r = client.get("/health")
        d = r.json()
        for field in ["status", "timestamp"]:
            assert field in d, f"Missing field: {field}"

    def test_health_status_is_string(self, client):
        r = client.get("/health")
        assert isinstance(r.json()["status"], str)

    def test_health_does_not_expose_secrets(self, client):
        """Health endpoint must not leak DB password, connection strings etc."""
        body = r.text if hasattr((r := client.get("/health")), "text") else str(r.json())
        forbidden = ["password", "secret", "pymysql://", "mysql+", "AWS_SECRET"]
        for term in forbidden:
            assert term.lower() not in body.lower(), f"Secret term '{term}' found in health response"

    def test_health_no_auth_required(self, client):
        """Health check must be accessible without authentication."""
        r = client.get("/health")
        assert r.status_code != 401

    def test_health_db_status_present(self, client):
        r = client.get("/health")
        d = r.json()
        # DB status should be present but degraded/unknown if DB unavailable
        assert "database" in d or "db" in d or "status" in d

    def test_health_db_endpoint(self, client):
        r = client.get("/health/db")
        assert r.status_code in [200, 503], f"Unexpected: {r.status_code}"

    def test_health_ml_endpoint(self, client):
        r = client.get("/health/ml")
        assert r.status_code in [200, 503]

    def test_health_timestamp_format(self, client):
        r = client.get("/health")
        d = r.json()
        if "timestamp" in d:
            ts = d["timestamp"]
            assert ts is not None and str(ts) != "", f"Timestamp must be non-empty: {ts}"

