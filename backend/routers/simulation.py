import json
import logging
from datetime import datetime, UTC
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.auth import get_current_user
from backend.models import User, SimulationRun, SimulationResult, AuditLedger
from backend import audit_ledger
from backend import notifications
from backend.simulation.engine import SimulationEngine

logger = logging.getLogger("warehouse.simulation_router")

router = APIRouter(prefix="/simulation", tags=["Simulation Lab"])


def log_simulation_audit(db: Session, user_id: int, action: str, details: dict):
    audit_ledger.append_entry(db, action, details)
    db.commit()


def run_simulation_in_background(run_id: int, db_session_maker):
    """Executes a simulation run in a background worker process/thread, updating db status."""
    db = db_session_maker()
    try:
        run = db.query(SimulationRun).filter(SimulationRun.id == run_id).first()
        if not run:
            logger.error("Simulation run %s not found in database for background execution.", run_id)
            return

        run.status = "RUNNING"
        run.started_at = datetime.now(UTC).replace(tzinfo=None)
        db.commit()

        notifications.send_change_alert("SIMULATION_STARTED", {
            "warehouse_id": run.warehouse_id,
            "simulation_id": run.id,
            "mode": run.mode,
            "duration": run.simulation_duration,
            "created_by": run.created_by
        })

        # Instantiate engine
        engine = SimulationEngine(
            db=db,
            warehouse_id=run.warehouse_id,
            mode=run.mode,
            duration=run.simulation_duration,
            random_seed=run.random_seed,
            config=run.configuration,
            created_by=run.created_by
        )

        # Run SimPy simulation
        kpis = engine.run()

        # Save results to simulation_results table
        for metric, val in kpis.items():
            unit = "minutes" if "minutes" in metric or "duration" in metric else (
                "pct" if "pct" in metric or "rate" in metric else (
                    "seconds" if "seconds" in metric else "units"
                )
            )
            category = "robot" if "robot" in metric or "fleet" in metric else (
                "routing" if "A_star" in metric or "replanning" in metric or "collision" in metric or "deadlocks" in metric else (
                    "charging" if "charging" in metric else "throughput"
                )
            )
            db.add(SimulationResult(
                simulation_run_id=run.id,
                metric=metric,
                value=float(val),
                unit=unit,
                category=category
            ))

        # Save event logs inside simulation runs configuration as transient outputs
        run.configuration = {
            **run.configuration,
            "event_log": engine.event_log[:1000]  # Cap logs count to save space
        }

        run.status = "COMPLETED"
        run.completed_at = datetime.now(UTC).replace(tzinfo=None)
        db.commit()

        notifications.send_change_alert("SIMULATION_COMPLETED", {
            "warehouse_id": run.warehouse_id,
            "simulation_id": run.id,
            "mode": run.mode,
            "status": "COMPLETED",
            "message": f"Simulation run #{run.id} completed successfully."
        })

    except Exception as e:
        logger.error("Background simulation execution run %s failed: %s", run_id, e)
        db.rollback()
        run = db.query(SimulationRun).filter(SimulationRun.id == run_id).first()
        if run:
            run.status = "FAILED"
            run.error_message = str(e)
            run.completed_at = datetime.now(UTC).replace(tzinfo=None)
            db.commit()
            notifications.send_change_alert("SIMULATION_FAILED", {
                "warehouse_id": run.warehouse_id,
                "simulation_id": run.id,
                "mode": run.mode,
                "status": "FAILED",
                "error": str(e),
                "message": f"Simulation run #{run.id} failed: {str(e)}"
            })

    finally:
        db.close()


