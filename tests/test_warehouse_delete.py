import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.models import (
    Warehouse, Robot, Task, Order, OrderItem, Inventory, WarehouseLocation,
    WarehouseGridCell, DigitalTwinSimulation, AuditLedger, User
)
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
def admin_headers(db_session):
    admin = db_session.query(User).filter(User.username == "admin").first()
    if not admin:
        db_session.add(User(username="admin", password_hash="dummy", role="admin", is_active=True))
        db_session.commit()
    token = create_access_token(data={"sub": "admin", "role": "admin"})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def viewer_headers(db_session):
    # Ensure viewer_user exists in database
    viewer = db_session.query(User).filter(User.username == "viewer_user").first()
    if not viewer:
        db_session.add(User(username="viewer_user", password_hash="dummy", role="viewer", is_active=True))
        db_session.commit()
    token = create_access_token(data={"sub": "viewer_user", "role": "viewer"})
    return {"Authorization": f"Bearer {token}"}

def test_delete_warehouse_unauthenticated():
    r = client.delete("/warehouses/WH-NONEXISTENT")
    assert r.status_code == 401

def test_delete_warehouse_forbidden_for_non_admin(viewer_headers):
    r = client.delete("/warehouses/WH-BLR-01", headers=viewer_headers)
    assert r.status_code == 403

def test_delete_nonexistent_warehouse(admin_headers):
    r = client.delete("/warehouses/WH-NONEXISTENT-999", headers=admin_headers)
    assert r.status_code == 404

def test_delete_warehouse_blocked_when_simulation_active(admin_headers, db_session):
    wh_id = "WH-SIM-ACTIVE-TEST"
    # Create test warehouse & active simulation
    wh = Warehouse(id=wh_id, name="Sim Active Facility", location="Test", city="Test")
    db_session.add(wh)
    db_session.commit()

    sim = DigitalTwinSimulation(
        warehouse_id=wh_id,
        simulation_status="RUNNING",
        tick_count=1,
        simulation_time_seconds=2.0
    )
    db_session.add(sim)
    db_session.commit()

    # Attempt deletion while simulation is running
    r = client.delete(f"/warehouses/{wh_id}", headers=admin_headers)
    assert r.status_code == 409
    assert "simulation is active" in r.json()["detail"]

    # Cleanup active simulation
    db_session.delete(sim)
    db_session.delete(wh)
    db_session.commit()

def test_admin_successful_warehouse_deletion_and_isolation(admin_headers, db_session):
    wh_a = "WH-DEL-TEST-A"
    wh_b = "WH-DEL-TEST-B"

    # Create Warehouse A and Warehouse B with child records
    for wh_id, wh_name in [(wh_a, "Facility A"), (wh_b, "Facility B")]:
        db_session.add(Warehouse(id=wh_id, name=wh_name, location="City", city="City"))
        db_session.add(WarehouseLocation(id=f"{wh_id}-LOC-1", warehouse_id=wh_id, zone="ZONE-1", aisle="A-1", rack="R-1", shelf="S-1", x=1.0, y=1.0, location_type="STORAGE"))
        db_session.add(WarehouseGridCell(warehouse_id=wh_id, x=1, y=1, cell_type="STORAGE"))
        db_session.add(Robot(robot_code=f"RB-{wh_id}-01", name="Robot 1", warehouse_id=wh_id, status="AVAILABLE"))
    db_session.commit()

    # Delete Warehouse A
    r_del = client.delete(f"/warehouses/{wh_a}", headers=admin_headers)
    assert r_del.status_code == 200
    assert r_del.json()["status"] == "deleted"

    # Verify Warehouse A and all its child records are deleted
    assert db_session.query(Warehouse).filter(Warehouse.id == wh_a).first() is None
    assert db_session.query(WarehouseLocation).filter(WarehouseLocation.warehouse_id == wh_a).first() is None
    assert db_session.query(WarehouseGridCell).filter(WarehouseGridCell.warehouse_id == wh_a).first() is None
    assert db_session.query(Robot).filter(Robot.warehouse_id == wh_a).first() is None

    # Verify Warehouse B and its child records remain 100% intact & isolated
    assert db_session.query(Warehouse).filter(Warehouse.id == wh_b).first() is not None
    assert db_session.query(WarehouseLocation).filter(WarehouseLocation.warehouse_id == wh_b).first() is not None
    assert db_session.query(WarehouseGridCell).filter(WarehouseGridCell.warehouse_id == wh_b).first() is not None
    assert db_session.query(Robot).filter(Robot.warehouse_id == wh_b).first() is not None

    # Verify Audit Ledger record was generated
    audit_entry = db_session.query(AuditLedger).filter(
        AuditLedger.event_type == "WAREHOUSE_DELETED"
    ).first()
    assert audit_entry is not None

    # Cleanup Warehouse B
    client.delete(f"/warehouses/{wh_b}", headers=admin_headers)
