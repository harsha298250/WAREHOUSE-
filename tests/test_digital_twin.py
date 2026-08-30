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
def test_digital_twin_database_reconciliation():
    headers = {"Authorization": f"Bearer {get_token()}"}
    res = client.get("/apps/digital-twin/WH-BLR-01", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["data_mode"] == "REAL DATABASE RECONCILED"
    assert "data_provenance" in data
    assert "inventory" in data["data_provenance"]
    assert "SIMULATED TELEMETRY" in str(data)

@pytest.mark.skipif(_NEEDS_MYSQL, reason="INTEGRATION: requires MySQL with stock data")
def test_digital_twin_invalid_warehouse():
    headers = {"Authorization": f"Bearer {get_token()}"}
    res = client.get("/apps/digital-twin/WH-NONEXISTENT", headers=headers)
    assert res.status_code == 404