@router.post("/runs", summary="Create and run a new SimPy discrete-event simulation")
def create_simulation_run(
    payload: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail="Insufficient privileges.")

    warehouse_id = payload.get("warehouse_id")
    mode = payload.get("mode", "OFFLINE_SNAPSHOT")
    duration = payload.get("duration", 480.0)
    seed = payload.get("random_seed", 42)
    config = payload.get("configuration", {})

    if not warehouse_id:
        raise HTTPException(status_code=400, detail="Warehouse ID is required.")
    if mode not in ("OFFLINE_SNAPSHOT", "HISTORICAL_REPLAY", "EXPERIMENT"):
        raise HTTPException(status_code=400, detail=f"Invalid simulation mode: {mode}")

    # Create SimulationRun entry
    run = SimulationRun(
        name=payload.get("name", f"SimPy {mode} Run"),
        warehouse_id=warehouse_id,
        mode=mode,
        status="QUEUED",
        created_by=current_user.username,
        simulation_duration=float(duration),
        random_seed=int(seed),
        configuration=config,
        data_source="PostgreSQL live DB" if mode == "OFFLINE_SNAPSHOT" else (
            "PostgreSQL historical tables" if mode == "HISTORICAL_REPLAY" else "Simulation custom parameters"
        )
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    log_simulation_audit(db, current_user.id, "SIMULATION_RUN_CREATED", {
        "run_id": run.id,
        "mode": run.mode,
        "created_by": current_user.username
    })

    # Trigger run in background thread/task
    from backend.database import SessionLocal
    background_tasks.add_task(run_simulation_in_background, run.id, SessionLocal)

    return run


@router.get("/runs", summary="Get all simulation runs list")
def get_simulation_runs(
    warehouse_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(SimulationRun)
    if warehouse_id:
        query = query.filter(SimulationRun.warehouse_id == warehouse_id)
    return query.order_by(SimulationRun.created_at.desc()).all()


@router.get("/runs/{id}", summary="Get simulation run details")
def get_simulation_run(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    run = db.query(SimulationRun).filter(SimulationRun.id == id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Simulation run not found.")
    return run


@router.get("/runs/{id}/results", summary="Get computed KPI results of a simulation run")
def get_simulation_results(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    run = db.query(SimulationRun).filter(SimulationRun.id == id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Simulation run not found.")

    results = db.query(SimulationResult).filter(SimulationResult.simulation_run_id == id).all()
    return {
        "run_id": id,
        "status": run.status,
        "error_message": run.error_message,
        "results": [
            {
                "metric": r.metric,
                "value": r.value,
                "unit": r.unit,
                "category": r.category
            }
            for r in results
        ]
    }


@router.get("/runs/{id}/metrics", summary="Get event logs and metrics summary")
def get_simulation_metrics(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    run = db.query(SimulationRun).filter(SimulationRun.id == id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Simulation run not found.")

    # Event logs are stored transiently inside configuration
    event_log = run.configuration.get("event_log", [])
    results = db.query(SimulationResult).filter(SimulationResult.simulation_run_id == id).all()

    return {
        "run_id": id,
        "event_log": event_log,
        "metrics_summary": {r.metric: r.value for r in results}
    }


@router.delete("/runs/{id}", summary="Delete a simulation run history entry")
def delete_simulation_run(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can delete simulation runs.")

    run = db.query(SimulationRun).filter(SimulationRun.id == id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Simulation run not found.")

    db.delete(run)
    db.commit()

    log_simulation_audit(db, current_user.id, "SIMULATION_RUN_DELETED", {
        "run_id": id,
        "deleted_by": current_user.username
    })

    return {"status": "success", "message": "Simulation run deleted successfully."}


@router.post("/runs/{id}/compare", summary="Compare two simulation runs metrics side-by-side")
def compare_simulation_runs(
    id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    compare_id = payload.get("compare_with_id")
    if not compare_id:
        raise HTTPException(status_code=400, detail="compare_with_id is required.")

    run_a = db.query(SimulationRun).filter(SimulationRun.id == id).first()
    run_b = db.query(SimulationRun).filter(SimulationRun.id == compare_id).first()

    if not run_a or not run_b:
        raise HTTPException(status_code=404, detail="One or both simulation runs not found.")

    results_a = db.query(SimulationResult).filter(SimulationResult.simulation_run_id == id).all()
    results_b = db.query(SimulationResult).filter(SimulationResult.simulation_run_id == compare_id).all()

    metrics_a = {r.metric: {"value": r.value, "unit": r.unit} for r in results_a}
    metrics_b = {r.metric: {"value": r.value, "unit": r.unit} for r in results_b}

    all_metrics = set(list(metrics_a.keys()) + list(metrics_b.keys()))

    comparison = {}
    for m in all_metrics:
        val_a = metrics_a.get(m, {}).get("value")
        val_b = metrics_b.get(m, {}).get("value")
        unit = metrics_a.get(m, {}).get("unit") or metrics_b.get(m, {}).get("unit")
        
        diff = None
        pct_diff = None
        if val_a is not None and val_b is not None:
            diff = round(val_b - val_a, 2)
            pct_diff = round((diff / val_a) * 100.0, 2) if val_a != 0.0 else 0.0

        comparison[m] = {
            "run_a_value": val_a,
            "run_b_value": val_b,
            "difference": diff,
            "percent_difference": pct_diff,
            "unit": unit
        }

    return {
        "run_a": {
            "id": run_a.id,
            "name": run_a.name,
            "mode": run_a.mode,
            "robot_count": run_a.configuration.get("robots", {}).get("robot_count", 3),
            "seed": run_a.random_seed
        },
        "run_b": {
            "id": run_b.id,
            "name": run_b.name,
            "mode": run_b.mode,
            "robot_count": run_b.configuration.get("robots", {}).get("robot_count", 3),
            "seed": run_b.random_seed
        },
        "comparison": comparison
    }
