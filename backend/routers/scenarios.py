import json
import logging
import io
import csv
import os
import threading
from datetime import datetime, UTC
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.auth import get_current_user
from backend.models import User, Scenario, Experiment, ExperimentRun, AuditLedger
from backend import audit_ledger
from backend.celery_app import execute_experiment_task, safe_task_dispatch

logger = logging.getLogger("warehouse.scenarios_router")

router = APIRouter(prefix="/scenarios", tags=["Scenario Lab"])


# ---------------------------------------------------------------------------
# Audit Helper
# ---------------------------------------------------------------------------
def log_scenario_audit(db: Session, user_id: int, action: str, details: dict):
    audit_ledger.append_entry(db, action, details)
    db.commit()


# ---------------------------------------------------------------------------
# Scenario Endpoints
# ---------------------------------------------------------------------------

@router.get("", summary="Get all active scenarios")
def get_scenarios(
    warehouse_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Scenario).filter(Scenario.status == "ACTIVE")
    if warehouse_id:
        query = query.filter(Scenario.warehouse_id == warehouse_id)
    results = query.order_by(Scenario.created_at.desc()).all()
    
    seen = set()
    unique_results = []
    for s in results:
        key = (s.name, s.warehouse_id)
        if key not in seen:
            seen.add(key)
            unique_results.append(s)
    return unique_results


@router.post("", summary="Create a new simulation scenario")
def create_scenario(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail="Insufficient privileges.")

    # Validation of incoming scenario configuration
    name = payload.get("name")
    warehouse_id = payload.get("warehouse_id")
    if not name or not warehouse_id:
        raise HTTPException(status_code=400, detail="Scenario name and warehouse ID are required.")

    # Check for duplicate scenario name in same warehouse
    exists = db.query(Scenario).filter(
        Scenario.name == name,
        Scenario.warehouse_id == warehouse_id,
        Scenario.status == "ACTIVE"
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail=f"Scenario with name '{name}' already exists in this warehouse.")

    config = payload.get("configuration", {})
    # Set standard parameter structures
    config.setdefault("demand", {"order_volume": 5, "order_arrival_rate": 50})
    config.setdefault("robots", {"robot_count": 3, "initial_battery_pct": 100.0, "robot_speed": 1.0})
    config.setdefault("failures", {"enabled": False, "failure_tick": 100})
    config.setdefault("simulation", {"duration_ticks": 500})
    config.setdefault("inventory", {"initial_stock_units": 100, "reorder_threshold_units": 20})
    config.setdefault("warehouse", {"blocked_cells": []})

    scen = Scenario(
        name=name,
        description=payload.get("description", ""),
        warehouse_id=warehouse_id,
        scenario_type=payload.get("scenario_type", "BASELINE"),
        configuration=config,
        random_seed=payload.get("random_seed", 42),
        status="ACTIVE",
        tags=json.dumps(payload.get("tags", [])),
        notes=payload.get("notes", ""),
        created_by=current_user.username
    )
    db.add(scen)
    db.commit()
    db.refresh(scen)

    log_scenario_audit(db, current_user.id, "SCENARIO_CREATED", {
        "scenario_id": scen.id,
        "name": scen.name,
        "created_by": current_user.username
    })

    return {
        "id": scen.id,
        "name": scen.name,
        "description": scen.description,
        "warehouse_id": scen.warehouse_id,
        "scenario_type": scen.scenario_type,
        "configuration": scen.configuration,
        "random_seed": scen.random_seed,
        "status": scen.status,
        "tags": scen.tags,
        "notes": scen.notes,
        "created_by": scen.created_by,
        "created_at": scen.created_at.isoformat() if scen.created_at else None,
        "updated_at": scen.updated_at.isoformat() if scen.updated_at else None
    }


@router.get("/{id}", summary="Get scenario by ID")
def get_scenario_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    scen = db.query(Scenario).filter(Scenario.id == id, Scenario.status == "ACTIVE").first()
    if not scen:
        raise HTTPException(status_code=404, detail="Scenario not found.")
    return scen


@router.put("/{id}", summary="Update scenario configuration")
def update_scenario(
    id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail="Insufficient privileges.")

    scen = db.query(Scenario).filter(Scenario.id == id, Scenario.status == "ACTIVE").first()
    if not scen:
        raise HTTPException(status_code=404, detail="Scenario not found.")

    if "name" in payload:
        scen.name = payload["name"]
    if "description" in payload:
        scen.description = payload["description"]
    if "configuration" in payload:
        scen.configuration = payload["configuration"]
    if "random_seed" in payload:
        scen.random_seed = payload["random_seed"]
    if "scenario_type" in payload:
        scen.scenario_type = payload["scenario_type"]
    if "tags" in payload:
        scen.tags = json.dumps(payload["tags"])
    if "notes" in payload:
        scen.notes = payload["notes"]

    scen.updated_at = datetime.now(UTC).replace(tzinfo=None)
    db.commit()

    log_scenario_audit(db, current_user.id, "SCENARIO_MODIFIED", {
        "scenario_id": scen.id,
        "name": scen.name,
        "updated_by": current_user.username
    })

    return scen


