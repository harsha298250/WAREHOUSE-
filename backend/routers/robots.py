import logging
import json
import threading
import time
from datetime import datetime, timezone, timedelta, UTC
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select, text, and_
from sqlalchemy.orm import Session

from backend.database import get_db, engine
from backend.models import (
    Robot, RobotTelemetryEvent, Task, TaskEvent, WarehouseLocation, Warehouse,
    User, AuditLedger, Order, OrderEvent, WarehouseGridCell,
    WarehouseObstacle, RobotRoute, RobotReservation
)
from backend.auth import get_current_user
from backend import audit_ledger as ledger
from backend import notifications
from backend.routers.tasks import complete_task, TaskCompleteSchema, transition_status
from backend.routers.pathfinding import run_a_star, initialize_warehouse_grid_if_empty
from backend.models import DigitalTwinSimulation

logger = logging.getLogger("robots")
router = APIRouter(prefix="/robots", tags=["Robots"])

def get_current_global_tick(db: Session, warehouse_id: str) -> int:
    sim = db.query(DigitalTwinSimulation).filter(
        DigitalTwinSimulation.warehouse_id == warehouse_id
    ).order_by(DigitalTwinSimulation.id.desc()).first()
    if sim:
        return sim.tick_count
    max_events = db.execute(text("SELECT COALESCE(MAX(id), 0) FROM robot_telemetry")).scalar()
    return int(max_events)

# In-Memory Simulation State
# ---------------------------------------------------------------------------
SIMULATION_RUNNING = False
SIMULATION_INTERVAL = 2.0  # seconds per tick
sim_thread = None

class SystemUser:
    def __init__(self):
        self.id = 1
        self.username = "SimulationEngine"
        self.role = "admin"

# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------
class RobotCreateSchema(BaseModel):
    robot_code: str = Field(..., json_schema_extra={"example": "ROB-001"})
    name: str = Field(..., json_schema_extra={"example": "Picker Bot 1"})
    warehouse_id: str = Field(..., json_schema_extra={"example": "WH-TEST-01"})
    robot_type: str = "AGV"
    max_payload: float = 200.0
    max_speed: float = 1.5
    enabled: bool = True
    metadata: Optional[str] = "{}"

class RobotUpdateSchema(BaseModel):
    name: Optional[str] = None
    enabled: Optional[bool] = None
    status: Optional[str] = None
    battery_level: Optional[float] = None
    robot_type: Optional[str] = None
    max_payload: Optional[float] = None
    max_speed: Optional[float] = None
    metadata: Optional[str] = None
    current_x: Optional[float] = None
    current_y: Optional[float] = None
    current_location_id: Optional[str] = None

class RobotManualAssignSchema(BaseModel):
    task_id: int

class IntelligentRecommendRequest(BaseModel):
    task_id: int

class IntelligentAssignRequest(BaseModel):
    task_id: int
    robot_code: str
    assignment_method: Optional[str] = "INTELLIGENT"

class RobotTelemetrySchema(BaseModel):

    event_type: str
    x: float
    y: float
    battery: float
    status: str
    task_id: Optional[int] = None
    metadata: Optional[str] = "{}"

# ---------------------------------------------------------------------------
# Robot State Transition Rules
# ---------------------------------------------------------------------------
ALLOWED_ROBOT_TRANSITIONS = {
    "IDLE": ["AVAILABLE", "ASSIGNED", "OFFLINE", "WAITING_FOR_CHARGER", "CHARGING"],
    "AVAILABLE": ["ASSIGNED", "CHARGING", "OFFLINE", "IDLE", "WAITING_FOR_CHARGER"],
    "ASSIGNED": ["MOVING", "PAUSED", "OFFLINE", "AVAILABLE", "FAILED", "WAITING", "WAITING_FOR_CHARGER"],
    "MOVING": ["PICKING", "PAUSED", "FAILED", "OFFLINE", "RETURNING", "AVAILABLE", "CHARGING", "WAITING", "DROPPING", "WAITING_FOR_CHARGER"],
    "PICKING": ["RETURNING", "PAUSED", "FAILED", "OFFLINE", "AVAILABLE", "WAITING_FOR_CHARGER"],
    "RETURNING": ["AVAILABLE", "IDLE", "PAUSED", "FAILED", "OFFLINE", "CHARGING", "WAITING", "DROPPING", "WAITING_FOR_CHARGER"],
    "DROPPING": ["AVAILABLE", "FAILED", "OFFLINE", "WAITING_FOR_CHARGER"],
    "CHARGING": ["AVAILABLE", "IDLE", "OFFLINE", "FAILED", "WAITING_FOR_CHARGER"],
    "PAUSED": ["MOVING", "PICKING", "RETURNING", "ASSIGNED", "CHARGING", "OFFLINE", "FAILED", "AVAILABLE", "WAITING", "DROPPING", "WAITING_FOR_CHARGER"],
    "WAITING": ["MOVING", "RETURNING", "PAUSED", "AVAILABLE", "FAILED", "OFFLINE", "DROPPING", "WAITING_FOR_CHARGER"],
    "WAITING_FOR_CHARGER": ["CHARGING", "AVAILABLE", "FAILED", "OFFLINE", "PAUSED", "IDLE"],
    "OFFLINE": ["AVAILABLE", "IDLE", "MAINTENANCE"],
    # Allow FAILED robots to recover to AVAILABLE so the simulation can revive them
    "FAILED": ["MAINTENANCE", "OFFLINE", "AVAILABLE"],
    "MAINTENANCE": ["AVAILABLE", "IDLE", "OFFLINE"]
}

def transition_robot_status(
    db: Session,
    robot: Robot,
    target_status: str,
    user_id: Optional[int] = None,
    notes: Optional[str] = None
) -> None:
    curr = robot.status
    if target_status not in ALLOWED_ROBOT_TRANSITIONS.get(curr, []):
        raise HTTPException(
            status_code=409,
            detail=f"Invalid robot state transition from '{curr}' to '{target_status}'"
        )
    robot.status = target_status
    robot.updated_at = datetime.now(UTC).replace(tzinfo=None)
    
    # Log audit event
    ledger.append_entry(db, "ROBOT_STATUS_CHANGED", {
        "robot_code": robot.robot_code,
        "previous_status": curr,
        "new_status": target_status,
        "user_id": user_id,
        "notes": notes or ""
    })
    db.flush()

# ---------------------------------------------------------------------------
# Helper: distance calculation
# ---------------------------------------------------------------------------
def calculate_manhattan_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    return abs(x2 - x1) + abs(y2 - y1)

# ---------------------------------------------------------------------------
# Simulation Engine: Single Step/Tick Execution
# ---------------------------------------------------------------------------
# Starvation-prevention waiting tracker
WAIT_TICKS = {}

