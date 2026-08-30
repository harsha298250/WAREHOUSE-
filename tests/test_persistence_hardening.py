import pytest
from sqlalchemy import text
from backend.database import SessionLocal
from backend.models import Warehouse, Inventory, Order, OrderItem, Task, Robot, User, AuditLedger, WarehouseLocation, Item
from backend.auth import hash_password

def test_persistence_test_entity(db):
    """
    Perform an actual database persistence test:
    1. Create/update a warehouse entity.
    2. Commit it.
    3. Close the database session.
    4. Create a new session.
    5. Read the entity again.
    6. Verify the value persists.
    """
    # 1. Create warehouse
    wh = Warehouse(id="WH-TEST-PERSIST", name="Persistence Test WH", location="Test Land")
    db.add(wh)
    db.commit()
    db.close() # Close session

    # 2. Load in a new clean session
    new_db = SessionLocal()
    try:
        loaded = new_db.query(Warehouse).filter(Warehouse.id == "WH-TEST-PERSIST").first()
        assert loaded is not None
        assert loaded.name == "Persistence Test WH"
        assert loaded.location == "Test Land"
    finally:
        # Cleanup
        new_db.execute(text("DELETE FROM warehouses WHERE id = 'WH-TEST-PERSIST'"))
        new_db.commit()
        new_db.close()

def test_role_change_password_verification(client, db):
    """
    Test role change API authentication requirements:
    1. Incorrect admin password must reject role change with 403.
    2. Correct admin password must update role in database and write audit event.
    """
    # Seed fresh isolated admin and viewer users
    temp_admin = User(
        username="test_admin_hardening",
        password_hash=hash_password("HardeningAdmin@123"),
        role="admin",
        is_active=True
    )
    temp_viewer = User(
        username="test_viewer_hardening",
        password_hash=hash_password("HardeningViewer@123"),
        role="viewer",
        is_active=True
    )
    db.add_all([temp_admin, temp_viewer])
    db.commit()

    from backend.auth import create_access_token
    local_admin_token = create_access_token(data={"sub": temp_admin.username, "role": "admin"})

    # 1. Reject on incorrect password
    r = client.put(
        f"/users/{temp_viewer.id}/role",
        json={"role": "operator", "reason": "Hardening check", "confirm_password": "WRONG_PASSWORD"},
        headers={"Authorization": f"Bearer {local_admin_token}"}
    )
    assert r.status_code == 403
    assert "Incorrect administrator password" in r.json()["detail"]

    # Re-verify database didn't change
    db.refresh(temp_viewer)
    assert temp_viewer.role == "viewer"

    # 2. Allow on correct password
    r = client.put(
        f"/users/{temp_viewer.id}/role",
        json={"role": "operator", "reason": "Hardening check", "confirm_password": "HardeningAdmin@123"},
        headers={"Authorization": f"Bearer {local_admin_token}"}
    )
    assert r.status_code == 200
    
    # Verify database updated
    db.refresh(temp_viewer)
    assert temp_viewer.role == "operator"

    # Verify audit event created
    audit = db.query(AuditLedger).order_by(AuditLedger.id.desc()).first()
    assert audit is not None
    assert audit.event_type == "role_changed"
    assert "operator" in audit.details

    # Clean up
    db.delete(temp_admin)
    db.delete(temp_viewer)
    db.commit()

def test_invalid_foreign_key_robot_rejection(client, admin_token, db):
    """
    Test that creating a robot with a non-existent warehouse_id is rejected with 404.
    """
    r = client.post(
        "/robots",
        json={
            "robot_code": "BOT-INVALID-WH",
            "name": "Invalid Warehouse Bot",
            "warehouse_id": "WH-NONEXISTENT",
            "robot_type": "AGV",
            "max_payload": 150.0,
            "max_speed": 1.0,
            "enabled": True
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert r.status_code == 404
    assert "not found" in r.json()["detail"]

def test_invalid_inventory_quantity_rejection(client, admin_token, db):
    """
    Test that adjustments resulting in negative on-hand stock are rejected with 400.
    """
    # Create temp warehouse and item
    wh = Warehouse(id="WH-TEMP-INV", name="Temp Inv WH", location="Local")
    item = Item(id="ITM-TEMP-INV", name="Temp Item", category="parts", unit_cost=10.0, safety_stock=5)
    db.add_all([wh, item])
    db.commit()

    # Seed initial inventory
    inv = Inventory(warehouse_id="WH-TEMP-INV", item_id="ITM-TEMP-INV", on_hand=10, reserved=0, available=10)
    db.add(inv)
    db.commit()

    # Request manual negative adjustment exceeding current on-hand quantity (10 - 15 = -5)
    r = client.post(
        "/wms/inventory/adjust",
        json={
            "warehouse_id": "WH-TEMP-INV",
            "item_id": "ITM-TEMP-INV",
            "adjustment": -15,
            "reason": "Test negative check"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert r.status_code == 400
    assert "negative" in r.json()["detail"]

    # Re-verify stock didn't decrease below zero
    db.refresh(inv)
    assert inv.on_hand == 10

    # Clean up
    db.delete(inv)
    db.delete(item)
    db.delete(wh)
    db.commit()

def test_transaction_rollback_on_failure(db):
    """
    Verify transaction rollback in case of validation failures.
    """
    # Create temp items
    wh = Warehouse(id="WH-TX-ROLLBACK", name="Tx Rollback WH", location="Local")
    db.add(wh)
    db.commit()

    # Run query inside transaction
    session = SessionLocal()
    try:
        session.add(Warehouse(id="WH-TX-OK", name="Ok WH", location="Local"))
        session.flush()

        # Deliberate failure: insert duplicate key to trigger exception
        session.add(Warehouse(id="WH-TX-ROLLBACK", name="Duplicate WH", location="Local"))
        session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()

    # Check that OK WH was NOT committed (the entire transaction rolled back)
    check_session = SessionLocal()
    try:
        ok_wh = check_session.query(Warehouse).filter(Warehouse.id == "WH-TX-OK").first()
        assert ok_wh is None
    finally:
        check_session.execute(text("DELETE FROM warehouses WHERE id = 'WH-TX-ROLLBACK'"))
        check_session.commit()
        check_session.close()
