import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
from backend.models import Task, Warehouse, Item
from backend.routers.tasks import transition_status


def test_task_state_machine_transitions(db: Session):
    """Verifies that transition_status allows valid transitions and rejects invalid ones."""
    wh = Warehouse(id="WH-SM-1", name="SM WH")
    db.add(wh)
    db.commit()

    item = Item(id="ITM-SM", name="SM Item", weight_kg=1.0)
    db.add(item)
    db.commit()

    task = Task(
        task_number="TSK-SM-1", warehouse_id="WH-SM-1", task_type="PICK", product_id="ITM-SM",
        requested_quantity=1, status="QUEUED"
    )
    db.add(task)
    db.commit()

    # Valid: QUEUED -> ASSIGNED
    transition_status(db, task, "ASSIGNED", user_id=1, operator_name="AdminUser")
    assert task.status == "ASSIGNED"

    # Valid: ASSIGNED -> IN_PROGRESS
    transition_status(db, task, "IN_PROGRESS", user_id=1, operator_name="AdminUser")
    assert task.status == "IN_PROGRESS"

    # Invalid: IN_PROGRESS -> QUEUED (not in ALLOWED_TRANSITIONS)
    with pytest.raises(HTTPException) as exc:
        transition_status(db, task, "QUEUED", user_id=1, operator_name="AdminUser")
    assert exc.value.status_code == 409
    assert "Invalid task status transition" in exc.value.detail

    # Valid: IN_PROGRESS -> COMPLETED
    transition_status(db, task, "COMPLETED", user_id=1, operator_name="AdminUser")
    assert task.status == "COMPLETED"

    # Invalid: COMPLETED -> IN_PROGRESS (Terminal state)
    with pytest.raises(HTTPException) as exc:
        transition_status(db, task, "IN_PROGRESS", user_id=1, operator_name="AdminUser")
    assert exc.value.status_code == 409
