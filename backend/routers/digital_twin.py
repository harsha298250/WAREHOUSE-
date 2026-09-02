"""
digital_twin.py — Phase 7: Database-Reconciled Digital Twin & Real-Time Warehouse Simulation

Provides REST endpoints for:
- Digital Twin state (warehouse + robots + routes + obstacles + tasks + inventory)
- Simulation lifecycle (start/pause/resume/step/stop/reset)
- Event stream (SimulationEvent records)
- Simulation metrics / KPIs
- Snapshot management

Sync mechanism: REST polling (frontend polls /state every 2s when RUNNING).
Simulation tick engine: reuses execute_simulation_tick() from robots.py.
Inventory isolation: production inventory.on_hand is NEVER mutated;
  simulated picks are tracked in SimulationSnapshot.sim_inventory_delta.
"""

import json
import logging
from datetime import datetime, UTC
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.auth import get_current_user, require_admin
from backend import audit_ledger as ledger
from backend import notifications
from backend.models import (
    Warehouse, Robot, Task, RobotRoute, RobotTelemetryEvent,
    WarehouseGridCell, WarehouseObstacle, Inventory, WarehouseLocation, Item,
    DigitalTwinSimulation, SimulationSnapshot, SimulationEvent, User, Order, OrderItem
)
from backend.routers.robots import execute_simulation_tick
from backend.charging_manager import get_warehouse_charging_queue_info

logger = logging.getLogger("warehouse")

router = APIRouter(prefix="/digital-twin", tags=["Digital Twin"])

# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class SimulationStartRequest(BaseModel):
    warehouse_id: str
    scenario_type: str = "NORMAL_OPERATIONS"
    speed_multiplier: float = 1.0
    seed: int = 42
    mode: str = "SIMULATION"

class SimulationSpeedRequest(BaseModel):
    speed_multiplier: float = 1.0

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

VALID_STATUSES = {"IDLE", "READY", "RUNNING", "PAUSED", "COMPLETED", "STOPPED", "ERROR"}
SEVERITY_MAP = {
    "BATTERY_CRITICAL": "CRITICAL",
    "ROBOT_FAILED": "CRITICAL",
    "SIMULATION_ERROR": "CRITICAL",
    "BATTERY_LOW": "WARNING",
    "ROUTE_REPLANNED": "WARNING",
    "COLLISION_AVOIDED": "WARNING",
    "ROBOT_WAITING": "WARNING",
    "TASK_FAILED": "WARNING",
    "OBSTACLE_CREATED": "WARNING",
    "TASK_COMPLETED": "SUCCESS",
    "SIMULATION_COMPLETED": "SUCCESS",
}

def _severity(event_type: str) -> str:
    return SEVERITY_MAP.get(event_type, "INFO")


def _add_sim_event(db: Session, sim: DigitalTwinSimulation, event_type: str, message: str,
                   robot_id: int = None, task_id: int = None,
                   location_id: str = None, route_id: int = None, metadata: dict = None):
    ev = SimulationEvent(
        simulation_id=sim.id,
        warehouse_id=sim.warehouse_id,
        event_type=event_type,
        severity=_severity(event_type),
        sim_time_seconds=sim.simulation_time_seconds,
        real_timestamp=datetime.now(UTC).replace(tzinfo=None),
        robot_id=robot_id,
        task_id=task_id,
        location_id=location_id,
        route_id=route_id,
        message=message,
        event_metadata=json.dumps(metadata or {}),
    )
    db.add(ev)


def _take_snapshot(db: Session, sim: DigitalTwinSimulation, version: int = None) -> SimulationSnapshot:
    """Capture current robot/task/obstacle states into a snapshot (inventory unchanged)."""
    robots = db.query(Robot).filter(Robot.warehouse_id == sim.warehouse_id).all()
    tasks = db.query(Task).filter(
        Task.warehouse_id == sim.warehouse_id,
        Task.status.in_(["QUEUED", "PRIORITIZED", "ASSIGNED", "IN_PROGRESS"])
    ).all()
    obstacles = db.query(WarehouseObstacle).filter(
        WarehouseObstacle.warehouse_id == sim.warehouse_id,
        WarehouseObstacle.active == True
    ).all()

    robot_states = [
        {
            "id": r.id, "robot_code": r.robot_code, "status": r.status,
            "current_x": r.current_x, "current_y": r.current_y,
            "battery_level": r.battery_level, "assigned_task_id": r.assigned_task_id,
            "current_location_id": r.current_location_id,
        }
        for r in robots
    ]
    task_states = [
        {
            "id": t.id, "task_number": t.task_number, "status": t.status,
            "assigned_robot_id": t.assigned_robot_id,
        }
        for t in tasks
    ]
    obstacle_states = [
        {"id": o.id, "x": o.x, "y": o.y, "width": o.width, "height": o.height,
         "active": o.active, "obstacle_type": o.obstacle_type}
        for o in obstacles
    ]

    # Count existing snapshots for version
    existing_count = db.query(SimulationSnapshot).filter(
        SimulationSnapshot.simulation_id == sim.id
    ).count()
    snap_version = version if version is not None else (existing_count + 1)

    snap = SimulationSnapshot(
        simulation_id=sim.id,
        warehouse_id=sim.warehouse_id,
        snapshot_version=snap_version,
        taken_at=datetime.now(UTC).replace(tzinfo=None),
        sim_time_seconds=sim.simulation_time_seconds,
        robot_states=json.dumps(robot_states),
        task_states=json.dumps(task_states),
        obstacle_states=json.dumps(obstacle_states),
        sim_inventory_delta=json.dumps({}),
        snapshot_metadata=json.dumps({"tick_count": sim.tick_count})
    )
    db.add(snap)
    db.commit()
    db.refresh(snap)
    return snap


def _restore_snapshot(db: Session, snap: SimulationSnapshot):
    """Restore robot/task/obstacle states from a snapshot. Does NOT touch inventory.on_hand."""
    robot_states = json.loads(snap.robot_states)
    task_states = json.loads(snap.task_states)
    obstacle_states = json.loads(snap.obstacle_states)

    for rs in robot_states:
        robot = db.query(Robot).filter(Robot.id == rs["id"]).first()
        if robot:
            robot.status = rs["status"]
            robot.current_x = rs["current_x"]
            robot.current_y = rs["current_y"]
            robot.battery_level = rs["battery_level"]
            robot.assigned_task_id = rs["assigned_task_id"]
            robot.current_location_id = rs["current_location_id"]
            db.add(robot)

    for ts in task_states:
        task = db.query(Task).filter(Task.id == ts["id"]).first()
        if task:
            task.status = ts["status"]
            task.assigned_robot_id = ts["assigned_robot_id"]
            db.add(task)

    # Restore obstacles to snapshot state
    current_obs = db.query(WarehouseObstacle).filter(
        WarehouseObstacle.warehouse_id == snap.warehouse_id
    ).all()
    snap_obs_ids = {o["id"] for o in obstacle_states}
    for o in current_obs:
        if o.id not in snap_obs_ids:
            db.delete(o)
    for os in obstacle_states:
        obs = db.query(WarehouseObstacle).filter(WarehouseObstacle.id == os["id"]).first()
        if obs:
            obs.active = os["active"]
            db.add(obs)

    db.commit()


