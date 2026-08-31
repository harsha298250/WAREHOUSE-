import logging
import json
import time
from datetime import datetime, UTC
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import UniqueConstraint

from backend.database import get_db
from backend.models import (
    WarehouseGridCell, WarehouseObstacle, RobotRoute, Robot, Task,
    AuditLedger, Warehouse
)
from backend.auth import get_current_user
from backend import audit_ledger
import heapq

logger = logging.getLogger("pathfinding")
router = APIRouter(prefix="/pathfinding", tags=["Pathfinding"])

class PathfindingPlanRequest(BaseModel):
    warehouse_id: str
    start_x: int
    start_y: int
    goal_x: int
    goal_y: int
    robot_id: Optional[int] = None
    algorithm: Optional[str] = "A_STAR" # A_STAR | DIJKSTRA | COMPARE

class TaskRouteRequest(BaseModel):
    task_id: int
    robot_code: Optional[str] = None
    algorithm: Optional[str] = "A_STAR" # A_STAR | DIJKSTRA | COMPARE

class RerouteRequest(BaseModel):
    robot_code: str
    algorithm: Optional[str] = "A_STAR"

class ObstacleCreateRequest(BaseModel):

    warehouse_id: str
    obstacle_type: str = "TEMPORARY_BLOCK" # RACK | WALL | EQUIPMENT | TEMPORARY_BLOCK | RESTRICTED_ZONE
    x: int
    y: int
    width: int = 1
    height: int = 1
    severity: str = "MEDIUM"

def initialize_warehouse_grid_if_empty(db: Session, warehouse_id: str):
    # Verify warehouse exists
    wh = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not wh:
        return

    exists = db.query(WarehouseGridCell).filter(WarehouseGridCell.warehouse_id == warehouse_id).first()
    if exists:
        return

    # Populate 12x5 layout
    cells = []
    for row in range(1, 6):
        for col in range(1, 13):
            cell_type = "FLOOR"
            traversable = True
            cost = 1.0

            # Map the exact layout of coordinates matching UI
            if row == 5 and col in (1, 2):
                cell_type = "RECEIVING"
            elif row == 5 and col in (3, 4):
                cell_type = "PACKING"
            elif row == 5 and col in (11, 12):
                cell_type = "CHARGING"
            elif (row in (1, 3)) and col >= 2 and col <= 11:
                cell_type = "RACK"
                traversable = False
                cost = 999.0 # Racks are non-traversable
            else:
                cell_type = "AISLE"
            
            cells.append(WarehouseGridCell(
                warehouse_id=warehouse_id,
                x=col,
                y=row,
                cell_type=cell_type,
                traversable=traversable,
                cost=cost
            ))
    db.add_all(cells)
    db.commit()


