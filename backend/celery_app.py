import os
import logging
from datetime import datetime, date, timezone, UTC
from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("warehouse.celery")

# Read broker and backend URLs
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672//")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Setup Celery client (uses RabbitMQ for messaging/broker and Redis for result storage)
backend_url = REDIS_URL
if backend_url.startswith("rediss://") and "ssl_cert_reqs" not in backend_url:
    sep = "&" if "?" in backend_url else "?"
    backend_url = f"{backend_url}{sep}ssl_cert_reqs=none"

celery = Celery(
    "warehouse_tasks",
    broker=RABBITMQ_URL,
    backend=backend_url
)


from backend.timeout_policy import REDIS_CONNECT_TIMEOUT, REDIS_SOCKET_TIMEOUT

# Standard configurations
celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300, # 5 minutes max per task
    task_soft_time_limit=240,
    broker_connection_timeout=5.0,  # fail fast on broker connection (seconds)
    broker_connection_max_retries=1, # do not retry connection indefinitely
    broker_transport_options={
        'max_retries': 1,
        'interval_start': 0.1,
        'interval_step': 0.2,
        'interval_max': 0.5,
    },
    redis_socket_timeout=REDIS_SOCKET_TIMEOUT,
    redis_socket_connect_timeout=REDIS_CONNECT_TIMEOUT,
    result_backend_transport_options={
        "socket_timeout": REDIS_SOCKET_TIMEOUT,
        "socket_connect_timeout": REDIS_CONNECT_TIMEOUT,
        "retry_policy": {
            "max_retries": 2
        }
    }
)

# Configure Celery Beat scheduler for automated daily backups and periodic health scans
celery.conf.beat_schedule = {
    "daily-disaster-recovery-backup": {
        "task": "backend.celery_app.execute_disaster_recovery_backup_task",
        "schedule": crontab(hour=0, minute=0), # Run every day at midnight UTC
    },
    "collect-health-telemetry-snapshots": {
        "task": "backend.celery_app.collect_health_telemetry_task",
        "schedule": 30.0, # Run every 30 seconds
    }
}


@celery.task(bind=True, max_retries=3, default_retry_delay=10)
def send_resend_email_task(self, subject: str, body: str, recipient: str, notification_id: int):
    """
    Celery background task to dispatch transactional email via Resend provider.
    Includes automated retry policy for handling transient connection errors.
    """
    from backend.database import SessionLocal
    from backend.models import Notification
    from backend import resend_client
    
    logger.info("Executing Celery email task for notification ID: %s", notification_id)
    db = SessionLocal()
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    
    if not notif:
        logger.error("Notification record %s not found in database.", notification_id)
        db.close()
        return
        
    try:
        # Track metric for Prometheus
        from backend.routers.metrics import CELERY_TASKS_TOTAL
        CELERY_TASKS_TOTAL.labels(task_name="send_resend_email", status="running").inc()
        
        success = resend_client.send_html_email(subject, body, recipient)
        
        if success:
            notif.status = "SENT"
            notif.delivered_at = datetime.now(UTC).replace(tzinfo=None)
            CELERY_TASKS_TOTAL.labels(task_name="send_resend_email", status="success").inc()
            logger.info("Celery email delivery successful for: %s", recipient)
        else:
            raise Exception("Resend API delivery failed (returned False)")
            
    except Exception as e:
        logger.warning("Celery email delivery failed (attempt %s/%s): %s", self.request.retries + 1, self.max_retries, e)
        notif.retry_count = self.request.retries + 1
        db.commit()
        
        # Increment failure status
        from backend.routers.metrics import CELERY_TASKS_TOTAL
        CELERY_TASKS_TOTAL.labels(task_name="send_resend_email", status="failed").inc()
        
        # Retry task if attempts are remaining
        try:
            self.retry(exc=e)
        except Exception as retry_exc:
            notif.status = "FAILED"
            notif.failed_at = datetime.now(UTC).replace(tzinfo=None)
            db.commit()
            raise retry_exc
    finally:
        db.commit()
        db.close()


