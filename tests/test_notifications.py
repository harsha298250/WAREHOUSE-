import pytest
from datetime import datetime, timedelta
from backend.models import User, Notification, NotificationPreference, UserWarehouseAccess
from backend.event_processor import publish_event, get_user_preference
from tests.conftest import TestSessionLocal as SessionLocal
from backend.auth import hash_password

@pytest.fixture
def test_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True)
def clear_login_limits():
    try:
        from backend.main import _login_attempts
        _login_attempts.clear()
    except ImportError:
        pass
    yield
    try:
        from backend.main import _login_attempts
        _login_attempts.clear()
    except ImportError:
        pass

@pytest.fixture(autouse=True)
def seed_test_users_local(test_db):
    from backend.models import Warehouse
    wh = test_db.query(Warehouse).filter(Warehouse.id == "WH-BLR-01").first()
    if not wh:
        wh = Warehouse(id="WH-BLR-01", name="Bengaluru Warehouse", location="Bengaluru")
        test_db.add(wh)

    # Seed isolated admin user
    admin = test_db.query(User).filter(User.username == "notif_admin").first()
    if not admin:
        admin = User(
            username="notif_admin",
            email="admin@example.com",
            password_hash=hash_password("TestAdmin@123"),
            role="admin",
            is_active=True,
            is_verified=True
        )
        test_db.add(admin)
    else:
        admin.is_active = True
        admin.password_hash = hash_password("TestAdmin@123")
        admin.failed_login_count = 0
        admin.locked_until = None
    
    # Seed staff user
    staff = test_db.query(User).filter(User.username == "test_staff").first()
    if not staff:
        staff = User(
            username="test_staff",
            email="staff@example.com",
            password_hash=hash_password("TestStaff@123"),
            role="staff",
            is_active=True,
            is_verified=True
        )
        test_db.add(staff)
    else:
        staff.is_active = True
        staff.password_hash = hash_password("TestStaff@123")
        staff.failed_login_count = 0
        staff.locked_until = None
        
    test_db.commit()

@pytest.fixture
def auth_headers(client, test_db):
    admin = test_db.query(User).filter(User.username == "notif_admin").first()
    if not admin:
        admin = User(
            username="notif_admin",
            email="admin@example.com",
            password_hash=hash_password("TestAdmin@123"),
            role="admin",
            is_active=True,
            is_verified=True
        )
        test_db.add(admin)
    else:
        admin.is_active = True
        admin.failed_login_count = 0
        admin.locked_until = None
        admin.password_hash = hash_password("TestAdmin@123")
    test_db.commit()

    r = client.post("/auth/login", json={"username": "notif_admin", "password": "TestAdmin@123"})
    assert r.status_code == 200, f"auth_headers login failed: {r.status_code} {r.text}"
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def staff_headers(client, test_db):
    staff = test_db.query(User).filter(User.username == "test_staff").first()
    if not staff:
        staff = User(
            username="test_staff",
            email="staff@example.com",
            password_hash=hash_password("TestStaff@123"),
            role="staff",
            is_active=True,
            is_verified=True
        )
        test_db.add(staff)
    else:
        staff.is_active = True
        staff.failed_login_count = 0
        staff.locked_until = None
        staff.password_hash = hash_password("TestStaff@123")
    test_db.commit()

    r = client.post("/auth/login", json={"username": "test_staff", "password": "TestStaff@123"})
    assert r.status_code == 200, f"staff_headers login failed: {r.status_code} {r.text}"
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

