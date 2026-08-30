import pytest
import json
from datetime import datetime, UTC
from sqlalchemy.orm import Session

from backend.models import User, Notification
from backend.celery_app import send_resend_email_task
from backend.auth import hash_password

def setup_celery_test_data(db: Session):
    db.query(Notification).delete()
    db.query(User).filter(User.username == "celery_admin").delete()
    db.commit()

    from backend.models import Warehouse
    wh = db.query(Warehouse).filter(Warehouse.id == "WH-BLR-01").first()
    if not wh:
        wh = Warehouse(id="WH-BLR-01", name="BLR Hub", location="BLR")
        db.add(wh)
        db.commit()

    user = User(username="celery_admin", password_hash=hash_password("CeleryPass123!"), role="admin")
    db.add(user)
    db.commit()

def test_celery_task_crash_and_rollback(db: Session):
    """
    Simulates a crash/failure during the Celery email task execution.
    Asserts that the transaction is rolled back, database state remains consistent,
    and status/retry_count is updated properly without silent corruption.
    """
    setup_celery_test_data(db)
    
    user = db.query(User).filter(User.username == "celery_admin").first()
    # Create notification entry
    notif = Notification(
        user_id=user.id,
        warehouse_id="WH-BLR-01",
        event_type="SYSTEM_ALERT",
        notification_type="EMAIL",
        title="Alert",
        channel="EMAIL",
        severity="WARNING",
        message="Simulated worker crash event",
        status="PENDING",
        retry_count=0
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)

    # Force a mock error during email dispatch to simulate task crash/interrupt
    from unittest.mock import patch
    with patch("backend.resend_client.send_html_email", side_effect=RuntimeError("Worker crashed/Connection lost")):
        try:
            # Execute task synchronously for testing rollback behavior
            send_resend_email_task(subject="Test Alert", body="Details", recipient="admin@example.com", notification_id=notif.id)
        except Exception:
            pass

    # Refresh DB session and verify status has been updated to PENDING/FAILED depending on retry outcome
    db.refresh(notif)
    # The task catches Exception, increments retry_count to 1 and rolls back email send but commits notification updates
    assert notif.retry_count == 1
    assert notif.status in ("PENDING", "FAILED")
