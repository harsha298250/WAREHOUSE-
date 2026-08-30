# Phase 3 Robotics & Warehouse Automation Existing System Audit

This document contains the step-by-step system audit of the robotics, pathfinding, and optimization layer in the Smart Warehouse Platform.

---

## 1. Codebase Architecture & File Locations

* **Robot Data Model**: [`backend/models.py`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/backend/models.py) (lines 422-470)
* **Robot API Router**: [`backend/routers/robots.py`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/backend/routers/robots.py)
* **A* Pathfinding & Grid Router**: [`backend/routers/pathfinding.py`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/backend/routers/pathfinding.py)
* **OR-Tools CP-SAT Router**: [`backend/routers/or_tools_scheduler.py`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/backend/routers/or_tools_scheduler.py)
* **Digital Twin Sync Router**: [`backend/routers/digital_twin.py`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/backend/routers/digital_twin.py)
* **WMS Operations Router**: [`backend/routers/wms.py`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/backend/routers/wms.py)
* **Audit Trail Logic**: [`backend/audit_ledger.py`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/backend/audit_ledger.py)

---

## 2. Existing Robotics Capabilities (Verified Working)

1. **Robot Model**: Encompasses ID, code, status, battery, current X/Y, target X/Y, payload constraints (`max_payload`), and capabilities.
2. **Robot State transitions**: Validated against `ALLOWED_ROBOT_TRANSITIONS` rules in `robots.py` (lines 87-100). Invalid status moves raise HTTP 409 errors.
3. **A* Pathfinding Router**: Located in `pathfinding.py` (lines 87-160). Successfully plans 4-directional moves on grid cells, avoiding static obstacles and honoring cost parameters.
4. **Collision Avoidance Heuristics**: Integrated in `execute_simulation_tick` in `robots.py` (lines 380-427). Vertex, head-on/edge, and swap collisions are checked, applying waiting states or priority-based resolution.
5. **Route Replanning & Deadlocks**: Re-plans route detouring after 3 ticks of waiting, and pauses the robot (deadlock detected) after 5 ticks of waiting.
6. **Battery Management**: Decrements battery during moves (0.5% per tick) and flat-penalizes picking (5.0%). Recharges at `+15.0%` per tick.
7. **OR-Tools CP-SAT Solver**: Solves resource optimization, matching queued tasks to eligible robots in `or_tools_scheduler.py` (lines 178-296), with a safe, deterministic greedy fallback.

---

## 3. System Gaps & Inconsistencies (Modifications Required)

### 🚨 Critical: Broken Audit Ledger Chaining
* **Issue**: In `robots.py` (lines 128, 325, 495, 512) and `or_tools_scheduler.py` (lines 360, 425), audit logs are manually inserted into `AuditLedger` using hardcoded `"SYSTEM"` strings for `prev_hash` and `hash`. This bypasses the SHA-256 chaining logic in `audit_ledger.py`, breaking the tamper-evident validation checks (`verify_chain`).
* **Correction**: Modify these call sites to use `audit_ledger.append_entry(db, event_type, details)` to preserve chain integrity.

### ⚠️ Incomplete Robot State Machine Verification
* **Issue**: While `transition_robot_status` rejects invalid transitions, some endpoints bypass it and write direct assignments without validating transitions.
* **Correction**: Ensure all endpoints and simulation updates run transitions through the validator.

### ⚠️ Missing Single Task Scheduling Constraints
* **Issue**: Single task optimization in `optimize_single_task` uses a greedy matching function, but does not explicitly verify payload capacity and battery parameters against the active route's coordinates.
* **Correction**: Verify and assert payload and battery constraints in all task assignment flows.

---

## 4. Architectural Rules (Must NOT be Changed)
* **PostgreSQL** must remain the sole authoritative source of truth.
* **OR-Tools** CP-SAT is restricted to task assignments (the **who**), while **A*** plans routes (the **how**).
* **SimPy** simulation runs must remain completely isolated from live production database records.
