import pytest
import os
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_ui_index_loads():
    """Verify index.html page loads and serves correctly."""
    r = client.get("/")
    assert r.status_code == 200
    assert "html" in r.headers["content-type"].lower()
    assert "WAREHOUSE OS" in r.text

def test_ui_static_assets_serve():
    """Verify static Javascript resources serve correctly without missing files."""
    assets = [
        "/static/js/api.js",
        "/static/js/app.js",
        "/static/js/analytics.js",
        "/static/js/apps.js",
        "/static/js/scenario_lab.js",
        "/static/js/system_health.js",
        "/static/css/style.css"
    ]
    for asset in assets:
        r = client.get(asset)
        assert r.status_code == 200, f"Static asset {asset} failed to retrieve!"
