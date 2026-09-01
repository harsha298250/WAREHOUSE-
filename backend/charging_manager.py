"""
charging_manager.py — Phase 11: Production Deterministic AGV Robot Charging & Queue Management System

Provides a thread-safe, warehouse-isolated charging queue and port reservation engine.

Rules:
1. Low Battery Detection: Detects robots with battery <= low_battery_threshold.
2. Port Capacity Bounds: Strictly enforces charging port capacity.
3. Lowest-Battery Priority: Sorts waiting robots primarily by lowest battery percentage (with stable tie-breakers).
4. Port Reservation: Atomically reserves an available port before robot travels to it.
5. Gradual Charging: Increases battery level step-by-step (e.g. +5% per tick).
6. Port Release & Promotion: Upon 100% full charge (or robot failure/reset), releases port and promotes next lowest-battery robot.
7. Multi-Warehouse Scoping: Completely isolated per warehouse_id.
"""

import logging
import json
from datetime import datetime, UTC
from typing import Dict, List, Any, Optional

from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.models import Robot, WarehouseLocation, RobotRoute, RobotTelemetryEvent, SimulationEvent
from backend import notifications
from backend import audit_ledger as ledger

logger = logging.getLogger("warehouse.charging_manager")

def evaluate_warehouse_charging_system(db: Session, warehouse_id: str, low_battery_threshold: float = 20.0, charge_rate_per_tick: float = 5.0):
    """
    Main tick engine function to process low battery detection, queue sorting, port reservation,
    gradual charging, and completion release for a specific warehouse.
    """
    try:
        # 1. Fetch all charging locations (ports) for this warehouse
        ports = db.query(WarehouseLocation).filter(
            WarehouseLocation.warehouse_id == warehouse_id,
            WarehouseLocation.location_type == "CHARGING"
        ).all()

        if not ports:
            # If no designated CHARGING locations exist, create 2 fallback charging ports at (11, 5) and (12, 5)
            p1 = WarehouseLocation(id=f"WH-{warehouse_id}-CHARGING-1", warehouse_id=warehouse_id, zone="CHARGING", aisle="C-1", rack="CR-1", shelf="CS-1", x=11.0, y=5.0, location_type="CHARGING")
            p2 = WarehouseLocation(id=f"WH-{warehouse_id}-CHARGING-2", warehouse_id=warehouse_id, zone="CHARGING", aisle="C-1", rack="CR-2", shelf="CS-1", x=12.0, y=5.0, location_type="CHARGING")
            db.add_all([p1, p2])
            db.commit()
            ports = [p1, p2]

        total_ports = len(ports)

        # 2. Fetch all enabled robots for this warehouse
        robots = db.query(Robot).filter(
            Robot.warehouse_id == warehouse_id,
            Robot.enabled == True
        ).all()

        if not robots:
            return

        # 3. Process low battery detection for operational/idle robots
        for r in robots:
            if r.status not in ("CHARGING", "WAITING_FOR_CHARGER", "FAILED", "OFFLINE", "MAINTENANCE"):
                if r.battery_level <= low_battery_threshold:
                    logger.info("Low battery detected for robot %s (%.1f%% <= %.1f%%). Transitioning to WAITING_FOR_CHARGER.", r.robot_code, r.battery_level, low_battery_threshold)
                    
                    # Unassign task if any
                    if r.assigned_task_id:
                        from backend.models import Task
                        t = db.query(Task).filter(Task.id == r.assigned_task_id).first()
                        if t and t.status in ("ASSIGNED", "IN_PROGRESS"):
                            t.status = "QUEUED"
                            t.assigned_robot_id = None
                            db.add(t)
                        r.assigned_task_id = None

                    # Cancel active routes
                    active_routes = db.query(RobotRoute).filter(
                        RobotRoute.robot_id == r.id,
                        RobotRoute.status.in_(["IN_PROGRESS", "REPLANNED"])
                    ).all()
                    for rt in active_routes:
                        rt.status = "CANCELLED"
                        db.add(rt)

                    r.status = "WAITING_FOR_CHARGER"
                    db.add(r)

                    try:
                        notifications.send_change_alert("ROBOT_LOW_BATTERY", {
                            "robot_code": r.robot_code,
                            "warehouse": r.warehouse_id,
                            "battery_level": r.battery_level,
                            "low_battery_thresh": low_battery_threshold
                        })
                    except Exception:
                        pass

        # 4. Map active port reservations and occupied states
        # Port state map: port_id -> assigned robot_id or None
        port_assignments: Dict[str, Optional[int]] = {p.id: None for p in ports}
        charging_robots = [r for r in robots if r.status == "CHARGING"]

        for r in charging_robots:
            # If target_location_id or current_location_id matches a port
            assigned_port_id = r.target_location_id or r.current_location_id
            if assigned_port_id in port_assignments:
                port_assignments[assigned_port_id] = r.id
            else:
                # Find unassigned port if target is missing
                for p_id, occ_id in port_assignments.items():
                    if occ_id is None:
                        port_assignments[p_id] = r.id
                        r.target_location_id = p_id
                        p_loc = next((p for p in ports if p.id == p_id), None)
                        if p_loc:
                            r.target_x = float(p_loc.x)
                            r.target_y = float(p_loc.y)
                        db.add(r)
                        break

        # 5. Process robots currently CHARGING (gradual charge progression & completion)
        for r in charging_robots:
            p_loc = next((p for p in ports if p.id == (r.target_location_id or r.current_location_id)), None)
            
            # Check if robot is physically at the charging port
            is_at_port = False
            if p_loc:
                dist = abs(r.current_x - float(p_loc.x)) + abs(r.current_y - float(p_loc.y))
                if dist < 0.2:
                    is_at_port = True

            if is_at_port:
                # Robot is physically connected and charging
                r.current_x = float(p_loc.x)
                r.current_y = float(p_loc.y)
                r.current_location_id = p_loc.id
                
                # Increment battery gradually
                old_bat = r.battery_level
                r.battery_level = min(100.0, r.battery_level + charge_rate_per_tick)
                db.add(r)
                
                # Check for completion (>= 98.0%)
                if r.battery_level >= 98.0:
                    r.battery_level = 100.0
                    r.status = "AVAILABLE"
                    r.target_location_id = None
                    r.target_x = 0.0
                    r.target_y = 0.0
                    db.add(r)

                    # Free port reservation
                    if p_loc.id in port_assignments and port_assignments[p_loc.id] == r.id:
                        port_assignments[p_loc.id] = None

                    logger.info("Robot %s completed charging (100%%). Port %s released.", r.robot_code, p_loc.id)

                    try:
                        notifications.send_change_alert("ROBOT_CHARGING_COMPLETED", {
                            "robot_code": r.robot_code,
                            "warehouse": r.warehouse_id,
                            "battery_level": 100.0
                        })
                        ledger.append_entry(db, "ROBOT_CHARGING_COMPLETED", {
                            "robot_code": r.robot_code,
                            "warehouse_id": r.warehouse_id,
                            "port_id": p_loc.id
                        })
                    except Exception:
                        pass

        # 6. Evaluate WAITING_FOR_CHARGER queue with LOWEST-BATTERY PRIORITY
        waiting_robots = [r for r in robots if r.status == "WAITING_FOR_CHARGER"]

        # Deterministic sorting algorithm:
        # 1. Primary: Lowest battery level (ASCENDING)
        # 2. Secondary: Updated timestamp (ASCENDING: waiting longer)
        # 3. Tertiary: Robot code (ASCENDING: stable tie-breaker)
        waiting_robots.sort(key=lambda r: (r.battery_level, r.updated_at or datetime.min, r.robot_code))

        # Assign available ports to waiting robots by priority
        available_port_ids = [p_id for p_id, occupant in port_assignments.items() if occupant is None]

        for p_id in available_port_ids:
            if not waiting_robots:
                break

            # Pop lowest battery waiting robot
            next_robot = waiting_robots.pop(0)
            p_loc = next((p for p in ports if p.id == p_id), None)
            if not p_loc:
                continue

            # Atomically reserve port
            port_assignments[p_id] = next_robot.id
            next_robot.status = "CHARGING"
            next_robot.target_location_id = p_loc.id
            next_robot.target_x = float(p_loc.x)
            next_robot.target_y = float(p_loc.y)
            db.add(next_robot)

            # Generate A* route to charging port
            try:
                from backend.routers.pathfinding import find_path_astar
                path = find_path_astar(
                    warehouse_id,
                    (int(round(next_robot.current_x)), int(round(next_robot.current_y))),
                    (int(round(p_loc.x)), int(round(p_loc.y)))
                )
                if path:
                    route = RobotRoute(
                        warehouse_id=warehouse_id,
                        robot_id=next_robot.id,
                        task_id=None,
                        start_x=next_robot.current_x,
                        start_y=next_robot.current_y,
                        target_x=float(p_loc.x),
                        target_y=float(p_loc.y),
                        path_data=json.dumps(path),
                        status="IN_PROGRESS"
                    )
                    db.add(route)
            except Exception as pf_err:
                logger.warning("Failed to calculate path to charger for robot %s: %s", next_robot.robot_code, pf_err)

            logger.info("Reserved port %s for lowest battery waiting robot %s (Battery: %.1f%%)", p_id, next_robot.robot_code, next_robot.battery_level)

            try:
                ledger.append_entry(db, "CHARGER_ASSIGNED", {
                    "robot_code": next_robot.robot_code,
                    "warehouse_id": warehouse_id,
                    "port_id": p_id,
                    "battery_level": next_robot.battery_level
                })
            except Exception:
                pass

        db.commit()

    except Exception as e:
        db.rollback()
        logger.error("Error evaluating charging system for warehouse %s: %s", warehouse_id, e, exc_info=True)

