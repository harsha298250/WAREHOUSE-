"""
main.py — Cloud-Based Smart Warehouse Automation API (PostgreSQL + JWT auth edition)
Refactored and modularized using APIRouters under routers/.
"""
import sys
import os
import time
import logging
import threading
from contextlib import asynccontextmanager

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize logging at the very top so all imported modules use it
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("warehouse")

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.database import engine
from backend import cloud_storage

# Import Routers
from backend.sentry import init_sentry

from backend.routers import auth, warehouses, ai, apps, reports, health, wms, tasks, robots, pathfinding, digital_twin, security, notifications, metrics, ai_assistant, or_tools_scheduler, backups, analytics, scenarios, simulation, settings, decision_support

# Re-export state variables for tests compatibility
from backend.routers.auth import _login_attempts, _pending_password_changes


# Thread lifecycle control events for background workers
BACKUP_WORKER_STOP_EVENT = threading.Event()
HEALTH_WORKER_STOP_EVENT = threading.Event()
SIMULATION_WORKER_STOP_EVENT = threading.Event()

BACKUP_WORKER_THREAD = None
HEALTH_WORKER_THREAD = None
SIMULATION_WORKER_THREAD = None


def schedule_backups_worker():
    # Only run backup worker if Celery worker is NOT enabled (fallback mode)
    if os.getenv("CELERY_ENABLED", "false").lower() == "true":
        logger.info("Celery scheduling is enabled. Background thread backup worker deactivated.")
        return
        
    # Wait for application startup
    if BACKUP_WORKER_STOP_EVENT.wait(timeout=5):
        return
    logger.info("Background Auto-Backup scheduler active.")
    
    while not BACKUP_WORKER_STOP_EVENT.is_set():
        try:
            from sqlalchemy.orm import sessionmaker
            from backend import audit_ledger
            from backend.models import AuditLedger
            from datetime import datetime, date, timezone, UTC
            
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            db = SessionLocal()
            try:
                # Check if we already did an auto-backup today
                today_start = datetime.combine(date.today(), datetime.min.time())
                has_run_today = db.query(AuditLedger).filter(
                    AuditLedger.event_type == "auto_cloud_backup",
                    AuditLedger.timestamp >= today_start
                ).first()
                
                if not has_run_today:
                    logger.info("Auto-Backup running...")
                    # Trigger the new disaster recovery logical backup
                    result = cloud_storage.run_disaster_recovery_backup(db)
                    
                    if result.get("status") == "SUCCESS":
                        audit_ledger.append_entry(db, "auto_cloud_backup", {
                            "backup_id": result.get("backup_id"),
                            "file_key": result.get("file_key"),
                            "sha256": result.get("sha256"),
                            "size_kb": result.get("size_kb")
                        })
                        logger.info("Auto-Backup successful: %s", result.get("file_key"))
                    else:
                        logger.error("Auto-Backup execution failed: %s", result.get("message"))
            except Exception as e:
                db.rollback()
                raise e
            finally:
                db.close()
        except Exception as e:
            logger.error("Auto-Backup scheduler error: %s", e)
            
        # Check every 1 hour (3600 seconds) or responsive exit on stop signal
        if BACKUP_WORKER_STOP_EVENT.wait(timeout=3600):
            break