def execute_simulation_tick(db: Session, routing_strategy: str = "A_STAR_CONGESTION_AWARE"):
    import random
    from backend.models import Robot, Task, Order, OrderItem, Item, WarehouseLocation, RobotRoute, RobotTelemetryEvent, RobotReservation, InventoryMovement, WarehouseObstacle, WarehouseGridCell
    from backend.settings import get_settings
    app_settings = get_settings(db)
    effective_robot_speed = float(app_settings.get("robot_speed", 1.2))
    effective_low_battery_thresh = float(app_settings.get("low_battery_thresh", 20.0))

    robots_before = {r.id: {
        "status": r.status, "x": r.current_x, "y": r.current_y, "battery": r.battery_level, "warehouse_id": r.warehouse_id
    } for r in db.query(Robot).all()}
    tasks_before = {t.id: {"status": t.status, "warehouse_id": t.warehouse_id} for t in db.query(Task).all()}

    # Phase 11: Evaluate charging system (queue & lowest battery priority) per warehouse
    active_whs = {r.warehouse_id for r in db.query(Robot).all() if r.warehouse_id}
    from backend.charging_manager import evaluate_warehouse_charging_system
    for wh_id in active_whs:
        evaluate_warehouse_charging_system(db, wh_id, low_battery_threshold=effective_low_battery_thresh)

    # Recover FAILED robots: release their tasks back to QUEUED so the fleet can
    # pick them up again, then mark the robot as AVAILABLE.
    failed_robots = db.query(Robot).filter(
        Robot.enabled == True,
        Robot.status == "FAILED"
    ).all()
    for fr in failed_robots:
        if fr.assigned_task_id:
            stuck_task = db.query(Task).filter(Task.id == fr.assigned_task_id).first()
            if stuck_task and stuck_task.status in ("IN_PROGRESS", "ASSIGNED"):
                stuck_task.status = "QUEUED"
                stuck_task.assigned_robot_id = None
                db.add(stuck_task)
                logger.info("Revived task %s from FAILED robot %s → QUEUED",
                            stuck_task.task_number, fr.robot_code)
        fr.assigned_task_id = None
        # Directly overwrite status (bypassing transition guard) since FAILED is a recovery
        fr.status = "AVAILABLE"
        fr.updated_at = datetime.now(UTC).replace(tzinfo=None)
        ledger.append_entry(db, "ROBOT_STATUS_CHANGED", {
            "robot_code": fr.robot_code,
            "previous_status": "FAILED",
            "new_status": "AVAILABLE",
            "notes": "Auto-recovered from FAILED state by simulation watchdog"
        })
        db.flush()

    # Auto-replenish tasks & dispatch to AVAILABLE robots per warehouse
    for wh_id in active_whs:
        # 1. Maintain at least 5 queued picking tasks per warehouse
        q_cnt = db.query(Task).filter(
            Task.warehouse_id == wh_id,
            Task.status.in_(["QUEUED", "PRIORITIZED"])
        ).count()
        if q_cnt < 3:
            items = db.query(Item).all()
            if not items:
                dummy = Item(id="ITM-DUMMY", name="Standard Parcel", unit_cost=10.0, safety_stock=5, sku="SKU-DUMMY")
                db.add(dummy)
                db.flush()
                items = [dummy]
            storage_locs = db.query(WarehouseLocation).filter(WarehouseLocation.warehouse_id == wh_id, WarehouseLocation.location_type == "STORAGE").all()
            packing_locs = db.query(WarehouseLocation).filter(WarehouseLocation.warehouse_id == wh_id, WarehouseLocation.location_type == "PACKING").all()
            if not storage_locs or not packing_locs:
                s_loc = WarehouseLocation(id=f"{wh_id}-STORAGE-1", warehouse_id=wh_id, x=2.0, y=2.0, location_type="STORAGE", zone="STORAGE", aisle="S-1", rack="R-1", shelf="1", capacity=500)
                p_loc = WarehouseLocation(id=f"{wh_id}-PACKING-1", warehouse_id=wh_id, x=10.0, y=2.0, location_type="PACKING", zone="PACKING", aisle="P-1", rack="P-1", shelf="1", capacity=500)
                if not db.query(WarehouseLocation).filter(WarehouseLocation.id == s_loc.id).first():
                    db.add(s_loc)
                if not db.query(WarehouseLocation).filter(WarehouseLocation.id == p_loc.id).first():
                    db.add(p_loc)
                db.flush()
                storage_locs = [s_loc] if not storage_locs else storage_locs
                packing_locs = [p_loc] if not packing_locs else packing_locs

            for k in range(5 - q_cnt):
                order_id = f"SIM-ORD-{random.randint(1000, 9999)}"
                order = Order(id=order_id, customer_ref=f"Auto Sim Order {k+1}", warehouse_id=wh_id, status="CREATED", priority="MEDIUM")
                db.add(order)
                db.flush()
                rand_item = random.choice(items)
                db.add(OrderItem(order_id=order_id, item_id=rand_item.id, requested_qty=1))
                src = random.choice(storage_locs)
                dest = random.choice(packing_locs)
                new_task = Task(
                    task_number=f"SIM-TSK-{random.randint(10000, 99999)}",
                    warehouse_id=wh_id,
                    task_type="PICK",
                    priority="MEDIUM",
                    priority_score=50,
                    status="QUEUED",
                    order_id=order_id,
                    product_id=rand_item.id,
                    source_location_id=src.id,
                    destination_location_id=dest.id,
                    requested_quantity=1,
                    completed_quantity=0
                )
                db.add(new_task)
            db.flush()

        # 2. Dispatch queued tasks to available robots
        unassigned_tasks = db.query(Task).filter(
            Task.warehouse_id == wh_id,
            Task.status.in_(["QUEUED", "PRIORITIZED"]),
            Task.assigned_robot_id == None
        ).order_by(Task.priority_score.desc(), Task.id.asc()).all()

        if unassigned_tasks:
            avail_robots = db.query(Robot).filter(
                Robot.warehouse_id == wh_id,
                Robot.enabled == True,
                Robot.status == "AVAILABLE",
                Robot.assigned_task_id == None,
                Robot.battery_level > 20.0
            ).all()

            for task in unassigned_tasks:
                if not avail_robots:
                    break
                src_loc = db.query(WarehouseLocation).filter(WarehouseLocation.id == task.source_location_id).first()
                src_x = float(src_loc.x) if src_loc else 1.0
                src_y = float(src_loc.y) if src_loc else 1.0

                best_robot = min(avail_robots, key=lambda r: abs(r.current_x - src_x) + abs(r.current_y - src_y))
                avail_robots.remove(best_robot)

                best_robot.assigned_task_id = task.id
                best_robot.status = "ASSIGNED"
                best_robot.target_location_id = task.source_location_id
                best_robot.target_x = src_x
                best_robot.target_y = src_y
                best_robot.updated_at = datetime.now(UTC).replace(tzinfo=None)
                db.add(best_robot)

                task.assigned_robot_id = best_robot.id
                task.status = "ASSIGNED"
                task.assigned_at = datetime.now(UTC).replace(tzinfo=None)
                db.add(task)

        # 3. Assign dynamic patrol targets to any remaining idle robots
        idle_robots = db.query(Robot).filter(
            Robot.warehouse_id == wh_id,
            Robot.enabled == True,
            Robot.status == "AVAILABLE",
            Robot.assigned_task_id == None,
            Robot.battery_level > 20.0
        ).all()
        patrol_points = [(1.0, 5.0), (4.0, 5.0), (6.0, 5.0), (8.0, 5.0), (10.0, 5.0), (2.0, 2.0), (5.0, 2.0), (8.0, 2.0)]
        for idx, ir in enumerate(idle_robots):
            pt = patrol_points[(idx + int(ir.current_x)) % len(patrol_points)]
            if abs(ir.current_x - pt[0]) > 0.5 or abs(ir.current_y - pt[1]) > 0.5:
                ir.target_x = pt[0]
                ir.target_y = pt[1]
                ir.status = "MOVING"
                db.add(ir)

    db.flush()

    # Get active robots
    robots = db.query(Robot).filter(
        Robot.enabled == True,
        ~Robot.status.in_(["OFFLINE", "FAILED", "MAINTENANCE"])
    ).all()

    # Preload current cells and state
    current_cells = {}
    active_routes = {}
    next_cells = {}
    robot_priorities = {}

    for r in robots:
        # Clamp to valid grid boundaries [0.0, 12.0] and [0.0, 5.0]
        r.current_x = max(0.0, min(12.0, float(r.current_x)))
        r.current_y = max(0.0, min(5.0, float(r.current_y)))
        current_cells[r.id] = (int(round(r.current_x)), int(round(r.current_y)))
        r.last_heartbeat_at = datetime.now(UTC).replace(tzinfo=None)

        if r.status == "CHARGING":
            has_arrived = (r.target_x is None or r.target_y is None or 
                           (r.target_x == 0.0 and r.target_y == 0.0) or
                           (abs(r.current_x - r.target_x) < 0.1 and abs(r.current_y - r.target_y) < 0.1))
            if has_arrived:
                # Charging logic
                r.battery_level = min(100.0, r.battery_level + 15.0)
                db.add(RobotTelemetryEvent(
                    robot_id=r.id,
                    event_type="BATTERY_UPDATED",
                    x=r.current_x,
                    y=r.current_y,
                    battery=r.battery_level,
                    status="CHARGING",
                    task_id=r.assigned_task_id
                ))
                if r.battery_level >= 100.0:
                    transition_robot_status(db, r, "AVAILABLE", notes="Charging complete. Battery full.")
                    r.target_location_id = None
                    r.target_x = 0.0
                    r.target_y = 0.0
                    notifications.send_change_alert("ROBOT_CHARGING_COMPLETED", {
                        "robot_code": r.robot_code,
                        "battery": 100.0
                    })
                continue

        if r.status == "PAUSED":
            # Auto-resume paused robots after a 1-tick cooldown so deadlocks
            # can resolve.  PAUSED → MOVING if still assigned, else AVAILABLE.
            if r.assigned_task_id:
                task_paused = db.query(Task).filter(Task.id == r.assigned_task_id).first()
                if task_paused:
                    # Resume toward source unless we already picked up (RETURNING phase)
                    resume_status = "MOVING"
                    # Heuristic: if target_x/target_y matches destination, we were RETURNING
                    dest_loc_p = db.query(WarehouseLocation).filter(
                        WarehouseLocation.id == task_paused.destination_location_id
                    ).first()
                    if dest_loc_p and r.target_x is not None and r.target_y is not None:
                        if (abs(r.target_x - dest_loc_p.x) < 0.1 and
                                abs(r.target_y - dest_loc_p.y) < 0.1):
                            resume_status = "RETURNING"
                    r.status = resume_status
                    r.updated_at = datetime.now(UTC).replace(tzinfo=None)
                    ledger.append_entry(db, "ROBOT_STATUS_CHANGED", {
                        "robot_code": r.robot_code,
                        "previous_status": "PAUSED",
                        "new_status": resume_status,
                        "notes": "Auto-resumed from PAUSED by simulation deadlock recovery"
                    })
                    db.flush()
                else:
                    r.assigned_task_id = None
                    r.status = "AVAILABLE"
                    db.flush()
            else:
                r.status = "AVAILABLE"
                r.updated_at = datetime.now(UTC).replace(tzinfo=None)
                db.flush()
            # Fall through to let the remainder of this tick process the robot

        if r.status == "DROPPING":
            task = db.query(Task).filter(Task.id == r.assigned_task_id).with_for_update().first() if r.assigned_task_id else None
            if task:
                try:
                    user_sys = SystemUser()
                    payload = TaskCompleteSchema(
                        completed_quantity=task.requested_quantity,
                        notes=f"Simulated execution complete by robot {r.robot_code}"
                    )
                    complete_task(task_id=task.id, payload=payload, db=db, user=user_sys)
                    r.total_tasks_completed += 1
                    r.assigned_task_id = None
                    transition_robot_status(db, r, "AVAILABLE", notes="Task successfully completed by robot fleet simulation.")
                    r.target_location_id = None
                    r.target_x = 0.0
                    r.target_y = 0.0
                    notifications.send_change_alert("ROBOT_TASK_COMPLETED", {
                        "robot_code": r.robot_code,
                        "task_number": task.task_number
                    })
                except Exception as e:
                    import traceback
                    logger.error("Simulation failed to complete task %s: %s\n%s", task.id, e, traceback.format_exc())
                    transition_robot_status(db, r, "FAILED", notes=f"Simulation error during completion: {str(e)}")
                    task.status = "FAILED"
                db.commit()
            else:
                r.assigned_task_id = None
                transition_robot_status(db, r, "AVAILABLE", notes="Dropping complete. No task found.")
                db.commit()
            continue

        has_target = False
        goal_x, goal_y = None, None
        task = None

        if r.assigned_task_id:
            task = db.query(Task).filter(Task.id == r.assigned_task_id).with_for_update().first()
            if not task:
                r.assigned_task_id = None
                r.status = "AVAILABLE"
                continue

            has_target = True
            source_loc = db.query(WarehouseLocation).filter(WarehouseLocation.id == task.source_location_id).first()
            dest_loc = db.query(WarehouseLocation).filter(WarehouseLocation.id == task.destination_location_id).first()
            sx = int(round(source_loc.x)) if source_loc else 1
            sy = int(round(source_loc.y)) if source_loc else 1
            dx_dest = int(round(dest_loc.x)) if dest_loc else 1
            dy_dest = int(round(dest_loc.y)) if dest_loc else 1

            goal_x, goal_y = sx, sy
            if r.status in ("RETURNING", "DROPPING"):
                goal_x, goal_y = dx_dest, dy_dest
            elif r.status == "WAITING":
                # WAITING robots: infer goal from their stored target coordinates.
                # target_x/target_y are set to destination when status was RETURNING.
                if (r.target_x is not None and r.target_y is not None and
                        dest_loc is not None and
                        abs(r.target_x - dest_loc.x) < 0.5 and
                        abs(r.target_y - dest_loc.y) < 0.5):
                    goal_x, goal_y = dx_dest, dy_dest

            if r.status == "ASSIGNED":
                transition_robot_status(db, r, "MOVING", notes=f"Driving to pick task source {task.source_location_id}")
                task.status = "IN_PROGRESS"
                task.started_at = datetime.now(UTC).replace(tzinfo=None)
                admin_user = db.query(User).filter(User.role == "admin").first() or db.query(User).first()
                event_user_id = admin_user.id if admin_user else None
                db.add(TaskEvent(
                    task_id=task.id,
                    event_type="TASK_IN_PROGRESS",
                    previous_status="ASSIGNED",
                    new_status="IN_PROGRESS",
                    user_id=event_user_id,
                    created_at=datetime.now(UTC).replace(tzinfo=None),
                    reason="Robot started moving to pickup location."
                ))
        elif r.status == "CHARGING" and r.target_x is not None and r.target_y is not None and not (r.target_x == 0.0 and r.target_y == 0.0):
            has_target = True
            goal_x = int(round(r.target_x))
            goal_y = int(round(r.target_y))

        if has_target:
            # Retrieve route
            route = db.query(RobotRoute).filter(
                RobotRoute.robot_id == r.id,
                RobotRoute.status == "ACTIVE"
            ).order_by(RobotRoute.created_at.desc()).first()

            if route:
                # Check if route is blocked by any active obstacle
                try:
                    path_list = json.loads(route.path_data)
                    obs = db.query(WarehouseObstacle).filter(
                        WarehouseObstacle.warehouse_id == r.warehouse_id,
                        WarehouseObstacle.active == True
                    ).all()
                    obstacles_set = set()
                    for o in obs:
                        for w in range(o.width):
                            for h in range(o.height):
                                obstacles_set.add((o.x + w, o.y + h))
                    
                    is_blocked = False
                    for p in path_list[1:]:
                        if tuple(p) in obstacles_set:
                            is_blocked = True
                            break
                    
                    if is_blocked:
                        route.status = "REPLANNED"
                        route.completed_at = datetime.now(UTC).replace(tzinfo=None)
                        db.add(route)
                        db.flush()
                        route = None  # Force replanning using A*
                except Exception as route_check_err:
                    logger.warning("Failed to verify if route is blocked: %s", route_check_err)

            if not route:
                # We must plan a route using A*
                start_x, start_y = current_cells[r.id]

                # Generate default layout if empty
                initialize_warehouse_grid_if_empty(db, r.warehouse_id)

                # Fetch grid cells
                cells = db.query(WarehouseGridCell).filter(WarehouseGridCell.warehouse_id == r.warehouse_id).all()
                grid_map = {}
                for c in cells:
                    cost = c.cost
                    if c.cell_type == "RESTRICTED" or c.restricted:
                        cost = 10.0
                    elif c.cell_type == "HIGH_RISK":
                        cost = 5.0
                    else:
                        cost = 1.0
                    grid_map[(c.x, c.y)] = {"traversable": c.traversable, "cost": cost, "type": c.cell_type}

                # Congestion-aware costs mapping: any cell occupied by OTHER robots gets cost = 15.0
                if routing_strategy == "A_STAR_CONGESTION_AWARE":
                    for other_r in robots:
                        if other_r.id != r.id:
                            ox, oy = int(round(other_r.current_x)), int(round(other_r.current_y))
                            if (ox, oy) in grid_map:
                                grid_map[(ox, oy)]["cost"] = 15.0

                # Fetch obstacles
                obs = db.query(WarehouseObstacle).filter(
                    WarehouseObstacle.warehouse_id == r.warehouse_id,
                    WarehouseObstacle.active == True
                ).all()
                obstacles = set()
                for o in obs:
                    for w in range(o.width):
                        for h in range(o.height):
                            obstacles.add((o.x + w, o.y + h))

                path, cost, duration, msg, expanded_count = run_a_star((start_x, start_y), (goal_x, goal_y), grid_map, obstacles)

                if not path:
                    logger.error(f"Route planning failed for {r.robot_code}: {msg}")
                    if r.status == "CHARGING":
                        r.target_x = r.current_x
                        r.target_y = r.current_y
                        r.status = "AVAILABLE"
                    else:
                        transition_robot_status(db, r, "AVAILABLE", notes=f"Pathfinding failed: {msg}")
                        r.assigned_task_id = None
                        if task:
                            task.status = "FAILED"
                    notifications.send_change_alert("ROUTE_FAILED", {
                        "robot_code": r.robot_code,
                        "task_number": task.task_number if task else "CHARGE",
                        "reason": msg
                    })
                    continue

                # Save new route
                route = RobotRoute(
                    robot_id=r.id,
                    task_id=task.id if task else None,
                    warehouse_id=r.warehouse_id,
                    start_x=start_x,
                    start_y=start_y,
                    goal_x=goal_x,
                    goal_y=goal_y,
                    algorithm="A_STAR",
                    path_data=json.dumps(path),
                    distance=float(len(path) - 1),
                    cost=cost,
                    status="ACTIVE"
                )
                db.add(route)
                db.flush()
                db.refresh(route)

                # Clear old reservations
                db.query(RobotReservation).filter(RobotReservation.robot_id == r.id).delete()
                
                curr_tick = get_current_global_tick(db, r.warehouse_id)
                for t_idx, coord in enumerate(path):
                    db.add(RobotReservation(
                        robot_id=r.id,
                        warehouse_id=r.warehouse_id,
                        x=coord[0],
                        y=coord[1],
                        tick=curr_tick + t_idx
                    ))
                db.flush()

                if task:
                    ledger.append_entry(db, "PATH_PLANNED", {
                        "robot_code": r.robot_code,
                        "task_number": task.task_number,
                        "distance": len(path) - 1,
                        "cost": cost,
                        "planning_time_ms": duration
                    })
                else:
                    ledger.append_entry(db, "PATH_PLANNED", {
                        "robot_code": r.robot_code,
                        "task_number": "CHARGE",
                        "distance": len(path) - 1,
                        "cost": cost,
                        "planning_time_ms": duration
                    })

            # Retrieve active route coordinates list
            path_list = json.loads(route.path_data)
            if len(path_list) > 1:
                next_cells[r.id] = tuple(path_list[1])
                active_routes[r.id] = route
                
                # Compute priorities
                base_priority = task.priority_score if task else 50
                wait_bonus = WAIT_TICKS.get(r.id, 0) * 10
                robot_priorities[r.id] = base_priority + wait_bonus
            else:
                # Already at goal coordinate cell (len == 1) — handle arrival immediately
                route.status = "COMPLETED"
                route.completed_at = datetime.now(UTC).replace(tzinfo=None)

                if r.status == "MOVING" and task:
                    r.current_location_id = task.source_location_id
                    transition_robot_status(db, r, "PICKING", notes="Already at source. Commencing pick operations.")
                    db.add(RobotTelemetryEvent(
                        robot_id=r.id,
                        event_type="STATUS_CHANGED",
                        x=r.current_x,
                        y=r.current_y,
                        battery=r.battery_level,
                        status="PICKING",
                        task_id=r.assigned_task_id
                    ))
                elif r.status == "RETURNING" and task:
                    r.current_location_id = task.destination_location_id
                    route.status = "COMPLETED"
                    route.completed_at = datetime.now(UTC).replace(tzinfo=None)
                    transition_robot_status(db, r, "DROPPING", notes="Arrived at destination. Commencing drop operations.")
                    db.add(RobotTelemetryEvent(
                        robot_id=r.id,
                        event_type="STATUS_CHANGED",
                        x=r.current_x,
                        y=r.current_y,
                        battery=r.battery_level,
                        status="DROPPING",
                        task_id=r.assigned_task_id
                    ))
                elif r.status == "CHARGING":
                    r.current_location_id = r.target_location_id
                    r.current_x = float(goal_x)
                    r.current_y = float(goal_y)
                    db.add(RobotTelemetryEvent(
                        robot_id=r.id,
                        event_type="STATUS_CHANGED",
                        x=r.current_x,
                        y=r.current_y,
                        battery=r.battery_level,
                        status="CHARGING",
                        task_id=r.assigned_task_id
                    ))
                db.commit()

    # Group collision checks by warehouse
    robot_warehouses = {r.id: r.warehouse_id for r in robots}
    # Conflict check
    conflicts = set()
    for r_id, next_cell in next_cells.items():
        curr_cell = current_cells[r_id]
        r_wh = robot_warehouses.get(r_id)

        # Check collision with static robots
        for other_id, other_curr_cell in current_cells.items():
            if r_id == other_id:
                continue
            if robot_warehouses.get(other_id) != r_wh:
                continue
            if other_id not in next_cells:  # Static robot (paused, idle, charging, etc.)
                if next_cell == other_curr_cell:
                    conflicts.add(r_id)

        for other_id, other_next_cell in next_cells.items():
            if r_id == other_id:
                continue
            if robot_warehouses.get(other_id) != r_wh:
                continue

            other_curr_cell = current_cells[other_id]

            conflict = False
            # Check same cell conflict
            if next_cell == other_next_cell:
                conflict = True
            # Check head-on swap conflict
            elif next_cell == other_curr_cell and other_next_cell == curr_cell:
                conflict = True

            if conflict:
                p_self = robot_priorities.get(r_id, 0)
                p_other = robot_priorities.get(other_id, 0)

                if p_self < p_other:
                    conflicts.add(r_id)
                elif p_self > p_other:
                    conflicts.add(other_id)
                else:
                    if r_id < other_id:
                        conflicts.add(r_id)
                    else:
                        conflicts.add(other_id)

    # Apply steps for each robot
    for r in robots:
        is_charging_and_moving = (r.status == "CHARGING" and r.target_x is not None and r.target_y is not None and
                                  not (abs(r.current_x - r.target_x) < 0.1 and abs(r.current_y - r.target_y) < 0.1))
        
        if r.assigned_task_id or is_charging_and_moving:
            task = None
            if r.assigned_task_id:
                task = db.query(Task).filter(Task.id == r.assigned_task_id).first()
                if not task:
                    continue

            route = active_routes.get(r.id)
            
            # If status is PICKING, wait 1 step then head to destination
            if r.status == "PICKING" and task:
                r.battery_level = max(0.0, r.battery_level - 5.0) # flat picking penalty
                transition_robot_status(db, r, "RETURNING", notes=f"Picking complete. Transporting to dest {task.destination_location_id}")
                r.target_location_id = task.destination_location_id
                
                dest_loc = db.query(WarehouseLocation).filter(WarehouseLocation.id == task.destination_location_id).first()
                r.target_x = dest_loc.x if dest_loc else 1.0
                r.target_y = dest_loc.y if dest_loc else 1.0

                # Mark route completed to recalculate for RETURNING
                if route:
                    route.status = "COMPLETED"
                    route.completed_at = datetime.now(UTC).replace(tzinfo=None)
                db.flush()
                
                db.add(RobotTelemetryEvent(
                    robot_id=r.id,
                    event_type="STATUS_CHANGED",
                    x=r.current_x,
                    y=r.current_y,
                    battery=r.battery_level,
                    status="RETURNING",
                    task_id=r.assigned_task_id
                ))
                continue

            # If status is DROPPING, complete task and release robot back to AVAILABLE
            if r.status == "DROPPING" and task:
                try:
                    complete_task(task.id, payload=TaskCompleteSchema(completed_quantity=task.requested_quantity), db=db, user=SystemUser())
                except Exception as comp_err:
                    logger.warning("Auto task completion failed for task %s: %s", task.id, comp_err)
                    task.status = "COMPLETED"
                    task.completed_quantity = task.requested_quantity

                r.assigned_task_id = None
                r.target_location_id = None
                transition_robot_status(db, r, "AVAILABLE", notes=f"Task {task.task_number} completed. Robot returned to AVAILABLE.")
                db.flush()
                
                db.add(RobotTelemetryEvent(
                    robot_id=r.id,
                    event_type="STATUS_CHANGED",
                    x=r.current_x,
                    y=r.current_y,
                    battery=r.battery_level,
                    status="AVAILABLE",
                    task_id=None
                ))
                continue

            if not route:
                continue

            path_list = json.loads(route.path_data)

            if r.id in conflicts:
                # Wait
                r.status = "WAITING"
                WAIT_TICKS[r.id] = WAIT_TICKS.get(r.id, 0) + 1
                
                db.add(RobotTelemetryEvent(
                    robot_id=r.id,
                    event_type="POSITION_UPDATED",
                    x=r.current_x,
                    y=r.current_y,
                    battery=r.battery_level,
                    status="WAITING",
                    task_id=r.assigned_task_id,
                    metadata=json.dumps({"wait_reason": "COLLISION_AVOIDANCE"})
                ))

                if WAIT_TICKS[r.id] > 5:
                    transition_robot_status(db, r, "PAUSED", notes="Deadlock corridor collision protection: robot paused.")
                    WAIT_TICKS[r.id] = 0
                    ledger.append_entry(db, "DEADLOCK_DETECTED", {
                        "robot_code": r.robot_code,
                        "task_number": task.task_number if task else "CHARGE",
                        "reason": "CORRIDOR_DEADLOCK"
                    })
                    continue

                if WAIT_TICKS[r.id] == 3:
                    # Invalidate route and force dynamic replanning detouring this cell
                    route.status = "REPLANNED"
                    route.completed_at = datetime.now(UTC).replace(tzinfo=None)

                    ledger.append_entry(db, "PATH_REPLANNED", {
                        "robot_code": r.robot_code,
                        "task_number": task.task_number if task else "CHARGE",
                        "reason": "ROBOT_CONFLICT"
                    })
                    notifications.send_change_alert("ROUTE_REPLANNED", {
                        "robot_code": r.robot_code,
                        "task_number": task.task_number if task else "CHARGE",
                        "reason": "Replanned due to path congestion."
                    })
                continue

            # No conflict: proceed!
            if len(path_list) > 1:
                next_pos = path_list[1]
                r.current_x = float(next_pos[0])
                r.current_y = float(next_pos[1])
                r.total_distance += effective_robot_speed
                r.battery_level = max(0.0, r.battery_level - 0.5) # 0.5% per step
                if r.battery_level <= effective_low_battery_thresh and r.status != "CHARGING":
                    notifications.send_change_alert("ROBOT_LOW_BATTERY", {
                        "robot_code": r.robot_code,
                        "warehouse": r.warehouse_id,
                        "battery_level": r.battery_level,
                        "low_battery_thresh": effective_low_battery_thresh
                    })
                db.add(RobotTelemetryEvent(
                    robot_id=r.id,
                    event_type="POSITION_UPDATED",
                    x=r.current_x,
                    y=r.current_y,
                    battery=r.battery_level,
                    status=r.status,
                    task_id=r.assigned_task_id
                ))

                # Remove step from route path_data
                path_list.pop(0)
                route.path_data = json.dumps(path_list)

                # Reset wait ticks
                WAIT_TICKS[r.id] = 0

                if len(path_list) == 1:
                    # Arrived!
                    if r.status == "MOVING" and task:
                        r.current_location_id = task.source_location_id
                        transition_robot_status(db, r, "PICKING", notes="Arrived at source. Commencing pick operations.")
                        route.status = "COMPLETED"
                        route.completed_at = datetime.now(UTC).replace(tzinfo=None)
                        db.add(RobotTelemetryEvent(
                            robot_id=r.id,
                            event_type="STATUS_CHANGED",
                            x=r.current_x,
                            y=r.current_y,
                            battery=r.battery_level,
                            status="PICKING",
                            task_id=r.assigned_task_id
                        ))
                    elif r.status == "RETURNING" and task:
                        r.current_location_id = task.destination_location_id
                        route.status = "COMPLETED"
                        route.completed_at = datetime.now(UTC).replace(tzinfo=None)
                        transition_robot_status(db, r, "DROPPING", notes="Arrived at destination. Commencing drop operations.")
                        db.add(RobotTelemetryEvent(
                            robot_id=r.id,
                            event_type="STATUS_CHANGED",
                            x=r.current_x,
                            y=r.current_y,
                            battery=r.battery_level,
                            status="DROPPING",
                            task_id=r.assigned_task_id
                        ))
                    elif r.status == "CHARGING":
                        # Arrived at charger!
                        r.current_location_id = r.target_location_id
                        r.current_x = float(r.target_x)
                        r.current_y = float(r.target_y)
                        route.status = "COMPLETED"
                        route.completed_at = datetime.now(UTC).replace(tzinfo=None)
                        db.add(route)
                        db.add(RobotTelemetryEvent(
                            robot_id=r.id,
                            event_type="STATUS_CHANGED",
                            x=r.current_x,
                            y=r.current_y,
                            battery=r.battery_level,
                            status="CHARGING",
                            task_id=r.assigned_task_id
                        ))
                else:
                    # Write regular position update
                    db.add(RobotTelemetryEvent(
                        robot_id=r.id,
                        event_type="POSITION_UPDATED",
                        x=r.current_x,
                        y=r.current_y,
                        battery=r.battery_level,
                        status=r.status,
                        task_id=r.assigned_task_id
                    ))

        # Check battery alert triggers
        if r.battery_level <= 10.0:
            notifications.send_change_alert("ROBOT_CRITICAL_BATTERY", {
                "robot_code": r.robot_code,
                "battery": r.battery_level
            })
        elif r.battery_level <= 25.0:
            notifications.send_change_alert("ROBOT_LOW_BATTERY", {
                "robot_code": r.robot_code,
                "battery": r.battery_level
            })

    # Update dynamic robot utilization percent for all robots
    all_robots = db.query(Robot).all()
    for r in all_robots:
        is_active_and_busy = r.enabled and r.status in ("MOVING", "PICKING", "RETURNING", "WAITING", "PAUSED")
        current_util = r.utilization_percent or 0.0
        r.utilization_percent = round(current_util * 0.9 + (100.0 if is_active_and_busy else 0.0) * 0.1, 1)

    db.commit()

    # Compare and broadcast changes to live subscribers
    try:
        from backend.sync_broadcast import broadcaster
        robots_after = db.query(Robot).all()
        tasks_after = db.query(Task).all()

        for r in robots_after:
            prev = robots_before.get(r.id)
            if not prev:
                continue

            # ROBOT_MOVED
            if prev["x"] != r.current_x or prev["y"] != r.current_y:
                broadcaster.broadcast_live(r.warehouse_id, {
                    "event_type": "ROBOT_MOVED",
                    "entity_type": "robot",
                    "entity_id": r.robot_code,
                    "data": {"x": r.current_x, "y": r.current_y, "total_distance": r.total_distance, "battery_level": r.battery_level}
                })

            # ROBOT_STATUS_CHANGED
            if prev["status"] != r.status:
                broadcaster.broadcast_live(r.warehouse_id, {
                    "event_type": "ROBOT_STATUS_CHANGED",
                    "entity_type": "robot",
                    "entity_id": r.robot_code,
                    "data": {"status": r.status}
                })

            # ROBOT_BATTERY_CHANGED
            if prev["battery"] != r.battery_level:
                broadcaster.broadcast_live(r.warehouse_id, {
                    "event_type": "ROBOT_BATTERY_CHANGED",
                    "entity_type": "robot",
                    "entity_id": r.robot_code,
                    "data": {"battery_level": r.battery_level}
                })

        for t in tasks_after:
            prev = tasks_before.get(t.id)
            if not prev:
                continue

            # TASK_STATUS_CHANGED
            if prev["status"] != t.status:
                broadcaster.broadcast_live(t.warehouse_id, {
                    "event_type": "TASK_STATUS_CHANGED",
                    "entity_type": "task",
                    "entity_id": t.task_number,
                    "data": {"status": t.status}
                })
    except Exception as broadcast_err:
        logger.warning("Live sync broadcast failed: %s", broadcast_err)