@celery.task
def generate_pdf_report_task(warehouse_id: str, report_type: str, date_range: str):
    """Celery background task to generate inventory PDF reports."""
    from backend.database import SessionLocal
    from backend.reports import generate_pdf_report
    
    logger.info("Generating PDF report for warehouse %s, type: %s", warehouse_id, report_type)
    db = SessionLocal()
    try:
        from backend.routers.metrics import CELERY_TASKS_TOTAL
        CELERY_TASKS_TOTAL.labels(task_name="generate_pdf_report", status="running").inc()
        
        # Run report PDF generation logic
        # For demo purposes, we call the PDF report logic
        # Actual PDF builder should save the file keys
        result = generate_pdf_report(db, warehouse_id, report_type, date_range)
        
        CELERY_TASKS_TOTAL.labels(task_name="generate_pdf_report", status="success").inc()
        logger.info("PDF report generation completed successfully.")
        return result
    except Exception as e:
        from backend.routers.metrics import CELERY_TASKS_TOTAL
        CELERY_TASKS_TOTAL.labels(task_name="generate_pdf_report", status="failed").inc()
        logger.error("Failed to generate PDF report: %s", e)
        raise e
    finally:
        db.close()


@celery.task
def run_forecasting_calculation_task(warehouse_id: str, item_id: str):
    """Celery background task to calculate forecasting and cache outcomes in Redis."""
    from backend.database import SessionLocal
    from ml.forecast import forecast_item
    from backend import redis_client
    
    logger.info("Executing Celery forecasting task for %s / %s", warehouse_id, item_id)
    db = SessionLocal()
    try:
        from backend.routers.metrics import CELERY_TASKS_TOTAL
        CELERY_TASKS_TOTAL.labels(task_name="run_forecasting", status="running").inc()
        
        # Execute forecasting logic
        results = forecast_item(db, warehouse_id, item_id)
        
        # Cache results in Redis for 1 hour (3600 seconds)
        cache_key = f"forecast:{warehouse_id}:{item_id}"
        redis_client.set_cache(cache_key, results, ttl_seconds=3600)
        
        CELERY_TASKS_TOTAL.labels(task_name="run_forecasting", status="success").inc()
        logger.info("Forecast calculations complete and cached in Redis.")
        return results
    except Exception as e:
        from backend.routers.metrics import CELERY_TASKS_TOTAL
        CELERY_TASKS_TOTAL.labels(task_name="run_forecasting", status="failed").inc()
        logger.error("Forecasting job calculation failed: %s", e)
        raise e
    finally:
        db.close()


@celery.task
def execute_disaster_recovery_backup_task():
    """Daily database logical backup routine run in background."""
    from backend.database import SessionLocal
    from backend import cloud_storage
    from backend import audit_ledger
    from backend.models import AuditLedger
    
    logger.info("Executing Celery background auto-cloud backup task...")
    db = SessionLocal()
    try:
        from backend.routers.metrics import CELERY_TASKS_TOTAL
        CELERY_TASKS_TOTAL.labels(task_name="auto_cloud_backup", status="running").inc()
        
        # Trigger disaster recovery logical backup
        result = cloud_storage.run_disaster_recovery_backup(db)
        
        if result.get("status") == "SUCCESS":
            audit_ledger.append_entry(db, "auto_cloud_backup", {
                "backup_id": result.get("backup_id"),
                "file_key": result.get("file_key"),
                "sha256": result.get("sha256"),
                "size_kb": result.get("size_kb"),
                "triggered_by": "celery_worker"
            })
            CELERY_TASKS_TOTAL.labels(task_name="auto_cloud_backup", status="success").inc()
            logger.info("Celery Auto-Backup completed successfully: %s", result.get("file_key"))
            return result
        else:
            raise Exception(result.get("message", "Unknown backup error"))
    except Exception as e:
        from backend.routers.metrics import CELERY_TASKS_TOTAL
        CELERY_TASKS_TOTAL.labels(task_name="auto_cloud_backup", status="failed").inc()
        logger.error("Celery Auto-Backup failed: %s", e)
        raise e
    finally:
        db.close()