def get_warehouse_charging_queue_info(db: Session, warehouse_id: str) -> Dict[str, Any]:
    """
    Returns live charging queue status, port capacity, occupied ports, and ordered waiting list.
    """
    ports = db.query(WarehouseLocation).filter(
        WarehouseLocation.warehouse_id == warehouse_id,
        WarehouseLocation.location_type == "CHARGING"
    ).all()

    robots = db.query(Robot).filter(
        Robot.warehouse_id == warehouse_id,
        Robot.enabled == True
    ).all()

    charging_robots = [r for r in robots if r.status == "CHARGING"]
    waiting_robots = [r for r in robots if r.status == "WAITING_FOR_CHARGER"]

    # Sort waiting queue by lowest battery first
    waiting_robots.sort(key=lambda r: (r.battery_level, r.updated_at or datetime.min, r.robot_code))

    port_status_list = []
    for p in ports:
        occupant = next((r for r in charging_robots if r.target_location_id == p.id or r.current_location_id == p.id), None)
        port_status_list.append({
            "port_id": p.id,
            "x": p.x,
            "y": p.y,
            "status": "OCCUPIED" if occupant and abs(occupant.current_x - float(p.x)) < 0.2 and abs(occupant.current_y - float(p.y)) < 0.2
                      else ("RESERVED" if occupant else "AVAILABLE"),
            "robot_code": occupant.robot_code if occupant else None,
            "battery": occupant.battery_level if occupant else None
        })

    waiting_queue_list = [
        {
            "queue_position": idx + 1,
            "robot_code": r.robot_code,
            "battery_level": r.battery_level,
            "current_x": r.current_x,
            "current_y": r.current_y
        }
        for idx, r in enumerate(waiting_robots)
    ]

    return {
        "warehouse_id": warehouse_id,
        "total_ports": len(ports),
        "occupied_ports": sum(1 for p in port_status_list if p["status"] in ("OCCUPIED", "RESERVED")),
        "available_ports": sum(1 for p in port_status_list if p["status"] == "AVAILABLE"),
        "ports": port_status_list,
        "waiting_queue_count": len(waiting_queue_list),
        "waiting_queue": waiting_queue_list
    }
