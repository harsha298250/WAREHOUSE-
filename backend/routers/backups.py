import logging
from typing import List, Optional
from datetime import datetime, UTC
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.auth import get_current_user, require_admin
from backend.models import User, BackupRecord
from backend import cloud_storage
from backend import audit_ledger as ledger

logger = logging.getLogger("warehouse.backups")

router = APIRouter(prefix="/api/backups", tags=["Backups"])


@router.get("")
def list_backups(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Lists all backup logs chronologically, accessible to authorized WMS users."""
    history = db.query(BackupRecord).order_by(BackupRecord.id.desc()).all()
    return [
        {
            "id": r.id,
            "backup_id": r.backup_id,
            "filename": r.filename,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "started_at": r.started_at.isoformat() if r.started_at else None,
            "completed_at": r.completed_at.isoformat() if r.completed_at else None,
            "size_bytes": r.size_bytes,
            "sha256": r.sha256,
            "status": r.status,
            "storage_key": r.storage_key,
            "storage_provider": r.storage_provider,
            "bucket": r.bucket,
            "verification_status": r.verification_status,
            "verification_at": r.verification_at.isoformat() if r.verification_at else None,
            "restore_test_status": r.restore_test_status,
            "restore_test_at": r.restore_test_at.isoformat() if r.restore_test_at else None,
            "backup_type": r.backup_type,
            "initiated_by": r.initiated_by,
            "error_message": r.error_message
        }
        for r in history
    ]


@router.get("/{backup_id}")
def get_backup(
    backup_id: str, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Fetches full metadata details for a specific backup record."""
    r = db.query(BackupRecord).filter(BackupRecord.backup_id == backup_id).first()
    if not r:
        raise HTTPException(status_code=404, detail=f"Backup record '{backup_id}' not found.")
        
    return {
        "id": r.id,
        "backup_id": r.backup_id,
        "filename": r.filename,
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "started_at": r.started_at.isoformat() if r.started_at else None,
        "completed_at": r.completed_at.isoformat() if r.completed_at else None,
        "size_bytes": r.size_bytes,
        "sha256": r.sha256,
        "status": r.status,
        "storage_key": r.storage_key,
        "storage_provider": r.storage_provider,
        "bucket": r.bucket,
        "verification_status": r.verification_status,
        "verification_at": r.verification_at.isoformat() if r.verification_at else None,
        "restore_test_status": r.restore_test_status,
        "restore_test_at": r.restore_test_at.isoformat() if r.restore_test_at else None,
        "backup_type": r.backup_type,
        "initiated_by": r.initiated_by,
        "error_message": r.error_message
    }


@router.post("")
def run_backup(
    background_tasks: BackgroundTasks,
    backup_type: str = "MANUAL",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Triggers database dump extraction and uploads to cloud storage.
    Enforces RBAC verification (Admin role only) and logs requests.
    """
    logger.info("Admin %s triggered backup of type %s", current_user.username, backup_type)
    
    # Audit request
    ledger.append_entry(db, "BACKUP_REQUESTED", {
        "initiated_by": current_user.username,
        "backup_type": backup_type,
        "timestamp": datetime.now(UTC).replace(tzinfo=None).isoformat()
    })
    
    # Check if Celery worker is enabled
    import os
    celery_enabled = os.getenv("CELERY_ENABLED", "false").lower() == "true"
    
    if celery_enabled:
        try:
            from backend.celery_app import execute_async_backup, safe_task_dispatch
            task = safe_task_dispatch(execute_async_backup, backup_type, current_user.username)
            task_id = getattr(task, "id", None)
            return {
                "status": "QUEUED",
                "message": "Logical database dump queued successfully in Celery task worker.",
                "task_id": task_id
            }
        except Exception as e:
            logger.error("Failed to queue backup in Celery worker: %s. Falling back to background thread.", e)
            
    # Fallback to local background tasks to avoid blocking the client thread
    # We pre-generate a unique backup ID to return immediately
    import secrets
    backup_id = f"BK-{secrets.token_hex(8).upper()}"
    
    def run_backup_job():
        # Open separate db session for the thread
        from backend.database import SessionLocal
        job_db = SessionLocal()
        try:
            cloud_storage.run_disaster_recovery_backup(
                db=job_db, 
                backup_type=backup_type, 
                initiated_by=current_user.username
            )
        except Exception as job_err:
            logger.error("Background thread backup job failed: %s", job_err)
        finally:
            job_db.close()
            
    background_tasks.add_task(run_backup_job)
    
    return {
        "status": "RUNNING",
        "backup_id": backup_id,
        "message": "Logical database dump initiated in local background worker thread."
    }


@router.post("/{backup_id}/verify")
def verify_backup(
    background_tasks: BackgroundTasks,
    backup_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Performs cryptographic validation of the backup package against database SHA-256 metadata.
    Enforces RBAC verification (Admin role only) and logs verification actions.
    """
    logger.info("Admin %s triggered verification for backup %s", current_user.username, backup_id)
    
    rec = db.query(BackupRecord).filter(BackupRecord.backup_id == backup_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail=f"Backup record '{backup_id}' not found.")
        
    # Audit request
    ledger.append_entry(db, "BACKUP_VERIFY_REQUESTED", {
        "initiated_by": current_user.username,
        "backup_id": backup_id,
        "timestamp": datetime.now(UTC).replace(tzinfo=None).isoformat()
    })
    
    import os
    celery_enabled = os.getenv("CELERY_ENABLED", "false").lower() == "true"
    
    if celery_enabled:
        try:
            from backend.celery_app import execute_async_verification, safe_task_dispatch
            task = safe_task_dispatch(execute_async_verification, backup_id)
            task_id = getattr(task, "id", None)
            return {
                "status": "QUEUED",
                "message": "Integrity checksum verification queued successfully in Celery task worker.",
                "task_id": task_id
            }
        except Exception as e:
            logger.error("Failed to queue verification in Celery: %s", e)
            
    # Fallback to local background task
    def run_verify_job():
        from backend.database import SessionLocal
        job_db = SessionLocal()
        try:
            cloud_storage.verify_backup_integrity(job_db, backup_id)
        except Exception as job_err:
            logger.error("Background thread verification job failed: %s", job_err)
        finally:
            job_db.close()
            
    background_tasks.add_task(run_verify_job)
    
    return {
        "status": "RUNNING",
        "message": "Integrity checksum verification initiated in background."
    }


@router.post("/{backup_id}/restore-test")
def run_restore_test(
    background_tasks: BackgroundTasks,
    backup_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Initiates dry-run restore validation within an isolated SQLite temporary database.
    Checks schema, integrity relationships, and seed records. Prevents production overwrites.
    """
    logger.info("Admin %s triggered dry-run restore test for backup %s", current_user.username, backup_id)
    
    rec = db.query(BackupRecord).filter(BackupRecord.backup_id == backup_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail=f"Backup record '{backup_id}' not found.")
        
    # Audit request
    ledger.append_entry(db, "BACKUP_RESTORE_TEST_STARTED", {
        "initiated_by": current_user.username,
        "backup_id": backup_id,
        "timestamp": datetime.now(UTC).replace(tzinfo=None).isoformat()
    })
    
    import os
    celery_enabled = os.getenv("CELERY_ENABLED", "false").lower() == "true"
    
    if celery_enabled:
        try:
            from backend.celery_app import execute_async_restore_test, safe_task_dispatch
            task = safe_task_dispatch(execute_async_restore_test, backup_id)
            task_id = getattr(task, "id", None)
            return {
                "status": "QUEUED",
                "message": "Restore dry-run validation queued successfully in Celery task worker.",
                "task_id": task_id
            }
        except Exception as e:
            logger.error("Failed to queue restore-test in Celery: %s", e)
            
    # Fallback to local background task
    def run_restore_test_job():
        from backend.database import SessionLocal
        job_db = SessionLocal()
        try:
            cloud_storage.run_backup_restore_test(job_db, backup_id)
        except Exception as job_err:
            logger.error("Background thread restore-test job failed: %s", job_err)
        finally:
            job_db.close()
            
    background_tasks.add_task(run_restore_test_job)
    
    return {
        "status": "RUNNING",
        "message": "Restore dry-run validation initiated in background."
    }
