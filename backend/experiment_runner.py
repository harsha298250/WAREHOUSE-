import os
import time
import json
import logging
import tempfile
import statistics
import random
from datetime import datetime, timedelta, UTC
from typing import Dict, Any, List
from unittest.mock import patch

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from backend.models import (
    Base, Warehouse, WarehouseLocation, WarehouseGridCell, WarehouseObstacle,
    Item, Inventory, Order, OrderItem, OrderEvent, Task, TaskEvent, Robot,
    RobotRoute, RobotTelemetryEvent, SimulationEvent
)
from backend import analytics_engine as analytics
from backend.routers.robots import execute_simulation_tick, transition_robot_status, calculate_manhattan_distance

logger = logging.getLogger("warehouse.experiment_runner")

# Check if OR-Tools is installed
or_tools_available = False
try:
    from ortools.sat.python import cp_model
    or_tools_available = True
except ImportError:
    pass


def run_ortools_scheduler_on_db(db, warehouse_id: str):
    """Executes a real OR-Tools CP-SAT task-robot assignment on the temporary database state."""
    # Find active available robots
    robots = db.query(Robot).filter(
        Robot.warehouse_id == warehouse_id,
        Robot.enabled == True,
        Robot.assigned_task_id.is_(None),
        ~Robot.status.in_(["OFFLINE", "FAILED", "MAINTENANCE", "CHARGING"])
    ).all()

    # Find unassigned tasks
    tasks = db.query(Task).filter(
        Task.warehouse_id == warehouse_id,
        Task.status.in_(["QUEUED", "PRIORITIZED", "FAILED"])
    ).order_by(Task.priority_score.desc()).all()

    if not robots or not tasks:
        return

    num_robots = len(robots)
    num_tasks = min(len(tasks), num_robots * 2)  # Limit search depth
    tasks = tasks[:num_tasks]

    # Calculate distance matrix (cost matrix)
    distance_matrix = []
    for r_idx, r in enumerate(robots):
        row = []
        for t_idx, t in enumerate(tasks):
            # Fetch target source location
            loc = db.query(WarehouseLocation).filter(WarehouseLocation.id == t.source_location_id).first()
            tx = loc.x if loc else 1.0
            ty = loc.y if loc else 1.0
            dist = calculate_manhattan_distance(r.current_x, r.current_y, tx, ty)
            
            # Apply battery warnings penalty
            bat_penalty = 50.0 if r.battery_level < 30.0 else 0.0
            cost = int(dist + bat_penalty)
            row.append(cost)
        distance_matrix.append(row)

    if not or_tools_available:
        # Fallback to simple greedy heuristic assignment
        for t in tasks:
            best_robot = None
            min_cost = float('inf')
            for r in robots:
                if r.assigned_task_id is None:
                    dist = calculate_manhattan_distance(r.current_x, r.current_y, 0, 0)
                    if dist < min_cost:
                        min_cost = dist
                        best_robot = r
            if best_robot:
                best_robot.assigned_task_id = t.id
                best_robot.status = "ASSIGNED"
                t.assigned_robot_id = best_robot.robot_code
                t.status = "ASSIGNED"
        return

    try:
        model = cp_model.CpModel()
        x = {}
        for r_idx in range(num_robots):
            for t_idx in range(num_tasks):
                x[r_idx, t_idx] = model.NewBoolVar(f'x_{r_idx}_{t_idx}')

        # Each task is assigned to at most one robot
        for t_idx in range(num_tasks):
            model.Add(sum(x[r_idx, t_idx] for r_idx in range(num_robots)) <= 1)

        # Each robot gets at most 1 task assigned
        for r_idx in range(num_robots):
            model.Add(sum(x[r_idx, t_idx] for t_idx in range(num_tasks)) <= 1)

        # Objective: Minimize total path routing cost weight
        model.Minimize(
            sum(x[r_idx, t_idx] * distance_matrix[r_idx][t_idx]
                for r_idx in range(num_robots)
                for t_idx in range(num_tasks))
        )

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 1.0
        status = solver.Solve(model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            for r_idx in range(num_robots):
                for t_idx in range(num_tasks):
                    if solver.BooleanValue(x[r_idx, t_idx]):
                        r = robots[r_idx]
                        t = tasks[t_idx]
                        r.assigned_task_id = t.id
                        r.status = "ASSIGNED"
                        t.assigned_robot_id = r.robot_code
                        t.status = "ASSIGNED"
    except Exception as e:
        logger.error("OR-Tools scheduling solver failed during simulation loop: %s", e)


def run_heuristic_scheduler_on_db(db, warehouse_id: str):
    """Executes standard priority-greedy task assignments on the temporary database state."""
    robots = db.query(Robot).filter(
        Robot.warehouse_id == warehouse_id,
        Robot.enabled == True,
        Robot.assigned_task_id.is_(None),
        ~Robot.status.in_(["OFFLINE", "FAILED", "MAINTENANCE", "CHARGING"])
    ).all()

    tasks = db.query(Task).filter(
        Task.warehouse_id == warehouse_id,
        Task.status.in_(["QUEUED", "PRIORITIZED", "FAILED"])
    ).order_by(Task.priority_score.desc()).all()

    if not robots or not tasks:
        return

    for task in tasks:
        # Find nearest eligible robot
        selected_robot = None
        min_cost = float("inf")
        source_loc = db.query(WarehouseLocation).filter(WarehouseLocation.id == task.source_location_id).first()
        tx = source_loc.x if source_loc else 1.0
        ty = source_loc.y if source_loc else 1.0

        for r in robots:
            if r.assigned_task_id is not None:
                continue
            if r.battery_level < 10.0 or (r.battery_level < 25.0 and task.priority != "CRITICAL"):
                continue
            dist = calculate_manhattan_distance(r.current_x, r.current_y, tx, ty)
            bat_penalty = 50.0 if r.battery_level < 30.0 else 0.0
            cost = dist + bat_penalty
            if cost < min_cost:
                min_cost = cost
                selected_robot = r

        if selected_robot:
            selected_robot.assigned_task_id = task.id
            selected_robot.status = "ASSIGNED"
            task.assigned_robot_id = selected_robot.robot_code
            task.status = "ASSIGNED"


def execute_single_repetition(
    prod_db_session,
    warehouse_id: str,
    scenario_type: str,
    config: Dict[str, Any],
    algorithm_name: str,
    seed: int
) -> Dict[str, Any]:
    """Runs a single simulation run inside an isolated temporary SQLite database."""
    # 1. Setup isolated SQLite file
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    temp_engine = create_engine(f"sqlite:///{db_path}")
    TempSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=temp_engine)

    # 2. Build mirrored schema
    Base.metadata.create_all(bind=temp_engine)
    temp_db = TempSessionLocal()

    try:
        # 3. Seed configurations
        # Warehouses & Locations
        wh = prod_db_session.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
        if not wh:
            wh = Warehouse(id=warehouse_id, name="Test Warehouse")
        temp_db.add(Warehouse(id=wh.id, name=wh.name, location=wh.location))
        
        locs = prod_db_session.query(WarehouseLocation).filter(WarehouseLocation.warehouse_id == warehouse_id).all()
        for l in locs:
            temp_db.add(WarehouseLocation(
                id=l.id, warehouse_id=l.warehouse_id, x=l.x, y=l.y,
                location_type=l.location_type, zone=l.zone, aisle=l.aisle,
                rack=l.rack, shelf=l.shelf
            ))

        # Grid layout & obstacles
        cells = prod_db_session.query(WarehouseGridCell).filter(WarehouseGridCell.warehouse_id == warehouse_id).all()
        for c in cells:
            temp_db.add(WarehouseGridCell(
                warehouse_id=c.warehouse_id, x=c.x, y=c.y, traversable=c.traversable,
                cost=c.cost, cell_type=c.cell_type
            ))
            
        obstacles = prod_db_session.query(WarehouseObstacle).filter(WarehouseObstacle.warehouse_id == warehouse_id).all()
        for o in obstacles:
            temp_db.add(WarehouseObstacle(
                id=o.id, warehouse_id=o.warehouse_id, x=o.x, y=o.y, width=o.width, height=o.height, active=o.active
            ))

        # Seed custom scenario blocked layout cells if configured
        warehouse_params = config.get("warehouse", {})
        blocked_cells = warehouse_params.get("blocked_cells", [])
        for bc in blocked_cells:
            # Mark cell traversable = False
            cell = temp_db.query(WarehouseGridCell).filter(
                WarehouseGridCell.warehouse_id == warehouse_id,
                WarehouseGridCell.x == bc[0],
                WarehouseGridCell.y == bc[1]
            ).first()
            if cell:
                cell.traversable = False

        # Items
        items = prod_db_session.query(Item).all()
        for i in items:
            temp_db.add(Item(
                id=i.id, name=i.name, sku=i.sku, unit_cost=i.unit_cost,
                safety_stock=i.safety_stock, reorder_threshold=i.reorder_threshold
            ))
        temp_db.commit()

        # Seed initial inventory levels
        inventory_params = config.get("inventory", {})
        initial_stock = inventory_params.get("initial_stock_units", 100)
        reorder_th = inventory_params.get("reorder_threshold_units", 20)
        
        # Override item reorder threshold settings if configured
        for i in items:
            inv = Inventory(
                warehouse_id=warehouse_id, item_id=i.id,
                on_hand=initial_stock, reserved=0, available=initial_stock, damaged=0
            )
            temp_db.add(inv)
            i.reorder_threshold = reorder_th
        temp_db.commit()

        # Robots
        robot_params = config.get("robots", {})
        robot_count = robot_params.get("robot_count", 3)
        initial_battery = robot_params.get("initial_battery_pct", 100.0)
        robot_speed = robot_params.get("robot_speed", 1.0)
        
        for idx in range(1, robot_count + 1):
            robot_code = f"ROB-S{idx}"
            # Scatter coordinates slightly around start
            temp_db.add(Robot(
                robot_code=robot_code, name=f"Sim Bot {idx}", warehouse_id=warehouse_id,
                status="AVAILABLE", battery_level=initial_battery, max_speed=robot_speed,
                current_x=1.0 + idx, current_y=1.0, total_tasks_completed=0, total_distance=0.0
            ))
        temp_db.commit()

        # Orders & Tasks
        demand_params = config.get("demand", {})
        order_volume = demand_params.get("order_volume", 5)
        order_arrival_rate = demand_params.get("order_arrival_rate", 50)  # Ticks between new orders

        # Seed initial orders
        for idx in range(1, order_volume + 1):
            order_id = f"ORD-S{idx}"
            temp_db.add(Order(
                id=order_id, customer_ref=f"Sim Customer {idx}", warehouse_id=warehouse_id,
                status="CREATED", priority="MEDIUM"
            ))
            
            # Select random item
            rand_item = random.choice(items)
            temp_db.add(OrderItem(order_id=order_id, item_id=rand_item.id, requested_qty=1))
            
            # Create corresponding PICK task
            # Find eligible source storage location
            src_loc = temp_db.query(WarehouseLocation).filter(
                WarehouseLocation.warehouse_id == warehouse_id,
                WarehouseLocation.location_type == "STORAGE"
            ).first()
            dest_loc = temp_db.query(WarehouseLocation).filter(
                WarehouseLocation.warehouse_id == warehouse_id,
                WarehouseLocation.location_type == "PACKING"
            ).first()

            temp_db.add(Task(
                task_number=f"TSK-S{idx}", warehouse_id=warehouse_id, task_type="PICK",
                priority="MEDIUM", priority_score=10, status="QUEUED", order_id=order_id,
                product_id=rand_item.id, source_location_id=src_loc.id if src_loc else "L-01",
                destination_location_id=dest_loc.id if dest_loc else "L-02",
                requested_quantity=1, completed_quantity=0
            ))
        temp_db.commit()

        # 4. Simulation loop parameterization
        sim_params = config.get("simulation", {})
        duration_ticks = sim_params.get("duration_ticks", 500)
        random.seed(seed)

        # 5. Patch notifications during running
        with patch("backend.notifications.send_change_alert", return_value=True):
            for tick in range(1, duration_ticks + 1):
                # A. Handle dynamic arrival of new orders
                if tick % order_arrival_rate == 0:
                    new_idx = order_volume + (tick // order_arrival_rate)
                    order_id = f"ORD-S{new_idx}"
                    temp_db.add(Order(
                        id=order_id, customer_ref=f"Sim Burst Cust {new_idx}", warehouse_id=warehouse_id,
                        status="CREATED", priority="MEDIUM"
                    ))
                    rand_item = random.choice(items)
                    temp_db.add(OrderItem(order_id=order_id, item_id=rand_item.id, requested_qty=1))
                    
                    src_loc = temp_db.query(WarehouseLocation).filter(
                        WarehouseLocation.warehouse_id == warehouse_id,
                        WarehouseLocation.location_type == "STORAGE"
                    ).first()
                    dest_loc = temp_db.query(WarehouseLocation).filter(
                        WarehouseLocation.warehouse_id == warehouse_id,
                        WarehouseLocation.location_type == "PACKING"
                    ).first()

                    temp_db.add(Task(
                        task_number=f"TSK-S{new_idx}", warehouse_id=warehouse_id, task_type="PICK",
                        priority="MEDIUM", priority_score=10, status="QUEUED", order_id=order_id,
                        product_id=rand_item.id, source_location_id=src_loc.id if src_loc else "L-01",
                        destination_location_id=dest_loc.id if dest_loc else "L-02",
                        requested_quantity=1, completed_quantity=0
                    ))
                    temp_db.commit()

                # B. Failure injection: Robot failures
                failure_params = config.get("failures", {})
                if failure_params.get("enabled", False):
                    fail_tick = failure_params.get("failure_tick", 100)
                    fail_robot_code = "ROB-S1"
                    if tick == fail_tick:
                        robot_to_fail = temp_db.query(Robot).filter(Robot.robot_code == fail_robot_code).first()
                        if robot_to_fail:
                            robot_to_fail.status = "FAILED"
                            # Requeue task
                            if robot_to_fail.assigned_task_id:
                                t = temp_db.query(Task).filter(Task.id == robot_to_fail.assigned_task_id).first()
                                if t:
                                    t.status = "FAILED"  # Marks it failed so scheduler picks it up again
                                robot_to_fail.assigned_task_id = None
                            temp_db.commit()

                # C. Automated scheduling strategy assignments
                if algorithm_name == "OR_TOOLS_ASSIGNMENT":
                    run_ortools_scheduler_on_db(temp_db, warehouse_id)
                else:
                    run_heuristic_scheduler_on_db(temp_db, warehouse_id)
                temp_db.commit()

                # D. Route path planning strategies Selection
                # Mapping A_STAR_BASELINE vs A_STAR_CONGESTION_AWARE
                routing_strategy = "A_STAR_BASELINE"
                if algorithm_name == "A_STAR_CONGESTION_AWARE":
                    routing_strategy = "A_STAR_CONGESTION_AWARE"

                execute_simulation_tick(temp_db, routing_strategy=routing_strategy)
                temp_db.commit()

        # 6. Extract operational KPIs
        # Cycle time: use standard period from start of sim to now
        start_dt = datetime.now(UTC).replace(tzinfo=None) - timedelta(hours=2)
        end_dt = datetime.now(UTC).replace(tzinfo=None) + timedelta(hours=1)
        
        ord_metrics = analytics.compute_order_analytics(temp_db, warehouse_id, start_dt, end_dt)
        task_metrics = analytics.compute_task_analytics(temp_db, warehouse_id, start_dt, end_dt)
        robot_metrics = analytics.compute_robot_analytics(temp_db, warehouse_id, start_dt, end_dt)
        routing_metrics = analytics.compute_routing_analytics(temp_db, warehouse_id, start_dt, end_dt)

        extracted_kpis = {
            "orders_completed": ord_metrics["throughput"]["value"],
            "order_completion_rate": ord_metrics["completion_rate"]["value"],
            "avg_cycle_time_hours": ord_metrics["avg_cycle_time_hours"]["value"],
            "tasks_created": task_metrics["tasks_created"]["value"],
            "tasks_completed": task_metrics["tasks_completed"]["value"],
            "tasks_failed": task_metrics["tasks_failed"]["value"],
            "avg_queue_time_minutes": task_metrics["avg_queue_time_minutes"]["value"],
            "avg_task_duration_minutes": task_metrics["avg_duration_minutes"]["value"],
            "robot_fleet_size": robot_metrics["fleet_size"]["value"],
            "avg_robot_utilization": robot_metrics["avg_utilization"]["value"],
            "route_count": routing_metrics["route_count"]["value"],
            "replanning_count": routing_metrics["replanning_count"]["value"],
            "collision_events": routing_metrics["collision_events"]["value"]
        }

        temp_db.close()
        return {
            "status": "COMPLETED",
            "metrics": extracted_kpis
        }

    except Exception as run_err:
        logger.error("Simulation run execution failed: %s", run_err)
        if temp_db:
            temp_db.close()
        return {
            "status": "FAILED",
            "error": str(run_err)
        }

    finally:
        # Clean up database file
        temp_engine.dispose()
        try:
            os.close(db_fd)
            os.remove(db_path)
        except Exception:
            pass


def aggregate_experiment_runs(run_metrics_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculates mean, median, min, max, stddev stats across repetition runs."""
    if not run_metrics_list:
        return {}

    keys = run_metrics_list[0].keys()
    aggregated = {}

    for k in keys:
        values = [r[k] for r in run_metrics_list if r[k] is not None]
        if not values:
            aggregated[k] = {"mean": None, "median": None, "min": None, "max": None, "stddev": None, "count": 0}
            continue

        mean = round(statistics.mean(values), 2)
        median = round(statistics.median(values), 2)
        minimum = min(values)
        maximum = max(values)
        stddev = round(statistics.stdev(values), 2) if len(values) > 1 else 0.0

        aggregated[k] = {
            "mean": mean,
            "median": median,
            "min": minimum,
            "max": maximum,
            "stddev": stddev,
            "count": len(values)
        }

    return aggregated
