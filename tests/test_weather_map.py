import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from backend.models import Warehouse, User
from backend.auth import hash_password
from backend import weather_service
from backend.redis_client import set_cache, get_cache, delete_cache

MOCK_WEATHER_PAYLOAD = {
    "current": {
        "temperature_2m": 25.5,
        "apparent_temperature": 27.0,
        "relative_humidity_2m": 60,
        "wind_speed_10m": 12.5,
        "weather_code": 3,
        "precipitation": 0.0
    },
    "daily": {
        "time": ["2026-08-21", "2026-08-22", "2026-08-23"],
        "temperature_2m_max": [28.0, 29.0, 27.5],
        "temperature_2m_min": [21.0, 22.0, 20.5],
        "precipitation_sum": [0.0, 1.5, 0.0],
        "weather_code": [3, 61, 2]
    }
}

# 1. Coordinates range validation (create warehouse)
def test_create_warehouse_coordinates_validation(client, admin_token):
    # Latitude too low (-91)
    r = client.post(
        "/warehouses",
        json={"id": "WH-TEST-ERR1", "name": "Err 1", "location": "Test", "latitude": -91.0, "longitude": 0.0},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert r.status_code == 422

    # Latitude too high (91)
    r = client.post(
        "/warehouses",
        json={"id": "WH-TEST-ERR2", "name": "Err 2", "location": "Test", "latitude": 91.0, "longitude": 0.0},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert r.status_code == 422

    # Longitude too low (-181)
    r = client.post(
        "/warehouses",
        json={"id": "WH-TEST-ERR3", "name": "Err 3", "location": "Test", "latitude": 0.0, "longitude": -181.0},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert r.status_code == 422

    # Longitude too high (181)
    r = client.post(
        "/warehouses",
        json={"id": "WH-TEST-ERR4", "name": "Err 4", "location": "Test", "latitude": 0.0, "longitude": 181.0},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert r.status_code == 422

# 2. Coordinates range validation (update coordinates)
def test_update_coordinates_range_validation(client, admin_token, db):
    wh = Warehouse(id="WH-VAL-TEST", name="Val Test", location="Test", latitude=0.0, longitude=0.0)
    db.add(wh)
    db.commit()

    # Invalid latitude
    r = client.put(
        f"/warehouses/{wh.id}/coordinates",
        json={"latitude": 95.0, "longitude": 0.0},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert r.status_code == 422

    # Invalid longitude
    r = client.put(
        f"/warehouses/{wh.id}/coordinates",
        json={"latitude": 0.0, "longitude": 190.0},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert r.status_code == 422

    db.delete(wh)
    db.commit()

# 3. Warehouse coordinates returned correctly
def test_warehouse_coordinates_returned(client, db, admin_token):
    wh = Warehouse(id="WH-COORD-GET", name="Coord Get", location="Loc", latitude=12.3456, longitude=78.9012)
    db.add(wh)
    db.commit()

    r = client.get("/warehouses", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200
    res = r.json()
    match = next((w for w in res if w["id"] == wh.id), None)
    assert match is not None
    assert match["latitude"] == 12.3456
    assert match["longitude"] == 78.9012

    db.delete(wh)
    db.commit()

# 4. Warehouse without coordinates handled correctly (400 Bad Request)
def test_warehouse_without_coords_handled(client, db, admin_token):
    wh = Warehouse(id="WH-NO-COORD", name="No Coord", location="Loc", latitude=None, longitude=None)
    db.add(wh)
    db.commit()

    r = client.get(f"/warehouses/{wh.id}/weather", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 400
    assert "coordinates not configured" in r.json()["detail"].lower()

    db.delete(wh)
    db.commit()

# 5. Weather endpoint requires authentication
def test_weather_requires_auth(client):
    r = client.get("/warehouses/WH-BLR-01/weather")
    assert r.status_code == 401

# 6. Unauthorized user rejected (e.g. invalid token)
def test_weather_unauthorized_token_rejected(client):
    r = client.get("/warehouses/WH-BLR-01/weather", headers={"Authorization": "Bearer invalid_token_xyz"})
    assert r.status_code == 401

# 7. Authorized user allowed
def test_weather_authorized_allowed(client, db, admin_token):
    wh = Warehouse(id="WH-AUTH-OK", name="Auth Ok", location="Loc", latitude=12.97, longitude=77.59)
    db.add(wh)
    db.commit()

    with patch("backend.weather_service.fetch_weather_from_provider", return_value=MOCK_WEATHER_PAYLOAD):
        r = client.get(f"/warehouses/{wh.id}/weather", headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200

    db.delete(wh)
    db.commit()

# 8. Weather service success and data normalization
def test_weather_service_success_normalization():
    delete_cache("warehouse_weather/WH-NORM-TEST")
    
    with patch("backend.weather_service.fetch_weather_from_provider", return_value=MOCK_WEATHER_PAYLOAD) as mock_fetch:
        res = weather_service.get_warehouse_weather("WH-NORM-TEST", 12.0, 77.0)
        assert mock_fetch.call_count == 1
        assert res["warehouse_id"] == "WH-NORM-TEST"
        assert res["current"]["temperature"] == 25.5
        assert res["current"]["apparent_temperature"] == 27.0
        assert res["current"]["humidity"] == 60
        assert res["current"]["wind_speed"] == 12.5
        assert res["current"]["weather_code"] == 3
        assert res["current"]["precipitation"] == 0.0
        assert len(res["forecast"]) == 3
        assert res["forecast"][0]["date"] == "2026-08-21"
        assert res["forecast"][0]["temp_max"] == 28.0
        assert res["forecast"][0]["temp_min"] == 21.0
        assert res["source"] == "Open-Meteo"

# 9. Weather API timeout handling (503 Service Unavailable)
def test_weather_api_timeout(client, db, admin_token):
    wh = Warehouse(id="WH-TIMEOUT", name="Timeout Wh", location="Loc", latitude=12.97, longitude=77.59)
    db.add(wh)
    db.commit()

    with patch("backend.weather_service.fetch_weather_from_provider", side_effect=Exception("Timeout occurred")):
        r = client.get(f"/warehouses/{wh.id}/weather", headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 503
        assert "weather service temporarily unavailable" in r.json()["detail"].lower()

    db.delete(wh)
    db.commit()

# 10. Weather API failure handling (Open-Meteo returns non-200)
def test_weather_api_non_200(client, db, admin_token):
    wh = Warehouse(id="WH-NON-200", name="Non 200 Wh", location="Loc", latitude=12.97, longitude=77.59)
    db.add(wh)
    db.commit()

    with patch("backend.weather_service.fetch_weather_from_provider", side_effect=RuntimeError("Open-Meteo returned status 500")):
        r = client.get(f"/warehouses/{wh.id}/weather", headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 503

    db.delete(wh)
    db.commit()

# 11. Invalid external response handling (malformed payload)
def test_weather_api_malformed(client, db, admin_token):
    wh = Warehouse(id="WH-MALFORMED", name="Malformed Wh", location="Loc", latitude=12.97, longitude=77.59)
    db.add(wh)
    db.commit()

    with patch("backend.weather_service.fetch_weather_from_provider", side_effect=ValueError("Malformed response from Open-Meteo")):
        r = client.get(f"/warehouses/{wh.id}/weather", headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 503

    db.delete(wh)
    db.commit()

# 12. Redis cache hit & miss verification
def test_redis_cache_hit_and_miss():
    wh_id = "WH-CACHE-TEST-9"
    cache_store = {}
    
    def mock_get_cache(key):
        return cache_store.get(key)
        
    def mock_set_cache(key, val, ttl_seconds=None):
        cache_store[key] = val
        return True

    with patch("backend.weather_service.get_cache", side_effect=mock_get_cache), \
         patch("backend.weather_service.set_cache", side_effect=mock_set_cache):
         
        with patch("backend.weather_service.fetch_weather_from_provider", return_value=MOCK_WEATHER_PAYLOAD) as mock_fetch:
            res1 = weather_service.get_warehouse_weather(wh_id, 12.0, 77.0)
            assert mock_fetch.call_count == 1
            assert res1["source"] == "Open-Meteo"
            
        with patch("backend.weather_service.fetch_weather_from_provider", return_value=MOCK_WEATHER_PAYLOAD) as mock_fetch:
            res2 = weather_service.get_warehouse_weather(wh_id, 12.0, 77.0)
            assert mock_fetch.call_count == 0
            assert res2["source"] == "Open-Meteo (Cache)"

# 13. Missing warehouse handling (404 Not Found)
def test_weather_missing_warehouse(client, admin_token):
    r = client.get("/warehouses/WH-NONEXISTENT/weather", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 404

# 14. Coordinate changes logged in Audit Ledger
def test_coordinate_changes_audited(client, db, admin_token):
    wh = Warehouse(id="WH-AUDIT-CO", name="Audit Co", location="Loc", latitude=10.0, longitude=20.0)
    db.add(wh)
    db.commit()

    from backend.models import AuditLedger
    
    r = client.put(
        f"/warehouses/{wh.id}/coordinates",
        json={"latitude": 11.0, "longitude": 21.0},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert r.status_code == 200

    audit = db.query(AuditLedger).filter(AuditLedger.event_type == "warehouse_location_changed").order_by(AuditLedger.id.desc()).first()
    assert audit is not None
    import json
    details = json.loads(audit.details)
    assert details["warehouse_id"] == wh.id
    assert details["old_latitude"] == 10.0
    assert details["new_latitude"] == 11.0

    db.delete(wh)
    db.commit()
