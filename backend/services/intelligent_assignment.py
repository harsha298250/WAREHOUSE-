import logging
import json
from datetime import datetime, UTC
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException

from backend.models import Robot, Task, WarehouseLocation, AuditLedger
from backend import audit_ledger as ledger
from backend.routers.robots import calculate_manhattan_distance, transition_robot_status
from backend.routers.tasks import transition_status
from backend.routers.pathfinding import run_a_star, initialize_warehouse_grid_if_empty

logger = logging.getLogger("intelligent_assignment")

# Configurable Normalized Weights (Must sum to 1.0)
WEIGHT_DISTANCE = 0.40
WEIGHT_BATTERY = 0.25
WEIGHT_WORKLOAD = 0.20
WEIGHT_PRIORITY_FIT = 0.15

MIN_OPERATIONAL_BATTERY = 15.0  # Threshold reserve percentage


def evaluate_robot_candidate(db: Session, task: Task, robot: Robot) -> Dict:
    """
    Evaluates a candidate robot for a given task using deterministic scoring.
    Returns candidate metrics, component scores, total score, and eligibility status.
    """
    # 1. Candidate Eligibility Checks
    if robot.warehouse_id != task.warehouse_id:
        return {
            "robot_id": robot.id,
            "robot_code": robot.robot_code,
            "eligible": False,
            "rejection_reason": f"Robot belongs to warehouse '{robot.warehouse_id}', task requires '{task.warehouse_id}'."
        }

    if not robot.enabled:
        return {
            "robot_id": robot.id,
            "robot_code": robot.robot_code,
            "eligible": False,
            "rejection_reason": "Robot is currently disabled."
        }

    if robot.status in ("OFFLINE", "FAILED", "MAINTENANCE"):
        return {
            "robot_id": robot.id,
            "robot_code": robot.robot_code,
            "eligible": False,
            "rejection_reason": f"Robot status is '{robot.status}'."
        }

    if robot.status == "CHARGING" and robot.battery_level < 90.0:
        return {
            "robot_id": robot.id,
            "robot_code": robot.robot_code,
            "eligible": False,
            "rejection_reason": f"Robot is currently charging (battery level: {robot.battery_level:.1f}%)."
        }

    if robot.assigned_task_id is not None or robot.status in ("ASSIGNED", "MOVING", "PICKING", "RETURNING"):
        return {
            "robot_id": robot.id,
            "robot_code": robot.robot_code,
            "eligible": False,
            "rejection_reason": f"Robot is currently busy with task {robot.assigned_task_id} (status: {robot.status})."
        }

    if robot.battery_level < MIN_OPERATIONAL_BATTERY:
        return {
            "robot_id": robot.id,
            "robot_code": robot.robot_code,
            "eligible": False,
            "rejection_reason": f"Battery level ({robot.battery_level:.1f}%) is below operational threshold ({MIN_OPERATIONAL_BATTERY:.1f}%)."
        }

    # Location coordinates
    src_loc = None
    if task.source_location_id:
        src_loc = db.query(WarehouseLocation).filter(WarehouseLocation.id == task.source_location_id).first()

    src_x = src_loc.x if src_loc else 0.0
    src_y = src_loc.y if src_loc else 0.0

    rx = robot.current_x or 0.0
    ry = robot.current_y or 0.0

    # Pathfinding route distance to source
    route_distance = None
    try:
        initialize_warehouse_grid_if_empty(db, task.warehouse_id)
        start_cell = (int(round(rx)), int(round(ry)))
        goal_cell = (int(round(src_x)), int(round(src_y)))
        
        from backend.models import WarehouseGridCell, WarehouseObstacle
        cells = db.query(WarehouseGridCell).filter(WarehouseGridCell.warehouse_id == task.warehouse_id).all()
        grid_map = {(c.x, c.y): {"traversable": c.traversable, "cost": c.cost} for c in cells}
        
        obs = db.query(WarehouseObstacle).filter(
            WarehouseObstacle.warehouse_id == task.warehouse_id,
            WarehouseObstacle.active == True
        ).all()
        obstacles = set((o.x, o.y) for o in obs)

        path, cost, _ = run_a_star(start_cell, goal_cell, grid_map, obstacles)
        if path:
            route_distance = cost
    except Exception as e:
        logger.debug("A* route calculation fallback for robot %s: %s", robot.robot_code, e)

    if route_distance is None:
        route_distance = calculate_manhattan_distance(rx, ry, src_x, src_y)

    # Route distance from source to destination (if destination specified)
    dst_distance = 0.0
    if task.destination_location_id:
        dst_loc = db.query(WarehouseLocation).filter(WarehouseLocation.id == task.destination_location_id).first()
        if dst_loc:
            dst_distance = calculate_manhattan_distance(src_x, src_y, dst_loc.x or 0.0, dst_loc.y or 0.0)

    total_route_distance = route_distance + dst_distance
    # Estimated route energy consumption (0.2% battery per meter) + safety reserve
    estimated_energy_cost = total_route_distance * 0.2
    required_battery = MIN_OPERATIONAL_BATTERY + estimated_energy_cost

    if robot.battery_level < required_battery:
        return {
            "robot_id": robot.id,
            "robot_code": robot.robot_code,
            "eligible": False,
            "rejection_reason": f"Battery level ({robot.battery_level:.1f}%) is insufficient for route requirement ({required_battery:.1f}% including reserve)."
        }

    # Payload capacity check
    task_weight = 0.0
    prod = getattr(task, "product", None)
    if not prod and getattr(task, "product_id", None):
        from backend.models import Item
        prod = db.query(Item).filter(Item.id == task.product_id).first()
    if prod and getattr(prod, "weight_kg", None):
        task_weight = (task.requested_quantity or 1) * prod.weight_kg

    if task_weight > (robot.max_payload or 200.0):
        return {
            "robot_id": robot.id,
            "robot_code": robot.robot_code,
            "eligible": False,
            "rejection_reason": f"Payload weight ({task_weight:.1f}kg) exceeds max capacity ({robot.max_payload:.1f}kg)."
        }

    # Capability / Robot Type check
    task_meta = {}
    if getattr(task, "task_metadata", None):
        try:
            task_meta = json.loads(task.task_metadata) if isinstance(task.task_metadata, str) else task.task_metadata
        except Exception:
            pass

    req_type = task_meta.get("required_robot_type") or task_meta.get("robot_type") or task_meta.get("required_type")
    if req_type and robot.robot_type and robot.robot_type.upper() != req_type.upper():
        return {
            "robot_id": robot.id,
            "robot_code": robot.robot_code,
            "eligible": False,
            "rejection_reason": f"Robot type '{robot.robot_type}' does not match required type '{req_type}'."
        }

    req_capability = task_meta.get("required_capability") or task_meta.get("required_capabilities")
    if req_capability:
        robot_meta = {}
        if getattr(robot, "robot_metadata", None):
            try:
                robot_meta = json.loads(robot.robot_metadata) if isinstance(robot.robot_metadata, str) else robot.robot_metadata
            except Exception:
                pass
        elif getattr(robot, "metadata", None):
            try:
                robot_meta = json.loads(robot.metadata) if isinstance(robot.metadata, str) else robot.metadata
            except Exception:
                pass
        caps = robot_meta.get("capabilities", []) if isinstance(robot_meta, dict) else []
        if isinstance(req_capability, list):
            missing = [c for c in req_capability if c not in caps]
            if missing:
                return {
                    "robot_id": robot.id,
                    "robot_code": robot.robot_code,
                    "eligible": False,
                    "rejection_reason": f"Robot lacks required capability '{missing[0]}'."
                }
        elif req_capability not in caps:
            return {
                "robot_id": robot.id,
                "robot_code": robot.robot_code,
                "eligible": False,
                "rejection_reason": f"Robot lacks required capability '{req_capability}'."
            }

    # 2. Derive Metrics & Workload
    active_tasks_count = db.query(Task).filter(
        Task.assigned_robot_id == robot.robot_code,
        Task.status.in_(["ASSIGNED", "IN_PROGRESS", "PAUSED"])
    ).count()

    # 3. Component Normalized Scores (0 - 100)
    distance_score = max(0.0, 100.0 - (route_distance * 3.0))
    battery_score = min(100.0, max(0.0, float(robot.battery_level)))
    workload_score = 100.0 / (1.0 + active_tasks_count)

    # Priority Fit Score & Dynamic Weights
    priority_score = 100.0
    w_dist, w_bat, w_work, w_prio = WEIGHT_DISTANCE, WEIGHT_BATTERY, WEIGHT_WORKLOAD, WEIGHT_PRIORITY_FIT

    if task.priority == "CRITICAL":
        w_dist, w_bat, w_work, w_prio = 0.50, 0.25, 0.10, 0.15
        if robot.battery_level < 40.0:
            priority_score = 40.0
    elif task.priority == "HIGH":
        w_dist, w_bat, w_work, w_prio = 0.45, 0.25, 0.15, 0.15
        if robot.battery_level < 30.0:
            priority_score = 60.0

    # Total Weighted Score
    total_score = (
        (distance_score * w_dist) +
        (battery_score * w_bat) +
        (workload_score * w_work) +
        (priority_score * w_prio)
    )

    return {
        "robot_id": robot.id,
        "robot_code": robot.robot_code,
        "name": robot.name,
        "eligible": True,
        "total_score": round(total_score, 1),
        "distance_m": round(route_distance, 1),
        "battery_level": round(robot.battery_level, 1),
        "active_workload": active_tasks_count,
        "route_cost": round(route_distance, 1),
        "scores_breakdown": {
            "distance_score": round(distance_score, 1),
            "battery_score": round(battery_score, 1),
            "workload_score": round(workload_score, 1),
            "priority_score": round(priority_score, 1)
        },
        "reason": f"Distance to source: {route_distance:.1f}m | Battery: {robot.battery_level:.0f}% | Active tasks: {active_tasks_count}"
    }