def _build_state(db: Session, warehouse_id: str, sim: DigitalTwinSimulation = None) -> dict:
    """Build full Digital Twin state payload."""
    wh = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not wh:
        raise HTTPException(404, f"Warehouse '{warehouse_id}' not found.")

    # Grid cells
    from backend.routers.pathfinding import initialize_warehouse_grid_if_empty
    initialize_warehouse_grid_if_empty(db, warehouse_id)
    cells = db.query(WarehouseGridCell).filter(WarehouseGridCell.warehouse_id == warehouse_id).all()
    grid = [
        {"x": c.x, "y": c.y, "type": c.cell_type, "traversable": c.traversable,
         "cost": c.cost, "occupied": c.occupied}
        for c in cells
    ]

    # Robots
    robots = db.query(Robot).filter(Robot.warehouse_id == warehouse_id).all()
    robot_list = []
    for r in robots:
        # Get active route
        active_route = db.query(RobotRoute).filter(
            RobotRoute.robot_id == r.id,
            RobotRoute.status == "ACTIVE"
        ).order_by(RobotRoute.created_at.desc()).first()

        # Get last few telemetry positions (trail)
        trail_events = db.query(RobotTelemetryEvent).filter(
            RobotTelemetryEvent.robot_id == r.id,
            RobotTelemetryEvent.event_type == "POSITION_UPDATED"
        ).order_by(RobotTelemetryEvent.timestamp.desc()).limit(5).all()
        trail = [{"x": t.x, "y": t.y} for t in reversed(trail_events)]

        robot_list.append({
            "id": r.id,
            "robot_code": r.robot_code,
            "name": r.name,
            "status": r.status,
            "battery_level": r.battery_level,
            "current_x": r.current_x,
            "current_y": r.current_y,
            "target_x": r.target_x,
            "target_y": r.target_y,
            "current_location_id": r.current_location_id,
            "target_location_id": r.target_location_id,
            "assigned_task_id": r.assigned_task_id,
            "robot_type": r.robot_type,
            "enabled": r.enabled,
            "total_tasks_completed": r.total_tasks_completed,
            "total_distance": r.total_distance,
            "active_route": {
                "id": active_route.id,
                "path_data": json.loads(active_route.path_data),
                "goal_x": active_route.goal_x,
                "goal_y": active_route.goal_y,
                "distance": active_route.distance,
                "algorithm": active_route.algorithm,
                "status": active_route.status,
            } if active_route else None,
            "trail": trail,
        })

    # Active tasks
    tasks = db.query(Task).filter(
        Task.warehouse_id == warehouse_id,
        Task.status.in_(["QUEUED", "PRIORITIZED", "ASSIGNED", "IN_PROGRESS"])
    ).order_by(Task.priority_score.desc()).limit(50).all()
    task_list = []
    for t in tasks:
        task_list.append({
            "id": t.id,
            "task_number": t.task_number,
            "task_type": t.task_type,
            "status": t.status,
            "priority": t.priority,
            "priority_score": t.priority_score,
            "assigned_robot_id": t.assigned_robot_id,
            "source_location_id": t.source_location_id,
            "destination_location_id": t.destination_location_id,
            "requested_quantity": t.requested_quantity,
            "order_id": t.order_id,
            "product_id": t.product_id,
        })

    # Obstacles
    obstacles = db.query(WarehouseObstacle).filter(
        WarehouseObstacle.warehouse_id == warehouse_id
    ).all()
    obstacle_list = [
        {"id": o.id, "x": o.x, "y": o.y, "width": o.width, "height": o.height,
         "active": o.active, "obstacle_type": o.obstacle_type, "severity": o.severity}
        for o in obstacles
    ]

    # Inventory locations
    inv_locs = db.query(Inventory, WarehouseLocation, Item).join(
        WarehouseLocation, Inventory.location_id == WarehouseLocation.id
    ).join(Item, Inventory.item_id == Item.id).filter(
        Inventory.warehouse_id == warehouse_id
    ).limit(100).all()

    location_inventory = {}
    for inv, loc, item in inv_locs:
        health = "HEALTHY"
        if inv.on_hand == 0:
            health = "OUT_OF_STOCK"
        elif inv.on_hand <= item.safety_stock:
            health = "CRITICAL"
        elif inv.available < item.safety_stock:
            health = "LOW"

        location_inventory[loc.id] = {
            "location_id": loc.id,
            "zone": loc.zone,
            "aisle": loc.aisle,
            "x": loc.x,
            "y": loc.y,
            "location_type": loc.location_type,
            "item_id": item.id,
            "item_name": item.name,
            "sku": item.sku,
            "on_hand": inv.on_hand,
            "reserved": inv.reserved,
            "available": inv.available,
            "damaged": inv.damaged,
            "safety_stock": item.safety_stock,
            "health_status": health,
        }

    # All routes (recent active/completed for visualization)
    routes = db.query(RobotRoute).filter(
        RobotRoute.warehouse_id == warehouse_id,
        RobotRoute.status.in_(["ACTIVE", "PLANNED", "REPLANNED"])
    ).order_by(RobotRoute.created_at.desc()).limit(30).all()
    route_list = [
        {
            "id": r.id,
            "robot_id": r.robot_id,
            "task_id": r.task_id,
            "status": r.status,
            "algorithm": r.algorithm,
            "start_x": r.start_x, "start_y": r.start_y,
            "goal_x": r.goal_x, "goal_y": r.goal_y,
            "path_data": json.loads(r.path_data),
            "distance": r.distance,
            "cost": r.cost,
        }
        for r in routes
    ]

    # Replenishment recommendations summary
    from backend.models import ReplenishmentRecommendation
    rep_recs = db.query(ReplenishmentRecommendation).filter(
        ReplenishmentRecommendation.warehouse_id == warehouse_id
    ).all()
    rep_items = [
        {
            "id": r.id,
            "item_id": r.item_id,
            "item_name": r.item_name,
            "current_stock": r.current_stock,
            "reorder_point": r.reorder_point,
            "recommended_qty": r.recommended_qty,
            "urgency": r.urgency,
            "status": r.status,
            "reason": r.reason
        }
        for r in rep_recs
    ]
    replenishment_summary = {
        "total_recommended": sum(1 for r in rep_recs if r.urgency in ("REORDER_RECOMMENDED", "URGENT_REORDER")),
        "urgent_count": sum(1 for r in rep_recs if r.urgency == "URGENT_REORDER"),
        "approved_count": sum(1 for r in rep_recs if r.status == "APPROVED"),
        "completed_count": sum(1 for r in rep_recs if r.status == "COMPLETED"),
        "items": rep_items[:20]
    }

    # Operational Alerts
    alerts = []
    for r in robot_list:
        if r["battery_level"] is not None and r["battery_level"] < 20.0:
            alerts.append({
                "severity": "CRITICAL" if r["battery_level"] < 15.0 else "WARNING",
                "category": "BATTERY",
                "message": f"Robot {r['robot_code']} battery low ({r['battery_level']:.1f}%)"
            })
    for o in obstacle_list:
        if o["active"]:
            alerts.append({
                "severity": "WARNING",
                "category": "OBSTACLE",
                "message": f"Active obstacle at ({o['x']}, {o['y']}) severity {o['severity']}"
            })
    for loc_id, inv_info in location_inventory.items():
        if inv_info["health_status"] in ("CRITICAL", "OUT_OF_STOCK"):
            alerts.append({
                "severity": "CRITICAL" if inv_info["health_status"] == "OUT_OF_STOCK" else "WARNING",
                "category": "INVENTORY",
                "message": f"Item {inv_info['item_name']} at location {loc_id} is {inv_info['health_status']}"
            })
    for t in task_list:
        if t["priority"] in ("CRITICAL", "HIGH") and not t["assigned_robot_id"]:
            alerts.append({
                "severity": "WARNING",
                "category": "TASK",
                "message": f"Unassigned high-priority task {t['task_number']} ({t['priority']})"
            })

    # KPIs
    kpi_summary = {
        "active_robots": sum(1 for r in robot_list if r["status"] in ("MOVING", "PICKING", "RETURNING")),
        "available_robots": sum(1 for r in robot_list if r["status"] == "AVAILABLE"),
        "active_tasks": sum(1 for t in task_list if t["status"] in ("ASSIGNED", "IN_PROGRESS")),
        "pending_tasks": sum(1 for t in task_list if t["status"] in ("QUEUED", "PRIORITIZED")),
        "completed_tasks": db.query(Task).filter(Task.warehouse_id == warehouse_id, Task.status == "COMPLETED").count(),
        "low_stock_items": sum(1 for inv in location_inventory.values() if inv["health_status"] in ("CRITICAL", "OUT_OF_STOCK", "LOW")),
        "replenishment_pending": replenishment_summary["total_recommended"] + replenishment_summary["approved_count"],
        "active_routes": len(route_list),
        "blocked_routes": sum(1 for o in obstacle_list if o["active"])
    }

    # Simulation
    sim_data = None
    if sim:
        sim_data = {
            "id": sim.id,
            "simulation_status": sim.simulation_status,
            "simulation_time_seconds": sim.simulation_time_seconds,
            "speed_multiplier": sim.speed_multiplier,
            "seed": sim.seed,
            "mode": sim.mode,
            "scenario_type": sim.scenario_type,
            "tick_count": sim.tick_count,
            "started_at": sim.started_at.isoformat() if sim.started_at else None,
            "paused_at": sim.paused_at.isoformat() if sim.paused_at else None,
        }

    return {
        "warehouse_id": warehouse_id,
        "warehouse_name": wh.name,
        "data_mode": "SIMULATION STATE" if sim and sim.simulation_status == "RUNNING" else "OBSERVATION STATE",
        "telemetry_mode": "SIMULATED TELEMETRY",
        "is_live": not (sim and sim.simulation_status == "RUNNING"),
        "timestamp": datetime.now(UTC).replace(tzinfo=None).isoformat(),
        "simulation": sim_data,
        "grid": grid,
        "robots": robot_list,
        "tasks": task_list,
        "obstacles": obstacle_list,
        "routes": route_list,
        "location_inventory": location_inventory,
        "replenishment_summary": replenishment_summary,
        "operational_alerts": alerts,
        "kpis": kpi_summary,
        "charging_system": get_warehouse_charging_queue_info(db, warehouse_id),
        "fleet_summary": {
            "total": len(robot_list),
            "available": sum(1 for r in robot_list if r["status"] == "AVAILABLE"),
            "moving": sum(1 for r in robot_list if r["status"] == "MOVING"),
            "picking": sum(1 for r in robot_list if r["status"] == "PICKING"),
            "returning": sum(1 for r in robot_list if r["status"] == "RETURNING"),
            "waiting": sum(1 for r in robot_list if r["status"] == "WAITING"),
            "charging": sum(1 for r in robot_list if r["status"] == "CHARGING"),
            "failed": sum(1 for r in robot_list if r["status"] == "FAILED"),
        }
    }



