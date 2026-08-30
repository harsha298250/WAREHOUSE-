# Phase 11 SimPy Discrete-Event Simulation Report

This report documents the design, architecture, and implementation of the SimPy-based discrete-event warehouse simulation layer.

## 1. Architecture Overview
The simulation is built as a modular, decoupled layer in `backend/simulation/`. It runs completely in-memory using PostgreSQL database snapshots without altering the live operational state.

```
PostgreSQL
    ↓ (DB Session)
Snapshot Engine (Detached models)
    ↓
SimPy Event Loop & Timed Grid Reservations
    ↓
Computed Metrics & Persistence (SimulationRun / SimulationResult)
```

## 2. In-Memory Entities (`backend/simulation/models.py`)
To isolate the simulation, we defined independent data models matching existing WMS models:
- **`SimulatedRobot`**: Tracks coordinates, status, battery, distance, charging, and path steps.
- **`SimulatedTask`**: Manages pickup/drop locations, quantity, and priority.
- **`SimulatedOrder`**: Groups tasks and monitors overall order fulfillment times.
- **`SimulatedGridCell` / `SimulatedLocation`**: Maps grid nodes, traversability, and charging zones.

## 3. Event-Driven Concurrency (`backend/simulation/processes.py`)
SimPy processes model the actual warehouse workflows under simulated time:
- **`order_arrival_process`**: Generates orders according to a Poisson process (configurable arrival rate) or replays historical timestamps (`HISTORICAL_REPLAY`).
- **`scheduler_process`**: Invokes OR-Tools assignments of unassigned tasks to available robots.
- **`robot_process`**: Orchestrates robot movements, route planning, conflict avoidance, charging, and picking states.

## 4. Timed Grid Cell Reservations
To prevent collisions, the engine utilizes a time-aware reservation dictionary:
- `self.reservations[(x, y, tick)] = robot_id`
- Robots reserve their target cell for the specific timestep.
- **Conflicts**: If another robot has reserved the cell or a swap/head-on conflict is detected, the robot waits.
- **Detours**: If blocked for 3 ticks, the robot clears its path and replans, modifying cell costs dynamically to avoid congestion.
- **Deadlock Release**: If blocked for 5 ticks, the robot transitions to `PAUSED`, releases its reservations, and waits to let traffic pass.
