"""
tests/test_claim_task_workflow.py

Master Automated Security & State Machine Verification Suite:
Covers all 20 required scenarios for Auth, User Roles, Operator DB ID assignment,
Order-Task-Operator connectivity, Assign/Claim workflows, and state machine enforcement.
"""

import os
import json
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from backend.main import app
from backend.database import get_db
from backend.models import User, Task, Order, OrderItem, Warehouse, Item, WarehouseLocation, Inventory
from backend.auth import hash_password

client = TestClient(app)


# Helper function to mock google verification
def mock_google_token_info(email: str, email_verified: bool = True, sub: str = "mock-google-sub-id"):
    return {
        "iss": "https://accounts.google.com",
        "aud": "mock-test-client-id",
        "email": email,
        "email_verified": email_verified,
        "sub": sub,
        "name": email.split("@")[0].title()
    }


@pytest.fixture(autouse=True)
def setup_google_oauth_env():
    """Ensure GOOGLE_CLIENT_ID is set for OAuth tests."""
    orig = os.environ.get("GOOGLE_CLIENT_ID")
    os.environ["GOOGLE_CLIENT_ID"] = "mock-test-client-id"
    yield
    if orig is None:
        os.environ.pop("GOOGLE_CLIENT_ID", None)
    else:
        os.environ["GOOGLE_CLIENT_ID"] = orig


