import random
import logging
from typing import TYPE_CHECKING, Any, Dict, List, Tuple, Optional
import simpy

if TYPE_CHECKING:
    from backend.simulation.engine import SimulationEngine

logger = logging.getLogger("warehouse.simulation.processes")


def order_arrival_process(env: simpy.Environment, sim_engine: "SimulationEngine"):
    """Generates simulated orders based on poisson arrival rates or historical data."""
    if sim_engine.mode == "HISTORICAL_REPLAY":
        # Sort historical orders by their time delta from start
        if not sim_engine.historical_orders:
            logger.warning("No historical orders found to replay.")
            return

        for order_data in sim_engine.historical_orders:
            delay = max(0.0, order_data["arrival_delay_minutes"])
            yield env.timeout(delay)
            sim_engine.create_simulated_order(order_data)
    else:
        # Synthetic / Poisson arrival process
        order_count = 0
        arrival_rate = sim_engine.config.get("demand", {}).get("order_arrival_rate", 15.0)  # minutes
        while True:
            # Poisson arrival interval
            interval = sim_engine.rng.expovariate(1.0 / arrival_rate)
            yield env.timeout(interval)
            
            order_count += 1
            order_data = {
                "order_id": f"ORD-SIM-{order_count}",
                "customer_ref": f"Sim Client {order_count}",
                "priority": sim_engine.rng.choice(["LOW", "MEDIUM", "HIGH", "CRITICAL"])
            }
            sim_engine.create_simulated_order(order_data)


def scheduler_process(env: simpy.Environment, sim_engine: "SimulationEngine"):
    """Runs CP-SAT or greedy fallback scheduling strategy periodically."""
    interval = 1.0  # run scheduler every 1 simulated minute
    while True:
        sim_engine.run_assignment_scheduler()
        yield env.timeout(interval)


