"""
operational_pathfinding.py — Operational routing service connecting Tasks,
Robots, and Pathfinding algorithms (A* & Dijkstra) cleanly.
"""

import logging
import json
import time
from typing import Dict, Any, Optional, Tuple, List
from sqlalchemy.orm import Session
from fastapi import HTTPException

from backend.models import (
    Task, Robot, WarehouseLocation, WarehouseGridCell, WarehouseObstacle,
    RobotRoute, AuditLedger, Warehouse
)
from backend.routers.pathfinding import (
    initialize_warehouse_grid_if_empty,
    run_a_star_verbose,
    run_dijkstra_verbose,
    validate_path
)
from backend import notifications

logger = logging.getLogger("operational_pathfinding")


def map_location_to_grid(db: Session, warehouse_id: str, location_identifier: Optional[str]) -> Optional[Tuple[int, int]]:
    """
    Map location identifier (WarehouseLocation ID or coordinate string) to integer grid (x, y).
    Returns None if location cannot be mapped.
    """
    if not location_identifier:
        return None

    # Check direct WarehouseLocation model
    loc = db.query(WarehouseLocation).filter(WarehouseLocation.id == location_identifier).first()
    if loc and loc.x is not None and loc.y is not None:
        return (int(round(loc.x)), int(round(loc.y)))

    # Check if identifier is formatted as "X,Y" or "X-Y"
    cleaned = location_identifier.replace("WH-", "").replace("ZONE-", "")
    parts = cleaned.replace("-", ",").split(",")
    if len(parts) >= 2:
        try:
            x, y = int(parts[0]), int(parts[1])
            return (x, y)
        except ValueError:
            pass

    return None


