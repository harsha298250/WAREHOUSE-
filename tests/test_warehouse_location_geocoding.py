import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.main import app
from backend.models import Warehouse
from backend.database import SessionLocal
from backend.auth import create_access_token

client = TestClient(app)

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def admin_headers():
    token = create_access_token({"sub": "test_admin", "role": "admin"})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def viewer_headers():
    token = create_access_token({"sub": "test_viewer", "role": "viewer"})
    return {"Authorization": f"Bearer {token}"}


def test_create_warehouse_with_manual_coordinates(db_session, admin_headers):
    # Clean up if exists
    db_session.query(Warehouse).filter(Warehouse.id == "WH-TEST-COORD").delete()
    db_session.commit()

    payload = {
        "id": "WH-TEST-COORD",
        "name": "Test Coord Center",
        "location": "Some street, India",
        "city": "Amaravati",
        "state": "Andhra Pradesh",
        "country": "India",
        "latitude": 16.5062,
        "longitude": 80.5180
    }
    
    # Priority 1: manual coordinates should be used directly without calling geocoding
    with patch("backend.routers.warehouses.geocode_address") as mock_geocode:
        response = client.post("/warehouses", json=payload, headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "created"
        mock_geocode.assert_not_called()

    # Query DB to verify details
    w = db_session.query(Warehouse).filter(Warehouse.id == "WH-TEST-COORD").first()
    assert w is not None
    assert w.latitude == 16.5062
    assert w.longitude == 80.5180
    assert w.city == "Amaravati"

    # Cleanup
    db_session.delete(w)
    db_session.commit()


def test_create_warehouse_with_automatic_geocoding(db_session, admin_headers):
    db_session.query(Warehouse).filter(Warehouse.id == "WH-TEST-GEO").delete()
    db_session.commit()

    payload = {
        "id": "WH-TEST-GEO",
        "name": "Geocoded Fulfillment Hub",
        "location": "Amaravati, Andhra Pradesh, India",
        "city": "Amaravati",
        "state": "Andhra Pradesh",
        "country": "India"
    }

    # Mock geocode service resolving Amaravati to coordinates
    mock_lat, mock_lon, mock_addr = 16.5062, 80.5180, "Amaravati, Guntur, Andhra Pradesh, India"
    with patch("backend.routers.warehouses.geocode_address", return_value=(mock_lat, mock_lon, mock_addr)) as mock_geocode:
        response = client.post("/warehouses", json=payload, headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "created"
        assert response.json()["warning"] is None
        mock_geocode.assert_called_once_with(
            "Geocoded Fulfillment Hub", "Amaravati", "Andhra Pradesh", "India", "Amaravati, Andhra Pradesh, India"
        )

    w = db_session.query(Warehouse).filter(Warehouse.id == "WH-TEST-GEO").first()
    assert w is not None
    assert w.latitude == mock_lat
    assert w.longitude == mock_lon
    assert w.location == mock_addr

    db_session.delete(w)
    db_session.commit()


def test_create_warehouse_geocoding_failure_fallback(db_session, admin_headers):
    db_session.query(Warehouse).filter(Warehouse.id == "WH-TEST-FAIL").delete()
    db_session.commit()

    payload = {
        "id": "WH-TEST-FAIL",
        "name": "Failing Center",
        "location": "Invalid Fake Address"
    }

    # Mock geocoder failing to resolve
    with patch("backend.routers.warehouses.geocode_address", return_value=(None, None, None)) as mock_geocode:
        response = client.post("/warehouses", json=payload, headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "created"
        assert "warning" in response.json()
        assert "Location could not be automatically resolved" in response.json()["warning"]
        mock_geocode.assert_called_once()

    w = db_session.query(Warehouse).filter(Warehouse.id == "WH-TEST-FAIL").first()
    assert w is not None
    assert w.latitude is None
    assert w.longitude is None
    assert w.location == "Invalid Fake Address"

    db_session.delete(w)
    db_session.commit()


def test_update_warehouse_with_geocoding(db_session, admin_headers):
    db_session.query(Warehouse).filter(Warehouse.id == "WH-TEST-PUT").delete()
    db_session.commit()

    # Create original warehouse
    w = Warehouse(id="WH-TEST-PUT", name="Original Name", location="Original Location", latitude=12.0, longitude=77.0)
    db_session.add(w)
    db_session.commit()

    update_payload = {
        "name": "Updated Name",
        "location": "New Location Address",
        "city": "Kolkata",
        "state": "West Bengal",
        "country": "India",
        "latitude": None,
        "longitude": None
    }

    mock_lat, mock_lon, mock_addr = 22.5726, 88.3639, "Kolkata, West Bengal, India"
    with patch("backend.routers.warehouses.geocode_address", return_value=(mock_lat, mock_lon, mock_addr)) as mock_geocode:
        response = client.put("/warehouses/WH-TEST-PUT", json=update_payload, headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "updated"
        mock_geocode.assert_called_once()

    # Refresh DB
    db_session.expire_all()
    w_updated = db_session.query(Warehouse).filter(Warehouse.id == "WH-TEST-PUT").first()
    assert w_updated.name == "Updated Name"
    assert w_updated.latitude == mock_lat
    assert w_updated.longitude == mock_lon
    assert w_updated.location == mock_addr

    db_session.delete(w_updated)
    db_session.commit()


def test_patch_warehouse_location_reverse_geocoding(db_session, admin_headers):
    db_session.query(Warehouse).filter(Warehouse.id == "WH-TEST-PATCH").delete()
    db_session.commit()

    w = Warehouse(id="WH-TEST-PATCH", name="Patch Name", location="Original Location", latitude=12.0, longitude=77.0)
    db_session.add(w)
    db_session.commit()

    patch_payload = {
        "latitude": 13.0827,
        "longitude": 80.2707
    }

    mock_addr = "Chennai, Tamil Nadu, India"
    with patch("backend.routers.warehouses.reverse_geocode", return_value=mock_addr) as mock_reverse:
        response = client.patch("/warehouses/WH-TEST-PATCH/location", json=patch_payload, headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "updated"
        assert response.json()["location"] == mock_addr
        mock_reverse.assert_called_once_with(13.0827, 80.2707)

    db_session.expire_all()
    w_patched = db_session.query(Warehouse).filter(Warehouse.id == "WH-TEST-PATCH").first()
    assert w_patched.latitude == 13.0827
    assert w_patched.longitude == 80.2707
    assert w_patched.location == mock_addr

    db_session.delete(w_patched)
    db_session.commit()


def test_viewer_role_access_restriction(db_session, viewer_headers):
    # Ensure viewer role is not authorized to create, update, or patch
    payload = {
        "id": "WH-VIEWER-FAIL",
        "name": "Viewer Center",
        "location": "India"
    }
    
    response = client.post("/warehouses", json=payload, headers=viewer_headers)
    assert response.status_code == 403

    response = client.put("/warehouses/WH-BLR-01", json=payload, headers=viewer_headers)
    assert response.status_code == 403

    response = client.patch("/warehouses/WH-BLR-01/location", json={"latitude": 12.0, "longitude": 77.0}, headers=viewer_headers)
    assert response.status_code == 403