def schedule_health_telemetry_worker():
    # Only run health telemetry worker if Celery is NOT enabled (fallback mode)
    if os.getenv("CELERY_ENABLED", "false").lower() == "true":
        logger.info("Celery scheduling is enabled. Background thread health worker deactivated.")
        return
        
    if HEALTH_WORKER_STOP_EVENT.wait(timeout=5):
        return
    logger.info("Background Health Telemetry scheduler active.")
    
    while not HEALTH_WORKER_STOP_EVENT.is_set():
        try:
            from sqlalchemy.orm import sessionmaker
            from backend.routers.health import perform_deep_telemetry
            from backend.models import SystemHealthSnapshot
            from datetime import datetime, timedelta, UTC
            
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            db = SessionLocal()
            try:
                telemetry = perform_deep_telemetry(db)
                for service, info in telemetry.items():
                    if isinstance(info, dict) and "status" in info:
                        db.add(SystemHealthSnapshot(
                            service=service,
                            status=info["status"],
                            latency_ms=info.get("latency_ms"),
                            timestamp=datetime.now(UTC).replace(tzinfo=None)
                        ))
                
                # Cleanup snapshots older than 24 hours
                cutoff = datetime.now(UTC).replace(tzinfo=None) - timedelta(hours=24)
                db.query(SystemHealthSnapshot).filter(SystemHealthSnapshot.timestamp < cutoff).delete()
                db.commit()
            except Exception as e:
                db.rollback()
                raise e
            finally:
                db.close()
        except Exception as e:
            logger.error("Background health telemetry scheduler error: %s", e)
            
        if HEALTH_WORKER_STOP_EVENT.wait(timeout=30):
            break