from fastapi.responses import StreamingResponse
from fastapi import Request
import asyncio
import uuid

async def get_current_user_dt(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    token = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]
    if not token:
        token = request.query_params.get("token")
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated. Access token required.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    from backend.auth import SECRET_KEY, ALGORITHM
    from jose import jwt, JWTError
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(401, "Could not validate credentials")
    except JWTError:
        raise HTTPException(401, "Could not validate credentials")
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(401, "User not found")
    if hasattr(user, 'is_active') and not user.is_active:
        raise HTTPException(403, "Account is deactivated.")
    return user

@router.get("/{warehouse_id}/sync", summary="Establish real-time Digital Twin synchronization stream")
async def sync_dt_state(
    warehouse_id: str,
    mode: str = "LIVE",
    simulation_run_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user_dt)
):
    # 1. Enforce RBAC
    if user.role != "admin":
        from backend.models import UserWarehouseAccess
        access = db.query(UserWarehouseAccess).filter(
            UserWarehouseAccess.user_id == user.id,
            UserWarehouseAccess.warehouse_id == warehouse_id
        ).first()
        if not access:
            raise HTTPException(403, f"Access to warehouse '{warehouse_id}' is restricted.")

    # Build snapshot in current database session scope
    sim = None
    if mode == "LIVE":
        from backend.models import DigitalTwinSimulation
        sim = db.query(DigitalTwinSimulation).filter(
            DigitalTwinSimulation.warehouse_id == warehouse_id,
            DigitalTwinSimulation.simulation_status.in_(["RUNNING", "PAUSED", "READY"])
        ).order_by(DigitalTwinSimulation.id.desc()).first()
    
    snapshot = _build_state(db, warehouse_id, sim)

    # 2. Setup subscription queue
    queue = asyncio.Queue(maxsize=100)
    from backend.sync_broadcast import broadcaster
    
    if mode == "SIMULATION":
        if not simulation_run_id:
            raise HTTPException(400, "simulation_run_id is required in SIMULATION mode.")
        broadcaster.subscribe_sim(simulation_run_id, queue)
    else:
        broadcaster.subscribe_live(warehouse_id, queue)

    async def event_generator():
        try:
            yield f"data: {json.dumps({'event_type': 'SNAPSHOT', 'mode': mode, 'warehouse_id': warehouse_id, 'data': snapshot})}\n\n"

            # Listen to broadcaster queue
            seq_num = 0
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=15.0)
                    seq_num += 1
                    event_payload = {
                        "event_id": f"evt-{uuid.uuid4()}",
                        "event_type": event.get("event_type"),
                        "mode": mode,
                        "warehouse_id": warehouse_id,
                        "entity_type": event.get("entity_type"),
                        "entity_id": event.get("entity_id"),
                        "sequence_number": seq_num,
                        "timestamp": datetime.now(UTC).replace(tzinfo=None).isoformat(),
                        "data": event.get("data", {})
                    }
                    yield f"data: {json.dumps(event_payload)}\n\n"
                    queue.task_done()
                except asyncio.TimeoutError:
                    yield ": ping\n\n"
        except asyncio.CancelledError:
            logger.info("SSE client disconnected from sync stream")
        finally:
            if mode == "SIMULATION":
                broadcaster.unsubscribe_sim(simulation_run_id, queue)
            else:
                broadcaster.unsubscribe_live(warehouse_id, queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream", headers={
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no"
    })


