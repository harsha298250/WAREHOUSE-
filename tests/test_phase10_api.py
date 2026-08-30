import pytest
from sqlalchemy.orm import Session
from backend.models import User, Task, Robot, Warehouse, Item, WarehouseLocation
from backend.auth import hash_password


def get_token(client, username, password):
    r = client.post("/auth/login", json={"username": username, "password": password})
    assert r.status_code == 200
    return r.json()["access_token"]


def test_api_security_rbac_and_unauthorized_access(client, db: Session):
    """Verifies that dispatch control APIs enforce authentication and viewer RBAC restrictions."""
    # Seed items & warehouse
    wh = Warehouse(id="WH-API-TEST", name="API WH")
    db.add(wh)
    db.commit()

    item = Item(id="ITM-API", name="API Item")
    db.add(item)
    db.commit()

    loc = WarehouseLocation(id="LOC-API-1", warehouse_id="WH-API-TEST", location_type="CHARGING", x=12.0, y=5.0, zone="A", aisle="01", rack="01", shelf="01")
    db.add(loc)
    db.commit()

    robot = Robot(
        robot_code="ROB-API-A", name="Rob API A", warehouse_id="WH-API-TEST",
        current_x=1.0, current_y=1.0, battery_level=50.0, enabled=True, status="AVAILABLE"
    )
    db.add(robot)
    db.commit()

    task = Task(
        task_number="TSK-API-1", warehouse_id="WH-API-TEST", task_type="PICK", product_id="ITM-API",
        requested_quantity=1, status="QUEUED"
    )
    db.add(task)
    db.commit()

    # 1. Unauthenticated request rejection
    routes = [
        ("POST", "/ai/tasks/optimize-assignment"),
        ("POST", f"/ai/tasks/{task.id}/optimize-assignment"),
        ("POST", f"/robots/{robot.id}/charge"),
    ]

    for method, path in routes:
        r = client.post(path)
        assert r.status_code == 401, f"{path} should reject unauthenticated request with 401"

    # 2. Viewer role forbidden (403)
    viewer_token = get_token(client, "test_viewer", "TestViewer@123")
    headers_viewer = {"Authorization": f"Bearer {viewer_token}"}

    for method, path in routes:
        r = client.post(path, headers=headers_viewer)
        assert r.status_code == 403, f"{path} should forbid viewers with 403"

    # 3. Manager/Admin role allowed (200 or 422 if bounds check fail but authorized)
    manager_token = get_token(client, "test_manager", "TestManager@123")
    headers_manager = {"Authorization": f"Bearer {manager_token}"}

    # single task optimize single should complete successfully
    r = client.post(f"/ai/tasks/{task.id}/optimize-assignment", headers=headers_manager)
    assert r.status_code in (200, 422)  # Authorized!