def schedule_simulation_worker():
    # Check if we are running in tests (to avoid locking SQLite / database during tests)
    import sys
    if "pytest" in sys.modules or os.getenv("ENVIRONMENT") == "testing":
        logger.info("Test environment detected. Background simulation worker thread deactivated.")
        return

    # Wait for application startup
    if SIMULATION_WORKER_STOP_EVENT.wait(timeout=5):
        return
    logger.info("Background Simulation ticking worker active.")
    
    while not SIMULATION_WORKER_STOP_EVENT.is_set():
        try:
            from sqlalchemy.orm import sessionmaker
            from backend.models import DigitalTwinSimulation
            from backend.models import DigitalTwinSimulation, WarehouseGridCell
            from backend.routers.robots import execute_simulation_tick
            from backend.routers.digital_twin import _emit_tick_events, cleanup_simulation_tasks, setup_scenario_conditions
            
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            db = SessionLocal()
            try:
                # Find all active simulations that are RUNNING
                running_sims = db.query(DigitalTwinSimulation).filter(
                    DigitalTwinSimulation.simulation_status == "RUNNING"
                ).all()
                
                if running_sims:
                    from datetime import datetime, UTC
                    from backend.models import Robot, Task, WarehouseLocation
                    from backend.routers.robots import transition_robot_status

                    for sim in running_sims:
                        wh_id = sim.warehouse_id
                        
                        # 1. Route low battery robots to charging stations if available
                        robots = db.query(Robot).filter(
                            Robot.warehouse_id == wh_id,
                            Robot.enabled == True
                        ).all()
                        
                        for r in robots:
                            if r.status == "AVAILABLE" and not r.assigned_task_id and r.battery_level < 20.0:
                                charge_loc = db.query(WarehouseLocation).filter(
                                    WarehouseLocation.warehouse_id == wh_id,
                                    WarehouseLocation.location_type == "CHARGING"
                                ).first()
                                if charge_loc:
                                    r.target_location_id = charge_loc.id
                                    r.target_x = charge_loc.x or 0.0
                                    r.target_y = charge_loc.y or 0.0
                                    transition_robot_status(db, r, "CHARGING", None, f"Auto-routing low battery robot to charge: {charge_loc.id}")
                                    
                                    from backend.models import SimulationEvent
                                    db.add(SimulationEvent(
                                        simulation_id=sim.id,
                                        event_type="BATTERY_LOW",
                                        severity="WARNING",
                                        message=f"Robot {r.robot_code} battery low — returning to charging.",
                                        sim_time_seconds=sim.simulation_time_seconds,
                                        warehouse_id=wh_id,
                                        real_timestamp=datetime.now(UTC).replace(tzinfo=None),
                                        robot_id=r.id,
                                        event_metadata="{}"
                                    ))
                                    db.add(r)
                                    logger.info(f"Auto-routed low battery robot {r.robot_code} to charge station {charge_loc.id}")
                        
                        # 2. Assign queued/prioritized tasks to available robots in this warehouse
                        available_robots = [r for r in robots if r.status == "AVAILABLE" and not r.assigned_task_id and r.battery_level >= 20.0]
                        queued_tasks = db.query(Task).filter(
                            Task.warehouse_id == wh_id,
                            Task.status.in_(["QUEUED", "PRIORITIZED", "FAILED"])
                        ).order_by(Task.priority_score.desc()).all()
                        
                        if available_robots and queued_tasks:
                            for task in queued_tasks:
                                if not available_robots:
                                    break
                                best_robot = None
                                min_dist = float("inf")
                                loc = db.query(WarehouseLocation).filter(WarehouseLocation.id == task.source_location_id).first()
                                tx = loc.x if loc else 1.0
                                ty = loc.y if loc else 1.0
                                
                                for r in available_robots:
                                    dist = abs(r.current_x - tx) + abs(r.current_y - ty)
                                    if dist < min_dist:
                                        min_dist = dist
                                        best_robot = r
                                        
                                if best_robot:
                                    best_robot.assigned_task_id = task.id
                                    best_robot.status = "ASSIGNED"
                                    task.assigned_robot_id = best_robot.robot_code
                                    task.status = "ASSIGNED"
                                    task.assigned_at = datetime.now(UTC).replace(tzinfo=None)
                                    db.add(best_robot)
                                    db.add(task)
                                    available_robots.remove(best_robot)
                                    logger.info(f"Simulation Scheduler: Assigned task {task.task_number} to robot {best_robot.robot_code}")
                            db.commit()

                    # Execute a simulation tick (updates robots & routes across warehouses)
                    execute_simulation_tick(db)
                    
                    for sim in running_sims:
                        sim.tick_count += 1
                        # Increment simulation time accounting for speed multiplier
                        sim.simulation_time_seconds += 1.0 * (sim.speed_multiplier or 1.0)
                        db.add(sim)
                        db.commit()
                        
                        # Emit tick events (which broadcasts to SSE stream)
                        _emit_tick_events(db, sim)
            except Exception as e:
                db.rollback()
                logger.error("Simulation ticking worker error: %s", e)
            finally:
                db.close()
        except Exception as e:
            logger.error("Simulation ticking worker session error: %s", e)
            
        # Determine dynamic sleep time based on max speed multiplier of running simulations
        sleep_time = 1.0
        try:
            from sqlalchemy.orm import sessionmaker
            from backend.models import DigitalTwinSimulation
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            db = SessionLocal()
            try:
                running_sims = db.query(DigitalTwinSimulation).filter(
                    DigitalTwinSimulation.simulation_status == "RUNNING"
                ).all()
                if running_sims:
                    max_speed = max([sim.speed_multiplier for sim in running_sims], default=1.0)
                    # Cap speed to 10.0x maximum, 0.1x minimum
                    max_speed = max(0.1, min(10.0, max_speed))
                    sleep_time = 1.0 / max_speed
            finally:
                db.close()
        except Exception:
            pass
            
        if SIMULATION_WORKER_STOP_EVENT.wait(timeout=sleep_time):
            break





