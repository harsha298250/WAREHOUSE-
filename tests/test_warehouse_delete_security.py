"""
test_warehouse_delete_security.py — Master Unit Tests for Secure Warehouse Deletion & Admin Password Verification
"""

import pytest
from backend.models import Warehouse, User, Robot, DigitalTwinSimulation, AuditLedger
from backend.auth import hash_password

@pytest.fixture
def delete_test_data(db):
    """Fixture initializing a test warehouse, admin user, normal viewer, and dependent child records."""
    wh_id = "WH-DEL-SEC-01"

    # Clean old records if any
    db.query(Robot).filter(Robot.warehouse_id == wh_id).delete()
    db.query(DigitalTwinSimulation).filter(DigitalTwinSimulation.warehouse_id == wh_id).delete()
    db.query(Warehouse).filter(Warehouse.id == wh_id).delete()
    db.commit()

    # Create Warehouse
    wh = Warehouse(id=wh_id, name="Security Test Warehouse", city="Test City")
    db.add(wh)

    # Create Robot
    r = Robot(robot_code="RB-DEL-01", name="Delete Robot", warehouse_id=wh_id, battery_level=100.0, current_x=1.0, current_y=1.0)
    db.add(r)
    db.commit()

    return wh_id


def test_warehouse_delete_correct_password_success(client, admin_token, db, delete_test_data):
    """Verifies that an administrator providing the correct password successfully deletes the warehouse and logs WAREHOUSE_DELETED."""
    wh_id = delete_test_data

    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.request(
        "DELETE",
        f"/warehouses/{wh_id}",
        json={"password": "TestAdmin@123"},
        headers=headers
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    assert response.json().get("status") == "deleted"

    # Verify warehouse is removed from DB
    deleted_wh = db.query(Warehouse).filter(Warehouse.id == wh_id).first()
    assert deleted_wh is None

    # Verify Audit Ledger record
    audit_entry = db.query(AuditLedger).filter(
        AuditLedger.event_type == "WAREHOUSE_DELETED",
        AuditLedger.details.like(f"%{wh_id}%")
    ).first()
    assert audit_entry is not None, "Audit ledger record WAREHOUSE_DELETED missing!"


def test_warehouse_delete_incorrect_password_rejected(client, admin_token, db, delete_test_data):
    """Verifies that providing an incorrect admin password returns 403, keeps warehouse intact, and logs WAREHOUSE_DELETE_AUTH_FAILED."""
    wh_id = delete_test_data

    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.request(
        "DELETE",
        f"/warehouses/{wh_id}",
        json={"password": "WrongPassword123!"},
        headers=headers
    )

    assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.text}"
    assert "Incorrect administrator password" in response.json().get("detail", "")

    # Verify warehouse is STILL IN DATABASE
    wh = db.query(Warehouse).filter(Warehouse.id == wh_id).first()
    assert wh is not None

    # Verify Audit Ledger record WAREHOUSE_DELETE_AUTH_FAILED
    audit_entry = db.query(AuditLedger).filter(
        AuditLedger.event_type == "WAREHOUSE_DELETE_AUTH_FAILED",
        AuditLedger.details.like(f"%{wh_id}%")
    ).first()
    assert audit_entry is not None, "Audit ledger record WAREHOUSE_DELETE_AUTH_FAILED missing!"


def test_warehouse_delete_non_admin_forbidden(client, viewer_token, db, delete_test_data):
    """Verifies that non-admin users cannot delete warehouses (403 Forbidden)."""
    wh_id = delete_test_data

    headers = {"Authorization": f"Bearer {viewer_token}"}
    response = client.request(
        "DELETE",
        f"/warehouses/{wh_id}",
        json={"password": "TestAdmin@123"},
        headers=headers
    )

    assert response.status_code == 403

    # Warehouse remains untouched
    wh = db.query(Warehouse).filter(Warehouse.id == wh_id).first()
    assert wh is not None


def test_warehouse_delete_active_simulation_blocked(client, admin_token, db, delete_test_data):
    """Verifies that attempting deletion while a Digital Twin simulation is active returns 409 Conflict."""
    wh_id = delete_test_data

    # Create active simulation
    sim = DigitalTwinSimulation(
        warehouse_id=wh_id,
        simulation_status="RUNNING",
        speed_multiplier=1.0
    )
    db.add(sim)
    db.commit()

    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.request(
        "DELETE",
        f"/warehouses/{wh_id}",
        json={"password": "TestAdmin@123"},
        headers=headers
    )

    assert response.status_code == 409, f"Expected 409, got {response.status_code}: {response.text}"
    assert "simulation is active" in response.json().get("detail", "")

    # Clean up simulation
    sim.simulation_status = "STOPPED"
    db.commit()
