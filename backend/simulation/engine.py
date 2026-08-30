import json
import logging
import math
import random
import time
from datetime import datetime, timedelta, UTC
from typing import Dict, Any, List, Tuple, Optional, Set

import simpy
from sqlalchemy.orm import Session

from backend.models import (
    Warehouse, WarehouseLocation, WarehouseGridCell, WarehouseObstacle,
    Robot, Task, Order, OrderItem
)
from backend.routers.pathfinding import run_a_star
from backend.simulation.models import (
    SimulatedRobot, SimulatedTask, SimulatedOrder,
    SimulatedLocation, SimulatedGridCell, SimulatedObstacle
)
from backend.simulation.processes import (
    order_arrival_process, scheduler_process, robot_process
)

logger = logging.getLogger("warehouse.simulation.engine")

# Check if OR-Tools is installed
or_tools_available = False
try:
    from ortools.sat.python import cp_model
    or_tools_available = True
except ImportError:
    pass


class SimulationEngine:
    def __init__(
        self,
        db: Session,
        warehouse_id: str,
        mode: str,
        duration: float,  # in simulation minutes
        random_seed: int,
        config: Dict[str, Any],
        created_by: str = "system"
    ):
        self.db = db
        self.warehouse_id = warehouse_id
        self.mode = mode
        self.duration = duration
        self.random_seed = random_seed
        self.config = config
        self.created_by = created_by

        # Seed generators for reproducibility
        self.rng = random.Random(random_seed)

        # In-memory detached snapshot entities
        self.locations: Dict[str, SimulatedLocation] = {}
        self.grid_cells: Dict[Tuple[int, int], SimulatedGridCell] = {}
        self.obstacles: Set[Tuple[int, int]] = set()
        self.robots: Dict[str, SimulatedRobot] = {}
        self.tasks: Dict[int, SimulatedTask] = {}
        self.orders: Dict[str, SimulatedOrder] = {}

        # Charging resources
        self.charging_stations: List[SimulatedLocation] = []
        self.charging_resource: Optional[simpy.Resource] = None

        # Reservations tracker: (x, y, tick) -> robot_id
        self.reservations: Dict[Tuple[Tuple[int, int], int], int] = {}

        # Historical order queue (for Historical Replay mode)
        self.historical_orders: List[Dict[str, Any]] = []

        # Simulation metrics & event logging
        self.event_log: List[Dict[str, Any]] = []
        self.metrics: Dict[str, Any] = {
            "charging_queue_time": 0.0,
            "charging_sessions": 0,
            "charging_duration": 0.0,
            "A_star_calls": 0,
            "A_star_successes": 0,
            "A_star_failures": 0,
            "total_replans": 0,
            "total_conflicts": 0,
            "total_deadlocks": 0
        }

        # Data provenance record
        self.provenance: Dict[str, str] = {
            "warehouse_map": "REAL PROJECT DATA",
            "historical_orders": "REAL DATA" if mode == "HISTORICAL_REPLAY" else "GENERATED SIMULATION INPUT",
            "robot_count": "PROJECT CONFIGURATION",
            "robot_speed": "PROJECT CONFIGURATION",
            "battery_consumption": "SIMULATION PARAMETER",
            "charging_duration": "SIMULATION PARAMETER",
            "picking_duration": "SIMULATION PARAMETER"
        }

        self.mean_picking_time = config.get("simulation", {}).get("picking_duration", 3.0)

    def load_snapshot(self):
        """Loads read-only detached configurations from Postgres db into in-memory entities."""
        # 1. Load Warehouse & Locations
        wh = self.db.query(Warehouse).filter(Warehouse.id == self.warehouse_id).first()
        if not wh:
            raise ValueError(f"Warehouse {self.warehouse_id} not found in database.")

        locs = self.db.query(WarehouseLocation).filter(WarehouseLocation.warehouse_id == self.warehouse_id).all()
        for l in locs:
            sim_loc = SimulatedLocation(l.id, float(l.x), float(l.y), l.location_type)
            self.locations[l.id] = sim_loc
            if l.location_type == "CHARGING":
                self.charging_stations.append(sim_loc)

        # 2. Load Grid Cells
        cells = self.db.query(WarehouseGridCell).filter(WarehouseGridCell.warehouse_id == self.warehouse_id).all()
        for c in cells:
            # Map cost rules
            cost = 1.0
            if c.cell_type == "RESTRICTED" or c.restricted:
                cost = 10.0
            elif c.cell_type == "HIGH_RISK":
                cost = 5.0
            self.grid_cells[(c.x, c.y)] = SimulatedGridCell(c.x, c.y, c.traversable, cost, c.cell_type)

        # Apply custom layout blocks from config if present
        blocked_cells = self.config.get("warehouse", {}).get("blocked_cells", [])
        for bc in blocked_cells:
            cell_coord = (bc[0], bc[1])
            if cell_coord in self.grid_cells:
                self.grid_cells[cell_coord].traversable = False

        # 3. Load Obstacles
        obs = self.db.query(WarehouseObstacle).filter(
            WarehouseObstacle.warehouse_id == self.warehouse_id,
            WarehouseObstacle.active == True
        ).all()
        for o in obs:
            for w in range(o.width):
                for h in range(o.height):
                    self.obstacles.add((o.x + w, o.y + h))

        # 4. Load/Configure Robots
        robot_params = self.config.get("robots", {})
        robot_count = robot_params.get("robot_count", 3)
        initial_battery = robot_params.get("initial_battery_pct", 100.0)
        robot_speed = robot_params.get("robot_speed", 1.0)

        # Fetch real robots from db as template to maintain matching counts or codes if preferred
        real_robots = self.db.query(Robot).filter(Robot.warehouse_id == self.warehouse_id, Robot.enabled == True).all()
        
        for idx in range(1, robot_count + 1):
            robot_code = real_robots[idx-1].robot_code if idx <= len(real_robots) else f"ROB-S{idx}"
            # Scatter spawn points to avoid initial coordinate overlaps using real robot coordinates if possible
            if idx <= len(real_robots):
                spawn_x = float(real_robots[idx-1].current_x)
                spawn_y = float(real_robots[idx-1].current_y)
            else:
                spawn_x = 1.0 + idx
                spawn_y = 5.0  # docks / charging row (fully traversable)
            self.robots[robot_code] = SimulatedRobot(
                robot_id=idx,
                robot_code=robot_code,
                warehouse_id=self.warehouse_id,
                x=spawn_x,
                y=spawn_y,
                status="AVAILABLE",
                battery_level=initial_battery,
                max_speed=robot_speed
            )

        # 5. Load Historical Data if requested
        if self.mode == "HISTORICAL_REPLAY":
            # Fetch completed real orders in the last e.g. 10 days for historical arrival pattern modeling
            start_date = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=10)
            hist_orders = self.db.query(Order).filter(
                Order.warehouse_id == self.warehouse_id,
                Order.status == "COMPLETED",
                Order.created_at >= start_date
            ).order_by(Order.created_at.asc()).all()

            if hist_orders:
                start_ts = hist_orders[0].created_at
                for ho in hist_orders:
                    # Time offset from the start of historical timeline (in minutes)
                    offset_min = (ho.created_at - start_ts).total_seconds() / 60.0
                    order_items = self.db.query(OrderItem).filter(OrderItem.order_id == ho.id).all()
                    
                    self.historical_orders.append({
                        "order_id": ho.id,
                        "customer_ref": ho.customer_ref,
                        "priority": ho.priority or "MEDIUM",
                        "arrival_delay_minutes": offset_min,
                        "items": [{"item_id": oi.item_id, "requested_qty": oi.requested_qty} for oi in order_items]
                    })
            else:
                logger.warning("No real historical orders found. Falling back to synthetic generations.")
                self.mode = "OFFLINE_SNAPSHOT"

    def run(self) -> Dict[str, Any]:
        """Runs SimPy environment execution processes and aggregates metrics results."""
        self.load_snapshot()

        # Initialize SimPy
        self.env = simpy.Environment()

        # Set charging resource bottlenecks
        charging_capacity = max(1, len(self.charging_stations))
        self.charging_resource = simpy.Resource(self.env, capacity=charging_capacity)

        # Log startup
        self.log_event("SIMULATION_STARTED", details={"duration": self.duration, "seed": self.random_seed})

        # Register arrival generator process
        self.env.process(order_arrival_process(self.env, self))

        # Register periodic task scheduler process
        self.env.process(scheduler_process(self.env, self))

        # Register individual robot lifecycles
        for r_code, r_obj in self.robots.items():
            self.env.process(robot_process(self.env, r_obj, self))

        # Start clock
        start_time_wall = time.time()
        self.env.run(until=self.duration)
        end_time_wall = time.time()

        # Calculate final KPIs
        kpis = self.calculate_aggregate_kpis(end_time_wall - start_time_wall)
        self.log_event("SIMULATION_COMPLETED", details={"wall_clock_seconds": end_time_wall - start_time_wall})

        return kpis

    def create_simulated_order(self, order_data: Dict[str, Any]):
        """Triggered dynamically via arrival processes to construct simulated order and picking tasks."""
        order_id = order_data["order_id"]
        customer_ref = order_data["customer_ref"]
        priority = order_data["priority"]

        sim_order = SimulatedOrder(
            order_id=order_id,
            customer_ref=customer_ref,
            warehouse_id=self.warehouse_id,
            status="CREATED",
            priority=priority
        )
        sim_order.created_at_sim = self.env.now

        # Load items (either from historical replay parameters or random choice)
        items_payload = order_data.get("items")
        if not items_payload:
            # Fallback choice
            items_payload = [{"item_id": "ITM-SIM-01", "requested_qty": 1}]
            
        sim_order.items = items_payload
        self.orders[order_id] = sim_order
        self.log_event("ORDER_ARRIVED", task=None, details={"order_id": order_id, "priority": priority})

        # Create corresponding pick task
        task_id = len(self.tasks) + 1
        
        # Pick source storage zone location
        storage_locs = [l for l in self.locations.values() if l.location_type in ("STORAGE", "PICKING")]
        dest_locs = [l for l in self.locations.values() if l.location_type in ("PACKING", "SHIPPING", "STAGING", "RECEIVING")]
        
        src_loc = self.rng.choice(storage_locs) if storage_locs else (list(self.locations.values())[0] if self.locations else None)
        dest_loc = self.rng.choice(dest_locs) if dest_locs else (list(self.locations.values())[0] if self.locations else None)

        task_num = f"TSK-SIM-{task_id:04d}"
        sim_task = SimulatedTask(
            task_id=task_id,
            task_number=task_num,
            warehouse_id=self.warehouse_id,
            task_type="PICK",
            product_id=items_payload[0]["item_id"],
            source_location_id=src_loc.id if src_loc else "L-SRC",
            destination_location_id=dest_loc.id if dest_loc else "L-DEST",
            requested_quantity=items_payload[0]["requested_qty"],
            priority=priority,
            priority_score=100 if priority == "CRITICAL" else (50 if priority == "HIGH" else 10),
            order_id=order_id
        )
        sim_task.created_at_sim = self.env.now
        self.tasks[task_id] = sim_task
        self.log_event("TASK_CREATED", task=sim_task, details={"order_id": order_id})

    def run_assignment_scheduler(self):
        """Performs optimal OR-Tools assignments of tasks to robots in simulated memory."""
        # Filter available robots
        available_robots = [
            r for r in self.robots.values()
            if r.status == "AVAILABLE" and r.assigned_task_id is None
        ]
        
        # Filter unassigned tasks
        unassigned_tasks = [
            t for t in self.tasks.values()
            if t.status in ("QUEUED", "FAILED")
        ]

        if not available_robots or not unassigned_tasks:
            return

        # Check battery and queue charging dispatches
        active_available = []
        for r in available_robots:
            if r.battery_level < 20.0:
                r.status = "CHARGING_MOVING"
                r.target_location_id = self.get_nearest_charging_station(r).id
                r.active_path = []
                self.log_event("ROBOT_DISPATCHED_TO_CHARGE", robot=r)
            else:
                active_available.append(r)
        available_robots = active_available

        if not available_robots:
            return

        # Sort tasks by priority
        unassigned_tasks.sort(key=lambda x: x.priority_score, reverse=True)
        num_robots = len(available_robots)
        num_tasks = min(len(unassigned_tasks), num_robots * 2)
        tasks_pool = unassigned_tasks[:num_tasks]

        assigned = False
        if or_tools_available:
            try:
                # Build cost matrix based on Manhattan distance
                cost_matrix = []
                for r in available_robots:
                    row = []
                    for t in tasks_pool:
                        src_loc = self.locations.get(t.source_location_id)
                        tx = src_loc.x if src_loc else 1.0
                        ty = src_loc.y if src_loc else 1.0
                        dist = abs(r.current_x - tx) + abs(r.current_y - ty)
                        
                        # Apply battery penalty
                        bat_penalty = 50.0 if r.battery_level < 35.0 else 0.0
                        cost = int(dist + bat_penalty)
                        row.append(cost)
                    cost_matrix.append(row)

                model = cp_model.CpModel()
                x_vars = {}
                for r_idx in range(num_robots):
                    for t_idx in range(num_tasks):
                        x_vars[r_idx, t_idx] = model.NewBoolVar(f"x_{r_idx}_{t_idx}")

                # Unique mappings constraints
                for t_idx in range(num_tasks):
                    model.Add(sum(x_vars[r_idx, t_idx] for r_idx in range(num_robots)) <= 1)

                for r_idx in range(num_robots):
                    model.Add(sum(x_vars[r_idx, t_idx] for t_idx in range(num_tasks)) <= 1)

                # Objective: minimize overall cost values
                model.Minimize(
                    sum(x_vars[r_idx, t_idx] * cost_matrix[r_idx][t_idx]
                        for r_idx in range(num_robots)
                        for t_idx in range(num_tasks))
                )

                solver = cp_model.CpSolver()
                solver.parameters.max_time_in_seconds = 0.5
                status = solver.Solve(model)

                if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
                    for r_idx in range(num_robots):
                        for t_idx in range(num_tasks):
                            if solver.BooleanValue(x_vars[r_idx, t_idx]):
                                robot = available_robots[r_idx]
                                task = tasks_pool[t_idx]
                                robot.assigned_task_id = task.id
                                task.assigned_robot_id = robot.robot_code
                                task.status = "ASSIGNED"
                                assigned = True
            except Exception as solve_err:
                logger.error("SimPy engine solver runtime error: %s. Reverting to heuristic fallback.", solve_err)

        if not assigned:
            # Fallback Greedy Heuristic assignment
            for task in tasks_pool:
                best_robot = None
                min_cost = float("inf")
                
                src_loc = self.locations.get(task.source_location_id)
                tx = src_loc.x if src_loc else 1.0
                ty = src_loc.y if src_loc else 1.0

                for r in available_robots:
                    if r.assigned_task_id is not None:
                        continue
                    cost = abs(r.current_x - tx) + abs(r.current_y - ty)
                    if cost < min_cost:
                        min_cost = cost
                        best_robot = r

                if best_robot:
                    best_robot.assigned_task_id = task.id
                    task.assigned_robot_id = best_robot.robot_code
                    task.status = "ASSIGNED"
                    available_robots.remove(best_robot)

    def plan_route(self, robot: SimulatedRobot):
        """Builds coordinates path lists via Phase 10 A* search."""
        self.metrics["A_star_calls"] += 1
        
        # Identify source vs destination target goals
        goal_x, goal_y = 1.0, 1.0
        if robot.status == "CHARGING_MOVING":
            charger = self.get_nearest_charging_station(robot)
            goal_x, goal_y = charger.x, charger.y
        elif robot.status == "MOVING":
            task = self.tasks[robot.assigned_task_id]
            src_loc = self.locations.get(task.source_location_id)
            if src_loc:
                goal_x, goal_y = src_loc.x, src_loc.y
        elif robot.status == "RETURNING":
            task = self.tasks[robot.assigned_task_id]
            dest_loc = self.locations.get(task.destination_location_id)
            if dest_loc:
                goal_x, goal_y = dest_loc.x, dest_loc.y

        start = (int(round(robot.current_x)), int(round(robot.current_y)))
        goal = (int(round(goal_x)), int(round(goal_y)) )

        # Map grid traversal metrics
        grid_map = {}
        for coord, cell in self.grid_cells.items():
            grid_map[coord] = {"traversable": cell.traversable, "cost": cell.cost, "type": cell.cell_type}

        # Override start/goal traversability to allow path planning to/from shelves
        if start in grid_map:
            grid_map[start]["traversable"] = True
        if goal in grid_map:
            grid_map[goal]["traversable"] = True

        # Dynamically inject congested cells (cells occupied by OTHER robots)
        for other_r in self.robots.values():
            if other_r.robot_code != robot.robot_code:
                ox, oy = int(round(other_r.current_x)), int(round(other_r.current_y))
                if (ox, oy) in grid_map:
                    grid_map[(ox, oy)]["cost"] = 15.0  # congested cost penalty

        # Call existing A* pathfinder
        path, cost, duration, msg, expanded_count = run_a_star(start, goal, grid_map, self.obstacles)

        if path:
            self.metrics["A_star_successes"] += 1
            robot.active_path = path[1:]  # skip starting cell
            robot.path_cost = cost
        else:
            self.metrics["A_star_failures"] += 1

    def detect_collision_conflict(self, robot: SimulatedRobot, next_cell: Tuple[int, int], tick: int) -> bool:
        """Calculates vertex, head-on swap, or static overlaps using time-aware reservations."""
        # 1. Check reservation conflict at tick
        other_res = self.reservations.get((next_cell, tick))
        if other_res is not None and other_res != robot.id:
            # Conflict detected!
            return True

        # 2. Check head-on swap conflict
        # If another robot is moving from next_cell to robot's current cell at this tick
        curr_cell = (int(round(robot.current_x)), int(round(robot.current_y)))
        for other in self.robots.values():
            if other.robot_code == robot.robot_code:
                continue
            if other.status in ("MOVING", "RETURNING", "CHARGING_MOVING") and other.active_path:
                other_next = other.active_path[0]
                other_curr = (int(round(other.current_x)), int(round(other.current_y)))
                if next_cell == other_curr and other_next == curr_cell:
                    return True

        # 3. Check static robot occupancy conflict
        for other in self.robots.values():
            if other.robot_code == robot.robot_code:
                continue
            other_curr = (int(round(other.current_x)), int(round(other.current_y)))
            if next_cell == other_curr and other.status not in ("MOVING", "RETURNING", "CHARGING_MOVING"):
                return True

        return False

    def update_reservation(self, robot: SimulatedRobot, next_cell: Tuple[int, int], tick: int):
        """Registers a new space-time cell reservation, clearing previous entries."""
        # Clear old reservation for this robot
        curr_cell = (int(round(robot.current_x)), int(round(robot.current_y)))
        self.reservations.pop((curr_cell, tick - 1), None)
        # Register new reservation
        self.reservations[(next_cell, tick)] = robot.id

    def release_reservations(self, robot: SimulatedRobot):
        """Clears all grid cell reservations mapped to a given robot."""
        keys_to_remove = [k for k, v in self.reservations.items() if v == robot.id]
        for k in keys_to_remove:
            self.reservations.pop(k, None)

    def get_nearest_charging_station(self, robot: SimulatedRobot) -> SimulatedLocation:
        """Finds closest charging zone location coordinate."""
        if not self.charging_stations:
            # Fallback mock coordinate
            return SimulatedLocation("L-CHG-FALLBACK", 12.0, 5.0, "CHARGING")
            
        best_station = self.charging_stations[0]
        min_dist = float("inf")
        for cs in self.charging_stations:
            dist = abs(robot.current_x - cs.x) + abs(robot.current_y - cs.y)
            if dist < min_dist:
                min_dist = dist
                best_station = cs
        return best_station

    def complete_task(self, robot: SimulatedRobot, task: SimulatedTask):
        """Executes task completion, records timing metrics, and handles order status updates."""
        task.status = "COMPLETED"
        task.completed_at_sim = self.env.now
        
        robot.assigned_task_id = None
        robot.target_location_id = None
        robot.completed_tasks += 1
        robot.status = "AVAILABLE"

        self.log_event("TASK_COMPLETED", robot=robot, task=task)

        # Check order completion status
        order = self.orders.get(task.order_id)
        if order:
            # In our simplified simulation, 1 pick task corresponds to 1 order
            order.status = "COMPLETED"
            order.completed_at_sim = self.env.now
            self.log_event("ORDER_COMPLETED", task=None, details={"order_id": order.id})

    def log_event(self, event_type: str, robot: Optional[SimulatedRobot] = None, task: Optional[SimulatedTask] = None, details: Optional[Dict[str, Any]] = None):
        """Appends events to the simulation logging records list."""
        evt = {
            "timestamp_sim": round(self.env.now, 2),
            "event_type": event_type,
            "robot_code": robot.robot_code if robot else None,
            "task_number": task.task_number if task else None,
            "details": details or {}
        }
        self.event_log.append(evt)
        
        # Increment metrics counters
        if event_type == "ROUTE_REPLANNED":
            self.metrics["total_replans"] += 1
        elif event_type == "COLLISION_CONFLICT":
            self.metrics["total_conflicts"] += 1
        elif event_type == "DEADLOCK_DETECTED":
            self.metrics["total_deadlocks"] += 1

    def calculate_aggregate_kpis(self, wall_clock_duration: float) -> Dict[str, Any]:
        """Processes collected logs to return compiled statistics metrics summary dict."""
        completed_orders = [o for o in self.orders.values() if o.status == "COMPLETED"]
        completed_tasks = [t for t in self.tasks.values() if t.status == "COMPLETED"]
        failed_tasks = [t for t in self.tasks.values() if t.status == "FAILED"]

        # Cycle time (duration from created to completed)
        completion_times = [
            (o.completed_at_sim - o.created_at_sim) for o in completed_orders
            if o.completed_at_sim is not None
        ]
        avg_cycle = sum(completion_times) / len(completion_times) if completion_times else 0.0

        # Robot utilization details
        fleet_size = len(self.robots)
        total_travel_distance = sum(r.total_distance for r in self.robots.values())
        avg_travel_dist = total_travel_distance / fleet_size if fleet_size else 0.0

        total_busy = sum(r.travel_time + r.charging_time for r in self.robots.values())
        utilization = (total_busy / (fleet_size * self.duration)) * 100 if fleet_size and self.duration else 0.0

        avg_idle = sum(r.idle_time for r in self.robots.values()) / fleet_size if fleet_size else 0.0
        avg_wait = sum(r.waiting_time for r in self.robots.values()) / fleet_size if fleet_size else 0.0

        throughput_hourly = (len(completed_orders) / self.duration) * 60.0 if self.duration else 0.0

        return {
            "duration_minutes": self.duration,
            "wall_clock_execution_seconds": round(wall_clock_duration, 4),
            "total_orders_received": len(self.orders),
            "completed_orders": len(completed_orders),
            "throughput_orders_per_hour": round(throughput_hourly, 2),
            "fulfillment_rate_pct": round((len(completed_orders) / len(self.orders)) * 100, 2) if self.orders else 0.0,
            "average_completion_cycle_minutes": round(avg_cycle, 2),
            
            "completed_tasks": len(completed_tasks),
            "failed_tasks": len(failed_tasks),
            
            "fleet_size": fleet_size,
            "average_robot_utilization_pct": round(min(100.0, utilization), 2),
            "total_distance_traveled": total_travel_distance,
            "average_distance_per_robot": round(avg_travel_dist, 2),
            "average_robot_idle_minutes": round(avg_idle, 2),
            "average_robot_waiting_minutes": round(avg_wait, 2),

            "A_star_calls": self.metrics["A_star_calls"],
            "A_star_success_rate_pct": round((self.metrics["A_star_successes"] / self.metrics["A_star_calls"]) * 100, 2) if self.metrics["A_star_calls"] else 100.0,
            "replanning_events": self.metrics["total_replans"],
            "collision_conflicts": self.metrics["total_conflicts"],
            "deadlocks_detected": self.metrics["total_deadlocks"],

            "charging_sessions_count": self.metrics["charging_sessions"],
            "total_charging_minutes": self.metrics["charging_duration"],
            "average_charging_queue_wait_minutes": round(self.metrics["charging_queue_time"] / self.metrics["charging_sessions"], 2) if self.metrics["charging_sessions"] else 0.0
        }