# Start background thread immediately when router loads
start_simulation_thread = lambda: None
def start_sim():
    global sim_thread, SIMULATION_RUNNING
    if sim_thread is None:
        SIMULATION_RUNNING = True
        sim_thread = threading.Thread(target=run_simulation_loop, daemon=True)
        sim_thread.start()

# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------
@router.get("", summary="Get list of robots")
def list_robots(
    warehouse_id: Optional[str] = None,
    status: Optional[str] = None,
    enabled: Optional[bool] = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    query = db.query(Robot)
    if warehouse_id:
        query = query.filter(Robot.warehouse_id == warehouse_id)
    if status:
        query = query.filter(Robot.status == status)
    if enabled is not None:
        query = query.filter(Robot.enabled == enabled)
    return query.all()

@router.get("/{robot_id}", summary="Get robot detailed status")
def get_robot_detail(
    robot_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    r = db.query(Robot).filter(Robot.id == robot_id).first()
    if not r:
        raise HTTPException(404, "Robot not found")
    return r

@router.post("", status_code=201, summary="Register a new robot")
def create_robot(
    payload: RobotCreateSchema,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role not in ("admin", "manager"):
        raise HTTPException(403, "Insufficient permissions")

    # Uniqueness check
    exist = db.query(Robot).filter(Robot.robot_code == payload.robot_code).first()
    if exist:
        raise HTTPException(409, "Robot code already exists")

    # Verify warehouse exists
    wh = db.query(Warehouse).filter(Warehouse.id == payload.warehouse_id).first()
    if not wh:
        raise HTTPException(404, f"Warehouse '{payload.warehouse_id}' not found")

    # Initial staging location fallback
    stage_loc = db.query(WarehouseLocation).filter(
        WarehouseLocation.warehouse_id == payload.warehouse_id
    ).first()
    
    r = Robot(
        robot_code=payload.robot_code,
        name=payload.name,
        warehouse_id=payload.warehouse_id,
        robot_type=payload.robot_type,
        max_payload=payload.max_payload,
        max_speed=payload.max_speed,
        enabled=payload.enabled,
        current_location_id=stage_loc.id if stage_loc else None,
        current_x=stage_loc.x if stage_loc else 0.0,
        current_y=stage_loc.y if stage_loc else 0.0,
        status="AVAILABLE"
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return {"status": "created", "robot_id": r.id, "robot_code": r.robot_code}

@router.patch("/{robot_id}", summary="Edit robot fields")
def update_robot(
    robot_id: int,
    payload: RobotUpdateSchema,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role not in ("admin", "manager"):
        raise HTTPException(403, "Insufficient permissions")
    r = db.query(Robot).filter(Robot.id == robot_id).with_for_update().first()
    if not r:
        raise HTTPException(404, "Robot not found")

    old_x, old_y = r.current_x, r.current_y
    old_status = r.status
    
    for k, v in payload.model_dump(exclude_unset=True).items():
        if k == "status" and v is not None:
            transition_robot_status(db, r, v, user.id, "Manually updated via status patch API")
        elif v is not None:
            setattr(r, k, v)

    # Invalidate active route if position or status changed during task execution
    pos_changed = (payload.current_x is not None and payload.current_x != old_x) or \
                  (payload.current_y is not None and payload.current_y != old_y)
    if (pos_changed or (payload.status is not None and payload.status != old_status)) and r.assigned_task_id:
        active_route = db.query(RobotRoute).filter(
            RobotRoute.robot_id == r.id,
            RobotRoute.status == "ACTIVE"
        ).first()
        if active_route:
            active_route.status = "INVALIDATED"
            active_route.completed_at = datetime.now(UTC).replace(tzinfo=None)

    # Live sync broadcast for Digital Twin
    try:
        from backend.sync_broadcast import broadcaster
        broadcaster.broadcast_live(r.warehouse_id, {
            "event_type": "ROBOT_UPDATED",
            "entity_type": "robot",
            "entity_id": r.robot_code,
            "data": {
                "x": r.current_x,
                "y": r.current_y,
                "status": r.status,
                "battery_level": r.battery_level,
                "enabled": r.enabled
            }
        })
    except Exception as e:
        logger.warning("Failed live broadcast for robot update: %s", e)
            
    db.commit()
    return {"status": "updated", "robot_id": r.id}

@router.delete("/{robot_id}", summary="Safely remove or deactivate a robot")
def remove_robot(
    robot_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role not in ("admin", "manager"):
        raise HTTPException(403, "Insufficient permissions to remove robots")
    r = db.query(Robot).filter(Robot.id == robot_id).with_for_update().first()
    if not r:
        raise HTTPException(404, "Robot not found")

    # Safe Removal Check: prevent deletion/deactivation if robot has an active task
    if r.assigned_task_id or r.status in ("ASSIGNED", "MOVING", "PICKING", "RETURNING", "PAUSED", "WAITING"):
        raise HTTPException(
            status_code=409,
            detail=f"Robot {r.robot_code} cannot be removed because it currently has an active task."
        )

    # Soft deactivation preserves historical audit ledger and telemetry logs
    r.enabled = False
    r.status = "OFFLINE"
    r.updated_at = datetime.now(UTC).replace(tzinfo=None)

    ledger.append_entry(db, "ROBOT_DEACTIVATED", {
        "robot_id": r.id,
        "robot_code": r.robot_code,
        "deactivated_by": user.username,
        "timestamp": datetime.now(UTC).replace(tzinfo=None).isoformat()
    })
    db.commit()

    return {
        "status": "deactivated",
        "robot_id": r.id,
        "robot_code": r.robot_code,
        "message": f"Robot {r.robot_code} safely deactivated."
    }

@router.post("/{robot_id}/assign", summary="Manually assign a task to a robot")
def manual_assign_robot(
    robot_id: int,
    payload: RobotManualAssignSchema,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role not in ("admin", "manager"):
        raise HTTPException(403, "Insufficient permissions")

    # Select for update to prevent concurrency race conditions
    r = db.query(Robot).filter(Robot.id == robot_id).with_for_update().first()
    t = db.query(Task).filter(Task.id == payload.task_id).with_for_update().first()

    if not r:
        raise HTTPException(404, "Robot not found")
    if not t:
        raise HTTPException(404, "Task not found")
    if r.warehouse_id != t.warehouse_id:
        raise HTTPException(409, "Robot and Task must belong to the same warehouse")
    if not r.enabled:
        raise HTTPException(409, "Robot is disabled")
    if r.status in ("OFFLINE", "FAILED", "MAINTENANCE"):
        raise HTTPException(409, f"Robot is currently offline or failed (status: {r.status})")
    if r.status == "CHARGING" and r.battery_level < 90.0:
        raise HTTPException(409, f"Robot is currently charging (battery level: {r.battery_level:.1f}%)")
    if r.assigned_task_id and r.assigned_task_id != t.id:
        raise HTTPException(409, "Robot is already executing another task")
    if t.status in ("COMPLETED", "CANCELLED"):
        raise HTTPException(409, f"Task is in terminal state '{t.status}'")
    if t.status == "ASSIGNED" and t.assigned_robot_id and t.assigned_robot_id != r.robot_code:
        raise HTTPException(409, f"Task is already assigned to robot {t.assigned_robot_id}")
    if r.battery_level < 25.0 and t.priority != "CRITICAL":
        raise HTTPException(409, "Robot has low battery and cannot accept non-critical tasks")
    if r.battery_level < 10.0:
        raise HTTPException(409, "Robot battery is critically low. Direct to charging station.")

    # Assign
    r.assigned_task_id = t.id
    transition_robot_status(db, r, "ASSIGNED", user.id, f"Manually assigned task {t.task_number}")
    t.assigned_robot_id = r.robot_code
    t.status = "ASSIGNED"
    
    # Audit log
    ledger.append_entry(db, "ROBOT_MANUALLY_ASSIGNED", {
        "robot_code": r.robot_code,
        "task_number": t.task_number,
        "user_id": user.id,
        "timestamp": datetime.now(UTC).replace(tzinfo=None).isoformat()
    })
    db.commit()
    
    # Notification
    notifications.send_change_alert("ROBOT_ASSIGNED", {
        "robot_code": r.robot_code,
        "task_number": t.task_number,
        "assigned_by": user.username
    })
    
    return {"status": "assigned", "robot_id": r.id, "task_id": t.id}

@router.post("/{robot_id}/release", summary="Release a task from a robot")
def release_robot_task(
    robot_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role not in ("admin", "manager"):
        raise HTTPException(403, "Insufficient permissions")
        
    r = db.query(Robot).filter(Robot.id == robot_id).with_for_update().first()
    if not r:
        raise HTTPException(404, "Robot not found")
        
    if not r.assigned_task_id:
        return {"status": "released", "message": "No active tasks to release"}

    t_id = r.assigned_task_id
    t = db.query(Task).filter(Task.id == t_id).first()
    
    r.assigned_task_id = None
    transition_robot_status(db, r, "AVAILABLE", user.id, "Released task assignment manually")
    r.target_location_id = None
    
    # Invalidate route
    active_route = db.query(RobotRoute).filter(
        RobotRoute.robot_id == r.id,
        RobotRoute.status == "ACTIVE"
    ).first()
    if active_route:
        active_route.status = "INVALIDATED"
        active_route.completed_at = datetime.now(UTC).replace(tzinfo=None)
        
    if t and t.status == "ASSIGNED":
        t.status = "QUEUED"
        t.assigned_robot_id = None
        
    db.commit()
    return {"status": "released", "robot_id": r.id, "task_released": t_id}

@router.post("/{robot_id}/simulate-failure", summary="Simulate a robot failure")
def simulate_robot_failure(
    robot_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role not in ("admin", "manager"):
        raise HTTPException(403, "Insufficient permissions")

    r = db.query(Robot).filter(Robot.id == robot_id).with_for_update().first()
    if not r:
        raise HTTPException(404, "Robot not found")

    r.failure_count += 1
    transition_robot_status(db, r, "FAILED", user.id, "Simulated hardware failure triggered.")
    
    # Audit log
    ledger.append_entry(db, "ROBOT_FAILURE_SIMULATED", {
        "robot_code": r.robot_code,
        "assigned_task_id": r.assigned_task_id,
        "timestamp": datetime.now(UTC).replace(tzinfo=None).isoformat()
    })
    
    # Fail/release task
    task_reassigned = False
    if r.assigned_task_id:
        t = db.query(Task).filter(Task.id == r.assigned_task_id).first()
        
        # Invalidate route
        active_route = db.query(RobotRoute).filter(
            RobotRoute.robot_id == r.id,
            RobotRoute.status == "ACTIVE"
        ).first()
        if active_route:
            active_route.status = "FAILED"
            active_route.completed_at = datetime.now(UTC).replace(tzinfo=None)

        if t:
            transition_status(
                db, t, "FAILED", user.id, "SimulationEngine",
                f"Task failed automatically: Assigned robot {r.robot_code} failed."
            )
            t.assigned_robot_id = None
            t.status = "FAILED"
            task_reassigned = True
            
        r.assigned_task_id = None

    db.commit()

    # Trigger notifications
    notifications.send_change_alert("ROBOT_FAILURE", {
        "robot_code": r.robot_code,
        "failure_count": r.failure_count
    })
    
    return {
        "status": "failed",
        "robot_id": r.id,
        "task_released_reassignable": task_reassigned
    }

@router.post("/{robot_id}/recover", summary="Recover a failed robot")
def recover_robot(
    robot_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role not in ("admin", "manager"):
        raise HTTPException(403, "Insufficient permissions")

    r = db.query(Robot).filter(Robot.id == robot_id).with_for_update().first()
    if not r:
        raise HTTPException(404, "Robot not found")

    if r.status != "FAILED":
        raise HTTPException(409, "Robot is not in FAILED status")

    transition_robot_status(db, r, "MAINTENANCE", user.id, "Robot recovering. Set to MAINTENANCE check.")
    transition_robot_status(db, r, "AVAILABLE", user.id, "Robot successfully recovered. Status: AVAILABLE.")
    
    # Recharge fully
    r.battery_level = 100.0

    ledger.append_entry(db, "ROBOT_RECOVERED", {
        "robot_code": r.robot_code,
        "timestamp": datetime.now(UTC).replace(tzinfo=None).isoformat()
    })
    db.commit()

    notifications.send_change_alert("ROBOT_RECOVERED", {
        "robot_code": r.robot_code
    })

    return {"status": "recovered", "robot_id": r.id, "battery_level": 100.0}

@router.post("/{robot_id}/charge", summary="Route robot to charging station")
def charge_robot(
    robot_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role not in ("admin", "manager"):
        raise HTTPException(403, "Insufficient permissions")

    r = db.query(Robot).filter(Robot.id == robot_id).with_for_update().first()
    if not r:
        raise HTTPException(404, "Robot not found")

    if r.assigned_task_id:
        raise HTTPException(409, "Robot is executing a task and cannot charge now")

    # Locate charging spot
    charge_loc = db.query(WarehouseLocation).filter(
        WarehouseLocation.warehouse_id == r.warehouse_id,
        WarehouseLocation.location_type == "CHARGING"
    ).first()
    
    if not charge_loc:
        raise HTTPException(404, "No charging locations found in this warehouse. Fallback staging.")
        
    r.target_location_id = charge_loc.id
    r.target_x = charge_loc.x or 0.0
    r.target_y = charge_loc.y or 0.0
    transition_robot_status(db, r, "CHARGING", user.id, f"Routing to charging location {charge_loc.id}")
    
    db.commit()
    return {"status": "charging_started", "robot_id": r.id, "station_id": charge_loc.id}

@router.post("/auto-assign", summary="Auto-assign priority tasks to eligible robots")
def auto_assign_task(
    warehouse_id: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role not in ("admin", "manager"):
        raise HTTPException(403, "Insufficient permissions")

    # 1. Fetch highest priority task (Queued/Prioritized/Failed)
    task = db.query(Task).filter(
        Task.warehouse_id == warehouse_id,
        Task.status.in_(["QUEUED", "PRIORITIZED", "FAILED"])
    ).order_by(Task.priority_score.desc()).with_for_update().first()

    if not task:
        return {
            "status": "no_tasks_queued",
            "success": False,
            "message": "No unassigned tasks found in queue."
        }

    # 2. Fetch candidates (only AVAILABLE, IDLE, or fully-charged CHARGING robots)
    robots = db.query(Robot).filter(
        Robot.warehouse_id == warehouse_id,
        Robot.enabled == True,
        Robot.assigned_task_id.is_(None),
        Robot.status.in_(["AVAILABLE", "IDLE", "CHARGING"])
    ).with_for_update().all()

    if not robots:
        return {
            "status": "no_available_robots",
            "success": False,
            "message": "No available robot is currently eligible for assignment.",
            "task_id": task.id
        }

    # Retrieve location coords ONCE outside loop
    source_loc = db.query(WarehouseLocation).filter(WarehouseLocation.id == task.source_location_id).first()
    tx = source_loc.x if source_loc else 0.0
    ty = source_loc.y if source_loc else 0.0

    dest_loc = db.query(WarehouseLocation).filter(WarehouseLocation.id == task.destination_location_id).first()
    dx_dest = dest_loc.x if dest_loc else 1.0
    dy_dest = dest_loc.y if dest_loc else 1.0

    charge_loc = db.query(WarehouseLocation).filter(
        WarehouseLocation.warehouse_id == warehouse_id,
        WarehouseLocation.location_type == "CHARGING"
    ).first()
    dist_to_charge = calculate_manhattan_distance(dx_dest, dy_dest, charge_loc.x, charge_loc.y) if charge_loc else 0.0

    candidates = []
    selected_robot = None
    min_cost = float("inf")

    # Get item weight info
    task_weight = task.requested_quantity * (task.product.weight_kg or 0.0) if task.product else 0.0

    for r in robots:
        rejection_reason = None

        # Check status constraint: CHARGING robots must be fully charged (>= 95%)
        if r.status == "CHARGING" and r.battery_level < 95.0:
            rejection_reason = f"Robot is currently charging ({r.battery_level:.1f}% battery)"
        elif r.status not in ("AVAILABLE", "IDLE", "CHARGING"):
            rejection_reason = f"Robot is currently in '{r.status}' state"

        # Check payload constraints
        if not rejection_reason and task_weight > r.max_payload:
            rejection_reason = f"Payload capacity exceeded (requires {task_weight:.1f}kg, max {r.max_payload:.1f}kg)"
        
        # Check battery constraints
        if not rejection_reason:
            dist_to_src = calculate_manhattan_distance(r.current_x, r.current_y, tx, ty)
            dist_to_dest = calculate_manhattan_distance(tx, ty, dx_dest, dy_dest)
            total_dist_est = dist_to_src + dist_to_dest + dist_to_charge
            battery_needed = (total_dist_est * 0.5) + 5.0

            if r.battery_level < battery_needed:
                rejection_reason = f"Insufficient battery to safely complete task & return (needs {battery_needed:.1f}%, has {r.battery_level:.1f}%)"
            elif r.battery_level < 10.0:
                rejection_reason = "Battery critically low (< 10%)"
            elif r.battery_level < 25.0 and task.priority != "CRITICAL":
                rejection_reason = "Low battery (< 25%) for non-critical task"

        if not rejection_reason:
            # Deterministic Score: weighted distance + battery penalty
            bat_penalty = (100.0 - r.battery_level) * 0.2
            cost = dist_to_src + bat_penalty
            
            candidates.append({
                "robot_code": r.robot_code,
                "cost": cost,
                "eligible": True,
                "reason": f"Distance to source: {dist_to_src:.1f}, battery penalty: {bat_penalty:.1f}"
            })
            
            if cost < min_cost:
                min_cost = cost
                selected_robot = r
        else:
            candidates.append({
                "robot_code": r.robot_code,
                "cost": None,
                "eligible": False,
                "reason": rejection_reason
            })

    if not selected_robot:
        return {
            "status": "rejections_only",
            "success": False,
            "message": "No available robot is currently eligible for assignment.",
            "candidates": candidates
        }

    # Execute Assignment atomically respecting state machine
    try:
        if selected_robot.status == "CHARGING":
            transition_robot_status(db, selected_robot, "AVAILABLE", user.id, "Fully charged: Transitioning from CHARGING to AVAILABLE for auto-assignment")
        
        selected_robot.assigned_task_id = task.id
        transition_robot_status(db, selected_robot, "ASSIGNED", user.id, f"Auto-assigned task {task.task_number}")
        selected_robot.updated_at = datetime.now(UTC).replace(tzinfo=None)

        task.assigned_robot_id = selected_robot.robot_code
        task.status = "ASSIGNED"
        task.updated_at = datetime.now(UTC).replace(tzinfo=None)

        ledger.append_entry(db, "ROBOT_AUTO_ASSIGNMENT", {
            "robot_code": selected_robot.robot_code,
            "task_number": task.task_number,
            "candidates": candidates,
            "cost": min_cost
        })
        db.commit()

        notifications.send_change_alert("ROBOT_ASSIGNED", {
            "robot_code": selected_robot.robot_code,
            "task_number": task.task_number,
            "assigned_by": "Auto-Assign Engine"
        })

        return {
            "status": "success",
            "success": True,
            "task_id": task.id,
            "selected_robot": selected_robot.robot_code,
            "estimated_cost": min_cost,
            "explanation": f"Selected {selected_robot.robot_code} because it is enabled, available, has sufficient battery, and has the lowest Estimated Assignment Cost of {min_cost:.1f}.",
            "candidates": candidates
        }
    except Exception as exc:
        db.rollback()
        logger.error("Auto-assignment transaction failed: %s", exc, exc_info=True)
        return {
            "status": "error",
            "success": False,
            "message": "Unable to assign robot due to a temporary database conflict. Please try again."
        }

@router.post("/recommend-assignment", summary="Generate explainable intelligent robot recommendation for a task (Non-mutating)")
def recommend_robot_assignment(
    payload: IntelligentRecommendRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role not in ("admin", "manager", "operator", "staff"):
        raise HTTPException(403, "Insufficient permissions to generate assignment recommendations")
    from backend.services.intelligent_assignment import recommend_robot_for_task
    return recommend_robot_for_task(db, payload.task_id)


@router.post("/assign-intelligent", summary="Execute intelligent/manual robot assignment with race condition protection")
def assign_robot_intelligent_endpoint(
    payload: IntelligentAssignRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role not in ("admin", "manager"):
        raise HTTPException(403, "Insufficient permissions to assign robots to tasks")
    from backend.services.intelligent_assignment import assign_robot_intelligently
    return assign_robot_intelligently(
        db=db,
        task_id=payload.task_id,
        robot_identifier=payload.robot_code,
        user_id=user.id,
        username=user.username,
        assignment_method=payload.assignment_method or "INTELLIGENT"
    )

# ---------------------------------------------------------------------------
# Simulation Control Endpoints
# ---------------------------------------------------------------------------

@router.post("/simulation/start", summary="Start simulation clock")
def simulation_start(user=Depends(get_current_user)):
    global SIMULATION_RUNNING
    if user.role not in ("admin", "manager"):
        raise HTTPException(403, "Insufficient permissions")
    SIMULATION_RUNNING = True
    start_sim()
    notifications.send_change_alert("SIMULATION_STARTED", {
        "user": user.username,
        "message": f"Robot fleet simulation loop started by {user.username}."
    })
    return {"status": "running", "message": "Robot simulation loop activated."}

@router.post("/simulation/pause", summary="Pause simulation clock")
def simulation_pause(user=Depends(get_current_user)):
    global SIMULATION_RUNNING
    if user.role not in ("admin", "manager"):
        raise HTTPException(403, "Insufficient permissions")
    SIMULATION_RUNNING = False
    notifications.send_change_alert("SIMULATION_STOPPED", {
        "user": user.username,
        "message": f"Robot fleet simulation loop paused by {user.username}."
    })
    return {"status": "paused", "message": "Robot simulation loop paused."}

@router.post("/simulation/resume", summary="Resume simulation clock")
def simulation_resume(user=Depends(get_current_user)):
    global SIMULATION_RUNNING
    if user.role not in ("admin", "manager"):
        raise HTTPException(403, "Insufficient permissions")
    SIMULATION_RUNNING = True
    start_sim()
    notifications.send_change_alert("SIMULATION_STARTED", {
        "user": user.username,
        "message": f"Robot fleet simulation loop resumed by {user.username}."
    })
    return {"status": "running", "message": "Robot simulation loop resumed."}


@router.post("/simulation/step", summary="Trigger a single manual step/tick")
def simulation_step(db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role not in ("admin", "manager"):
        raise HTTPException(403, "Insufficient permissions")
    
    # Run a tick step
    execute_simulation_tick(db)
    return {"status": "stepped", "message": "Simulation tick processed manually."}

@router.post("/simulation/reset", summary="Reset simulation fleet coordinates")
def simulation_reset(db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role not in ("admin", "manager"):
        raise HTTPException(403, "Insufficient permissions")

    # Release tasks, return to default staging coordinate spots
    robots = db.query(Robot).all()
    for r in robots:
        r.assigned_task_id = None
        r.status = "AVAILABLE"
        r.battery_level = 100.0
        r.total_tasks_completed = 0
        r.total_distance = 0.0
        r.total_operating_time = 0.0
        
        # Staging position reset
        stage_loc = db.query(WarehouseLocation).filter(
            WarehouseLocation.warehouse_id == r.warehouse_id
        ).first()
        r.current_location_id = stage_loc.id if stage_loc else None
        r.current_x = stage_loc.x if stage_loc else 0.0
        r.current_y = stage_loc.y if stage_loc else 0.0
        r.target_location_id = None
        r.target_x = r.current_x
        r.target_y = r.current_y
        
    db.query(RobotTelemetryEvent).delete()
    db.commit()
    return {"status": "reset", "message": "Robot fleet positions and telemetry reset successfully."}

@router.get("/{robot_id}/telemetry", summary="Get light-weight telemetry history log")
def get_robot_telemetry(
    robot_id: int,
    limit: int = 50,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    events = db.query(RobotTelemetryEvent).filter(
        RobotTelemetryEvent.robot_id == robot_id
    ).order_by(RobotTelemetryEvent.timestamp.desc()).limit(limit).all()
    return events

@router.get("/{robot_id}/history", summary="Get robot historical event updates")
def get_robot_history(
    robot_id: int,
    limit: int = 50,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # Find matching audit log ledger events for this robot
    robot = db.query(Robot).filter(Robot.id == robot_id).first()
    if not robot:
        raise HTTPException(404, "Robot not found")

    events = db.query(AuditLedger).filter(
        AuditLedger.details.like(f"%%{robot.robot_code}%%")
    ).order_by(AuditLedger.timestamp.desc()).limit(limit).all()
    
    return [
        {
            "id": e.id,
            "timestamp": e.timestamp,
            "event_type": e.event_type,
            "details": json.loads(e.details)
        } for e in events
    ]

# Global background loop worker
def run_simulation_loop():
    global SIMULATION_RUNNING
    from backend.database import SessionLocal
    while True:
        if SIMULATION_RUNNING:
            db = SessionLocal()
            try:
                execute_simulation_tick(db)
            except Exception as e:
                logger.error("Simulation engine loop error: %s", e)
            finally:
                db.close()
        time.sleep(SIMULATION_INTERVAL)