@pytest.fixture
def admin_user(db):
    """Seed an admin user for task creation and order creation."""
    user = db.query(User).filter(User.username == "test_claim_admin").first()
    if not user:
        user = User(
            username="test_claim_admin",
            email="claim_admin@example.com",
            password_hash=hash_password("AdminPass123!"),
            role="admin",
            full_name="Claim Test Admin",
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@pytest.fixture
def admin_token(client, admin_user):
    r = client.post("/auth/login", json={"username": "test_claim_admin", "password": "AdminPass123!"})
    assert r.status_code == 200
    return r.json()["access_token"]


@pytest.fixture
def operator_a(db):
    """Seed Operator A."""
    user = db.query(User).filter(User.username == "test_operator_a").first()
    if not user:
        user = User(
            username="test_operator_a",
            email="operator_a@example.com",
            password_hash=hash_password("OperatorPass123!"),
            role="operator",
            full_name="Operator Alpha",
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@pytest.fixture
def operator_a_token(client, operator_a):
    r = client.post("/auth/login", json={"username": "test_operator_a", "password": "OperatorPass123!"})
    assert r.status_code == 200
    return r.json()["access_token"]


@pytest.fixture
def operator_b(db):
    """Seed Operator B."""
    user = db.query(User).filter(User.username == "test_operator_b").first()
    if not user:
        user = User(
            username="test_operator_b",
            email="operator_b@example.com",
            password_hash=hash_password("OperatorPass123!"),
            role="operator",
            full_name="Operator Bravo",
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@pytest.fixture
def operator_b_token(client, operator_b):
    r = client.post("/auth/login", json={"username": "test_operator_b", "password": "OperatorPass123!"})
    assert r.status_code == 200
    return r.json()["access_token"]


@pytest.fixture
def setup_claim_test_data(db):
    """Seed warehouse, item, locations, and inventory for claim testing."""
    wh = db.query(Warehouse).filter(Warehouse.id == "WH-CLAIM-01").first()
    if not wh:
        wh = Warehouse(id="WH-CLAIM-01", name="Claim Test Warehouse", location="Zone C")
        db.add(wh)

    item = db.query(Item).filter(Item.id == "ITM-CLAIM-01").first()
    if not item:
        item = Item(id="ITM-CLAIM-01", name="Claim Test Item", sku="SKU-CLAIM-01", unit_cost=15.0)
        db.add(item)

    loc_src = db.query(WarehouseLocation).filter(WarehouseLocation.id == "WH-CLAIM-01-A-01").first()
    if not loc_src:
        loc_src = WarehouseLocation(
            id="WH-CLAIM-01-A-01", warehouse_id="WH-CLAIM-01", zone="A", aisle="01", rack="01", shelf="01",
            location_type="STORAGE", x=1.0, y=1.0
        )
        db.add(loc_src)

    loc_dst = db.query(WarehouseLocation).filter(WarehouseLocation.id == "WH-CLAIM-01-B-01").first()
    if not loc_dst:
        loc_dst = WarehouseLocation(
            id="WH-CLAIM-01-B-01", warehouse_id="WH-CLAIM-01", zone="B", aisle="01", rack="01", shelf="01",
            location_type="PICKING", x=2.0, y=2.0
        )
        db.add(loc_dst)

    inv = db.query(Inventory).filter(
        Inventory.warehouse_id == "WH-CLAIM-01",
        Inventory.item_id == "ITM-CLAIM-01",
        Inventory.location_id == "WH-CLAIM-01-A-01"
    ).first()
    if not inv:
        inv = Inventory(
            warehouse_id="WH-CLAIM-01",
            item_id="ITM-CLAIM-01",
            location_id="WH-CLAIM-01-A-01",
            on_hand=100,
            available=100,
            reserved=0
        )
        db.add(inv)

    db.commit()


# ============================================================================
# Scenarios 1–5: Google OAuth & User Authorization
# ============================================================================

def test_1_authorized_active_google_user_login_succeeds(db):
    """1. Authorized active Google user login succeeds."""
    email = "active_google_op@example.com"
    existing = db.query(User).filter(User.email == email).first()
    if not existing:
        user = User(
            username=email, email=email, password_hash=hash_password("Pass123!"),
            role="operator", full_name="Active Google Op", is_active=True
        )
        db.add(user)
        db.commit()

    token_info = mock_google_token_info(email, sub="sub-active-google-1")
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(token_info).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        res = client.post("/auth/google-signin", json={"id_token": "valid-active-google-token"})
        assert res.status_code == 200
        assert "access_token" in res.json()
        assert res.json()["user"]["role"] == "operator"


def test_2_inactive_google_user_login_rejected(db):
    """2. Inactive Google user login rejected (HTTP 403)."""
    email = "inactive_google_user@example.com"
    existing = db.query(User).filter(User.email == email).first()
    if not existing:
        user = User(
            username=email, email=email, password_hash=hash_password("Pass123!"),
            role="operator", full_name="Inactive User", is_active=False
        )
        db.add(user)
        db.commit()
    else:
        existing.is_active = False
        db.commit()

    token_info = mock_google_token_info(email, sub="sub-inactive-google-2")
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(token_info).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        res = client.post("/auth/google-signin", json={"id_token": "inactive-google-token"})
        assert res.status_code == 403
        assert "deactivated" in res.json()["detail"].lower() or "disabled" in res.json()["detail"].lower()


def test_3_unknown_google_email_rejected(db):
    """3. Unknown Google email rejected (HTTP 403)."""
    email = "unknown_stranger_333@gmail.com"
    db.query(User).filter(User.email == email).delete()
    db.commit()

    token_info = mock_google_token_info(email, sub="sub-unknown-3")
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(token_info).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        res = client.post("/auth/google-signin", json={"id_token": "unknown-google-token"})
        assert res.status_code == 403
        assert "not authorized" in res.json()["detail"].lower()


def test_4_unknown_google_email_does_not_create_viewer_account(db):
    """4. Unknown Google email does not create VIEWER account."""
    email = "unknown_no_viewer_444@gmail.com"
    db.query(User).filter(User.email == email).delete()
    db.commit()

    count_before = db.query(User).count()
    token_info = mock_google_token_info(email, sub="sub-unknown-4")
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(token_info).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        res = client.post("/auth/google-signin", json={"id_token": "no-viewer-token"})
        assert res.status_code == 403

    count_after = db.query(User).count()
    assert count_before == count_after
    assert db.query(User).filter(User.email == email).first() is None


def test_5_unauthorized_user_cannot_enter_viewer_mode(db):
    """5. Unauthorized user cannot enter viewer mode or access protected endpoints."""
    res = client.get("/users")
    assert res.status_code == 401

    res_tasks = client.get("/tasks")
    assert res_tasks.status_code == 401


# ============================================================================
# Scenarios 6–15: Task Lifecycle, Ownership & State Machine Rules
# ============================================================================

def test_6_direct_queued_to_in_progress_returns_409(client, admin_token, operator_a_token, setup_claim_test_data):
    """6. Direct QUEUED → IN_PROGRESS returns HTTP 409."""
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    op_headers = {"Authorization": f"Bearer {operator_a_token}"}

    payload = {
        "warehouse_id": "WH-CLAIM-01", "task_type": "PUTAWAY", "product_id": "ITM-CLAIM-01",
        "source_location_id": "WH-CLAIM-01-A-01", "destination_location_id": "WH-CLAIM-01-B-01",
        "requested_quantity": 10, "notes": "Test QUEUED -> IN_PROGRESS"
    }
    create_res = client.post("/tasks", json=payload, headers=admin_headers)
    assert create_res.status_code == 201
    task_id = create_res.json()["task_id"]

    start_res = client.post(f"/tasks/{task_id}/start", headers=op_headers)
    assert start_res.status_code == 409
    assert "Invalid task status transition" in start_res.json()["detail"]


def test_7_direct_queued_to_completed_returns_409(client, admin_token, operator_a_token, setup_claim_test_data):
    """7. Direct QUEUED → COMPLETED returns HTTP 409."""
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    op_headers = {"Authorization": f"Bearer {operator_a_token}"}

    payload = {
        "warehouse_id": "WH-CLAIM-01", "task_type": "PUTAWAY", "product_id": "ITM-CLAIM-01",
        "source_location_id": "WH-CLAIM-01-A-01", "destination_location_id": "WH-CLAIM-01-B-01",
        "requested_quantity": 10, "notes": "Test QUEUED -> COMPLETED"
    }
    create_res = client.post("/tasks", json=payload, headers=admin_headers)
    assert create_res.status_code == 201
    task_id = create_res.json()["task_id"]

    comp_res = client.post(f"/tasks/{task_id}/complete", json={"completed_quantity": 10}, headers=op_headers)
    assert comp_res.status_code == 409


def test_8_assigning_operator_stores_correct_db_user_id(client, admin_token, operator_a, setup_claim_test_data):
    """8. Assigning operator stores correct DB user ID (assigned_user_id)."""
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    payload = {
        "warehouse_id": "WH-CLAIM-01", "task_type": "PUTAWAY", "product_id": "ITM-CLAIM-01",
        "source_location_id": "WH-CLAIM-01-A-01", "destination_location_id": "WH-CLAIM-01-B-01",
        "requested_quantity": 15
    }
    create_res = client.post("/tasks", json=payload, headers=admin_headers)
    assert create_res.status_code == 201
    task_id = create_res.json()["task_id"]

    assign_res = client.post(f"/tasks/{task_id}/assign", json={"assigned_user_id": operator_a.id}, headers=admin_headers)
    assert assign_res.status_code == 200
    assert assign_res.json()["assigned_user_id"] == operator_a.id

    detail_res = client.get(f"/tasks/{task_id}", headers=admin_headers)
    assert detail_res.json()["assigned_user_id"] == operator_a.id


def test_9_assigning_operator_keeps_task_status_queued(client, admin_token, operator_a, setup_claim_test_data):
    """9. Assigning operator keeps task status QUEUED."""
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    payload = {
        "warehouse_id": "WH-CLAIM-01", "task_type": "PUTAWAY", "product_id": "ITM-CLAIM-01",
        "source_location_id": "WH-CLAIM-01-A-01", "destination_location_id": "WH-CLAIM-01-B-01",
        "requested_quantity": 15
    }
    create_res = client.post("/tasks", json=payload, headers=admin_headers)
    task_id = create_res.json()["task_id"]

    assign_res = client.post(f"/tasks/{task_id}/assign", json={"assigned_user_id": operator_a.id}, headers=admin_headers)
    assert assign_res.status_code == 200
    assert assign_res.json()["task_status"] == "QUEUED"

    detail_res = client.get(f"/tasks/{task_id}", headers=admin_headers)
    assert detail_res.json()["status"] == "QUEUED"


def test_10_assigned_operator_claim_transitions_queued_to_assigned(client, admin_token, operator_a_token, operator_a, setup_claim_test_data):
    """10. Assigned operator claim transitions QUEUED → ASSIGNED."""
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    op_headers = {"Authorization": f"Bearer {operator_a_token}"}

    payload = {
        "warehouse_id": "WH-CLAIM-01", "task_type": "PUTAWAY", "product_id": "ITM-CLAIM-01",
        "source_location_id": "WH-CLAIM-01-A-01", "destination_location_id": "WH-CLAIM-01-B-01",
        "requested_quantity": 20
    }
    create_res = client.post("/tasks", json=payload, headers=admin_headers)
    task_id = create_res.json()["task_id"]

    client.post(f"/tasks/{task_id}/assign", json={"assigned_user_id": operator_a.id}, headers=admin_headers)

    claim_res = client.post(f"/tasks/{task_id}/claim", headers=op_headers)
    assert claim_res.status_code == 200
    assert claim_res.json()["task_status"] == "ASSIGNED"

    detail_res = client.get(f"/tasks/{task_id}", headers=op_headers)
    assert detail_res.json()["status"] == "ASSIGNED"


def test_11_operator_b_claiming_operator_a_assigned_task_returns_409(client, admin_token, operator_a, operator_b_token, setup_claim_test_data):
    """11. Operator B claiming Operator A's assigned task returns HTTP 409."""
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    op_b_headers = {"Authorization": f"Bearer {operator_b_token}"}

    payload = {
        "warehouse_id": "WH-CLAIM-01", "task_type": "PUTAWAY", "product_id": "ITM-CLAIM-01",
        "source_location_id": "WH-CLAIM-01-A-01", "destination_location_id": "WH-CLAIM-01-B-01",
        "requested_quantity": 25
    }
    create_res = client.post("/tasks", json=payload, headers=admin_headers)
    task_id = create_res.json()["task_id"]

    # Assign task to Operator A
    client.post(f"/tasks/{task_id}/assign", json={"assigned_user_id": operator_a.id}, headers=admin_headers)

    # Operator B attempts to claim Operator A's assigned task -> HTTP 409
    claim_res = client.post(f"/tasks/{task_id}/claim", headers=op_b_headers)
    assert claim_res.status_code == 409
    assert "assigned to another operator" in claim_res.json()["detail"].lower()


def test_12_assigned_to_in_progress_via_start_succeeds(client, admin_token, operator_a_token, operator_a, setup_claim_test_data):
    """12. ASSIGNED → IN_PROGRESS via /start succeeds."""
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    op_headers = {"Authorization": f"Bearer {operator_a_token}"}

    payload = {
        "warehouse_id": "WH-CLAIM-01", "task_type": "PUTAWAY", "product_id": "ITM-CLAIM-01",
        "source_location_id": "WH-CLAIM-01-A-01", "destination_location_id": "WH-CLAIM-01-B-01",
        "requested_quantity": 30
    }
    create_res = client.post("/tasks", json=payload, headers=admin_headers)
    task_id = create_res.json()["task_id"]

    client.post(f"/tasks/{task_id}/claim", headers=op_headers)

    start_res = client.post(f"/tasks/{task_id}/start", headers=op_headers)
    assert start_res.status_code == 200
    assert start_res.json()["status"] == "in_progress"

    detail_res = client.get(f"/tasks/{task_id}", headers=op_headers)
    assert detail_res.json()["status"] == "IN_PROGRESS"


def test_13_in_progress_to_completed_via_complete_succeeds(client, admin_token, operator_a_token, setup_claim_test_data):
    """13. IN_PROGRESS → COMPLETED via /complete succeeds."""
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    op_headers = {"Authorization": f"Bearer {operator_a_token}"}

    payload = {
        "warehouse_id": "WH-CLAIM-01", "task_type": "PUTAWAY", "product_id": "ITM-CLAIM-01",
        "source_location_id": "WH-CLAIM-01-A-01", "destination_location_id": "WH-CLAIM-01-B-01",
        "requested_quantity": 30
    }
    create_res = client.post("/tasks", json=payload, headers=admin_headers)
    task_id = create_res.json()["task_id"]

    client.post(f"/tasks/{task_id}/claim", headers=op_headers)
    client.post(f"/tasks/{task_id}/start", headers=op_headers)

    comp_res = client.post(f"/tasks/{task_id}/complete", json={"completed_quantity": 30}, headers=op_headers)
    assert comp_res.status_code == 200
    assert comp_res.json()["status"].lower() == "completed"

    detail_res = client.get(f"/tasks/{task_id}", headers=op_headers)
    assert detail_res.json()["status"] == "COMPLETED"


def test_14_completed_to_in_progress_returns_409(client, admin_token, operator_a_token, setup_claim_test_data):
    """14. COMPLETED → IN_PROGRESS returns HTTP 409."""
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    op_headers = {"Authorization": f"Bearer {operator_a_token}"}

    payload = {
        "warehouse_id": "WH-CLAIM-01", "task_type": "PUTAWAY", "product_id": "ITM-CLAIM-01",
        "source_location_id": "WH-CLAIM-01-A-01", "destination_location_id": "WH-CLAIM-01-B-01",
        "requested_quantity": 5
    }
    create_res = client.post("/tasks", json=payload, headers=admin_headers)
    task_id = create_res.json()["task_id"]

    client.post(f"/tasks/{task_id}/claim", headers=op_headers)
    client.post(f"/tasks/{task_id}/start", headers=op_headers)
    client.post(f"/tasks/{task_id}/complete", json={"completed_quantity": 5}, headers=op_headers)

    start_again = client.post(f"/tasks/{task_id}/start", headers=op_headers)
    assert start_again.status_code == 409


def test_15_completed_to_completed_returns_409(client, admin_token, operator_a_token, setup_claim_test_data):
    """15. COMPLETED → COMPLETED returns HTTP 409."""
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    op_headers = {"Authorization": f"Bearer {operator_a_token}"}

    payload = {
        "warehouse_id": "WH-CLAIM-01", "task_type": "PUTAWAY", "product_id": "ITM-CLAIM-01",
        "source_location_id": "WH-CLAIM-01-A-01", "destination_location_id": "WH-CLAIM-01-B-01",
        "requested_quantity": 5
    }
    create_res = client.post("/tasks", json=payload, headers=admin_headers)
    task_id = create_res.json()["task_id"]

    client.post(f"/tasks/{task_id}/claim", headers=op_headers)
    client.post(f"/tasks/{task_id}/start", headers=op_headers)
    client.post(f"/tasks/{task_id}/complete", json={"completed_quantity": 5}, headers=op_headers)

    comp_again = client.post(f"/tasks/{task_id}/complete", json={"completed_quantity": 5}, headers=op_headers)
    assert comp_again.status_code == 409


# ============================================================================
# Scenarios 16–20: Order → Task → Operator Synchronization
# ============================================================================

def test_16_order_creation_generates_correct_task(client, admin_token, db, setup_claim_test_data):
    """16. Order creation generates correct task."""
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    order_payload = {
        "customer_ref": "CUST-SCEN-16",
        "warehouse_id": "WH-CLAIM-01",
        "items": [{"item_id": "ITM-CLAIM-01", "requested_qty": 4}]
    }
    ord_res = client.post("/wms/orders", json=order_payload, headers=admin_headers)
    assert ord_res.status_code in (200, 201)
    order_id = ord_res.json()["order_id"]

    task = db.query(Task).filter(Task.order_id == order_id).first()
    assert task is not None
    assert task.task_type == "PICK"
    assert task.requested_quantity == 4


def test_17_task_contains_correct_order_id(client, admin_token, db, setup_claim_test_data):
    """17. Task contains correct order_id."""
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    order_payload = {
        "customer_ref": "CUST-SCEN-17",
        "warehouse_id": "WH-CLAIM-01",
        "items": [{"item_id": "ITM-CLAIM-01", "requested_qty": 2}]
    }
    ord_res = client.post("/wms/orders", json=order_payload, headers=admin_headers)
    order_id = ord_res.json()["order_id"]

    task = db.query(Task).filter(Task.order_id == order_id).first()
    assert task.order_id == order_id


def test_18_task_assigned_user_id_references_user_record(client, admin_token, operator_a_token, operator_a, db, setup_claim_test_data):
    """18. Task assigned_user_id references user record."""
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    op_headers = {"Authorization": f"Bearer {operator_a_token}"}

    order_payload = {
        "customer_ref": "CUST-SCEN-18",
        "warehouse_id": "WH-CLAIM-01",
        "items": [{"item_id": "ITM-CLAIM-01", "requested_qty": 3}]
    }
    ord_res = client.post("/wms/orders", json=order_payload, headers=admin_headers)
    order_id = ord_res.json()["order_id"]

    task = db.query(Task).filter(Task.order_id == order_id).first()
    client.post(f"/tasks/{task.id}/claim", headers=op_headers)

    db.refresh(task)
    assert task.assigned_user_id == operator_a.id
    assert task.assigned_user.username == operator_a.username


def test_19_tasks_table_api_displays_assigned_operator_username(client, admin_token, operator_a_token, operator_a, db, setup_claim_test_data):
    """19. Tasks table/API displays assigned operator username."""
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    op_headers = {"Authorization": f"Bearer {operator_a_token}"}

    order_payload = {
        "customer_ref": "CUST-SCEN-19",
        "warehouse_id": "WH-CLAIM-01",
        "items": [{"item_id": "ITM-CLAIM-01", "requested_qty": 1}]
    }
    ord_res = client.post("/wms/orders", json=order_payload, headers=admin_headers)
    order_id = ord_res.json()["order_id"]

    task = db.query(Task).filter(Task.order_id == order_id).first()
    client.post(f"/tasks/{task.id}/claim", headers=op_headers)

    detail_res = client.get(f"/tasks/{task.id}", headers=admin_headers)
    assert detail_res.status_code == 200
    d = detail_res.json()
    assert d["assigned_user_id"] == operator_a.id
    assert d["assigned_user_name"] == operator_a.username

    list_res = client.get("/tasks?warehouse_id=WH-CLAIM-01", headers=admin_headers)
    task_in_list = next((t for t in list_res.json()["tasks"] if t["id"] == task.id), None)
    assert task_in_list is not None
    assert task_in_list["assigned_user_name"] == operator_a.username


def test_20_cancelling_task_preserves_order_task_relationship(client, admin_token, db, setup_claim_test_data):
    """20. Cancelling task preserves order/task relationship."""
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    order_payload = {
        "customer_ref": "CUST-SCEN-20",
        "warehouse_id": "WH-CLAIM-01",
        "items": [{"item_id": "ITM-CLAIM-01", "requested_qty": 2}]
    }
    ord_res = client.post("/wms/orders", json=order_payload, headers=admin_headers)
    order_id = ord_res.json()["order_id"]

    task = db.query(Task).filter(Task.order_id == order_id).first()
    assert task is not None

    cancel_res = client.post(f"/tasks/{task.id}/cancel", headers=admin_headers)
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "cancelled"

    db.refresh(task)
    assert task.status == "CANCELLED"
    assert task.order_id == order_id

    order = db.query(Order).filter(Order.id == order_id).first()
    assert order is not None
    assert order.status == "PICKING_FAILED"
