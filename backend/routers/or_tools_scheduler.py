import os
import time
import logging
import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime, UTC
from fastapi import APIRouter, Depends, HTTPException

from backend.database import get_db
from backend.auth import get_current_user
from backend.models import User, Task, Warehouse, Robot, WarehouseLocation, AuditLedger
from backend import audit_ledger
from backend.routers.robots import transition_robot_status
from backend.routers.tasks import transition_status

logger = logging.getLogger("warehouse.or_tools")

router = APIRouter(prefix="/ai", tags=["OR-Tools Scheduler"])

# Flag to track OR-Tools import availability
or_tools_available = False
try:
    from ortools.sat.python import cp_model
    or_tools_available = True
    logger.info("Google OR-Tools initialized successfully for scheduler optimization.")
except ImportError:
    logger.warning("Google OR-Tools not available in python runtime. Running scheduler in mock mode.")


def calculate_manhattan_distance(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)


def run_greedy_fallback(db: Session, tasks: List[Task], robots: List[Robot]) -> Dict[str, Any]:
    """
    Greedy deterministic fallback assignment heuristic.
    Matches tasks to closest eligible robots sequentially.
    """
    assignments = {}
    total_dist = 0
    reasons = {}

    for t in tasks:
        # Get item weight info
        task_weight = t.requested_quantity * (t.product.weight_kg or 0.0) if t.product else 0.0
        loc = db.query(WarehouseLocation).filter(WarehouseLocation.id == t.source_location_id).first()
        tx = loc.x if loc else 1.0
        ty = loc.y if loc else 1.0

        best_robot = None
        min_score = float("inf")
        best_dist = 0

        for r in robots:
            # Check matching warehouse
            if r.warehouse_id != t.warehouse_id:
                continue

            # Check payload constraints
            if task_weight > r.max_payload:
                continue

            # Calculate required battery
            dist_to_src = calculate_manhattan_distance(r.current_x, r.current_y, tx, ty)
            dest_loc = db.query(WarehouseLocation).filter(WarehouseLocation.id == t.destination_location_id).first()
            dx_dest = dest_loc.x if dest_loc else 1.0
            dy_dest = dest_loc.y if dest_loc else 1.0
            dist_to_dest = calculate_manhattan_distance(tx, ty, dx_dest, dy_dest)

            charge_loc = db.query(WarehouseLocation).filter(
                WarehouseLocation.warehouse_id == r.warehouse_id,
                WarehouseLocation.location_type == "CHARGING"
            ).first()
            dist_to_charge = 0.0
            if charge_loc:
                dist_to_charge = calculate_manhattan_distance(dx_dest, dy_dest, charge_loc.x, charge_loc.y)

            total_dist_est = dist_to_src + dist_to_dest + dist_to_charge
            battery_needed = (total_dist_est * 0.5) + 5.0

            if r.battery_level < battery_needed:
                continue

            # Scoring: distance + battery penalty
            bat_penalty = (100.0 - r.battery_level) * 0.2
            score = dist_to_src + bat_penalty

            if score < min_score:
                min_score = score
                best_robot = r
                best_dist = dist_to_src

        if best_robot:
            assignments[f"task_{t.id}"] = best_robot.robot_code
            total_dist += best_dist
        else:
            reasons[f"task_{t.id}"] = "No eligible robot found satisfying battery/payload limits."

    return {
        "status": "FALLBACK_SUCCESS",
        "assignments": assignments,
        "total_travel_distance": total_dist,
        "reasons": reasons
    }