def robot_process(env: simpy.Environment, robot: Any, sim_engine: "SimulationEngine"):
    """Handles simulated robot state transitions, movement ticks, conflict avoidance, and charging."""
    while True:
        # 1. AVAILABLE / IDLE State
        if robot.status == "AVAILABLE":
            if robot.assigned_task_id is not None:
                task = sim_engine.tasks[robot.assigned_task_id]
                robot.status = "ASSIGNED"
                robot.target_location_id = task.source_location_id
                robot.active_path = []
                sim_engine.log_event("TASK_ASSIGNED", robot=robot, task=task)
            else:
                # Idle battery drain (e.g. 0.05% per minute)
                robot.battery_level = max(0.0, robot.battery_level - 0.05)
                robot.idle_time += 1.0
                yield env.timeout(1.0)
                continue

        # 2. ASSIGNED state: transition to driving to pickup
        if robot.status == "ASSIGNED":
            task = sim_engine.tasks[robot.assigned_task_id]
            robot.status = "MOVING"
            task.status = "ASSIGNED"
            task.started_at_sim = env.now
            sim_engine.log_event("ROBOT_MOVING_TO_PICKUP", robot=robot, task=task)

        # 3. ROUTING & MOVEMENT: MOVING (to pickup) or RETURNING (to packing) or CHARGING_MOVING (to charger)
        if robot.status in ("MOVING", "RETURNING", "CHARGING_MOVING"):
            task = sim_engine.tasks[robot.assigned_task_id] if robot.assigned_task_id else None

            # Calculate route if empty
            if not robot.active_path:
                sim_engine.plan_route(robot)

            if not robot.active_path:
                # Pathfinding failed
                if task:
                    robot.failed_tasks += 1
                    task.status = "FAILED"
                    task.failed_at_sim = env.now
                    sim_engine.log_event("ROUTE_PLANNING_FAILED", robot=robot, task=task)
                    robot.assigned_task_id = None
                robot.status = "AVAILABLE"
                yield env.timeout(1.0)
                continue

            # Pop next coordinate step
            next_cell = robot.active_path[0]

            # Check collision conflicts
            conflict = sim_engine.detect_collision_conflict(robot, next_cell, int(round(env.now)))
            if conflict:
                robot.status = "WAITING"
                robot.wait_ticks += 1
                robot.waiting_time += 1.0
                robot.conflicts += 1
                sim_engine.log_event("COLLISION_CONFLICT", robot=robot, details={"conflict_cell": next_cell})

                # Detour / Replan on 3 ticks of wait
                if robot.wait_ticks == 3:
                    robot.replans += 1
                    robot.active_path = []  # forces route recalculation detouring this blocked cell
                    sim_engine.log_event("ROUTE_REPLANNED", robot=robot)
                # Paused corridor deadlock release on 5 ticks of wait
                elif robot.wait_ticks >= 5:
                    robot.status = "PAUSED"
                    sim_engine.log_event("DEADLOCK_DETECTED", robot=robot)
                    # Pause for 5 simulated minutes, release reservations
                    sim_engine.release_reservations(robot)
                    yield env.timeout(5.0)
                    robot.status = "AVAILABLE"
                    robot.wait_ticks = 0
                    robot.active_path = []
                else:
                    yield env.timeout(1.0)
                continue

            # Move successfully
            sim_engine.update_reservation(robot, next_cell, int(round(env.now)))
            robot.wait_ticks = 0
            
            # Simulated robot speed factor (ticks per cell step)
            speed = sim_engine.config.get("robots", {}).get("robot_speed", 1.0)
            step_duration = max(0.1, 1.0 / speed)
            yield env.timeout(step_duration)

            robot.current_x = float(next_cell[0])
            robot.current_y = float(next_cell[1])
            robot.total_distance += 1.0
            robot.travel_time += step_duration

            # Consume battery: 0.5% per step
            robot.battery_level = max(0.0, robot.battery_level - 0.5)
            robot.active_path.pop(0)

            # Check low battery conditions
            if robot.battery_level <= 25.0 and robot.status != "CHARGING_MOVING":
                # Check low battery
                if robot.battery_level <= 10.0:
                    sim_engine.log_event("ROBOT_CRITICAL_BATTERY", robot=robot)
                else:
                    sim_engine.log_event("ROBOT_LOW_BATTERY", robot=robot)

            # Check arrival
            if not robot.active_path:
                if robot.status == "MOVING":
                    robot.status = "PICKING"
                    task.status = "IN_PROGRESS"
                elif robot.status == "RETURNING":
                    sim_engine.complete_task(robot, task)
                elif robot.status == "CHARGING_MOVING":
                    robot.status = "CHARGING_QUEUE"
            continue

        # 4. PICKING State
        if robot.status == "PICKING":
            task = sim_engine.tasks[robot.assigned_task_id]
            sim_engine.log_event("PICK_STARTED", robot=robot, task=task)
            
            # Consume picking time
            picking_time = sim_engine.config.get("simulation", {}).get("picking_duration", 3.0)
            yield env.timeout(picking_time)
            
            # Picking battery penalty: 5%
            robot.battery_level = max(0.0, robot.battery_level - 5.0)
            sim_engine.log_event("PICK_COMPLETED", robot=robot, task=task)

            # Head to destination
            robot.status = "RETURNING"
            robot.target_location_id = task.destination_location_id
            robot.active_path = []
            continue

        # 5. CHARGING STATE (Resource Queueing)
        if robot.status == "CHARGING_QUEUE":
            sim_engine.log_event("CHARGING_QUEUE_ENTERED", robot=robot)
            queue_start = env.now
            
            # Request charger
            with sim_engine.charging_resource.request() as req:
                yield req
                
                # Charger acquired!
                queue_time = env.now - queue_start
                robot.waiting_time += queue_time
                sim_engine.metrics["charging_queue_time"] += queue_time
                
                robot.status = "CHARGING"
                sim_engine.log_event("CHARGING_STARTED", robot=robot)
                
                # Charge: restores 15% battery per simulated minute
                charge_duration = 0.0
                battery_before = robot.battery_level
                while robot.battery_level < 100.0:
                    yield env.timeout(1.0)
                    charge_duration += 1.0
                    robot.battery_level = min(100.0, robot.battery_level + 15.0)
                    robot.charging_time += 1.0
                
                sim_engine.metrics["charging_sessions"] += 1
                sim_engine.metrics["charging_duration"] += charge_duration
                sim_engine.log_event("CHARGING_COMPLETED", robot=robot, details={
                    "battery_restored": 100.0 - battery_before,
                    "charge_duration": charge_duration
                })
                
            robot.status = "AVAILABLE"
            continue

        # Fallback safety timeout if robot falls into undefined state
        yield env.timeout(1.0)