class TestNotificationSystem:

    def test_publish_event_persists_in_app(self, test_db):
        admin = test_db.query(User).filter(User.username == "notif_admin").first()
        assert admin is not None

        # Clean existing notifications for notif_admin
        test_db.query(Notification).filter(Notification.user_id == admin.id).delete()
        test_db.commit()

        # Publish security event
        publish_event(
            db=test_db,
            event_type="PASSWORD_CHANGED",
            warehouse_id=None,
            source_entity_type="USER",
            source_entity_id=str(admin.id),
            severity="WARNING",
            payload={"message": "Password changed successfully."}
        )

        # Verify notification record was persisted
        notif = test_db.query(Notification).filter(
            Notification.user_id == admin.id,
            Notification.event_type == "PASSWORD_CHANGED"
        ).first()

        assert notif is not None
        assert notif.channel == "IN_APP"
        assert notif.severity == "WARNING"
        assert notif.status == "DELIVERED"
        assert "Password changed" in notif.message

    def test_deduplication_policy(self, test_db):
        admin = test_db.query(User).filter(User.username == "notif_admin").first()
        assert admin is not None

        # Clear notifications
        test_db.query(Notification).filter(Notification.user_id == admin.id).delete()
        test_db.commit()

        # Publish first event
        publish_event(
            db=test_db,
            event_type="ORDER_EXCEPTION",
            warehouse_id=None,
            source_entity_type="ORDER",
            source_entity_id="ORD-001",
            severity="WARNING",
            payload={"message": "Order exception occurred"}
        )

        # Publish identical second event (duplicate)
        publish_event(
            db=test_db,
            event_type="ORDER_EXCEPTION",
            warehouse_id=None,
            source_entity_type="ORDER",
            source_entity_id="ORD-001",
            severity="WARNING",
            payload={"message": "Order exception occurred"}
        )

        # Count notifications
        count = test_db.query(Notification).filter(
            Notification.user_id == admin.id,
            Notification.event_type == "ORDER_EXCEPTION",
            Notification.channel == "IN_APP"
        ).count()

        # Deduplication must filter out the second event
        assert count == 1

    def test_preferences_api_endpoints(self, client, auth_headers):
        # 1. Fetch preferences
        r = client.get("/notification-preferences", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert "preferences" in data
        assert len(data["preferences"]) > 0

        # 2. Update preferences
        pref_payload = {
            "preferences": [
                {
                    "category": "orders",
                    "in_app_enabled": True,
                    "email_enabled": False,
                    "min_severity": "WARNING"
                }
            ]
        }
        r = client.put("/notification-preferences", json=pref_payload, headers=auth_headers)
        assert r.status_code == 200

        # Verify preference was updated
        r = client.get("/notification-preferences", headers=auth_headers)
        assert r.status_code == 200
        prefs = r.json()["preferences"]
        order_pref = next(p for p in prefs if p["category"] == "orders")
        assert order_pref["email_enabled"] is False
        assert order_pref["min_severity"] == "WARNING"

    def test_idor_protection(self, client, auth_headers, staff_headers, test_db):
        admin = test_db.query(User).filter(User.username == "notif_admin").first()
        staff = test_db.query(User).filter(User.username == "test_staff").first()

        # Clear notifications
        test_db.query(Notification).delete()
        test_db.commit()

        # Create a notification for Admin (owner is admin)
        notif = Notification(
            user_id=admin.id,
            event_type="SYSTEM_WARNING",
            notification_type="SYSTEM_ALERT",
            title="Admin Alert",
            message="Secret admin update.",
            severity="WARNING",
            status="DELIVERED",
            channel="IN_APP"
        )
        test_db.add(notif)
        test_db.commit()

        # Staff (non-owner) tries to view admin's notification details (IDOR attempt)
        r = client.get(f"/notifications/{notif.id}", headers=staff_headers)
        assert r.status_code == 403

        # Staff tries to mark read admin's notification
        r = client.post(f"/notifications/{notif.id}/read", headers=staff_headers)
        assert r.status_code == 403

        # Admin (owner) views it successfully
        r = client.get(f"/notifications/{notif.id}", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["title"] == "Admin Alert"

    def test_admin_history_permissions(self, client, auth_headers, staff_headers):
        # Admin gets full notification history
        r = client.get("/notification-history", headers=auth_headers)
        assert r.status_code == 200

        # Staff has no VIEW_AUDIT permissions so history access is blocked
        r = client.get("/notification-history", headers=staff_headers)
        assert r.status_code == 403

    def test_full_notification_lifecycle_read_unread_mark_all(self, client, auth_headers, test_db):
        admin = test_db.query(User).filter(User.username == "notif_admin").first()
        assert admin is not None

        # Clean existing notifications for notif_admin
        test_db.query(Notification).filter(Notification.user_id == admin.id).delete()
        test_db.commit()

        # 1. Create 3 notifications
        n1 = Notification(user_id=admin.id, event_type="TEST_1", notification_type="TEST", title="T1", message="M1", severity="INFO", status="DELIVERED", channel="IN_APP")
        n2 = Notification(user_id=admin.id, event_type="TEST_2", notification_type="TEST", title="T2", message="M2", severity="WARNING", status="DELIVERED", channel="IN_APP")
        n3 = Notification(user_id=admin.id, event_type="TEST_3", notification_type="TEST", title="T3", message="M3", severity="HIGH", status="DELIVERED", channel="IN_APP")
        test_db.add_all([n1, n2, n3])
        test_db.commit()

        # 2. GET unread count -> 3
        r = client.get("/notifications/unread-count", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["unread_count"] == 3

        # 3. Mark n1 read -> unread count 2
        r = client.post(f"/notifications/{n1.id}/read", headers=auth_headers)
        assert r.status_code == 200
        r_cnt = client.get("/notifications/unread-count", headers=auth_headers)
        assert r_cnt.json()["unread_count"] == 2

        # 4. Mark n1 unread -> unread count 3
        r = client.post(f"/notifications/{n1.id}/unread", headers=auth_headers)
        assert r.status_code == 200
        r_cnt = client.get("/notifications/unread-count", headers=auth_headers)
        assert r_cnt.json()["unread_count"] == 3

        # 5. Mark all read -> unread count 0
        r = client.post("/notifications/mark-all-read", headers=auth_headers)
        assert r.status_code == 200
        r_cnt = client.get("/notifications/unread-count", headers=auth_headers)
        assert r_cnt.json()["unread_count"] == 0

        # Verify DB status
        test_db.refresh(n1)
        assert n1.status == "READ"
        assert n1.read_at is not None

    def test_event_generated_notification_trigger(self, test_db):
        import time
        from backend.notifications import send_change_alert
        admin = test_db.query(User).filter(User.username == "notif_admin").first()
        if not admin:
            admin = User(
                username="notif_admin",
                email="admin@example.com",
                password_hash=hash_password("TestAdmin@123"),
                role="admin",
                is_active=True,
                is_verified=True
            )
            test_db.add(admin)
        else:
            admin.is_active = True
        test_db.commit()

        # Clean existing notifications and preference overrides for notif_admin
        test_db.query(Notification).filter(Notification.user_id == admin.id).delete()
        test_db.query(NotificationPreference).filter(NotificationPreference.user_id == admin.id).delete()
        test_db.commit()

        unique_ord_id = f"ORD-{int(time.time()*1000)}"

        # Trigger event notification
        res = send_change_alert("Order Created", details={"warehouse_id": "WH-BLR-01", "order_id": unique_ord_id, "message": f"Order {unique_ord_id} placed successfully"})
        assert res is True

        # Query database for generated notification
        notif = test_db.query(Notification).filter(
            Notification.user_id == admin.id,
            Notification.event_type == "ORDER_CREATED"
        ).first()

        assert notif is not None
        assert notif.channel == "IN_APP"
        assert unique_ord_id in notif.message