def benchmark_ortools_assignment(db: Session, warehouse_id: str) -> Dict[str, Any]:
    """
    Formulates and solves a robot task assignment problem using OR-Tools CP-SAT solver.
    Compares travel time and task span metrics against the default heuristic.
    Uses real robot fleet data from the database.
    """
    # Fetch pending tasks in the warehouse
    tasks = db.query(Task).filter(
        Task.warehouse_id == warehouse_id, 
        Task.status.in_(["QUEUED", "PRIORITIZED", "FAILED", "PENDING"])
    ).limit(10).all()
    
    # Query real robots from the database
    robot_records = db.query(Robot).filter(
        Robot.warehouse_id == warehouse_id,
        Robot.enabled == True,
        ~Robot.status.in_(["OFFLINE", "FAILED", "MAINTENANCE"])
    ).all()
    
    # If no real robots available, return explicit message
    if not robot_records:
        return {
            "status": "skipped",
            "message": "No robots available to benchmark for this warehouse.",
            "warehouse_id": warehouse_id,
            "comparison": {}
        }
    
    robots = [r.robot_code for r in robot_records]
    
    # Check if we have tasks to schedule
    if not tasks:
        return {
            "status": "skipped",
            "message": "No pending tasks in warehouse to schedule.",
            "comparison": {}
        }
        
    num_tasks = len(tasks)
    num_robots = len(robot_records)
    
    # Build distance matrix using real robot positions and task source locations
    distance_matrix = []
    for r_idx, robot in enumerate(robot_records):
        row = []
        for t_idx, task in enumerate(tasks):
            loc = db.query(WarehouseLocation).filter(
                WarehouseLocation.id == task.source_location_id
            ).first()
            tx = loc.x if loc else 1.0
            ty = loc.y if loc else 1.0
            dist = calculate_manhattan_distance(robot.current_x, robot.current_y, tx, ty)
            # Apply battery penalty for low-battery robots
            bat_penalty = 50.0 if robot.battery_level < 30.0 else 0.0
            row.append(int(dist + bat_penalty))
        distance_matrix.append(row)
        
    start_time = time.time()
    
    # --- 1. Solve using default heuristic (assign nearest available robot sequentially) ---
    fallback_res = run_greedy_fallback(db, tasks, robot_records)
    heuristic_assignments = fallback_res["assignments"]
    heuristic_total_dist = fallback_res["total_travel_distance"]
    heuristic_duration = time.time() - start_time
    
    # --- 2. Solve using OR-Tools CP-SAT solver ---
    ortools_assignments = {}
    ortools_total_dist = 0
    ortools_duration = 0.0
    solver_status = "UNKNOWN"
    
    if or_tools_available:
        try:
            ortools_start = time.time()
            model = cp_model.CpModel()
            
            # Variables: x[r, t] is 1 if robot r is assigned to task t
            x = {}
            for r in range(num_robots):
                for t in range(num_tasks):
                    x[r, t] = model.NewBoolVar(f'x_{r}_{t}')
            
            # Constraints checking
            for r in range(num_robots):
                robot = robot_records[r]
                for t in range(num_tasks):
                    task = tasks[t]
                    task_weight = task.requested_quantity * (task.product.weight_kg or 0.0) if task.product else 0.0
                    
                    # 1. Payload Constraint
                    if task_weight > robot.max_payload:
                        model.Add(x[r, t] == 0)
                        
                    # 2. Battery Constraint
                    loc = db.query(WarehouseLocation).filter(WarehouseLocation.id == task.source_location_id).first()
                    tx = loc.x if loc else 1.0
                    ty = loc.y if loc else 1.0
                    dist_to_src = calculate_manhattan_distance(robot.current_x, robot.current_y, tx, ty)
                    
                    dest_loc = db.query(WarehouseLocation).filter(WarehouseLocation.id == task.destination_location_id).first()
                    dx_dest = dest_loc.x if dest_loc else 1.0
                    dy_dest = dest_loc.y if dest_loc else 1.0
                    dist_to_dest = calculate_manhattan_distance(tx, ty, dx_dest, dy_dest)
                    
                    charge_loc = db.query(WarehouseLocation).filter(
                        WarehouseLocation.warehouse_id == robot.warehouse_id,
                        WarehouseLocation.location_type == "CHARGING"
                    ).first()
                    dist_to_charge = 0.0
                    if charge_loc:
                        dist_to_charge = calculate_manhattan_distance(dx_dest, dy_dest, charge_loc.x, charge_loc.y)
                        
                    total_dist_est = dist_to_src + dist_to_dest + dist_to_charge
                    battery_needed = (total_dist_est * 0.5) + 5.0
                    
                    if robot.battery_level < battery_needed:
                        model.Add(x[r, t] == 0)
            
            # Constraint: Each task assigned to exactly one robot (if feasible)
            for t in range(num_tasks):
                model.AddAtMostOne(x[r, t] for r in range(num_robots))
                
            # Constraint: Each robot assigned to at most one task per cycle
            for r in range(num_robots):
                model.Add(sum(x[r, t] for t in range(num_tasks)) <= 1)
                
            # Objective: Minimize total traveled distance & penalize low battery, prioritize task priority score
            objective_terms = []
            for r in range(num_robots):
                robot = robot_records[r]
                for t in range(num_tasks):
                    task = tasks[t]
                    dist = distance_matrix[r][t]
                    priority_bonus = task.priority_score or 0
                    term = 100000 + priority_bonus - dist
                    objective_terms.append(x[r, t] * term)
            model.Maximize(sum(objective_terms))
            
            # Solve
            solver = cp_model.CpSolver()
            solver.parameters.max_time_in_seconds = 2.0
            status = solver.Solve(model)
            
            if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
                solver_status = "OPTIMAL" if status == cp_model.OPTIMAL else "FEASIBLE"
                for r in range(num_robots):
                    for t in range(num_tasks):
                        if solver.BooleanValue(x[r, t]):
                            ortools_assignments[f"task_{tasks[t].id}"] = robots[r]
                            ortools_total_dist += distance_matrix[r][t]
            else:
                solver_status = "NO_FEASIBLE_ASSIGNMENT"
                ortools_assignments = heuristic_assignments
                ortools_total_dist = heuristic_total_dist
                
            ortools_duration = time.time() - ortools_start
        except Exception as e:
            logger.error("OR-Tools solver execution failed: %s", e)
            solver_status = "ERROR"
            ortools_assignments = heuristic_assignments
            ortools_total_dist = heuristic_total_dist
    else:
        # CP-SAT not installed - run greedy fallback solver
        solver_status = "GREEDY_FALLBACK"
        ortools_assignments = heuristic_assignments
        ortools_total_dist = heuristic_total_dist
        ortools_duration = 0.001
        
    return {
        "status": "success",
        "warehouse_id": warehouse_id,
        "solver_used": "OR-Tools CP-SAT" if or_tools_available else "Mock Solver",
        "solver_status": solver_status,
        "tasks_scheduled_count": num_tasks,
        "robots_count": num_robots,
        "robots_used": robots,
        "metrics": {
            "heuristic": {
                "total_travel_distance": heuristic_total_dist,
                "execution_time_seconds": heuristic_duration,
                "assignments": heuristic_assignments
            },
            "ortools_optimized": {
                "total_travel_distance": ortools_total_dist,
                "execution_time_seconds": ortools_duration,
                "assignments": ortools_assignments
            },
            "improvement_pct": round(((heuristic_total_dist - ortools_total_dist) / heuristic_total_dist) * 100, 2) if heuristic_total_dist > 0 else 0.0
        }
    }


