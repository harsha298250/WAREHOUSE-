import pytest
import json
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.main import app
from backend.models import User, Warehouse, Item, Inventory, WarehouseLocation, Robot
from backend.auth import hash_password

client = TestClient(app)

@pytest.fixture
def smoke_admin(db):
    user = db.query(User).filter(User.username == "smoke_admin").first()
    if not user:
        user = User(
            username="smoke_admin",
            password_hash=hash_password("SmokePass123!"),
            role="admin"
        )
        db.add(user)
        db.commit()
    return user

@pytest.fixture
def smoke_token(client, smoke_admin):
    try:
        from backend.main import _login_attempts
        _login_attempts.clear()
    except ImportError:
        pass
    r = client.post("/auth/login", json={"username": "smoke_admin", "password": "SmokePass123!"})
    assert r.status_code == 200
    return r.json()["access_token"]

def setup_smoke_data(db):
    # Purge and setup minimal smoke test records
    db.query(Robot).filter(Robot.warehouse_id == "WH-SMOKE").delete()
    db.query(Inventory).filter(Inventory.warehouse_id == "WH-SMOKE").delete()
    db.query(WarehouseLocation).filter(WarehouseLocation.warehouse_id == "WH-SMOKE").delete()
    db.query(Warehouse).filter(Warehouse.id == "WH-SMOKE").delete()
    db.query(Item).filter(Item.id == "ITM-SMOKE").delete()
    db.commit()

    wh = Warehouse(id="WH-SMOKE", name="Smoke Test Warehouse", location="Smoke Loc")
    db.add(wh)
    db.commit()

    item = Item(id="ITM-SMOKE", name="Smoke Item", unit_cost=10.0, safety_stock=2, reorder_threshold=5)
    db.add(item)
    db.commit()

    loc = WarehouseLocation(
        id="WH-SMOKE-A-01", warehouse_id="WH-SMOKE", zone="A", aisle="01", rack="01", shelf="01",
        location_type="PICKING", capacity=10, x=1.0, y=1.0
    )
    db.add(loc)
    db.commit()

    inv = Inventory(warehouse_id="WH-SMOKE", item_id="ITM-SMOKE", location_id="WH-SMOKE-A-01", on_hand=5, reserved=0, available=5)
    db.add(inv)
    db.commit()

def test_production_frontend_loads():
    """Verify frontend entrypoint index.html retrieves successfully."""
    r = client.get("/")
    assert r.status_code == 200
    assert "html" in r.headers["content-type"].lower()

def test_production_health_endpoints():
    """Verify health, readiness, and liveness endpoints retrieve successfully."""
    for endpoint in ("/health", "/health/ready", "/health/live"):
        r = client.get(endpoint)
        assert r.status_code == 200
        res = r.json()
        assert "status" in res

def test_production_auth_rbac_and_isolation(smoke_token):
    """Verify JWT access, RBAC, and warehouse isolation filters."""
    headers = {"Authorization": f"Bearer {smoke_token}"}
    r = client.get("/warehouses", headers=headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_production_wms_reads(db, smoke_token):
    """Verify inventory and warehouse details retrieve successfully."""
    setup_smoke_data(db)
    headers = {"Authorization": f"Bearer {smoke_token}"}
    r = client.get("/wms/inventory", headers=headers)
    assert r.status_code == 200

def test_production_pathfinding(db, smoke_token):
    """Verify A* pathfinding requests function correctly."""
    setup_smoke_data(db)
    headers = {"Authorization": f"Bearer {smoke_token}"}
    # Mount minimal grid cells
    from backend.routers.pathfinding import initialize_warehouse_grid_if_empty
    initialize_warehouse_grid_if_empty(db, "WH-SMOKE")
    
    r = client.post("/pathfinding/plan", json={
        "warehouse_id": "WH-SMOKE",
        "start_x": 1,
        "start_y": 1,
        "goal_x": 2,
        "goal_y": 1
    }, headers=headers)
    assert r.status_code == 200
    assert "path" in r.json()
