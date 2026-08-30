import pytest
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)
_NEEDS_MYSQL = os.getenv("TEST_DB_NAME", "sqlite") == "sqlite"

def get_token():
    try:
        from backend.main import _login_attempts
        _login_attempts.clear()
    except ImportError:
        pass
    r = client.post('/auth/login', json={'username': 'test_admin_hardened', 'password': 'AdminHardened@123'})
    if r.status_code != 200:
        r = client.post('/auth/login', json={'username': 'test_admin', 'password': 'TestAdmin@123'})
    return r.json().get('access_token')

@pytest.mark.skipif(_NEEDS_MYSQL, reason="INTEGRATION: requires MySQL with stock data")
def test_what_if_simulation():
    headers = {"Authorization": f"Bearer {get_token()}"}
    sim_res = client.post("/ai/simulate-scenario", json={
        "warehouse_id": "WH-BLR-01",
        "demand_surge_pct": 20.0,
        "supplier_delay_days": 5,
        "transport_disruption": True
    }, headers=headers)

    assert sim_res.status_code == 200
    data = sim_res.json()
    assert data["is_simulation"] is True
    assert "summary" in data
    assert "item_impacts" in data
    assert len(data["item_impacts"]) > 0