def get_operational_task_route(
    db: Session,
    task_id: int,
    robot_identifier: Optional[str] = None,
    algorithm: str = "A_STAR"
) -> Dict[str, Any]:
    """
    Computes a complete operational route: Robot -> Pickup Location -> Delivery Destination.
    Uses existing A* or Dijkstra implementations without altering core algorithms.
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(404, f"Task {task_id} not found.")

    warehouse_id = task.warehouse_id
    initialize_warehouse_grid_if_empty(db, warehouse_id)

    # 1. Resolve Robot
    robot = None
    if robot_identifier:
        robot = db.query(Robot).filter(
            (Robot.robot_code == robot_identifier) | (Robot.id == str(robot_identifier))
        ).first()
    elif task.assigned_robot_id:
        robot = db.query(Robot).filter(Robot.robot_code == task.assigned_robot_id).first()

    robot_assigned = robot is not None
    robot_code = robot.robot_code if robot else "NONE"

    # 2. Resolve Start Node (Robot location or default)
    if robot and robot.current_x is not None and robot.current_y is not None:
        start_node = (int(round(robot.current_x)), int(round(robot.current_y)))
    else:
        # Fallback start node if robot location not available
        start_node = (1, 5)  # Receiving cell default

    # 3. Resolve Pickup Node
    pickup_node = map_location_to_grid(db, warehouse_id, task.source_location_id)
    if not pickup_node:
        # Attempt fallback to location table by task warehouse
        loc_first = db.query(WarehouseLocation).filter(WarehouseLocation.warehouse_id == warehouse_id).first()
        if loc_first and loc_first.x is not None and loc_first.y is not None:
            pickup_node = (int(round(loc_first.x)), int(round(loc_first.y)))

    if not pickup_node:
        raise HTTPException(400, "Location cannot be mapped to warehouse route.")

    # 4. Resolve Destination Node
    dest_node = None
    if hasattr(task, "destination_location_id") and task.destination_location_id:
        dest_node = map_location_to_grid(db, warehouse_id, task.destination_location_id)

    if not dest_node:
        # Default delivery location for picking (e.g. Receiving / Drop-off zone at x=11, y=5 or charging/pack area)
        drop_cell = db.query(WarehouseGridCell).filter(
            WarehouseGridCell.warehouse_id == warehouse_id,
            WarehouseGridCell.cell_type.in_(["RECEIVING", "CHARGING", "PACKING"])
        ).first()
        if drop_cell:
            dest_node = (drop_cell.x, drop_cell.y)
        else:
            dest_node = (12, 5)

    # 5. Fetch Grid Map & Obstacles
    cells = db.query(WarehouseGridCell).filter(WarehouseGridCell.warehouse_id == warehouse_id).all()
    grid_map = {(c.x, c.y): {"traversable": c.traversable, "cost": c.cost, "type": c.cell_type} for c in cells}

    obs = db.query(WarehouseObstacle).filter(
        WarehouseObstacle.warehouse_id == warehouse_id,
        WarehouseObstacle.active == True
    ).all()
    obstacles = set((o.x, o.y) for o in obs)

    # Fetch settings
    from backend.settings import get_settings
    settings = get_settings(db)
    allow_diagonal = settings.get("allow_diagonal", False)

    # 6. Execute Pathfinding Algorithms
    alg = algorithm.upper()

    if alg == "COMPARE":
        # Run both A* and Dijkstra
        path_a1, cost_a1, dur_a1, msg_a1, exp_a1, expl_a1, rel_a1 = run_a_star_verbose(start_node, pickup_node, grid_map, obstacles, allow_diagonal)
        path_a2, cost_a2, dur_a2, msg_a2, exp_a2, expl_a2, rel_a2 = run_a_star_verbose(pickup_node, dest_node, grid_map, obstacles, allow_diagonal)

        path_d1, cost_d1, dur_d1, msg_d1, exp_d1, expl_d1, rel_d1 = run_dijkstra_verbose(start_node, pickup_node, grid_map, obstacles, allow_diagonal)
        path_d2, cost_d2, dur_d2, msg_d2, exp_d2, expl_d2, rel_d2 = run_dijkstra_verbose(pickup_node, dest_node, grid_map, obstacles, allow_diagonal)

        success_a = (path_a1 is not None) and (path_a2 is not None)
        success_d = (path_d1 is not None) and (path_d2 is not None)

        full_path_a = (path_a1 or []) + (path_a2[1:] if path_a2 else [])
        full_path_d = (path_d1 or []) + (path_d2[1:] if path_d2 else [])

        total_cost_a = cost_a1 + cost_a2
        total_cost_d = cost_d1 + cost_d2

        speed = robot.max_speed if robot and robot.max_speed else 1.5
        est_time_a = total_cost_a / speed if speed > 0 else total_cost_a / 1.5
        est_time_d = total_cost_d / speed if speed > 0 else total_cost_d / 1.5

        return {
            "success": success_a or success_d,
            "algorithm": "COMPARE",
            "task_id": task_id,
            "robot_code": robot_code,
            "robot_assigned": robot_assigned,
            "same_cost": abs(total_cost_a - total_cost_d) < 1e-4 if (success_a and success_d) else False,
            "a_star": {
                "success": success_a,
                "path": [{"x": p[0], "y": p[1]} for p in full_path_a],
                "pickup_segment": [{"x": p[0], "y": p[1]} for p in path_a1] if path_a1 else [],
                "delivery_segment": [{"x": p[0], "y": p[1]} for p in path_a2] if path_a2 else [],
                "distance_m": float(len(full_path_a) - 1) if full_path_a else 0.0,
                "cost": total_cost_a,
                "estimated_time_sec": round(est_time_a, 2),
                "nodes_count": len(full_path_a),
                "blocked_reason": msg_a1 if not path_a1 else (msg_a2 if not path_a2 else "")
            },
            "dijkstra": {
                "success": success_d,
                "path": [{"x": p[0], "y": p[1]} for p in full_path_d],
                "pickup_segment": [{"x": p[0], "y": p[1]} for p in path_d1] if path_d1 else [],
                "delivery_segment": [{"x": p[0], "y": p[1]} for p in path_d2] if path_d2 else [],
                "distance_m": float(len(full_path_d) - 1) if full_path_d else 0.0,
                "cost": total_cost_d,
                "estimated_time_sec": round(est_time_d, 2),
                "nodes_count": len(full_path_d),
                "blocked_reason": msg_d1 if not path_d1 else (msg_d2 if not path_d2 else "")
            }
        }

    # Single Algorithm (A_STAR or DIJKSTRA)
    if alg == "DIJKSTRA":
        p1, c1, dur1, msg1, exp1, expl1, rel1 = run_dijkstra_verbose(start_node, pickup_node, grid_map, obstacles, allow_diagonal)
        p2, c2, dur2, msg2, exp2, expl2, rel2 = run_dijkstra_verbose(pickup_node, dest_node, grid_map, obstacles, allow_diagonal)
    else:
        p1, c1, dur1, msg1, exp1, expl1, rel1 = run_a_star_verbose(start_node, pickup_node, grid_map, obstacles, allow_diagonal)
        p2, c2, dur2, msg2, exp2, expl2, rel2 = run_a_star_verbose(pickup_node, dest_node, grid_map, obstacles, allow_diagonal)

    if not p1 or not p2:
        fail_msg = msg1 if not p1 else msg2
        return {
            "success": False,
            "algorithm": alg,
            "task_id": task_id,
            "robot_code": robot_code,
            "robot_assigned": robot_assigned,
            "path": [],
            "pickup_segment": [],
            "delivery_segment": [],
            "distance_m": 0.0,
            "cost": 0.0,
            "estimated_time_sec": 0.0,
            "nodes_count": 0,
            "blocked_reason": f"No traversable route exists: {fail_msg}"
        }

    # Combine segments into complete route
    full_path = p1 + p2[1:]
    total_cost = c1 + c2
    speed = robot.max_speed if robot and robot.max_speed else 1.5
    est_time = total_cost / speed if speed > 0 else total_cost / 1.5

    # Path validation
    val_ok1, val_msg1 = validate_path(p1, grid_map, obstacles, allow_diagonal)
    val_ok2, val_msg2 = validate_path(p2, grid_map, obstacles, allow_diagonal)
    if not val_ok1 or not val_ok2:
        return {
            "success": False,
            "algorithm": alg,
            "task_id": task_id,
            "robot_code": robot_code,
            "robot_assigned": robot_assigned,
            "path": [],
            "blocked_reason": f"Route validation failed: {val_msg1 if not val_ok1 else val_msg2}"
        }

    path_json_list = [{"x": pt[0], "y": pt[1]} for pt in full_path]

    # If robot is assigned, update/create active RobotRoute record
    if robot:
        try:
            # Deactivate previous active routes for this robot
            db.query(RobotRoute).filter(
                RobotRoute.robot_id == robot.id,
                RobotRoute.status == "ACTIVE"
            ).update({"status": "REPLACED"})

            route_entry = RobotRoute(
                robot_id=robot.id,
                task_id=task.id,
                warehouse_id=task.warehouse_id,
                start_x=start_node[0],
                start_y=start_node[1],
                goal_x=dest_node[0],
                goal_y=dest_node[1],

                path_data=json.dumps(path_json_list),
                algorithm=alg,
                distance=float(len(full_path) - 1),
                cost=total_cost,
                status="ACTIVE"
            )
            db.add(route_entry)
            db.commit()

            # Broadcast for Digital Twin subscribers
            from backend.sync_broadcast import broadcaster
            broadcaster.broadcast_live(robot.warehouse_id, {
                "event_type": "ROUTE_CREATED",
                "entity_type": "robot",
                "entity_id": robot.robot_code,
                "data": {
                    "route_id": route_entry.id,
                    "task_id": task.id,
                    "path": path_json_list,
                    "cost": total_cost,
                    "algorithm": alg
                }
            })
            notifications.send_change_alert("ROUTE_UPDATED", {
                "robot_code": robot.robot_code,
                "task_id": task.id,
                "path": path_json_list,
                "cost": total_cost,
                "algorithm": alg
            })
        except Exception as ex:
            logger.warning("Failed to store RobotRoute or send notification: %s", ex)

    return {
        "success": True,
        "algorithm": alg,
        "task_id": task_id,
        "robot_code": robot_code,
        "robot_assigned": robot_assigned,
        "start_node": {"x": start_node[0], "y": start_node[1]},
        "pickup_node": {"x": pickup_node[0], "y": pickup_node[1]},
        "destination_node": {"x": dest_node[0], "y": dest_node[1]},
        "path": path_json_list,
        "pickup_segment": [{"x": p[0], "y": p[1]} for p in p1],
        "delivery_segment": [{"x": p[0], "y": p[1]} for p in p2],
        "distance_m": float(len(full_path) - 1),
        "cost": total_cost,
        "estimated_time_sec": round(est_time, 2),
        "nodes_count": len(full_path),
        "blocked_reason": ""
    }


def validate_and_reroute_robot_path(
    db: Session,
    robot_code: str,
    algorithm: str = "A_STAR"
) -> Dict[str, Any]:
    """
    Validates the active route for a robot against current obstacles.
    If blocked, automatically recalculates an alternative route.
    """
    robot = db.query(Robot).filter(Robot.robot_code == robot_code).first()
    if not robot:
        raise HTTPException(404, f"Robot {robot_code} not found.")

    if not robot.assigned_task_id:
        return {"status": "no_active_task", "rerouted": False, "message": "Robot has no assigned task."}

    # Retrieve current active route
    route = db.query(RobotRoute).filter(
        RobotRoute.robot_id == robot.id,
        RobotRoute.status == "ACTIVE"
    ).order_by(RobotRoute.created_at.desc()).first()

    if not route:
        # Generate new route for task
        res = get_operational_task_route(db, robot.assigned_task_id, robot.robot_code, algorithm)
        res["rerouted"] = True
        return res

    # Check active obstacles
    obs = db.query(WarehouseObstacle).filter(
        WarehouseObstacle.warehouse_id == robot.warehouse_id,
        WarehouseObstacle.active == True
    ).all()
    obstacles = set((o.x, o.y) for o in obs)

    current_path = json.loads(route.path_data) if route.path_data else []
    is_blocked = False
    for pt in current_path:
        if isinstance(pt, dict):
            coord = (pt.get("x"), pt.get("y"))
        elif isinstance(pt, (list, tuple)) and len(pt) >= 2:
            coord = (pt[0], pt[1])
        else:
            continue
        if coord in obstacles:
            is_blocked = True
            break

    if not is_blocked:
        return {
            "status": "valid",
            "rerouted": False,
            "message": "Current route remains valid and unblocked.",
            "route_id": route.id,
            "cost": route.cost
        }

    # Route is blocked -> Invalidate old route and recalculate
    logger.info("Active route for robot %s is blocked by obstacles. Recalculating route...", robot_code)
    route.status = "REPLANNED"
    db.commit()

    from backend.sync_broadcast import broadcaster
    broadcaster.broadcast_live(robot.warehouse_id, {
        "event_type": "ROUTE_REPLANNED",
        "entity_type": "robot",
        "entity_id": robot.robot_code,
        "data": {"old_route_id": route.id, "reason": "OBSTACLE_BLOCKED"}
    })

    new_route_res = get_operational_task_route(db, robot.assigned_task_id, robot.robot_code, algorithm)
    new_route_res["rerouted"] = True
    return new_route_res