def ensure_backup_records_schema():
    from sqlalchemy import inspect, text
    from backend.database import SessionLocal, engine
    inspector = inspect(engine)
    
    # Ensure tables are created first
    from backend.models import Base
    Base.metadata.create_all(bind=engine)
    
    if "backup_records" in inspector.get_table_names():
        columns = [c["name"] for c in inspector.get_columns("backup_records")]
        is_postgres = "postgres" in str(engine.url).lower()
        time_type = "TIMESTAMP" if is_postgres else "DATETIME"
        
        new_cols = {
            "backup_type": "VARCHAR(50) DEFAULT 'MANUAL'",
            "started_at": time_type,
            "completed_at": time_type,
            "storage_provider": "VARCHAR(50)",
            "bucket": "VARCHAR(255)",
            "checksum_algorithm": "VARCHAR(20) DEFAULT 'SHA-256'",
            "verification_status": "VARCHAR(50) DEFAULT 'PENDING'",
            "verification_at": time_type,
            "restore_test_status": "VARCHAR(50) DEFAULT 'PENDING'",
            "restore_test_at": time_type,
            "retention_status": "VARCHAR(50) DEFAULT 'ACTIVE'",
            "initiated_by": "VARCHAR(100)",
            "audit_ref": "VARCHAR(255)"
        }
        
        db = SessionLocal()
        try:
            for col_name, col_type in new_cols.items():
                if col_name not in columns:
                    logger.info("DB SCHEMA: Adding column '%s' to backup_records table...", col_name)
                    db.execute(text(f"ALTER TABLE backup_records ADD COLUMN {col_name} {col_type}"))
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error("DB SCHEMA migration failed: %s", e)
        finally:
            db.close()


def ensure_warehouses_schema():
    from sqlalchemy import inspect, text
    from backend.database import SessionLocal, engine
    from backend.models import Warehouse
    from backend.geocoding_service import geocode_address
    inspector = inspect(engine)
    
    # Ensure tables are created first
    from backend.models import Base
    Base.metadata.create_all(bind=engine)
    
    if "warehouses" in inspector.get_table_names():
        columns = [c["name"] for c in inspector.get_columns("warehouses")]
        new_cols = {
            "city": "VARCHAR(50)",
            "state": "VARCHAR(50)",
            "country": "VARCHAR(50)"
        }
        db = SessionLocal()
        try:
            for col_name, col_type in new_cols.items():
                if col_name not in columns:
                    logger.info("DB SCHEMA: Adding column '%s' to warehouses table...", col_name)
                    db.execute(text(f"ALTER TABLE warehouses ADD COLUMN {col_name} {col_type}"))
            db.commit()
            
            # Seed geocoding data migration for existing warehouses without coordinates
            un_geocoded = db.query(Warehouse).filter(
                (Warehouse.latitude == None) | (Warehouse.longitude == None)
            ).all()
            if un_geocoded:
                logger.info("DB SCHEMA: Running geocoding data migration for %s warehouses...", len(un_geocoded))
                for wh in un_geocoded:
                    lat, lon, display_name = geocode_address(wh.name, wh.city, wh.state, wh.country, wh.location)
                    if lat is not None and lon is not None:
                        wh.latitude = lat
                        wh.longitude = lon
                        if display_name and not wh.location:
                            wh.location = display_name
                        db.add(wh)
                        logger.info("DB SCHEMA: Geocoded existing warehouse %s to (%s, %s)", wh.id, lat, lon)
                db.commit()
        except Exception as e:
            db.rollback()
            logger.error("DB SCHEMA migration failed for warehouses table: %s", e)
        finally:
            db.close()


def seed_default_thresholds():
    from backend.database import SessionLocal
    from backend.models import HealthThresholdConfiguration
    
    defaults = {
        "queue_warning_depth": (10.0, "Warning threshold for RabbitMQ queue depth"),
        "queue_critical_depth": (50.0, "Critical threshold for RabbitMQ queue depth"),
        "api_latency_warning_ms": (300.0, "Warning threshold for API request response time"),
        "api_latency_critical_ms": (1000.0, "Critical threshold for API request response time"),
        "database_latency_warning_ms": (100.0, "Warning threshold for Database response time"),
        "database_latency_critical_ms": (500.0, "Critical threshold for Database response time"),
        "backup_age_warning_hours": (26.0, "Warning threshold for backup age"),
        "backup_age_critical_hours": (48.0, "Critical threshold for backup age"),
        "worker_stale_timeout_seconds": (60.0, "Heartbeat threshold for stale Celery worker status"),
        "api_error_rate_warning_pct": (5.0, "Warning threshold for API request error percentage"),
        "api_error_rate_critical_pct": (15.0, "Critical threshold for API request error percentage"),
    }
    
    db = SessionLocal()
    try:
        for key, (val, desc) in defaults.items():
            exists = db.query(HealthThresholdConfiguration).filter(HealthThresholdConfiguration.key == key).first()
            if not exists:
                db.add(HealthThresholdConfiguration(key=key, value=val, description=desc))
        db.commit()
        logger.info("Successfully seeded default health thresholds.")
    except Exception as e:
        db.rollback()
        logger.error("Failed to seed default health thresholds: %s", e)
    finally:
        db.close()


