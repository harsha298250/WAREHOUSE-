# 5 to 10 Minute System Demonstration Script

## Overview
This script guides a presenter through a structured demonstration of the Smart Warehouse Management & Optimization System (v3).

---

## Step-by-Step Demonstration Sequence

### 1. Introduction & Authentication (0:00 - 1:00)
- **Action**: Open browser at `http://localhost:8000`, enter credentials (`admin` / password).
- **What**: Authenticates session via JWT token.
- **Why**: Enforces Role-Based Access Control (RBAC) and security isolation.
- **Result**: Redirected to the Executive Dashboard.

### 2. Executive Dashboard (1:00 - 2:00)
- **Action**: Review KPI summary cards (Total Inventory, Active Tasks, AGV Fleet Status, Pending Replenishments).
- **What**: Displays real-time operational metrics fetched from PostgreSQL database tables.
- **Why**: Gives warehouse managers immediate operational visibility.
- **Result**: Confirms key warehouse metrics reflect actual WMS database records.

### 3. Warehouse & Inventory Management (2:00 - 3:00)
- **Action**: Navigate to `/warehouses` and `/inventory`. Select warehouse `WH-CHN-01`.
- **What**: Shows item stock levels, safety stock thresholds, and reorder points.
- **Why**: Allows tracking of product quantities and location assignments across zones.
- **Result**: Demonstrates non-negative stock validation and real-time inventory queries.

### 4. Task Lifecycle & AGV Robot Fleet (3:00 - 4:30)
- **Action**: Open `/tasks` and `/robots`. Observe task queue state (`QUEUED` $\rightarrow$ `ASSIGNED`).
- **What**: Tracks AGV robot battery percentages, status (`AVAILABLE`, `WORKING`, `CHARGING`), and task assignments.
- **Why**: Demonstrates automated task dispatching and fleet workload distribution.
- **Result**: Selected AGV is assigned to task and status updates dynamically.

### 5. Dual Algorithmic Pathfinding ($A^*$ vs Dijkstra) (4:30 - 6:00)
- **Action**: Open `/pathfinding`. Input start coordinates `(0, 0)` and goal `(4, 4)`. Calculate route using $A^*$, then Dijkstra.
- **What**: Computes grid path coordinates, step distance, and execution latency.
- **Why**: Demonstrates heuristic-driven $A^*$ optimization alongside unguided Dijkstra baseline.
- **Result**: Visual grid highlights shortest obstacle-avoiding path; execution metrics are displayed.

### 6. Real-Time Digital Twin (6:00 - 7:00)
- **Action**: Navigate to `/digital-twin`.
- **What**: Renders 2D grid visualization of warehouse layout, active AGV positions, and rack occupancy.
- **Why**: Provides real-time visual telemetry without modifying production database records.
- **Result**: Digital Twin reads authoritative backend state with zero side effects.

### 7. Smart Replenishment & Decision Support (7:00 - 8:30)
- **Action**: Open `/replenishment` and `/decision-support`.
- **What**: Displays priority recommendations, stockout risk alerts, and transparent Operational Health Score (0-100).
- **Why**: Provides explainable, data-driven suggestions with "Why?" reasons and action preview URLs.
- **Result**: Operator reviews recommendation reason and navigates to action URL; zero auto-mutations occur.

### 8. System Health & Settings (8:30 - 9:30)
- **Action**: Navigate to `/system/health` and `/settings`.
- **What**: Checks real-time health for PostgreSQL, Redis, RabbitMQ, Celery, and Email notifications.
- **Why**: Verifies system stability, broker timeouts, and environment configuration persistence.
- **Result**: Telemetry displays `HEALTHY` status; settings updates persist to database.

### 9. Conclusion (9:30 - 10:00)
- **Action**: Summarize platform stability, 100% test pass rate (185 regression tests), and presentation readiness.