@router.get("/optimize-scheduler")
def get_optimized_schedule(warehouse_id: str = "WH-BLR-01", db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Exposes scheduler optimization metrics comparison.
    Allows testing OR-Tools workload balancing results without replacing path-planning logic.
    """
    try:
        result = benchmark_ortools_assignment(db, warehouse_id)
        return result
    except Exception as e:
        logger.error("Optimizer routing error: %s", e)
        raise HTTPException(status_code=500, detail=f"Scheduling optimization benchmark failed: {str(e)}")


@router.post("/tasks/optimize-assignment", summary="Trigger OR-Tools scheduling run and assign active tasks")
def optimize_and_assign_tasks(
    warehouse_id: str = "WH-BLR-01",
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role not in ("admin", "manager"):
        raise HTTPException(403, "Insufficient permissions")

    res = benchmark_ortools_assignment(db, warehouse_id)
    if res.get("status") == "skipped":
        return res

    solver_status = res.get("solver_status", "UNKNOWN")
    assignments = res["metrics"]["ortools_optimized"]["assignments"]

    assigned_count = 0
    assigned_details = []

    for task_key, robot_code in assignments.items():
        task_id = int(task_key.replace("task_", ""))
        task = db.query(Task).filter(Task.id == task_id).with_for_update().first()
        robot = db.query(Robot).filter(
            Robot.robot_code == robot_code,
            Robot.warehouse_id == warehouse_id
        ).with_for_update().first()

        if task and robot and not robot.assigned_task_id and task.status in ("QUEUED", "PRIORITIZED", "FAILED"):
            # Commit the assignment
            robot.assigned_task_id = task.id
            transition_robot_status(db, robot, "ASSIGNED", user.id, f"Assigned via OR-Tools optimization run ({solver_status})")
            task.assigned_robot_id = robot.robot_code
            task.status = "ASSIGNED"
            task.assigned_at = datetime.now(UTC).replace(tzinfo=None)

            assigned_count += 1
            assigned_details.append({"task_number": task.task_number, "robot_code": robot.robot_code})

    if assigned_count > 0:
        audit_ledger.append_entry(db, "OR_TOOLS_BATCH_ASSIGNMENT", {
            "warehouse_id": warehouse_id,
            "assigned_count": assigned_count,
            "solver_status": solver_status,
            "assignments": assigned_details
        })
        db.commit()

    return {
        "status": "success",
        "solver_status": solver_status,
        "assigned_count": assigned_count,
        "assignments": assigned_details
    }


@router.post("/tasks/{task_id}/optimize-assignment", summary="Optimize assignment for a single specific task")
def optimize_single_task(
    task_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role not in ("admin", "manager"):
        raise HTTPException(403, "Insufficient permissions")

    task = db.query(Task).filter(Task.id == task_id).with_for_update().first()
    if not task:
        raise HTTPException(404, "Task not found")

    if task.status not in ("QUEUED", "PRIORITIZED", "FAILED"):
        raise HTTPException(409, f"Task is in state '{task.status}' and cannot be assigned.")

    # Fetch available robots
    robots = db.query(Robot).filter(
        Robot.warehouse_id == task.warehouse_id,
        Robot.enabled == True,
        ~Robot.status.in_(["OFFLINE", "FAILED", "MAINTENANCE"]),
        Robot.assigned_task_id.is_(None)
    ).with_for_update().all()

    if not robots:
        raise HTTPException(422, "No available robots in this warehouse to assign.")

    # Run greedy/fallback or A* distances to find best robot
    fallback_res = run_greedy_fallback(db, [task], robots)
    assignments = fallback_res["assignments"]

    task_key = f"task_{task.id}"
    if task_key not in assignments:
        reason = fallback_res["reasons"].get(task_key, "Infeasible battery/payload bounds.")
        raise HTTPException(422, f"Task assignment optimization failed: {reason}")

    robot_code = assignments[task_key]
    robot = next(r for r in robots if r.robot_code == robot_code)

    robot.assigned_task_id = task.id
    transition_robot_status(db, robot, "ASSIGNED", user.id, "Single task optimized assignment complete.")
    task.assigned_robot_id = robot.robot_code
    task.status = "ASSIGNED"
    task.assigned_at = datetime.now(UTC).replace(tzinfo=None)

    audit_ledger.append_entry(db, "OR_TOOLS_SINGLE_ASSIGNMENT", {
        "task_number": task.task_number,
        "robot_code": robot.robot_code,
        "user_id": user.id
    })
    db.commit()

    return {
        "status": "success",
        "task_id": task.id,
        "assigned_robot": robot.robot_code
    }