def ensure_admin_user_exists():
    from backend.database import SessionLocal
    from backend.models import User
    from backend.auth import hash_password
    db = SessionLocal()
    try:
        initial_password = os.getenv("INITIAL_ADMIN_PASSWORD", "AdminPassword123!")
        initial_username = os.getenv("INITIAL_ADMIN_USERNAME", "admin")
        admin = db.query(User).filter(User.username == initial_username).first()
        if not admin:
            admin_user = User(
                username=initial_username,
                password_hash=hash_password(initial_password),
                role="admin",
                full_name="System Administrator",
                email="admin@warehouse-os.internal",
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            logger.info("Auto-seeded default admin user '%s'", initial_username)
        else:
            admin.is_active = True
            admin.password_hash = hash_password(initial_password)
            db.commit()
            logger.info("Reset default admin user '%s' credentials to guarantee access", initial_username)
    except Exception as e:
        db.rollback()
        logger.error("Failed to seed admin user: %s", e)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB schema migrations, Sentry SDK, and seed health thresholds
    import asyncio
    from backend.sync_broadcast import broadcaster
    broadcaster.set_loop(asyncio.get_running_loop())
    
    ensure_backup_records_schema()
    ensure_warehouses_schema()
    init_sentry()
    seed_default_thresholds()
    ensure_admin_user_exists()

    from data_pipeline.provisioner import ensure_all_datasets_provisioned
    ensure_all_datasets_provisioned()
    
    # Launch background backup threads only outside testing to avoid SQLite database locks & leaked loops
    if os.getenv("ENVIRONMENT") != "testing":
        global BACKUP_WORKER_THREAD, HEALTH_WORKER_THREAD, SIMULATION_WORKER_THREAD
        
        BACKUP_WORKER_STOP_EVENT.clear()
        HEALTH_WORKER_STOP_EVENT.clear()
        SIMULATION_WORKER_STOP_EVENT.clear()
        
        if BACKUP_WORKER_THREAD is None or not BACKUP_WORKER_THREAD.is_alive():
            BACKUP_WORKER_THREAD = threading.Thread(target=schedule_backups_worker, daemon=True, name="BackupWorker")
            BACKUP_WORKER_THREAD.start()
        if HEALTH_WORKER_THREAD is None or not HEALTH_WORKER_THREAD.is_alive():
            HEALTH_WORKER_THREAD = threading.Thread(target=schedule_health_telemetry_worker, daemon=True, name="HealthWorker")
            HEALTH_WORKER_THREAD.start()
        if SIMULATION_WORKER_THREAD is None or not SIMULATION_WORKER_THREAD.is_alive():
            SIMULATION_WORKER_THREAD = threading.Thread(target=schedule_simulation_worker, daemon=True, name="SimulationWorker")
            SIMULATION_WORKER_THREAD.start()
            
    yield
    
    # Shutdown: Signal stop and cleanly join the threads to prevent leaks
    if os.getenv("ENVIRONMENT") != "testing":
        logger.info("Lifespan shutdown: stopping background workers.")
        BACKUP_WORKER_STOP_EVENT.set()
        HEALTH_WORKER_STOP_EVENT.set()
        SIMULATION_WORKER_STOP_EVENT.set()
        
        if BACKUP_WORKER_THREAD and BACKUP_WORKER_THREAD.is_alive():
            BACKUP_WORKER_THREAD.join(timeout=2.0)
        if HEALTH_WORKER_THREAD and HEALTH_WORKER_THREAD.is_alive():
            HEALTH_WORKER_THREAD.join(timeout=2.0)
        if SIMULATION_WORKER_THREAD and SIMULATION_WORKER_THREAD.is_alive():
            SIMULATION_WORKER_THREAD.join(timeout=2.0)
        logger.info("Lifespan shutdown: background workers stopped.")


app = FastAPI(
    title="Cloud-Based Smart Warehouse Automation API", 
    version="3.0",
    lifespan=lifespan
)

import uuid
from fastapi.responses import JSONResponse

# Correlation ID Middleware
@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
        request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# Custom Exception Handlers
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error("Unhandled error [Request ID: %s]: %s", request_id, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "The requested service encountered an internal error.",
            "request_id": request_id
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    request_id = getattr(request.state, "request_id", "unknown")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": f"HTTP_{exc.status_code}",
            "message": exc.detail,
            "detail": exc.detail,
            "request_id": request_id
        }
    )