def recommend_robot_for_task(db: Session, task_id: int) -> Dict:
    """
    Generates explainable, deterministic robot recommendations for a task without modifying database state.
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(404, f"Task {task_id} not found")

    if task.status in ("COMPLETED", "CANCELLED"):
        raise HTTPException(409, f"Task {task.task_number} is in terminal state '{task.status}' and cannot receive robot assignments.")

    robots = db.query(Robot).filter(Robot.warehouse_id == task.warehouse_id).all()
    if not robots:
        return {
            "status": "no_robots",
            "task_id": task_id,
            "task_number": task.task_number,
            "message": "No robots registered in this warehouse.",
            "recommended_robot": None,
            "candidates": []
        }

    evaluated_candidates = []
    for r in robots:
        res = evaluate_robot_candidate(db, task, r)
        evaluated_candidates.append(res)

    eligible_candidates = [c for c in evaluated_candidates if c.get("eligible")]
    eligible_candidates.sort(key=lambda x: x["total_score"], reverse=True)

    if not eligible_candidates:
        return {
            "status": "no_available_robots",
            "task_id": task_id,
            "task_number": task.task_number,
            "message": "No suitable robot currently available.",
            "recommended_robot": None,
            "candidates": evaluated_candidates
        }

    top = eligible_candidates[0]

    # Generate Natural Language Explanation
    explanation = (
        f"Selected robot {top['robot_code']} (Score: {top['total_score']}) because it is the closest eligible robot "
        f"({top['distance_m']}m from task source), has healthy battery ({top['battery_level']}%), "
        f"and has {top['active_workload']} active task(s)."
    )

    # Log recommendation event to Audit Ledger
    ledger.append_entry(db, "INTELLIGENT_ASSIGNMENT_RECOMMENDED", {
        "task_id": task.id,
        "task_number": task.task_number,
        "recommended_robot_code": top["robot_code"],
        "score": top["total_score"],
        "distance_m": top["distance_m"],
        "battery_level": top["battery_level"],
        "active_workload": top["active_workload"]
    })
    db.commit()

    return {
        "status": "recommendation_available",
        "task_id": task.id,
        "task_number": task.task_number,
        "warehouse_id": task.warehouse_id,
        "recommended_robot": {
            "robot_id": top["robot_id"],
            "robot_code": top["robot_code"],
            "name": top["name"],
            "score": top["total_score"],
            "distance_m": top["distance_m"],
            "battery_level": top["battery_level"],
            "active_workload": top["active_workload"],
            "route_cost": top["route_cost"],
            "explanation": explanation
        },
        "candidates": evaluated_candidates
    }


def assign_robot_intelligently(
    db: Session,
    task_id: int,
    robot_identifier: str,
    user_id: int,
    username: str,
    assignment_method: str = "INTELLIGENT"
) -> Dict:
    """
    Executes robot assignment with database transaction locking (with_for_update) to prevent race conditions.
    Supports idempotency (repeated assignment requests return existing assignment).
    """
    # Acquire transaction locks
    task = db.query(Task).filter(Task.id == task_id).with_for_update().first()
    if not task:
        raise HTTPException(404, f"Task {task_id} not found")

    if task.status in ("COMPLETED", "CANCELLED"):
        raise HTTPException(409, f"Task {task.task_number} is in terminal state '{task.status}' and cannot be assigned.")

    # Find robot by ID or robot_code
    robot = None
    if str(robot_identifier).isdigit():
        robot = db.query(Robot).filter(Robot.id == int(robot_identifier)).with_for_update().first()
    if not robot:
        robot = db.query(Robot).filter(Robot.robot_code == str(robot_identifier)).with_for_update().first()

    if not robot:
        raise HTTPException(404, f"Robot '{robot_identifier}' not found")

    # Idempotency check: If task is already assigned to THIS exact robot, return success
    if task.status == "ASSIGNED" and task.assigned_robot_id == robot.robot_code:
        return {
            "status": "assigned",
            "task_id": task.id,
            "task_number": task.task_number,
            "assigned_robot": robot.robot_code,
            "assignment_method": assignment_method,
            "message": f"Task {task.task_number} is already assigned to robot {robot.robot_code}."
        }

    # If task is assigned to a DIFFERENT robot, return Conflict
    if task.status == "ASSIGNED" and task.assigned_robot_id:
        raise HTTPException(409, f"Task {task.task_number} is already assigned to robot {task.assigned_robot_id}.")

    if robot.warehouse_id != task.warehouse_id:
        raise HTTPException(400, f"Robot {robot.robot_code} belongs to warehouse {robot.warehouse_id}, not {task.warehouse_id}.")

    if not robot.enabled or robot.status in ("OFFLINE", "FAILED", "MAINTENANCE") or robot.assigned_task_id is not None:
        raise HTTPException(409, f"Robot {robot.robot_code} is currently unavailable (status: {robot.status}, assigned_task_id: {robot.assigned_task_id}).")

    if robot.status == "CHARGING" and robot.battery_level < 90.0:
        raise HTTPException(409, f"Robot {robot.robot_code} is currently charging (battery level: {robot.battery_level:.1f}%).")

    # Perform assignment
    old_status = task.status
    task.assigned_robot_id = robot.robot_code
    
    # Update Task state machine: QUEUED / PRIORITIZED -> ASSIGNED
    if task.status in ("QUEUED", "PRIORITIZED"):
        transition_status(db, task, "ASSIGNED", user_id, username, f"Assigned to robot {robot.robot_code} via {assignment_method}")

    robot.assigned_task_id = task.id
    if robot.status in ("IDLE", "AVAILABLE"):
        transition_robot_status(db, robot, "ASSIGNED", user_id, f"Assigned task {task.task_number}")

    # Audit Ledger logging
    ledger.append_entry(db, "ROBOT_ASSIGNED", {
        "task_id": task.id,
        "task_number": task.task_number,
        "robot_code": robot.robot_code,
        "assignment_method": assignment_method,
        "assigned_by": username
    })
    db.commit()

    # Broadcast Live WebSocket/SSE event to listeners
    try:
        from backend.sync_broadcast import broadcaster
        broadcaster.broadcast_live(task.warehouse_id, {
            "event_type": "ROBOT_ASSIGNED",
            "task_id": task.id,
            "task_number": task.task_number,
            "robot_code": robot.robot_code,
            "robot_id": robot.id,
            "warehouse_id": task.warehouse_id,
            "status": task.status
        })
    except Exception as e:
        logger.debug("Failed to broadcast live assignment event: %s", e)

    return {
        "status": "assigned",
        "task_id": task.id,
        "task_number": task.task_number,
        "assigned_robot": robot.robot_code,
        "assignment_method": assignment_method,
        "message": f"Task {task.task_number} successfully assigned to robot {robot.robot_code} ({assignment_method})."
    }