@celery.task
def execute_async_backup(backup_type: str, username: str):
    """Asynchronous manual backup task."""
    from backend.database import SessionLocal
    from backend import cloud_storage
    from backend import audit_ledger
    logger.info("Executing Celery background async backup task...")
    db = SessionLocal()
    try:
        result = cloud_storage.run_disaster_recovery_backup(db, backup_type=backup_type, initiated_by=username)
        if result.get("status") in ("UPLOADED", "SUCCESS"):
            audit_ledger.append_entry(db, "BACKUP_COMPLETED", {
                "backup_id": result.get("backup_id"),
                "file_key": result.get("file_key"),
                "sha256": result.get("sha256"),
                "size_kb": result.get("size_kb"),
                "triggered_by": username
            })
            return result
        else:
            raise Exception(result.get("message"))
    except Exception as e:
        logger.error("Celery async backup failed: %s", e)
        raise e
    finally:
        db.close()


@celery.task
def execute_async_verification(backup_id: str):
    """Asynchronous backup integrity verification task."""
    from backend.database import SessionLocal
    from backend import cloud_storage
    logger.info("Executing Celery background integrity verification task for %s...", backup_id)
    db = SessionLocal()
    try:
        result = cloud_storage.verify_backup_integrity(db, backup_id)
        if result.get("status") == "SUCCESS":
            return result
        else:
            raise Exception(result.get("message"))
    except Exception as e:
        logger.error("Celery async verification failed: %s", e)
        raise e
    finally:
        db.close()


@celery.task
def execute_async_restore_test(backup_id: str):
    """Asynchronous restore test execution task."""
    from backend.database import SessionLocal
    from backend import cloud_storage
    logger.info("Executing Celery background dry-run restore test task for %s...", backup_id)
    db = SessionLocal()
    try:
        result = cloud_storage.run_backup_restore_test(db, backup_id)
        if result.get("status") == "SUCCESS":
            return result
        else:
            raise Exception(result.get("message"))
    except Exception as e:
        logger.error("Celery async restore test failed: %s", e)
        raise e
    finally:
        db.close()


