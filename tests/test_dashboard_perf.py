"""
tests/test_dashboard_perf.py — Dashboard response time performance unit test
"""
import time
import pytest


def test_dashboard_response_time_guarantee(client, admin_token):
    """Verify GET /analytics/dashboard execution time stays well below performance bounds."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # First call (may populate cache or run bounded query)
    start_time = time.time()
    res1 = client.get("/analytics/dashboard", headers=headers)
    duration1 = time.time() - start_time
    assert res1.status_code == 200
    assert "kpis" in res1.json()
    assert duration1 < 3.0, f"Cold dashboard request took too long: {duration1:.2f}s"

    # Second call (cached) should take < 200ms
    start_time = time.time()
    res2 = client.get("/analytics/dashboard", headers=headers)
    duration2 = time.time() - start_time
    assert res2.status_code == 200
    assert duration2 < 0.200, f"Cached dashboard request took longer than 200ms: {duration2*1000:.1f}ms"