@router.delete("/{id}", summary="Archive/Delete scenario")
def delete_scenario(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only Admin is permitted to delete/archive scenarios
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can archive scenarios.")

    scen = db.query(Scenario).filter(Scenario.id == id, Scenario.status == "ACTIVE").first()
    if not scen:
        raise HTTPException(status_code=404, detail="Scenario not found.")

    scen.status = "ARCHIVED"
    db.commit()

    log_scenario_audit(db, current_user.id, "SCENARIO_DELETED", {
        "scenario_id": scen.id,
        "name": scen.name,
        "archived_by": current_user.username
    })

    return {"status": "success", "message": "Scenario successfully archived."}


@router.post("/{id}/duplicate", summary="Duplicate an existing scenario layout")
def duplicate_scenario(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail="Insufficient privileges.")

    scen = db.query(Scenario).filter(Scenario.id == id, Scenario.status == "ACTIVE").first()
    if not scen:
        raise HTTPException(status_code=404, detail="Scenario not found.")

    dup = Scenario(
        name=f"Copy of {scen.name}",
        description=scen.description,
        warehouse_id=scen.warehouse_id,
        scenario_type=scen.scenario_type,
        configuration=scen.configuration,
        random_seed=scen.random_seed,
        status="ACTIVE",
        tags=scen.tags,
        notes=scen.notes,
        created_by=current_user.username
    )
    db.add(dup)
    db.commit()
    db.refresh(dup)

    log_scenario_audit(db, current_user.id, "SCENARIO_DUPLICATED", {
        "original_scenario_id": scen.id,
        "new_scenario_id": dup.id,
        "created_by": current_user.username
    })

    return dup


# ---------------------------------------------------------------------------
# Experiment Endpoints
# ---------------------------------------------------------------------------

@router.get("/experiments/list", summary="Get all experiment histories")
def get_experiments(
    scenario_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Experiment)
    if scenario_id:
        query = query.filter(Experiment.scenario_id == scenario_id)
    experiments = query.order_by(Experiment.created_at.desc()).all()
    
    result = []
    for exp in experiments:
        result.append({
            "id": exp.id,
            "scenario_id": exp.scenario_id,
            "experiment_name": exp.experiment_name,
            "description": exp.description,
            "status": exp.status,
            "algorithm_name": exp.algorithm_name,
            "algorithm_version": exp.algorithm_version,
            "configuration": exp.configuration,
            "random_seed": exp.random_seed,
            "repetitions": exp.repetitions,
            "started_at": exp.started_at.isoformat() if exp.started_at else None,
            "completed_at": exp.completed_at.isoformat() if exp.completed_at else None,
            "duration_seconds": exp.duration_seconds,
            "created_by": exp.created_by,
            "error_message": exp.error_message,
            "metrics_summary": exp.metrics_summary,
            "created_at": exp.created_at.isoformat() if exp.created_at else None
        })
    return result


@router.post("/experiments", summary="Initialize an experiment structure")
def create_experiment(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail="Insufficient privileges.")

    scen_id = payload.get("scenario_id")
    scen = db.query(Scenario).filter(Scenario.id == scen_id, Scenario.status == "ACTIVE").first()
    if not scen:
        raise HTTPException(status_code=404, detail="Scenario target not found.")

    # Concurrency safe limit safeguard checks
    repetitions = payload.get("repetitions", 1)
    if repetitions < 1 or repetitions > 10:
        raise HTTPException(status_code=400, detail="Scenario repetitions must be between 1 and 10.")

    exp = Experiment(
        scenario_id=scen.id,
        experiment_name=payload.get("experiment_name", f"Experiment: {scen.name}"),
        description=payload.get("description", ""),
        status="QUEUED",
        algorithm_name=payload.get("algorithm_name", "CURRENT_HEURISTIC"),
        algorithm_version="1.0",
        configuration=scen.configuration,
        random_seed=payload.get("random_seed", scen.random_seed),
        repetitions=repetitions,
        created_by=current_user.username
    )
    db.add(exp)
    db.commit()
    db.refresh(exp)

    log_scenario_audit(db, current_user.id, "EXPERIMENT_CREATED", {
        "experiment_id": exp.id,
        "name": exp.experiment_name,
        "created_by": current_user.username
    })

    # Trigger async execution
    celery_enabled = os.getenv("CELERY_ENABLED", "false").lower() == "true"
    workers_online = False
    if celery_enabled:
        try:
            from backend.celery_app import celery
            insp = celery.control.inspect(timeout=1.0)
            stats = insp.stats()
            workers_online = stats is not None and len(stats) > 0
        except Exception as e:
            logger.warning("Failed to check Celery workers, assuming offline: %s", e)
            workers_online = False

    if celery_enabled and workers_online:
        try:
            safe_task_dispatch(execute_experiment_task, exp.id)
            logger.info("Experiment %s queued in Celery successfully.", exp.id)
        except Exception as queue_err:
            logger.error("Failed to queue experiment in Celery: %s. Falling back to background thread.", queue_err)
            threading.Thread(target=execute_experiment_task, args=(exp.id,), daemon=True).start()
    else:
        # Fallback to local background thread
        logger.info("Celery disabled or no workers active. Starting experiment %s in local background thread...", exp.id)
        threading.Thread(target=execute_experiment_task, args=(exp.id,), daemon=True).start()

    return {
        "id": exp.id,
        "scenario_id": exp.scenario_id,
        "experiment_name": exp.experiment_name,
        "description": exp.description,
        "status": exp.status,
        "algorithm_name": exp.algorithm_name,
        "algorithm_version": exp.algorithm_version,
        "configuration": exp.configuration,
        "random_seed": exp.random_seed,
        "repetitions": exp.repetitions,
        "started_at": exp.started_at.isoformat() if exp.started_at else None,
        "completed_at": exp.completed_at.isoformat() if exp.completed_at else None,
        "duration_seconds": exp.duration_seconds,
        "created_by": exp.created_by,
        "error_message": exp.error_message,
        "metrics_summary": exp.metrics_summary,
        "created_at": exp.created_at.isoformat() if exp.created_at else None
    }


@router.get("/experiments/{id}", summary="Get experiment by ID with repetition runs")
def get_experiment_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    exp = db.query(Experiment).filter(Experiment.id == id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment history record not found.")

    runs = db.query(ExperimentRun).filter(ExperimentRun.experiment_id == id).order_by(ExperimentRun.repetition_number.asc()).all()

    return {
        "experiment": {
            "id": exp.id,
            "scenario_id": exp.scenario_id,
            "experiment_name": exp.experiment_name,
            "description": exp.description,
            "status": exp.status,
            "algorithm_name": exp.algorithm_name,
            "algorithm_version": exp.algorithm_version,
            "configuration": exp.configuration,
            "random_seed": exp.random_seed,
            "repetitions": exp.repetitions,
            "started_at": exp.started_at.isoformat() if exp.started_at else None,
            "completed_at": exp.completed_at.isoformat() if exp.completed_at else None,
            "duration_seconds": exp.duration_seconds,
            "created_by": exp.created_by,
            "error_message": exp.error_message,
            "metrics_summary": exp.metrics_summary,
            "created_at": exp.created_at.isoformat() if exp.created_at else None
        },
        "runs": [
            {
                "id": run.id,
                "experiment_id": run.experiment_id,
                "repetition_number": run.repetition_number,
                "random_seed": run.random_seed,
                "status": run.status,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
                "duration_seconds": run.duration_seconds,
                "error_message": run.error_message,
                "metrics": run.metrics,
                "created_at": run.created_at.isoformat() if run.created_at else None
            }
            for run in runs
        ]
    }


@router.post("/experiments/{id}/cancel", summary="Cancel a running experiment")
def cancel_experiment(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail="Insufficient privileges.")

    exp = db.query(Experiment).filter(Experiment.id == id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found.")

    if exp.status not in ("QUEUED", "RUNNING"):
        raise HTTPException(status_code=400, detail=f"Cannot cancel experiment in status {exp.status}.")

    exp.status = "CANCELLED"
    db.commit()

    log_scenario_audit(db, current_user.id, "EXPERIMENT_CANCELLED", {
        "experiment_id": exp.id,
        "name": exp.experiment_name,
        "cancelled_by": current_user.username
    })

    return {"status": "success", "message": "Experiment execution successfully cancelled."}


@router.post("/experiments/{id}/rerun", summary="Duplicate and execute experiment again")
def rerun_experiment(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail="Insufficient privileges.")

    exp = db.query(Experiment).filter(Experiment.id == id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found.")

    new_exp = Experiment(
        scenario_id=exp.scenario_id,
        experiment_name=f"{exp.experiment_name} (Rerun)",
        description=exp.description,
        status="QUEUED",
        algorithm_name=exp.algorithm_name,
        algorithm_version=exp.algorithm_version,
        configuration=exp.configuration,
        random_seed=exp.random_seed,
        repetitions=exp.repetitions,
        created_by=current_user.username
    )
    db.add(new_exp)
    db.commit()
    db.refresh(new_exp)

    log_scenario_audit(db, current_user.id, "EXPERIMENT_RERUN", {
        "original_experiment_id": exp.id,
        "new_experiment_id": new_exp.id,
        "created_by": current_user.username
    })

    # Trigger background run
    celery_enabled = os.getenv("CELERY_ENABLED", "false").lower() == "true"
    if celery_enabled:
        try:
            safe_task_dispatch(execute_experiment_task, new_exp.id)
        except Exception:
            threading.Thread(target=execute_experiment_task, args=(new_exp.id,), daemon=True).start()
    else:
        threading.Thread(target=execute_experiment_task, args=(new_exp.id,), daemon=True).start()

    return new_exp


@router.get("/experiments/{id}/export", summary="Export experiment results as CSV/JSON")
def export_experiment(
    id: int,
    format: str = Query("json", pattern="^(json|csv)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Auditor, Manager, Admin can export results
    if current_user.role not in ("admin", "manager", "auditor"):
        raise HTTPException(status_code=403, detail="Access denied. Exporters require elevated permissions.")

    exp = db.query(Experiment).filter(Experiment.id == id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found.")

    runs = db.query(ExperimentRun).filter(ExperimentRun.experiment_id == id).all()

    log_scenario_audit(db, current_user.id, "EXPERIMENT_EXPORTED", {
        "experiment_id": exp.id,
        "format": format,
        "exported_by": current_user.username
    })

    if format == "json":
        data = {
            "experiment_id": exp.id,
            "experiment_name": exp.experiment_name,
            "scenario_id": exp.scenario_id,
            "status": exp.status,
            "algorithm": exp.algorithm_name,
            "seed": exp.random_seed,
            "repetitions": exp.repetitions,
            "duration_seconds": exp.duration_seconds,
            "metrics_summary": exp.metrics_summary,
            "runs": [
                {
                    "run_number": r.repetition_number,
                    "seed": r.random_seed,
                    "status": r.status,
                    "duration_seconds": r.duration_seconds,
                    "metrics": r.metrics,
                    "error_message": r.error_message
                }
                for r in runs
            ]
        }
        return Response(
            content=json.dumps(data, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=experiment_{exp.id}_results.json"}
        )

    # Export CSV format
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write metadata headers
    writer.writerow(["Experiment ID", exp.id])
    writer.writerow(["Experiment Name", exp.experiment_name])
    writer.writerow(["Algorithm", exp.algorithm_name])
    writer.writerow(["Repetitions", exp.repetitions])
    writer.writerow([])
    
    # Write run metrics headers
    if runs and runs[0].metrics:
        metric_keys = list(runs[0].metrics.keys())
        writer.writerow(["Run Number", "Status", "Seed", "Duration (s)", "Error"] + metric_keys)
        
        for r in runs:
            row = [r.repetition_number, r.status, r.random_seed, r.duration_seconds or "", r.error_message or ""]
            for k in metric_keys:
                row.append(r.metrics.get(k, "") if r.metrics else "")
            writer.writerow(row)
            
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=experiment_{exp.id}_results.csv"}
    )


# ---------------------------------------------------------------------------
# Packing Station Simulation (SimPy Discrete-Event)
# ---------------------------------------------------------------------------

@router.post("/packing-simulation", summary="Run SimPy packing station discrete-event simulation")
def run_packing_simulation(
    payload: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """
    Runs a SimPy-based packing station simulation modeling operator resource
    contention. Returns queueing metrics: wait times, packing times,
    utilization, and queue depths.
    """
    from ml.simpy_simulator import run_simpy_experiment

    num_operators = payload.get("num_operators", 3)
    mean_packing_time = payload.get("mean_packing_time", 12.0)
    duration = payload.get("duration", 480.0)
    mean_arrival_interval = payload.get("mean_arrival_interval", 5.0)
    random_seed = payload.get("random_seed", None)

    # Validate inputs
    if num_operators < 1 or num_operators > 20:
        raise HTTPException(status_code=400, detail="num_operators must be between 1 and 20.")
    if duration < 10 or duration > 10000:
        raise HTTPException(status_code=400, detail="duration must be between 10 and 10000 minutes.")
    if mean_packing_time <= 0:
        raise HTTPException(status_code=400, detail="mean_packing_time must be positive.")
    if mean_arrival_interval <= 0:
        raise HTTPException(status_code=400, detail="mean_arrival_interval must be positive.")

    try:
        result = run_simpy_experiment(
            duration=duration,
            num_operators=num_operators,
            mean_arrival_interval=mean_arrival_interval,
            mean_packing_time=mean_packing_time,
            random_seed=random_seed
        )
        return result
    except Exception as e:
        logger.error("Packing simulation failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Packing simulation failed: {str(e)}")