# CORS — locked to specific origins for production, wildcard for dev
ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)


# Prometheus API Latency Metrics Middleware
@app.middleware("http")
async def prometheus_metrics_middleware(request: Request, call_next):
    from backend.routers.metrics import HTTP_REQUESTS_TOTAL, HTTP_REQUEST_DURATION
    
    endpoint = request.url.path
    method = request.method
    
    # Bypass metrics endpoint from logging requests to prevent self-scraping loops
    if endpoint == "/metrics" or endpoint.startswith("/static"):
        return await call_next(request)
        
    start_time = time.time()
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        status = str(response.status_code)
        HTTP_REQUESTS_TOTAL.labels(method=method, endpoint=endpoint, status=status).inc()
        HTTP_REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
        return response
    except Exception as e:
        duration = time.time() - start_time
        HTTP_REQUESTS_TOTAL.labels(method=method, endpoint=endpoint, status="500").inc()
        HTTP_REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
        raise e


# Security headers middleware
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Disable cache for static files in development to ensure browser loads latest code
    if request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
    return response


# Include Routers
app.include_router(auth.router)
app.include_router(warehouses.router)
app.include_router(ai.router)
app.include_router(apps.router)
app.include_router(reports.router)
app.include_router(health.router)
app.include_router(wms.router)
app.include_router(tasks.router)
app.include_router(robots.router)
app.include_router(pathfinding.router)
app.include_router(digital_twin.router)
app.include_router(security.router)  # Phase 9: Security Center
app.include_router(notifications.router)  # Phase 10: Event & Notification Automation System
app.include_router(metrics.router) # Prometheus metrics endpoint
app.include_router(ai_assistant.router) # OpenAI intelligence assistant
app.include_router(or_tools_scheduler.router) # OR-Tools optimization engine
app.include_router(backups.router) # Phase 11: Backups & Disaster Recovery
app.include_router(analytics.router) # Phase 12: Analytics, KPI & Performance Intelligence
app.include_router(scenarios.router) # Phase 13: Scenario Lab & Algorithm Experiments
app.include_router(simulation.router)
app.include_router(settings.router)
app.include_router(decision_support.router)




# Serve frontend static files
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.isdir(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

    @app.get("/favicon.ico")
    def favicon():
        fav_path = os.path.join(frontend_path, "favicon.svg")
        if os.path.isfile(fav_path):
            return FileResponse(fav_path, media_type="image/svg+xml")
        raise HTTPException(404)

    @app.get("/")
    def serve_index():
        return FileResponse(os.path.join(frontend_path, "index.html"))
