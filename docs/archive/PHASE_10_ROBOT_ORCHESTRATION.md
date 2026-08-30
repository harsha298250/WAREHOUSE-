# Phase 10: Intelligent Robot Orchestration System

This document outlines the architecture, algorithms, and design choices made during the implementation of the Phase 10 Robot Execution Layer.

## 1. Upgraded A* Pathfinding Architecture
The A* pathfinding system (`backend/routers/pathfinding.py`) was refactored to support complex operational cost structures and metadata validations:
- **Cost Mappings**:
  - Congested cells (cells occupied by other active/moving robots): `15.0` cost.
  - Restricted cells (cells flagged as restricted in metadata): `10.0` cost.
  - High-risk cells (cells flagged as high-risk in metadata): `5.0` cost.
  - Normal traversable floor cells: `1.0` cost.
- **Validation Routine (`validate_path`)**:
  - Ensures all path coordinates lie within layout boundaries.
  - Validates that every step between consecutive coordinates has a Manhattan distance of exactly `1.0` (prevents diagonal jumps or teleportation).
  - Checks traversability for each grid cell.
- **Enhanced Metrics**:
  - Returns the number of `expanded_nodes` during search to measure search space complexity.
  - Returns `execution_time_seconds` to track algorithm efficiency.

## 2. Workload Balancing Scheduler (Google OR-Tools CP-SAT)
Workload assignment is optimized using a Constraint Programming solver (`backend/routers/or_tools_scheduler.py`):
- **Decision Variables**: Boolean indicators $x_{r,t}$ indicating whether Robot $r$ is assigned to Task $t$.
- **Hard Constraints**:
  - **Payload Capacity**: The combined weight of the item(s) must not exceed `robot.max_payload`.
  - **Battery Range**: The robot must have sufficient battery to travel to the source location, complete the transport to the destination, and navigate to the nearest charging station.
  - **Warehouse Matching**: Robots can only be assigned to tasks within their home warehouse.
  - **Uniqueness**:
    - Each task is assigned to at most one robot.
    - Each robot is assigned to at most one task per scheduler cycle.
- **Objective Function**:
  - Maximizes task rewards based on task priority scores (`priority_score`) while minimizing Manhattan travel distance to prioritize high-value tasks and reduce overall congestion.
- **Greedy Fallback Heuristic**:
  - If the solver is infeasible (e.g. model constraints cannot be satisfied), the system falls back to a deterministic greedy matching heuristic to guarantee maximum task coverage.

## 3. Reservation-Based Collision Avoidance
Collision prevention is handled using a time-aware reservation system (`backend/routers/robots.py`):
- **Reservation Tracker**: Maps `(x, y, tick) -> robot_id` synced on a global tick counter to track cell occupancy.
- **Collision Types Handled**:
  - **Vertex Collision**: Multiple robots attempting to occupy the same cell at the same tick.
  - **Swap/Edge Collision**: Two adjacent robots attempting to cross paths (swap cells) in the same tick.
  - **Static Collision**: A moving robot attempting to step into a cell occupied by a static (paused, available, or charging) robot.
- **Replanning and Deadlock Protection**:
  - When a robot is blocked, it transitions to a `WAITING` state.
  - If a robot waits for `3` consecutive ticks, its current route is invalidated (`REPLANNED` status) and it computes a detour routing around the blocking cell.
  - If waiting persists for `5` consecutive ticks, a corridor deadlock is declared; the robot is transitioned to the `PAUSED` state, clearing the grid reservation.