@router.get("/state", summary="Get current Digital Twin state via query param")
def get_dt_state_query(
    warehouse_id: str = Query("WH-BLR-01"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role != "admin":
        from backend.models import UserWarehouseAccess
        access = db.query(UserWarehouseAccess).filter(
            UserWarehouseAccess.user_id == user.id,
            UserWarehouseAccess.warehouse_id == warehouse_id
        ).first()
        if not access:
            raise HTTPException(403, f"Access to warehouse '{warehouse_id}' is restricted.")

    sim = db.query(DigitalTwinSimulation).filter(
        DigitalTwinSimulation.warehouse_id == warehouse_id,
        DigitalTwinSimulation.simulation_status.in_(["RUNNING", "PAUSED", "READY"])
    ).order_by(DigitalTwinSimulation.id.desc()).first()

    if sim and sim.simulation_status == "RUNNING":
        try:
            execute_simulation_tick(db)
            sim.tick_count += 1
            sim.simulation_time_seconds += 1.0 * sim.speed_multiplier
            db.add(sim)
            db.commit()
            _emit_tick_events(db, sim)
        except Exception as e_tick:
            logger.warning("Auto-tick in get_dt_state_query failed: %s", e_tick)
            db.rollback()

    return _build_state(db, warehouse_id, sim)


@router.get("/{warehouse_id}/state", summary="Get current Digital Twin state")
def get_dt_state(
    warehouse_id: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role != "admin":
        from backend.models import UserWarehouseAccess
        access = db.query(UserWarehouseAccess).filter(
            UserWarehouseAccess.user_id == user.id,
            UserWarehouseAccess.warehouse_id == warehouse_id
        ).first()
        if not access:
            raise HTTPException(403, f"Access to warehouse '{warehouse_id}' is restricted.")

    sim = db.query(DigitalTwinSimulation).filter(
        DigitalTwinSimulation.warehouse_id == warehouse_id,
        DigitalTwinSimulation.simulation_status.in_(["RUNNING", "PAUSED", "READY"])
    ).order_by(DigitalTwinSimulation.id.desc()).first()

    if sim and sim.simulation_status == "RUNNING":
        try:
            execute_simulation_tick(db)
            sim.tick_count += 1
            sim.simulation_time_seconds += 1.0 * sim.speed_multiplier
            db.add(sim)
            db.commit()
            _emit_tick_events(db, sim)
        except Exception as e_tick:
            logger.warning("Auto-tick in get_dt_state failed: %s", e_tick)
            db.rollback()

    return _build_state(db, warehouse_id, sim)



@router.get("/{warehouse_id}/events", summary="Get Digital Twin event stream")
def get_dt_events(
    warehouse_id: str,
    severity: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Returns the Digital Twin event stream for the warehouse, most recent first."""
    q = db.query(SimulationEvent).filter(SimulationEvent.warehouse_id == warehouse_id)
    if severity:
        q = q.filter(SimulationEvent.severity == severity.upper())
    if event_type:
        q = q.filter(SimulationEvent.event_type == event_type.upper())
    events = q.order_by(SimulationEvent.real_timestamp.desc()).offset(offset).limit(limit).all()
    return [
        {
            "id": e.id,
            "simulation_id": e.simulation_id,
            "event_type": e.event_type,
            "severity": e.severity,
            "sim_time_seconds": e.sim_time_seconds,
            "real_timestamp": e.real_timestamp.isoformat(),
            "robot_id": e.robot_id,
            "task_id": e.task_id,
            "message": e.message,
            "metadata": json.loads(e.event_metadata),
        }
        for e in events
    ]


@router.get("/{warehouse_id}/heatmap", summary="Get location heatmap data")
def get_heatmap(
    warehouse_id: str,
    metric: str = Query("robot_traffic", description="inventory_density | robot_traffic | task_activity"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Returns heatmap intensity values per grid cell for the selected metric."""
    wh = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not wh:
        raise HTTPException(404, f"Warehouse '{warehouse_id}' not found.")

    cells = db.query(WarehouseGridCell).filter(WarehouseGridCell.warehouse_id == warehouse_id).all()
    heatmap = []

    if metric == "robot_traffic":
        # Count telemetry events per cell
        from sqlalchemy import func
        traffic = {}
        rows = db.query(
            RobotTelemetryEvent.x.label("x"),
            RobotTelemetryEvent.y.label("y"),
            func.count(RobotTelemetryEvent.id).label("cnt")
        ).join(Robot, RobotTelemetryEvent.robot_id == Robot.id).filter(
            Robot.warehouse_id == warehouse_id
        ).group_by(RobotTelemetryEvent.x, RobotTelemetryEvent.y).all()
        for row in rows:
            traffic[(int(row.x), int(row.y))] = row.cnt
        max_cnt = max(traffic.values(), default=1)
        for c in cells:
            cnt = traffic.get((c.x, c.y), 0)
            heatmap.append({"x": c.x, "y": c.y, "value": round(cnt / max_cnt, 3), "raw": cnt})

    elif metric == "task_activity":
        # Count tasks per source_location
        loc_tasks = {}
        tasks = db.query(Task).filter(Task.warehouse_id == warehouse_id).all()
        for t in tasks:
            if t.source_location_id:
                loc_tasks[t.source_location_id] = loc_tasks.get(t.source_location_id, 0) + 1
        loc_coords = {l.id: (l.x, l.y) for l in db.query(WarehouseLocation).filter(
            WarehouseLocation.warehouse_id == warehouse_id
        ).all()}
        cell_activity = {}
        for loc_id, cnt in loc_tasks.items():
            coords = loc_coords.get(loc_id)
            if coords:
                cx, cy = int(round(coords[0])), int(round(coords[1]))
                cell_activity[(cx, cy)] = cell_activity.get((cx, cy), 0) + cnt
        max_cnt = max(cell_activity.values(), default=1)
        for c in cells:
            cnt = cell_activity.get((c.x, c.y), 0)
            heatmap.append({"x": c.x, "y": c.y, "value": round(cnt / max_cnt, 3), "raw": cnt})

    elif metric == "inventory_density":
        # Sum on_hand per location mapped to grid cell
        inv_map = {}
        inv_data = db.query(Inventory, WarehouseLocation).join(
            WarehouseLocation, Inventory.location_id == WarehouseLocation.id
        ).filter(Inventory.warehouse_id == warehouse_id).all()
        for inv, loc in inv_data:
            cx, cy = int(round(loc.x or 0)), int(round(loc.y or 0))
            inv_map[(cx, cy)] = inv_map.get((cx, cy), 0) + inv.on_hand
        max_qty = max(inv_map.values(), default=1)
        for c in cells:
            qty = inv_map.get((c.x, c.y), 0)
            heatmap.append({"x": c.x, "y": c.y, "value": round(qty / max_qty, 3), "raw": qty})
    else:
        raise HTTPException(400, f"Unknown metric '{metric}'. Use: inventory_density | robot_traffic | task_activity")

    return {"warehouse_id": warehouse_id, "metric": metric, "heatmap": heatmap}


def cleanup_simulation_tasks(db: Session, warehouse_id: str):
    from backend.models import Task, Order, OrderItem
    try:
        db.query(Task).filter(
            Task.warehouse_id == warehouse_id,
            Task.task_number.like("SIM-TSK-%")
        ).delete(synchronize_session=False)

        sim_orders = db.query(Order).filter(
            Order.warehouse_id == warehouse_id,
            Order.id.like("SIM-ORD-%")
        ).all()
        if sim_orders:
            sim_order_ids = [o.id for o in sim_orders]
            db.query(OrderItem).filter(OrderItem.order_id.in_(sim_order_ids)).delete(synchronize_session=False)

        db.query(Order).filter(
            Order.warehouse_id == warehouse_id,
            Order.id.like("SIM-ORD-%")
        ).delete(synchronize_session=False)
        db.commit()
    except Exception as e:
        logger.warning("cleanup_simulation_tasks exception (non-fatal): %s", e)
        db.rollback()


def setup_scenario_conditions(db: Session, warehouse_id: str, scenario_type: str):
    import random
    from backend.models import Robot, WarehouseObstacle, Item, WarehouseLocation, Order, OrderItem, Task, RobotRoute, RobotTelemetryEvent, RobotReservation, InventoryMovement
    
    # Ensure there are 6 robots for the simulation across any registered warehouse
    existing_robots = db.query(Robot).filter(Robot.warehouse_id == warehouse_id).all()
    if len(existing_robots) < 4:
        wh_code = warehouse_id.split("-")[1] if "-" in warehouse_id else warehouse_id[:3].upper()
        # 1. Clean up route, reservation, and telemetry tables referencing these robots
        db.query(RobotRoute).filter(RobotRoute.warehouse_id == warehouse_id).delete(synchronize_session=False)
        db.query(RobotReservation).filter(RobotReservation.warehouse_id == warehouse_id).delete(synchronize_session=False)
        
        # 2. Reset task assignments
        db.query(Task).filter(Task.warehouse_id == warehouse_id).update(
            {Task.assigned_robot_id: None, Task.assigned_at: None}, synchronize_session=False
        )
        
        # 3. Now safely delete robots
        db.query(Robot).filter(Robot.warehouse_id == warehouse_id).delete(synchronize_session=False)
        
        initial_robots = [
            {"code": f"RB-{wh_code}-01", "x": 11.0, "y": 5.0, "status": "CHARGING", "loc": f"WH-{warehouse_id}-CHARGING-1", "battery": 100.0},
            {"code": f"RB-{wh_code}-02", "x": 12.0, "y": 5.0, "status": "CHARGING", "loc": f"WH-{warehouse_id}-CHARGING-2", "battery": 100.0},
            {"code": f"RB-{wh_code}-03", "x": 1.0, "y": 5.0, "status": "AVAILABLE", "loc": f"WH-{warehouse_id}-RECEIVING", "battery": 92.5},
            {"code": f"RB-{wh_code}-04", "x": 4.0, "y": 5.0, "status": "AVAILABLE", "loc": f"WH-{warehouse_id}-AISLE-4-5", "battery": 88.0},
            {"code": f"RB-{wh_code}-05", "x": 6.0, "y": 5.0, "status": "AVAILABLE", "loc": f"WH-{warehouse_id}-AISLE-6-5", "battery": 95.0},
            {"code": f"RB-{wh_code}-06", "x": 8.0, "y": 5.0, "status": "AVAILABLE", "loc": f"WH-{warehouse_id}-AISLE-8-5", "battery": 90.0},
        ]
        for idx, r_data in enumerate(initial_robots):
            name = f"AGV 0{idx + 1}"
            db.add(Robot(
                robot_code=r_data["code"],
                name=name,
                warehouse_id=warehouse_id,
                status=r_data["status"],
                battery_level=r_data["battery"],
                current_location_id=r_data["loc"],
                current_x=r_data["x"],
                current_y=r_data["y"],
                target_x=0.0,
                target_y=0.0,
                enabled=True,
                robot_type="AGV",
                max_payload=200.0,
                max_speed=1.5,
                total_distance=0.0,
                total_tasks_completed=0
            ))
        db.commit()
    else:
        # Disperse existing robots to unique, non-overlapping coordinates along traversable aisle
        distinct_starts = [
            (1.0, 5.0), (4.0, 5.0), (6.0, 5.0), (8.0, 5.0), (10.0, 5.0), (11.0, 5.0), (12.0, 5.0), (3.0, 5.0), (2.0, 5.0), (5.0, 5.0)
        ]
        for idx, r in enumerate(existing_robots):
            r.enabled = True
            pos = distinct_starts[idx % len(distinct_starts)]
            r.current_x = pos[0]
            r.current_y = pos[1]
            r.target_x = 0.0
            r.target_y = 0.0
            r.assigned_task_id = None
            if r.status in ["FAILED", "OFFLINE"]:
                r.status = "AVAILABLE"
                r.battery_level = 90.0
            elif r.battery_level is None or r.battery_level < 20.0:
                r.battery_level = 95.0
            db.add(r)

        # Clear stale routes and reservations so robots start fresh
        db.query(RobotRoute).filter(RobotRoute.warehouse_id == warehouse_id).delete(synchronize_session=False)
        db.query(RobotReservation).filter(RobotReservation.warehouse_id == warehouse_id).delete(synchronize_session=False)
        db.commit()

    # 1. Seeding tasks/orders if there are fewer than 3 queued/prioritized tasks
    queued_count = db.query(Task).filter(
        Task.warehouse_id == warehouse_id,
        Task.status.in_(["QUEUED", "PRIORITIZED"])
    ).count()
    
    if queued_count < 3:
        # Determine number of tasks to seed based on scenario
        task_count = 5
        if scenario_type == "HIGH_DEMAND":
            task_count = 10
            
        items = db.query(Item).all()
        if not items:
            dummy = Item(id="ITM-DUMMY", name="Standard Parcel", unit_cost=10.0, safety_stock=5, sku="SKU-DUMMY")
            db.add(dummy)
            db.commit()
            items = [dummy]
            
        locations = db.query(WarehouseLocation).filter(WarehouseLocation.warehouse_id == warehouse_id).all()
        storage_locs = [l for l in locations if l.location_type == "STORAGE"]
        packing_locs = [l for l in locations if l.location_type == "PACKING"]
        
        if not storage_locs:
            storage_locs = locations if locations else [WarehouseLocation(id="LOC-STORE", warehouse_id=warehouse_id, x=2.0, y=2.0, location_type="STORAGE")]
        if not packing_locs:
            packing_locs = locations if locations else [WarehouseLocation(id="LOC-PACK", warehouse_id=warehouse_id, x=10.0, y=2.0, location_type="PACKING")]
            
        for idx in range(1, task_count + 1):
            order_id = f"SIM-ORD-{random.randint(1000, 9999)}"
            while db.query(Order).filter(Order.id == order_id).first():
                order_id = f"SIM-ORD-{random.randint(1000, 9999)}"
                
            order = Order(id=order_id, customer_ref=f"Sim Customer {idx}", warehouse_id=warehouse_id, status="CREATED", priority="MEDIUM")
            db.add(order)
            db.commit()
            
            rand_item = random.choice(items)
            db.add(OrderItem(order_id=order_id, item_id=rand_item.id, requested_qty=1))
            
            src = random.choice(storage_locs)
            dest = random.choice(packing_locs)
            
            task = Task(
                task_number=f"SIM-TSK-{random.randint(10000, 99999)}",
                warehouse_id=warehouse_id,
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
            db.add(task)
        db.commit()

    # 2. Mutate robots or obstacles based on scenario_type
    robots = db.query(Robot).filter(Robot.warehouse_id == warehouse_id, Robot.enabled == True).all()
    
    if scenario_type == "ROBOT_FAILURE" and robots:
        robots[0].status = "FAILED"
        logger.info("ROBOT_FAILURE scenario: robot %s set to FAILED status", robots[0].robot_code)
        db.add(robots[0])
        
    elif scenario_type in ("CONGESTION", "OBSTACLE_EVENT"):
        block = db.query(WarehouseObstacle).filter(
            WarehouseObstacle.warehouse_id == warehouse_id,
            WarehouseObstacle.x == 5,
            WarehouseObstacle.y == 2
        ).first()
        if not block:
            block = WarehouseObstacle(
                warehouse_id=warehouse_id,
                x=5,
                y=2,
                width=1,
                height=1,
                active=True,
                severity="HIGH",
                obstacle_type="TEMPORARY_BLOCK",
                description="Simulated temporary blockage in main aisle."
            )
            db.add(block)
            logger.info("OBSTACLE_EVENT scenario: Temporary obstacle added at (5, 2)")
            
    elif scenario_type == "ROBOT_LOW_BATTERY" or (robots and robots[0].battery_level > 50.0 and "low" in scenario_type.lower()):
        for r in robots:
            r.battery_level = 15.0
            db.add(r)
        logger.info("ROBOT_LOW_BATTERY scenario: all robot batteries set to 15%")
        
    db.commit()


@router.post("/simulation/start", summary="Start a new simulation")
def start_simulation(
    req: SimulationStartRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    wh = db.query(Warehouse).filter(Warehouse.id == req.warehouse_id).first()
    if not wh:
        raise HTTPException(404, f"Warehouse '{req.warehouse_id}' not found.")

    try:
        # Stop any existing active simulations for this warehouse
        active = db.query(DigitalTwinSimulation).filter(
            DigitalTwinSimulation.warehouse_id == req.warehouse_id,
            DigitalTwinSimulation.simulation_status.in_(["RUNNING", "PAUSED"])
        ).all()
        for old_sim in active:
            old_sim.simulation_status = "STOPPED"
            old_sim.stopped_at = datetime.now(UTC).replace(tzinfo=None)
        db.commit()
    except Exception as e_stop:
        logger.warning("Failed to stop active simulations: %s", e_stop)
        db.rollback()

    # Clean up any leftover simulation tasks and set up new scenario conditions
    cleanup_simulation_tasks(db, req.warehouse_id)
    try:
        setup_scenario_conditions(db, req.warehouse_id, req.scenario_type)
    except Exception as e:
        logger.warning("setup_scenario_conditions failed (non-fatal): %s", e)
        try:
            db.rollback()
        except Exception:
            pass

    # Ensure grid cells exist for this warehouse (seed 12x5 grid if missing)
    existing_cells = db.query(WarehouseGridCell).filter(
        WarehouseGridCell.warehouse_id == req.warehouse_id
    ).count()
    if existing_cells == 0:
        logger.info("No grid cells found for %s — seeding 12x5 grid", req.warehouse_id)
        _cell_types = {
            (1, 5): "RECEIVING", (2, 5): "RECEIVING",
            (11, 5): "CHARGING", (12, 5): "CHARGING",
            (3, 5): "PACKING", (4, 5): "PACKING",
        }
        for _col in range(1, 13):
            for _row in range(1, 6):
                _ctype = _cell_types.get((_col, _row),
                    "RACK" if _row in (1, 2, 3, 4) and _col not in (1, 2, 11, 12) else "AISLE")
                db.add(WarehouseGridCell(
                    warehouse_id=req.warehouse_id, x=_col, y=_row,
                    cell_type=_ctype, traversable=True, cost=1.0, occupied=False
                ))
        try:
            db.commit()
        except Exception as eg:
            logger.warning("Grid cell seeding failed: %s", eg)
            db.rollback()


    sim = DigitalTwinSimulation(
        warehouse_id=req.warehouse_id,
        simulation_status="READY",
        speed_multiplier=req.speed_multiplier,
        seed=req.seed,
        mode=req.mode,
        scenario_type=req.scenario_type,
        created_by=user.username,
        simulation_time_seconds=0.0,
        tick_count=0,
    )
    db.add(sim)
    db.commit()
    db.refresh(sim)

    # Take initial snapshot (version 0 = baseline)
    _take_snapshot(db, sim, version=0)

    # Transition to RUNNING
    sim.simulation_status = "RUNNING"
    sim.started_at = datetime.now(UTC).replace(tzinfo=None)
    db.add(sim)

    _add_sim_event(db, sim, "SIMULATION_STARTED",
                   f"Simulation started. Scenario: {sim.scenario_type}. Seed: {sim.seed}.",
                   metadata={"scenario": sim.scenario_type, "speed": sim.speed_multiplier})
    db.commit()

    # Execute one initial tick
    try:
        execute_simulation_tick(db)
        sim.tick_count += 1
        sim.simulation_time_seconds += 1.0 * sim.speed_multiplier
        db.add(sim)
        db.commit()
        _emit_tick_events(db, sim)
    except Exception as e:
        logger.error("Simulation tick error on start: %s", e)

    try:
        ledger.append_entry(db, "SIMULATION_STARTED", {
            "simulation_id": sim.id, "warehouse_id": req.warehouse_id,
            "by": user.username, "scenario": req.scenario_type
        })
    except Exception as le:
        logger.warning("Ledger entry failed for SIMULATION_STARTED: %s", le)

    try:
        notifications.send_change_alert("SIMULATION_STARTED", {
            "warehouse_id": req.warehouse_id, "simulation_id": sim.id
        })
    except Exception as ne:
        logger.warning("Notification alert failed for SIMULATION_STARTED: %s", ne)

    return {"simulation_id": sim.id, "status": sim.simulation_status,
            "message": "Simulation started.", "tick_count": sim.tick_count}


@router.post("/simulation/{sim_id}/pause", summary="Pause a running simulation")
def pause_simulation(sim_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    sim = db.query(DigitalTwinSimulation).filter(DigitalTwinSimulation.id == sim_id).first()
    if not sim:
        raise HTTPException(404, "Simulation not found.")
    if sim.simulation_status != "RUNNING":
        raise HTTPException(409, f"Cannot pause simulation in status '{sim.simulation_status}'.")
    sim.simulation_status = "PAUSED"
    sim.paused_at = datetime.now(UTC).replace(tzinfo=None)
    db.add(sim)
    _add_sim_event(db, sim, "SIMULATION_PAUSED", f"Simulation paused at tick {sim.tick_count}.")
    db.commit()
    ledger.append_entry(db, "SIMULATION_PAUSED", {"simulation_id": sim_id, "by": user.username})
    return {"simulation_id": sim_id, "status": "PAUSED", "tick_count": sim.tick_count}


@router.post("/simulation/{sim_id}/resume", summary="Resume a paused simulation")
def resume_simulation(sim_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    sim = db.query(DigitalTwinSimulation).filter(DigitalTwinSimulation.id == sim_id).first()
    if not sim:
        raise HTTPException(404, "Simulation not found.")
    if sim.simulation_status != "PAUSED":
        raise HTTPException(409, f"Cannot resume simulation in status '{sim.simulation_status}'.")
    sim.simulation_status = "RUNNING"
    sim.paused_at = None
    db.add(sim)
    _add_sim_event(db, sim, "SIMULATION_RESUMED", f"Simulation resumed from tick {sim.tick_count}.")
    db.commit()
    ledger.append_entry(db, "SIMULATION_RESUMED", {"simulation_id": sim_id, "by": user.username})
    return {"simulation_id": sim_id, "status": "RUNNING", "tick_count": sim.tick_count}


@router.patch("/simulation/{sim_id}/speed", summary="Update simulation speed multiplier live")
def update_simulation_speed(
    sim_id: int,
    req: SimulationSpeedRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Updates speed_multiplier for an active simulation.
    The background simulation worker reads this value every cycle, so the
    speed change takes effect on the very next tick iteration.
    """
    sim = db.query(DigitalTwinSimulation).filter(DigitalTwinSimulation.id == sim_id).first()
    if not sim:
        raise HTTPException(404, "Simulation not found.")
    if sim.simulation_status in ("STOPPED", "COMPLETED", "ERROR"):
        raise HTTPException(409, f"Cannot change speed of simulation in status '{sim.simulation_status}'.")

    speed = max(0.1, min(10.0, req.speed_multiplier))
    sim.speed_multiplier = speed
    db.add(sim)
    _add_sim_event(db, sim, "SIMULATION_SPEED_CHANGED",
                   f"Simulation speed changed to {speed}x by {user.username}.",
                   metadata={"speed_multiplier": speed})
    db.commit()
    ledger.append_entry(db, "SIMULATION_SPEED_CHANGED", {
        "simulation_id": sim_id,
        "speed_multiplier": speed,
        "by": user.username
    })
    return {"simulation_id": sim_id, "speed_multiplier": speed, "status": sim.simulation_status}


@router.post("/simulation/{sim_id}/step", summary="Advance exactly one simulation tick")

def step_simulation(sim_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """
    Advances simulation by exactly one tick regardless of RUNNING/PAUSED/READY status.
    Safe to call from PAUSED for step-by-step inspection.
    """
    sim = db.query(DigitalTwinSimulation).filter(DigitalTwinSimulation.id == sim_id).first()
    if not sim:
        raise HTTPException(404, "Simulation not found.")
    if sim.simulation_status in ("STOPPED", "COMPLETED", "ERROR"):
        raise HTTPException(409, f"Cannot step simulation in status '{sim.simulation_status}'.")

    prev_status = sim.simulation_status
    if prev_status == "PAUSED":
        # Temporarily step without changing status
        pass
    elif prev_status == "IDLE" or prev_status == "READY":
        sim.simulation_status = "PAUSED"
        sim.started_at = sim.started_at or datetime.now(UTC).replace(tzinfo=None)

    try:
        execute_simulation_tick(db)
        sim.tick_count += 1
        sim.simulation_time_seconds += 1.0 * sim.speed_multiplier
        db.add(sim)
        db.commit()
        _emit_tick_events(db, sim)
    except Exception as e:
        logger.error("Step simulation error: %s", e)
        sim.simulation_status = "ERROR"
        sim.error_message = str(e)
        db.add(sim)
        _add_sim_event(db, sim, "SIMULATION_ERROR", f"Step failed: {str(e)[:200]}", metadata={"error": str(e)})
        db.commit()
        raise HTTPException(500, f"Simulation step failed: {str(e)[:200]}")

    return {"simulation_id": sim_id, "status": sim.simulation_status,
            "tick_count": sim.tick_count, "simulation_time_seconds": sim.simulation_time_seconds}


@router.post("/simulation/{sim_id}/stop", summary="Stop simulation (preserve results)")
def stop_simulation(sim_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    sim = db.query(DigitalTwinSimulation).filter(DigitalTwinSimulation.id == sim_id).first()
    if not sim:
        raise HTTPException(404, "Simulation not found.")
    if sim.simulation_status in ("STOPPED", "COMPLETED"):
        raise HTTPException(409, f"Simulation already in status '{sim.simulation_status}'.")

    # Take final snapshot
    _take_snapshot(db, sim)

    sim.simulation_status = "STOPPED"
    sim.stopped_at = datetime.now(UTC).replace(tzinfo=None)
    db.add(sim)
    _add_sim_event(db, sim, "SIMULATION_STOPPED",
                   f"Simulation stopped after {sim.tick_count} ticks.")
    db.commit()

    cleanup_simulation_tasks(db, sim.warehouse_id)

    ledger.append_entry(db, "SIMULATION_STOPPED", {
        "simulation_id": sim_id, "tick_count": sim.tick_count, "by": user.username
    })
    notifications.send_change_alert("SIMULATION_STOPPED", {
        "warehouse_id": sim.warehouse_id,
        "simulation_id": sim_id,
        "tick_count": sim.tick_count,
        "stopped_by": user.username,
        "message": f"Digital twin simulation #{sim_id} was stopped after {sim.tick_count} ticks."
    })
    return {"simulation_id": sim_id, "status": "STOPPED",
            "tick_count": sim.tick_count, "message": "Simulation stopped. Results preserved. Seeding tasks cleared."}


@router.post("/simulation/{sim_id}/reset", summary="Reset simulation to initial snapshot")
def reset_simulation(sim_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """
    Restores robot/task/obstacle states to snapshot version 0 (baseline).
    Does NOT delete production audit history.
    Does NOT touch inventory.on_hand.
    """
    sim = db.query(DigitalTwinSimulation).filter(DigitalTwinSimulation.id == sim_id).first()
    if not sim:
        raise HTTPException(404, "Simulation not found.")

    # Find baseline snapshot (version 0 or lowest available version)
    baseline = db.query(SimulationSnapshot).filter(
        SimulationSnapshot.simulation_id == sim_id
    ).order_by(SimulationSnapshot.snapshot_version.asc()).first()

    if not baseline:
        baseline = db.query(SimulationSnapshot).filter(
            SimulationSnapshot.warehouse_id == sim.warehouse_id
        ).order_by(SimulationSnapshot.snapshot_version.asc()).first()

    if baseline:
        _restore_snapshot(db, baseline)
    else:
        # Re-initialize baseline scenario conditions for this warehouse
        try:
            setup_scenario_conditions(db, sim.warehouse_id, sim.scenario_type or "NORMAL_OPERATIONS")
        except Exception as e_res:
            logger.warning("Reset scenario re-setup warning: %s", e_res)

    # Delete simulation events, telemetry records, and routes to start empty
    db.query(SimulationEvent).filter(SimulationEvent.simulation_id == sim_id).delete(synchronize_session=False)
    robot_ids = [r.id for r in db.query(Robot).filter(Robot.warehouse_id == sim.warehouse_id).all()]
    if robot_ids:
        db.query(RobotTelemetryEvent).filter(RobotTelemetryEvent.robot_id.in_(robot_ids)).delete(synchronize_session=False)
    db.query(RobotRoute).filter(RobotRoute.warehouse_id == sim.warehouse_id).delete(synchronize_session=False)

    sim.simulation_status = "READY"
    sim.simulation_time_seconds = 0.0
    sim.tick_count = 0
    sim.started_at = None
    sim.paused_at = None
    sim.stopped_at = None
    sim.completed_at = None
    sim.error_message = None
    db.add(sim)

    _add_sim_event(db, sim, "SIMULATION_RESET",
                   "Simulation reset to initial snapshot. Inventory unchanged.")
    db.commit()
    ledger.append_entry(db, "SIMULATION_RESET", {"simulation_id": sim_id, "by": user.username})
    return {"simulation_id": sim_id, "status": "READY",
            "message": "Simulation reset. Robot/task states restored from baseline snapshot. Inventory unchanged."}


@router.get("/simulation/{sim_id}", summary="Get simulation record")
def get_simulation(sim_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    sim = db.query(DigitalTwinSimulation).filter(DigitalTwinSimulation.id == sim_id).first()
    if not sim:
        raise HTTPException(404, "Simulation not found.")
    return {
        "id": sim.id,
        "warehouse_id": sim.warehouse_id,
        "simulation_status": sim.simulation_status,
        "simulation_time_seconds": sim.simulation_time_seconds,
        "speed_multiplier": sim.speed_multiplier,
        "seed": sim.seed,
        "mode": sim.mode,
        "scenario_type": sim.scenario_type,
        "tick_count": sim.tick_count,
        "created_at": sim.created_at.isoformat(),
        "started_at": sim.started_at.isoformat() if sim.started_at else None,
        "paused_at": sim.paused_at.isoformat() if sim.paused_at else None,
        "stopped_at": sim.stopped_at.isoformat() if sim.stopped_at else None,
        "completed_at": sim.completed_at.isoformat() if sim.completed_at else None,
        "error_message": sim.error_message,
        "created_by": sim.created_by,
    }


@router.get("/simulation/{sim_id}/events", summary="Get simulation-scoped events")
def get_sim_events(
    sim_id: int,
    severity: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    sim = db.query(DigitalTwinSimulation).filter(DigitalTwinSimulation.id == sim_id).first()
    if not sim:
        raise HTTPException(404, "Simulation not found.")
    q = db.query(SimulationEvent).filter(SimulationEvent.simulation_id == sim_id)
    if severity:
        q = q.filter(SimulationEvent.severity == severity.upper())
    if event_type:
        q = q.filter(SimulationEvent.event_type == event_type.upper())
    events = q.order_by(SimulationEvent.sim_time_seconds.asc(), SimulationEvent.id.asc()).offset(offset).limit(limit).all()
    return [
        {
            "id": e.id,
            "event_type": e.event_type,
            "severity": e.severity,
            "sim_time_seconds": e.sim_time_seconds,
            "real_timestamp": e.real_timestamp.isoformat(),
            "robot_id": e.robot_id,
            "task_id": e.task_id,
            "message": e.message,
            "metadata": json.loads(e.event_metadata),
        }
        for e in events
    ]


@router.get("/simulation/{sim_id}/metrics", summary="Get simulation KPIs")
def get_sim_metrics(sim_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """
    Returns simulation KPIs computed from actual event/robot/task records.
    All metrics are ESTIMATED SIMULATION METRICS, not real-world measurements.
    """
    sim = db.query(DigitalTwinSimulation).filter(DigitalTwinSimulation.id == sim_id).first()
    if not sim:
        raise HTTPException(404, "Simulation not found.")

    # Task metrics
    completed = db.query(SimulationEvent).filter(
        SimulationEvent.simulation_id == sim_id,
        SimulationEvent.event_type == "TASK_COMPLETED"
    ).count()
    started = db.query(SimulationEvent).filter(
        SimulationEvent.simulation_id == sim_id,
        SimulationEvent.event_type == "TASK_STARTED"
    ).count()
    failed = db.query(SimulationEvent).filter(
        SimulationEvent.simulation_id == sim_id,
        SimulationEvent.event_type == "TASK_FAILED"
    ).count()
    replanned = db.query(SimulationEvent).filter(
        SimulationEvent.simulation_id == sim_id,
        SimulationEvent.event_type == "ROUTE_REPLANNED"
    ).count()
    collisions = db.query(SimulationEvent).filter(
        SimulationEvent.simulation_id == sim_id,
        SimulationEvent.event_type == "COLLISION_AVOIDED"
    ).count()
    waiting = db.query(SimulationEvent).filter(
        SimulationEvent.simulation_id == sim_id,
        SimulationEvent.event_type == "ROBOT_WAITING"
    ).count()
    battery_low = db.query(SimulationEvent).filter(
        SimulationEvent.simulation_id == sim_id,
        SimulationEvent.event_type == "BATTERY_LOW"
    ).count()
    battery_crit = db.query(SimulationEvent).filter(
        SimulationEvent.simulation_id == sim_id,
        SimulationEvent.event_type == "BATTERY_CRITICAL"
    ).count()

    # Robot utilization: ratio of MOVING/PICKING/RETURNING robots to total enabled
    robots = db.query(Robot).filter(Robot.warehouse_id == sim.warehouse_id, Robot.enabled == True).all()
    active_robots = sum(1 for r in robots if r.status in ("MOVING", "PICKING", "RETURNING", "ASSIGNED"))
    total_robots = len(robots)

    task_completion_rate = round(completed / started, 3) if started > 0 else 0.0
    robot_utilization = round(active_robots / total_robots, 3) if total_robots > 0 else 0.0

    return {
        "simulation_id": sim_id,
        "metric_disclaimer": "ESTIMATED SIMULATION METRICS — not real-world measurements",
        "simulation_status": sim.simulation_status,
        "tick_count": sim.tick_count,
        "simulation_time_seconds": sim.simulation_time_seconds,
        "tasks": {
            "started": started,
            "completed": completed,
            "failed": failed,
            "task_completion_rate": task_completion_rate,
        },
        "robots": {
            "total": total_robots,
            "active": active_robots,
            "robot_utilization": robot_utilization,
        },
        "navigation": {
            "route_replans": replanned,
            "collision_avoidances": collisions,
            "robot_waiting_events": waiting,
        },
        "alerts": {
            "battery_low_events": battery_low,
            "battery_critical_events": battery_crit,
        },
    }


@router.post("/simulation/{sim_id}/snapshot", summary="Take a manual snapshot")
def take_snapshot(sim_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    sim = db.query(DigitalTwinSimulation).filter(DigitalTwinSimulation.id == sim_id).first()
    if not sim:
        raise HTTPException(404, "Simulation not found.")
    snap = _take_snapshot(db, sim)
    return {
        "snapshot_id": snap.id,
        "simulation_id": sim_id,
        "snapshot_version": snap.snapshot_version,
        "taken_at": snap.taken_at.isoformat(),
        "sim_time_seconds": snap.sim_time_seconds,
        "message": "Snapshot captured."
    }


@router.get("/simulation/{sim_id}/snapshots", summary="List simulation snapshots")
def list_snapshots(sim_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    sim = db.query(DigitalTwinSimulation).filter(DigitalTwinSimulation.id == sim_id).first()
    if not sim:
        raise HTTPException(404, "Simulation not found.")
    snaps = db.query(SimulationSnapshot).filter(
        SimulationSnapshot.simulation_id == sim_id
    ).order_by(SimulationSnapshot.snapshot_version.asc()).all()
    return [
        {
            "id": s.id,
            "snapshot_version": s.snapshot_version,
            "taken_at": s.taken_at.isoformat(),
            "sim_time_seconds": s.sim_time_seconds,
        }
        for s in snaps
    ]


# ---------------------------------------------------------------------------
# Internal: Emit simulation events from tick telemetry
# ---------------------------------------------------------------------------

def _emit_tick_events(db: Session, sim: DigitalTwinSimulation):
    """
    After each simulation tick, inspect robot/task/telemetry state changes
    and emit SimulationEvent records for significant changes.
    """
    try:
        robots = db.query(Robot).filter(Robot.warehouse_id == sim.warehouse_id).all()
        for r in robots:
            # Battery warnings (throttled to avoid duplicates)
            if r.battery_level <= 10.0:
                exists = db.query(SimulationEvent).filter(
                    SimulationEvent.simulation_id == sim.id,
                    SimulationEvent.event_type == "BATTERY_CRITICAL",
                    SimulationEvent.robot_id == r.id,
                    SimulationEvent.sim_time_seconds >= sim.simulation_time_seconds - 30.0
                ).first()
                if not exists:
                    _add_sim_event(db, sim, "BATTERY_CRITICAL",
                                   f"Robot {r.robot_code} battery critical: {r.battery_level:.1f}%",
                                   robot_id=r.id, metadata={"battery": r.battery_level})
            elif r.battery_level <= 25.0:
                exists = db.query(SimulationEvent).filter(
                    SimulationEvent.simulation_id == sim.id,
                    SimulationEvent.event_type == "BATTERY_LOW",
                    SimulationEvent.robot_id == r.id,
                    SimulationEvent.sim_time_seconds >= sim.simulation_time_seconds - 30.0
                ).first()
                if not exists:
                    _add_sim_event(db, sim, "BATTERY_LOW",
                                   f"Robot {r.robot_code} battery low: {r.battery_level:.1f}%",
                                   robot_id=r.id, metadata={"battery": r.battery_level})

            # Robot status events
            if r.status == "FAILED":
                exists = db.query(SimulationEvent).filter(
                    SimulationEvent.simulation_id == sim.id,
                    SimulationEvent.event_type == "ROBOT_FAILED",
                    SimulationEvent.robot_id == r.id
                ).first()
                if not exists:
                    _add_sim_event(db, sim, "ROBOT_FAILED",
                                   f"Robot {r.robot_code} failed.",
                                   robot_id=r.id, task_id=r.assigned_task_id)
            elif r.status == "WAITING":
                exists = db.query(SimulationEvent).filter(
                    SimulationEvent.simulation_id == sim.id,
                    SimulationEvent.event_type == "ROBOT_WAITING",
                    SimulationEvent.robot_id == r.id,
                    SimulationEvent.sim_time_seconds >= sim.simulation_time_seconds - 5.0
                ).first()
                if not exists:
                    _add_sim_event(db, sim, "ROBOT_WAITING",
                                   f"Robot {r.robot_code} waiting (collision avoidance).",
                                   robot_id=r.id)
            elif r.status == "MOVING":
                exists = db.query(SimulationEvent).filter(
                    SimulationEvent.simulation_id == sim.id,
                    SimulationEvent.event_type == "ROBOT_MOVING",
                    SimulationEvent.robot_id == r.id,
                    SimulationEvent.task_id == r.assigned_task_id
                ).first()
                if not exists and r.assigned_task_id:
                    t_obj = db.query(Task).filter(Task.id == r.assigned_task_id).first()
                    t_num = t_obj.task_number if t_obj else f"TSK-{r.assigned_task_id}"
                    _add_sim_event(db, sim, "ROBOT_MOVING",
                                   f"Robot {r.robot_code} moving to pickup location for task {t_num}.",
                                   robot_id=r.id, task_id=r.assigned_task_id)
            elif r.status == "PICKING":
                exists = db.query(SimulationEvent).filter(
                    SimulationEvent.simulation_id == sim.id,
                    SimulationEvent.event_type == "ROBOT_PICKING",
                    SimulationEvent.robot_id == r.id,
                    SimulationEvent.task_id == r.assigned_task_id
                ).first()
                if not exists and r.assigned_task_id:
                    _add_sim_event(db, sim, "ROBOT_PICKING",
                                   f"Robot {r.robot_code} reached pickup location.",
                                   robot_id=r.id, task_id=r.assigned_task_id)
            elif r.status == "RETURNING":
                exists = db.query(SimulationEvent).filter(
                    SimulationEvent.simulation_id == sim.id,
                    SimulationEvent.event_type == "ROBOT_RETURNING",
                    SimulationEvent.robot_id == r.id,
                    SimulationEvent.task_id == r.assigned_task_id
                ).first()
                if not exists and r.assigned_task_id:
                    _add_sim_event(db, sim, "ROBOT_RETURNING",
                                   f"Robot {r.robot_code} carrying inventory to packing.",
                                   robot_id=r.id, task_id=r.assigned_task_id)
            elif r.status == "DROPPING":
                exists = db.query(SimulationEvent).filter(
                    SimulationEvent.simulation_id == sim.id,
                    SimulationEvent.event_type == "ROBOT_DROPPING",
                    SimulationEvent.robot_id == r.id,
                    SimulationEvent.task_id == r.assigned_task_id
                ).first()
                if not exists and r.assigned_task_id:
                    _add_sim_event(db, sim, "ROBOT_DROPPING",
                                   f"Robot {r.robot_code} arrived at dropoff location.",
                                   robot_id=r.id, task_id=r.assigned_task_id)
            elif r.status == "CHARGING":
                exists = db.query(SimulationEvent).filter(
                    SimulationEvent.simulation_id == sim.id,
                    SimulationEvent.event_type == "ROBOT_CHARGING",
                    SimulationEvent.robot_id == r.id,
                    SimulationEvent.sim_time_seconds >= sim.simulation_time_seconds - 15.0
                ).first()
                if not exists:
                    _add_sim_event(db, sim, "ROBOT_CHARGING",
                                   f"Robot {r.robot_code} reached charger; battery replenishment started.",
                                   robot_id=r.id)

        # Route replanning events from RobotRoute
        replanned_routes = db.query(RobotRoute).filter(
            RobotRoute.warehouse_id == sim.warehouse_id,
            RobotRoute.status == "REPLANNED"
        ).all()
        for route in replanned_routes:
            r_obj = db.query(Robot).filter(Robot.id == route.robot_id).first()
            r_code = r_obj.robot_code if r_obj else f"RB-{route.robot_id}"
            exists = db.query(SimulationEvent).filter(
                SimulationEvent.simulation_id == sim.id,
                SimulationEvent.event_type == "ROUTE_REPLANNED",
                SimulationEvent.robot_id == route.robot_id,
                SimulationEvent.sim_time_seconds >= sim.simulation_time_seconds - 5.0
            ).first()
            if not exists:
                _add_sim_event(db, sim, "ROUTE_REPLANNED",
                               f"Robot {r_code} replanned route due to obstacle.",
                               robot_id=route.robot_id, task_id=route.task_id, route_id=route.id)

        # Task completion events
        completed_tasks = db.query(Task).filter(
            Task.warehouse_id == sim.warehouse_id,
            Task.status == "COMPLETED",
            Task.completed_at != None,
        ).order_by(Task.completed_at.desc()).limit(5).all()
        for t in completed_tasks:
            exists = db.query(SimulationEvent).filter(
                SimulationEvent.simulation_id == sim.id,
                SimulationEvent.event_type == "TASK_COMPLETED",
                SimulationEvent.task_id == t.id
            ).first()
            if not exists:
                r_code = t.assigned_robot_id or "AGV"
                _add_sim_event(db, sim, "TASK_COMPLETED",
                               f"Robot {r_code} completed task {t.task_number}.",
                               task_id=t.id)

        db.commit()

        # Broadcast simulation updates to subscribers
        try:
            from backend.sync_broadcast import broadcaster
            broadcaster.broadcast_sim(sim.id, {
                "event_type": "SIMULATION_TICK",
                "entity_type": "simulation",
                "entity_id": str(sim.id),
                "data": {
                    "tick_count": sim.tick_count,
                    "simulation_time_seconds": sim.simulation_time_seconds,
                    "simulation_status": sim.simulation_status
                }
            })
            for r in robots:
                broadcaster.broadcast_sim(sim.id, {
                    "event_type": "ROBOT_MOVED",
                    "entity_type": "robot",
                    "entity_id": r.robot_code,
                    "data": {"x": r.current_x, "y": r.current_y, "total_distance": r.total_distance, "battery_level": r.battery_level}
                })
                broadcaster.broadcast_sim(sim.id, {
                    "event_type": "ROBOT_STATUS_CHANGED",
                    "entity_type": "robot",
                    "entity_id": r.robot_code,
                    "data": {"status": r.status}
                })
                broadcaster.broadcast_sim(sim.id, {
                    "event_type": "ROBOT_BATTERY_CHANGED",
                    "entity_type": "robot",
                    "entity_id": r.robot_code,
                    "data": {"battery_level": r.battery_level}
                })
            for t in completed_tasks:
                broadcaster.broadcast_sim(sim.id, {
                    "event_type": "TASK_STATUS_CHANGED",
                    "entity_type": "task",
                    "entity_id": t.task_number,
                    "data": {"status": t.status}
                })
        except Exception as sim_broadcast_err:
            logger.warning("Simulation sync broadcast failed: %s", sim_broadcast_err)
    except Exception as e:
        logger.warning("Failed to emit tick events: %s", e)