@celery.task
def execute_experiment_task(experiment_id: int):
    """Celery background task to execute a Scenario Lab experiment run series.
    
    This function is safe to call both as:
    - A Celery task: execute_experiment_task.delay(experiment_id)
    - A plain thread function: threading.Thread(target=execute_experiment_task, args=(experiment_id,))
    """
    import time
    from backend.database import SessionLocal
    from backend.models import Experiment, Scenario, ExperimentRun
    from backend.experiment_runner import execute_single_repetition, aggregate_experiment_runs
    
    logger.info("Executing experiment task for ID: %s", experiment_id)
    db = SessionLocal()
    
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not experiment:
        logger.error("Experiment record %s not found in database.", experiment_id)
        db.close()
        return
        
    try:
        # Metrics counter — safe to skip if not in Celery worker context
        try:
            from backend.routers.metrics import CELERY_TASKS_TOTAL
            CELERY_TASKS_TOTAL.labels(task_name="execute_experiment", status="running").inc()
        except Exception:
            pass
        
        experiment.status = "RUNNING"
        experiment.started_at = datetime.now(UTC).replace(tzinfo=None)
        db.commit()
        
        scenario = experiment.scenario
        config = scenario.configuration
        
        run_results = []
        
        for idx in range(1, experiment.repetitions + 1):
            # Create ExperimentRun
            run_rec = ExperimentRun(
                experiment_id=experiment.id,
                repetition_number=idx,
                random_seed=experiment.random_seed + idx,
                status="RUNNING",
                started_at=datetime.now(UTC).replace(tzinfo=None)
            )
            db.add(run_rec)
            db.commit()
            
            # Run repetition
            t_start = time.time()
            result = execute_single_repetition(
                prod_db_session=db,
                warehouse_id=scenario.warehouse_id,
                scenario_type=scenario.scenario_type,
                config=config,
                algorithm_name=experiment.algorithm_name,
                seed=run_rec.random_seed
            )
            t_end = time.time()
            
            run_rec.completed_at = datetime.now(UTC).replace(tzinfo=None)
            run_rec.duration_seconds = t_end - t_start
            
            if result["status"] == "COMPLETED":
                run_rec.status = "COMPLETED"
                run_rec.metrics = result["metrics"]
                run_results.append(result["metrics"])
            else:
                run_rec.status = "FAILED"
                run_rec.error_message = result.get("error", "Repetition run execution failed.")
                
            db.commit()
            
        # Aggregate results
        if run_results:
            summary = aggregate_experiment_runs(run_results)
            experiment.metrics_summary = summary
            experiment.status = "COMPLETED"
        else:
            experiment.status = "FAILED"
            experiment.error_message = "All repetition runs failed."
            
        experiment.completed_at = datetime.now(UTC).replace(tzinfo=None)
        experiment.duration_seconds = (experiment.completed_at - experiment.started_at).total_seconds()
        db.commit()
        
        # Publish completion event — safe to skip if not available
        try:
            from backend import event_processor
            event_processor.publish_event(
                db=db,
                event_type="SIMULATION_COMPLETED",
                warehouse_id=scenario.warehouse_id,
                source_entity_type="EXPERIMENT",
                source_entity_id=str(experiment.id),
                severity="SUCCESS",
                payload={"message": f"Scenario lab experiment '{experiment.experiment_name}' completed successfully."}
            )
        except Exception as ep_err:
            logger.warning("Event processor publish failed (non-critical): %s", ep_err)
        
        # Metrics counter success — safe to skip outside Celery
        try:
            from backend.routers.metrics import CELERY_TASKS_TOTAL
            CELERY_TASKS_TOTAL.labels(task_name="execute_experiment", status="success").inc()
        except Exception:
            pass
        logger.info("Experiment task %s completed successfully.", experiment_id)
        
    except Exception as e:
        try:
            from backend.routers.metrics import CELERY_TASKS_TOTAL
            CELERY_TASKS_TOTAL.labels(task_name="execute_experiment", status="failed").inc()
        except Exception:
            pass
        logger.error("Experiment task %s execution failed: %s", experiment_id, e)
        try:
            db.rollback()
            experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
            if experiment:
                experiment.status = "FAILED"
                experiment.error_message = str(e)
                experiment.completed_at = datetime.now(UTC).replace(tzinfo=None)
                db.commit()
        except Exception as commit_err:
            logger.error("Failed to commit FAILED status for experiment: %s", commit_err)
            try:
                db.rollback()
            except Exception:
                pass
    finally:
        db.close()



@celery.task
def collect_health_telemetry_task():
    """
    Celery periodic task to collect and record health snapshots in database.
    Retains only the last 24 hours of data.
    """
    from backend.database import SessionLocal
    from backend.routers.health import perform_deep_telemetry
    from backend.models import SystemHealthSnapshot
    from datetime import timedelta, UTC
    
    logger.info("Executing periodic health metrics collection task...")
    db = SessionLocal()
    try:
        telemetry = perform_deep_telemetry(db)
        
        # Insert snapshots
        for service, info in telemetry.items():
            if isinstance(info, dict) and "status" in info:
                snapshot = SystemHealthSnapshot(
                    service=service,
                    status=info["status"],
                    latency_ms=info.get("latency_ms"),
                    timestamp=datetime.now(UTC).replace(tzinfo=None)
                )
                db.add(snapshot)
                
        # Clean up old snapshots (older than 24 hours)
        cutoff = datetime.now(UTC).replace(tzinfo=None) - timedelta(hours=24)
        db.query(SystemHealthSnapshot).filter(SystemHealthSnapshot.timestamp < cutoff).delete()
        
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error("Health metrics collection task failed: %s", e)
    finally:
        db.close()


@celery.task(max_retries=3, default_retry_delay=10)
def send_generic_email_task(subject: str, html_body: str, recipient: str):
    """
    Celery background task to dispatch any HTML email via Resend client.
    """
    from backend import resend_client
    logger.info("Executing Celery generic email task for recipient: %s", recipient)
    try:
        success = resend_client.send_html_email(subject, html_body, recipient)
        if not success:
            raise Exception("Resend API delivery failed (returned False)")
    except Exception as e:
        logger.warning("Celery generic email task failed: %s", e)
        raise e