def run_a_star_verbose(start, goal, grid_map, obstacles=None, allow_diagonal=False):
    # start, goal: tuples (x, y)
    # grid_map: dict (x, y) -> {"traversable": bool, "cost": float}
    # obstacles: set of (x, y) coordinates of active temporary blocks
    if start == goal:
        return [start], 0.0, 0.0, "Success", 0, [start], 0

    if start not in grid_map:
        return None, 0.0, 0.0, f"Start location {start} is out of bounds.", 0, [], 0
    if goal not in grid_map:
        return None, 0.0, 0.0, f"Goal location {goal} is out of bounds.", 0, [], 0

    if not grid_map[start]["traversable"]:
        return None, 0.0, 0.0, f"Start cell {start} is non-traversable (type: {grid_map[start]['type']}).", 0, [], 0
    if not grid_map[goal]["traversable"]:
        gx, gy = goal
        cell_type = grid_map[goal].get("type")
        if cell_type in ("RACK", "SHELF", "CHARGING"):
            neighbors = [(gx + dx, gy + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
            if allow_diagonal:
                neighbors += [(gx + dx, gy + dy) for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]]
            traversable_neighbors = [n for n in neighbors if n in grid_map and grid_map[n]["traversable"]]
            if traversable_neighbors:
                goal = min(traversable_neighbors, key=lambda n: abs(start[0] - n[0]) + abs(start[1] - n[1]))
            else:
                return None, 0.0, 0.0, f"Goal cell {goal} is non-traversable (type: {cell_type}) and has no traversable neighbors.", 0, [], 0
        else:
            return None, 0.0, 0.0, f"Goal cell {goal} is non-traversable (type: {cell_type}).", 0, [], 0

    if obstacles and (start in obstacles or goal in obstacles):
        return None, 0.0, 0.0, f"Start or goal is blocked by a simulated temporary obstacle.", 0, [], 0

    t0 = time.perf_counter()
    open_set = []
    # heapq elements: (f_score, (x, y))
    heapq.heappush(open_set, (0.0, start))
    came_from = {}
    
    g_score = {start: 0.0}
    # Octile distance heuristic for diagonal, Manhattan for orthogonal
    if allow_diagonal:
        # Octile distance: dx + dy + (sqrt(2) - 2) * min(dx, dy)
        h_score = lambda p: float(abs(goal[0] - p[0]) + abs(goal[1] - p[1]) + (1.4142 - 2.0) * min(abs(goal[0] - p[0]), abs(goal[1] - p[1])))
    else:
        h_score = lambda p: float(abs(goal[0] - p[0]) + abs(goal[1] - p[1]))
        
    f_score = {start: h_score(start)}
    expanded_nodes = 0
    explored_nodes = []
    edge_relaxations = 0

    while open_set:
        current = heapq.heappop(open_set)[1]
        if current in explored_nodes:
            continue
        expanded_nodes += 1
        explored_nodes.append(current)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()

            t1 = time.perf_counter()
            elapsed_ms = (t1 - t0) * 1000.0
            return path, g_score[goal], elapsed_ms, "Success", expanded_nodes, explored_nodes, edge_relaxations

        x, y = current
        neighbors = []
        # Orthogonal moves (cost = 1.0)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbors.append(((x + dx, y + dy), 1.0))
        
        # Diagonal moves (cost = 1.4142)
        if allow_diagonal:
            for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
                neighbors.append(((x + dx, y + dy), 1.4142))

        for neighbor, move_weight in neighbors:
            if neighbor not in grid_map:
                continue
            if not grid_map[neighbor]["traversable"]:
                continue
            if obstacles and neighbor in obstacles:
                continue

            # Prevent diagonal corner-cutting through wall/rack cells or obstacles
            dx = neighbor[0] - x
            dy = neighbor[1] - y
            if dx != 0 and dy != 0:
                side1 = (x + dx, y)
                side2 = (x, y + dy)
                if side1 not in grid_map or not grid_map[side1]["traversable"] or (obstacles and side1 in obstacles):
                    continue
                if side2 not in grid_map or not grid_map[side2]["traversable"] or (obstacles and side2 in obstacles):
                    continue

            step_cost = grid_map[neighbor]["cost"] * move_weight
            tentative_g = g_score[current] + step_cost
            edge_relaxations += 1

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + h_score(neighbor)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    t1 = time.perf_counter()
    elapsed_ms = (t1 - t0) * 1000.0
    return None, 0.0, elapsed_ms, "No traversable route exists (Fully blocked environment).", expanded_nodes, explored_nodes, edge_relaxations


def run_a_star(start, goal, grid_map, obstacles=None, allow_diagonal=False):
    path, cost, elapsed, msg, expanded, explored, relax = run_a_star_verbose(start, goal, grid_map, obstacles, allow_diagonal)
    return path, cost, elapsed, msg, expanded


def run_dijkstra_verbose(start, goal, grid_map, obstacles=None, allow_diagonal=False):
    # Dijkstra is A* with heuristic = 0
    if start == goal:
        return [start], 0.0, 0.0, "Success", 0, [start], 0

    if start not in grid_map:
        return None, 0.0, 0.0, f"Start location {start} is out of bounds.", 0, [], 0
    if goal not in grid_map:
        return None, 0.0, 0.0, f"Goal location {goal} is out of bounds.", 0, [], 0

    if not grid_map[start]["traversable"]:
        return None, 0.0, 0.0, f"Start cell {start} is non-traversable (type: {grid_map[start]['type']}).", 0, [], 0
    if not grid_map[goal]["traversable"]:
        gx, gy = goal
        cell_type = grid_map[goal].get("type")
        if cell_type in ("RACK", "SHELF", "CHARGING"):
            neighbors = [(gx + dx, gy + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
            if allow_diagonal:
                neighbors += [(gx + dx, gy + dy) for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]]
            traversable_neighbors = [n for n in neighbors if n in grid_map and grid_map[n]["traversable"]]
            if traversable_neighbors:
                goal = min(traversable_neighbors, key=lambda n: abs(start[0] - n[0]) + abs(start[1] - n[1]))
            else:
                return None, 0.0, 0.0, f"Goal cell {goal} is non-traversable (type: {cell_type}) and has no traversable neighbors.", 0, [], 0
        else:
            return None, 0.0, 0.0, f"Goal cell {goal} is non-traversable (type: {cell_type}).", 0, [], 0

    if obstacles and (start in obstacles or goal in obstacles):
        return None, 0.0, 0.0, f"Start or goal is blocked by a simulated temporary obstacle.", 0, [], 0

    t0 = time.perf_counter()
    open_set = []
    # heapq elements: (distance, (x, y))
    heapq.heappush(open_set, (0.0, start))
    came_from = {}
    
    g_score = {start: 0.0}
    expanded_nodes = 0
    explored_nodes = []
    edge_relaxations = 0

    while open_set:
        dist, current = heapq.heappop(open_set)
        if current in explored_nodes:
            continue
        expanded_nodes += 1
        explored_nodes.append(current)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()

            t1 = time.perf_counter()
            elapsed_ms = (t1 - t0) * 1000.0
            return path, g_score[goal], elapsed_ms, "Success", expanded_nodes, explored_nodes, edge_relaxations

        x, y = current
        neighbors = []
        # Orthogonal moves (cost = 1.0)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbors.append(((x + dx, y + dy), 1.0))
        
        # Diagonal moves (cost = 1.4142)
        if allow_diagonal:
            for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
                neighbors.append(((x + dx, y + dy), 1.4142))

        for neighbor, move_weight in neighbors:
            if neighbor not in grid_map:
                continue
            if not grid_map[neighbor]["traversable"]:
                continue
            if obstacles and neighbor in obstacles:
                continue

            # Prevent diagonal corner-cutting through wall/rack cells or obstacles
            dx = neighbor[0] - x
            dy = neighbor[1] - y
            if dx != 0 and dy != 0:
                side1 = (x + dx, y)
                side2 = (x, y + dy)
                if side1 not in grid_map or not grid_map[side1]["traversable"] or (obstacles and side1 in obstacles):
                    continue
                if side2 not in grid_map or not grid_map[side2]["traversable"] or (obstacles and side2 in obstacles):
                    continue

            step_cost = grid_map[neighbor]["cost"] * move_weight
            tentative_g = g_score[current] + step_cost
            edge_relaxations += 1

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                heapq.heappush(open_set, (tentative_g, neighbor))

    t1 = time.perf_counter()
    elapsed_ms = (t1 - t0) * 1000.0
    return None, 0.0, elapsed_ms, "No traversable route exists (Fully blocked environment).", expanded_nodes, explored_nodes, edge_relaxations


def run_dijkstra(start, goal, grid_map, obstacles=None, allow_diagonal=False):
    path, cost, elapsed, msg, expanded, explored, relax = run_dijkstra_verbose(start, goal, grid_map, obstacles, allow_diagonal)
    return path, cost, elapsed, msg, expanded


def validate_path(path, grid_map, obstacles=None, allow_diagonal=False):
    if not path:
        return False, "Empty path"
    
    start = path[0]
    goal = path[-1]
    
    if start not in grid_map:
        return False, f"Start location {start} is out of bounds."
    if goal not in grid_map:
        return False, f"Goal location {goal} is out of bounds."
        
    if not grid_map[start]["traversable"]:
        return False, f"Start cell {start} is non-traversable."
    if not grid_map[goal]["traversable"]:
        return False, f"Goal cell {goal} is non-traversable."
        
    for i, cell in enumerate(path):
        if cell not in grid_map:
            return False, f"Cell {cell} is out of bounds."
        if not grid_map[cell]["traversable"]:
            return False, f"Cell {cell} is non-traversable."
        if obstacles and cell in obstacles:
            return False, f"Cell {cell} is blocked by obstacle."
            
        if i > 0:
            prev = path[i - 1]
            dx = abs(cell[0] - prev[0])
            dy = abs(cell[1] - prev[1])
            if allow_diagonal:
                if dx > 1 or dy > 1 or (dx == 0 and dy == 0):
                    return False, f"Non-consecutive path jump from {prev} to {cell}."
                if dx == 1 and dy == 1:
                    side1 = (prev[0] + (cell[0] - prev[0]), prev[1])
                    side2 = (prev[0], prev[1] + (cell[1] - prev[1]))
                    if side1 not in grid_map or not grid_map[side1]["traversable"] or (obstacles and side1 in obstacles):
                        return False, f"Path cuts through non-traversable corner cell at {side1}."
                    if side2 not in grid_map or not grid_map[side2]["traversable"] or (obstacles and side2 in obstacles):
                        return False, f"Path cuts through non-traversable corner cell at {side2}."
            else:
                if (dx + dy) != 1:
                    return False, f"Non-consecutive path jump from {prev} to {cell}."
                
    return True, "Path is valid"


# ---------------------------------------------------------------------------
# API Routing
# ---------------------------------------------------------------------------
@router.post("/plan", summary="Generate path using selected algorithm or run dynamic comparison")
def plan_path(
    payload: PathfindingPlanRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # Initialize grid if needed
    initialize_warehouse_grid_if_empty(db, payload.warehouse_id)

    # Load cells
    cells = db.query(WarehouseGridCell).filter(WarehouseGridCell.warehouse_id == payload.warehouse_id).all()
    grid_map = {
        (c.x, c.y): {"traversable": c.traversable, "cost": c.cost, "type": c.cell_type}
        for c in cells
    }

    # Load obstacles
    obs = db.query(WarehouseObstacle).filter(
        WarehouseObstacle.warehouse_id == payload.warehouse_id,
        WarehouseObstacle.active == True
    ).all()
    obstacles = set()
    for o in obs:
        for w in range(o.width):
            for h in range(o.height):
                obstacles.add((o.x + w, o.y + h))

    start = (payload.start_x, payload.start_y)
    goal = (payload.goal_x, payload.goal_y)

    # Load diagonal allowance setting from database
    from backend.settings import get_settings
    settings = get_settings(db)
    allow_diagonal = settings.get("allow_diagonal", False)

    alg = payload.algorithm or "A_STAR"

    if alg == "COMPARE":
        # Run both A* and Dijkstra verbose versions
        path_a, cost_a, duration_a, msg_a, exp_a, expl_a, rel_a = run_a_star_verbose(start, goal, grid_map, obstacles, allow_diagonal)
        path_d, cost_d, duration_d, msg_d, exp_d, expl_d, rel_d = run_dijkstra_verbose(start, goal, grid_map, obstacles, allow_diagonal)

        success = (path_a is not None) and (path_d is not None)
        same_cost = False
        if success:
            same_cost = abs(cost_a - cost_d) < 1e-4

        return {
            "success": success,
            "algorithm": "COMPARE",
            "same_cost": same_cost,
            "a_star": {
                "success": path_a is not None,
                "path": [{"x": p[0], "y": p[1]} for p in path_a] if path_a else [],
                "distance": float(len(path_a) - 1) if path_a else 0.0,
                "cost": cost_a,
                "planning_time": duration_a,
                "expanded_nodes": exp_a,
                "explored_nodes": [{"x": p[0], "y": p[1]} for p in expl_a],
                "edge_relaxations": rel_a,
                "blocked_reason": msg_a if not path_a else ""
            },
            "dijkstra": {
                "success": path_d is not None,
                "path": [{"x": p[0], "y": p[1]} for p in path_d] if path_d else [],
                "distance": float(len(path_d) - 1) if path_d else 0.0,
                "cost": cost_d,
                "planning_time": duration_d,
                "expanded_nodes": exp_d,
                "explored_nodes": [{"x": p[0], "y": p[1]} for p in expl_d],
                "edge_relaxations": rel_d,
                "blocked_reason": msg_d if not path_d else ""
            }
        }

    # Single algorithm execution
    if alg == "DIJKSTRA":
        path, cost, duration, msg, expanded_count, explored_list, edge_rel = run_dijkstra_verbose(start, goal, grid_map, obstacles, allow_diagonal)
    else:
        path, cost, duration, msg, expanded_count, explored_list, edge_rel = run_a_star_verbose(start, goal, grid_map, obstacles, allow_diagonal)

    if not path:
        return {
            "success": False,
            "algorithm": alg,
            "path": [],
            "distance": 0.0,
            "cost": 0.0,
            "steps": 0,
            "planning_time": duration,
            "blocked_reason": msg,
            "expanded_nodes": expanded_count,
            "explored_nodes": [],
            "edge_relaxations": edge_rel
        }

    is_valid, val_msg = validate_path(path, grid_map, obstacles, allow_diagonal)
    if not is_valid:
        return {
            "success": False,
            "algorithm": alg,
            "path": [],
            "distance": 0.0,
            "cost": 0.0,
            "steps": 0,
            "planning_time": duration,
            "blocked_reason": f"Path validation failed: {val_msg}",
            "expanded_nodes": expanded_count,
            "explored_nodes": [],
            "edge_relaxations": edge_rel
        }

    return {
        "success": True,
        "algorithm": alg,
        "path": [{"x": p[0], "y": p[1]} for p in path],
        "distance": float(len(path) - 1),
        "cost": cost,
        "steps": len(path) - 1,
        "planning_time": duration,
        "blocked_reason": "",
        "expanded_nodes": expanded_count,
        "explored_nodes": [{"x": p[0], "y": p[1]} for p in explored_list],
        "edge_relaxations": edge_rel
    }

@router.post("/task-route", summary="Generate operational route for a task (Robot -> Pickup -> Destination)")
def plan_task_route_endpoint(
    payload: TaskRouteRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    from backend.services.operational_pathfinding import get_operational_task_route
    return get_operational_task_route(
        db=db,
        task_id=payload.task_id,
        robot_identifier=payload.robot_code,
        algorithm=payload.algorithm or "A_STAR"
    )

@router.get("/task-route/{task_id}", summary="Get operational route for a task by task_id")
def get_task_route_by_id(
    task_id: int,
    robot_code: Optional[str] = None,
    algorithm: Optional[str] = "A_STAR",
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    from backend.services.operational_pathfinding import get_operational_task_route
    return get_operational_task_route(
        db=db,
        task_id=task_id,
        robot_identifier=robot_code,
        algorithm=algorithm or "A_STAR"
    )

@router.post("/reroute", summary="Validate active robot route against obstacles and recalculate if blocked")
def reroute_robot_endpoint(
    payload: RerouteRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    from backend.services.operational_pathfinding import validate_and_reroute_robot_path
    return validate_and_reroute_robot_path(
        db=db,
        robot_code=payload.robot_code,
        algorithm=payload.algorithm or "A_STAR"
    )


@router.get("/warehouse/{warehouse_id}/grid", summary="Retrieve grid matrix layout and active obstacles")
def get_warehouse_grid(
    warehouse_id: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    initialize_warehouse_grid_if_empty(db, warehouse_id)

    cells = db.query(WarehouseGridCell).filter(WarehouseGridCell.warehouse_id == warehouse_id).all()
    obs = db.query(WarehouseObstacle).filter(
        WarehouseObstacle.warehouse_id == warehouse_id,
        WarehouseObstacle.active == True
    ).all()

    return {
        "warehouse_id": warehouse_id,
        "width": 12,
        "height": 5,
        "cells": [
            {
                "x": c.x,
                "y": c.y,
                "cell_type": c.cell_type,
                "traversable": c.traversable,
                "cost": c.cost,
                "occupied": c.occupied
            } for c in cells
        ],
        "obstacles": [
            {
                "id": o.id,
                "obstacle_type": o.obstacle_type,
                "x": o.x,
                "y": o.y,
                "width": o.width,
                "height": o.height,
                "severity": o.severity
            } for o in obs
        ]
    }

@router.post("/obstacles", summary="Simulate temporary blocking obstacles")
def create_obstacle(
    payload: ObstacleCreateRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role not in ("admin", "manager"):
        raise HTTPException(403, "Insufficient permissions")

    # Verify grid cell exists
    initialize_warehouse_grid_if_empty(db, payload.warehouse_id)
    cell = db.query(WarehouseGridCell).filter(
        WarehouseGridCell.warehouse_id == payload.warehouse_id,
        WarehouseGridCell.x == payload.x,
        WarehouseGridCell.y == payload.y
    ).first()

    if not cell:
        raise HTTPException(404, "Target coordinates out of bounds")

    o = WarehouseObstacle(
        warehouse_id=payload.warehouse_id,
        obstacle_type=payload.obstacle_type,
        x=payload.x,
        y=payload.y,
        width=payload.width,
        height=payload.height,
        active=True,
        severity=payload.severity
    )
    db.add(o)

    # Log audit
    audit_ledger.append_entry(db, "OBSTACLE_CREATED", {
        "warehouse_id": payload.warehouse_id,
        "x": payload.x,
        "y": payload.y,
        "obstacle_type": payload.obstacle_type
    })
    db.commit()
    db.refresh(o)
    return {"status": "created", "obstacle_id": o.id}

@router.delete("/obstacles/{obstacle_id}", summary="Remove obstacle from spatial mapping grid")
def remove_obstacle(
    obstacle_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role not in ("admin", "manager"):
        raise HTTPException(403, "Insufficient permissions")

    o = db.query(WarehouseObstacle).filter(WarehouseObstacle.id == obstacle_id).first()
    if not o:
        raise HTTPException(404, "Obstacle not found")

    o.active = False
    
    # Log audit
    audit_ledger.append_entry(db, "OBSTACLE_REMOVED", {
        "warehouse_id": o.warehouse_id,
        "x": o.x,
        "y": o.y,
        "obstacle_id": o.id
    })
    db.commit()
    return {"status": "removed", "obstacle_id": obstacle_id}

@router.get("/robots/{robot_id}/route", summary="Get current active route mapping")
def get_robot_route(
    robot_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    r = db.query(Robot).filter(Robot.id == robot_id).first()
    if not r:
        raise HTTPException(404, "Robot not found")

    route = db.query(RobotRoute).filter(
        RobotRoute.robot_id == robot_id,
        RobotRoute.status == "ACTIVE"
    ).order_by(RobotRoute.created_at.desc()).first()

    if not route:
        return {"status": "no_route", "route": []}

    return {
        "id": route.id,
        "robot_id": route.robot_id,
        "task_id": route.task_id,
        "start_x": route.start_x,
        "start_y": route.start_y,
        "goal_x": route.goal_x,
        "goal_y": route.goal_y,
        "path": json.loads(route.path_data),
        "distance": route.distance,
        "cost": route.cost,
        "status": route.status
    }

@router.get("/robots/{robot_id}/route/history", summary="Get historical routes planned for analytics comparison")
def get_robot_route_history(
    robot_id: int,
    limit: int = 50,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    routes = db.query(RobotRoute).filter(
        RobotRoute.robot_id == robot_id
    ).order_by(RobotRoute.created_at.desc()).limit(limit).all()

    return [
        {
            "id": r.id,
            "task_id": r.task_id,
            "start": (r.start_x, r.start_y),
            "goal": (r.goal_x, r.goal_y),
            "algorithm": r.algorithm,
            "distance": r.distance,
            "cost": r.cost,
            "status": r.status,
            "created_at": r.created_at
        } for r in routes
    ]


class GridCellUpdateRequest(BaseModel):
    x: int
    y: int
    cell_type: str
    traversable: bool
    cost: float

@router.put("/warehouse/{warehouse_id}/grid/cell", summary="Update specific grid cell layout properties")
def update_grid_cell(
    warehouse_id: str,
    payload: GridCellUpdateRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role not in ("admin", "manager"):
        raise HTTPException(403, "Insufficient permissions")

    initialize_warehouse_grid_if_empty(db, warehouse_id)
    cell = db.query(WarehouseGridCell).filter(
        WarehouseGridCell.warehouse_id == warehouse_id,
        WarehouseGridCell.x == payload.x,
        WarehouseGridCell.y == payload.y
    ).first()

    if not cell:
        raise HTTPException(404, "Grid cell not found")

    cell.cell_type = payload.cell_type
    # Enforce untraversable rules for RACK and WALL
    if payload.cell_type in ("RACK", "WALL"):
        cell.traversable = False
        cell.cost = 999.0
    else:
        cell.traversable = payload.traversable
        cell.cost = payload.cost
    db.commit()

    # Log audit entry
    from backend import audit_ledger
    audit_ledger.append_entry(db, "GRID_CELL_UPDATED", {
        "warehouse_id": warehouse_id,
        "x": payload.x,
        "y": payload.y,
        "cell_type": payload.cell_type,
        "traversable": payload.traversable,
        "cost": payload.cost
    })
    db.commit()
    return {"status": "updated", "x": payload.x, "y": payload.y}
