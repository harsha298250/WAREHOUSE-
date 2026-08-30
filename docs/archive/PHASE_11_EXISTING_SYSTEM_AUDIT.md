# Phase 11: Existing System Audit Report

This report documents the current status and design of the warehouse robotics and simulation architecture prior to implementing the SimPy discrete-event simulation layer.

## 1. Existing Simulation Functionality
- **V1/V2 Legacy Loop**: A basic tick-based, non-SimPy simulation loop resides in `backend/experiment_runner.py` for Scenario Lab experiments. It runs in increments of ticks (e.g., `duration_ticks = 500`) and calls `execute_simulation_tick(temp_db)` on an isolated, temporary SQLite database.
- **SimPy Packing Queue**: A localized SimPy model exists in `ml/simpy_simulator.py` (served via `/scenarios/packing-simulation`). It simulates packing station conveyors and operators using `simpy.Resource(env, capacity=num_operators)` but is entirely decoupled from the actual warehouse layout, robot movements, and task state machines.

## 2. Existing Robot Architecture
- **Robot Entity**: The `Robot` model in `backend/models.py` tracks `id`, `robot_code`, `name`, `status`, `battery_level`, `current_x`, `current_y`, `assigned_task_id`, `total_tasks_completed`, and `total_distance`.
- **Status Lifecycle**: Robots transition through states: `AVAILABLE`, `ASSIGNED`, `MOVING`, `PICKING`, `RETURNING`, `CHARGING`, `WAITING`, `PAUSED`, `FAILED`, and `OFFLINE`.
- **Telemetry Event Logging**: Positions and status changes write to the `RobotTelemetryEvent` table.

## 3. Existing Task Architecture
- **Task Entity**: Managed in `backend/models.py`. Tracks `task_number`, `task_type` (e.g. `PICK`), `status` (`QUEUED`, `ASSIGNED`, `IN_PROGRESS`, `COMPLETED`, `FAILED`), `assigned_robot_id`, `product_id`, `source_location_id`, and `destination_location_id`.
- **Workflow Hook**: Completion executes via `complete_task` in `backend/routers/tasks.py` which transitions the order status to `COMPLETED` / `PACKING` and releases inventory reservations.

## 4. Existing Warehouse Architecture
- **Warehouse Layout**: Defined by `Warehouse`, `WarehouseLocation` (e.g. storage zones vs. packing zones), `WarehouseGridCell` (layout traversability, costs, and cell types), and `WarehouseObstacle` (active blocks).
- **Default Seeder**: `initialize_warehouse_grid_if_empty` populates default boundaries and grid mappings.

## 5. Existing A* Implementation
- **Algorithm**: Implemented in `backend/routers/pathfinding.py` (`run_a_star`). Uses dynamic costs: `Normal=1.0`, `High-risk=5.0`, `Restricted=10.0`, and `Congested=15.0`.
- **Validation**: Verifies coordinate bounds, Manhattan adjacency (Manhattan distance = 1.0 per step), and cell traversability.

## 6. Existing OR-Tools Implementation
- **Assignment Solver**: Implemented in `backend/routers/or_tools_scheduler.py` (`benchmark_ortools_assignment`). Uses a CP-SAT solver to map unassigned tasks to available robots by optimizing travel costs and priority rewards under payload capacity, battery ranges, and warehouse constraints.
- **Fallback Heuristic**: Reverts to nearest-robot greedy heuristics on solver timeout or infeasibility.

## 7. Existing Collision System
- **Vertex & Swap Collisions**: Implemented in `execute_simulation_tick`. Prevents robots from occupying the same cell at the same step or crossing paths/swapping adjacent cells.
- **Static Collision**: Blocks entering cells occupied by idle/charging/paused robots.
- **Collision Isolation**: Prevents cross-warehouse collision tracking by filtering by `warehouse_id`.

## 8. Existing Reservation System
- **Timed Reservations**: Persisted in `RobotReservation` table mapping `(x, y, tick) -> robot_id`. Added during route planning and cleared/updated dynamically.

## 9. Existing Battery Logic
- **Depletion**: Robots consume `0.5%` battery per physical grid step and `5.0%` flat penalty upon finishing pick operations. Low/Critical alerts trigger at `25.0%` and `10.0%`.

## 10. Existing Charging Logic
- **Charging**: If a robot transitions to `CHARGING` status, it regains `15.0%` battery per tick until full (`100.0%`), then returns to `AVAILABLE`.

## 11. Existing Digital Twin
- **Observation Boundary**: Standardized endpoints in `backend/routers/digital_twin.py` display the current physical locations and states of active robots.

## 12. Existing APIs
- `/robots` and `/robots/simulation/step` trigger tick movements.
- `/scenarios` (GET, POST, PUT, DELETE) configure Scenario Lab parameters.
- `/scenarios/experiments` runs isolated baseline runs on SQLite files.

## 13. Existing Database Models
- `Scenario`: Holds layout, robot configurations, and seeds.
- `Experiment`: Groups simulation repetitions.
- `ExperimentRun`: Tracks individual execution repetition metrics and JSON results.

## 14. Existing RBAC
- Security roles (`admin`, `manager`, `operator`, `auditor`, `viewer`). `/scenarios` and dispatch endpoints require manager or admin credentials.

## 15. Existing Tests
- Regression testing is defined in `tests/test_phase10_*`, `tests/test_real_warehouse_operations.py`, and `tests/test_simulation_e2e.py`.

## 16. Existing Reusable Services
- A* routing (`run_a_star`), CP-SAT scheduling (`benchmark_ortools_assignment`), step verification, and transition actions are already fully developed.

## 17. Existing Limitations
- Sticking to ticks runs sequentially on the main server loop and cannot map actual event-driven concurrency. Storing reservations in a live SQLite/PostgreSQL table makes scaling simulation runs extremely database-heavy.

## 18. Phase 11 Integration Points
- SimPy must read warehouse layouts from database snapshots.
- SimPy processes must model `Robot`, `Task`, and `Order` workflows, calling `run_a_star` and `benchmark_ortools_assignment` on detatched in-memory models.
- SimPy events must compute Metrics (utilization, throughput, cycle times) and persist runs into `ExperimentRun` database models without touching operational tables.
