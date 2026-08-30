# Phase 3 Robotics Architecture

This document describes the architectural design of the robotics orchestration, route planning, and optimization modules.

---

## 1. Division of Responsibilities

The Smart Warehouse Platform utilizes a decoupled architecture to separate task assignment optimization from path planning:

```
+---------------------------------------+
|          Task Assignment              |
|        (OR-Tools Solver /             |
|       Deterministic Fallback)         |
+---------------------------------------+
                   | (Assigns Robot Code)
                   v
+---------------------------------------+
|         Route Path Planning           |
|            (A* Pathfinder)            |
+---------------------------------------+
```

### A. OR-Tools (The "Who")
* **Role**: Batch task scheduling and workload balancing.
* **Constraints Enforced**:
  - Robot payload capacity must exceed product weight.
  - Robot battery must exceed the estimated journey distance.
  - At most one task per robot, at most one robot per task.
* **Fallback**: Safe greedy matching that assigns tasks to the nearest eligible robot sequentially.

### B. A* Pathfinder (The "How")
* **Role**: Coordinate-level path generation.
* **Algorithm Details**:
  - Uses standard A* search with Manhattan distance heuristic ($f(n) = g(n) + h(n)$).
  - Constrains search to 4 directions (UP, DOWN, LEFT, RIGHT).
  - Reads costs from grid cells (normal=1.0, high-risk=5.0, restricted=10.0, congested=15.0).

---

## 2. Collision Avoidance & Deadlock Management

Collision avoidance is executed sequentially during simulation ticks:
1. **Vertex conflicts**: Two robots attempting to enter the same coordinate cell are blocked, transitioning the lower priority robot to `WAITING` status.
2. **Head-on conflicts**: Swapping coordinates is detected and resolved via wait states.
3. **Deadlocks**:
   - On **3 ticks** of waiting: Route status is set to `REPLANNED` and a new A* path is planned detouring the blocked cell.
   - On **5 ticks** of waiting: The robot transitions to `PAUSED` and a `DEADLOCK_DETECTED` audit log is appended.
