# Viva Preparation & System Defense Guide

## Overview
This document prepares the engineering team to defend the Smart Warehouse Automation & Optimization Platform (v3) during viva examinations and technical reviews. All answers reflect the actual codebase architecture.

---

## 27 Essential Viva Questions & Answers

### 1. What is the project?
A cloud-based, multi-facility Smart Warehouse Management and Optimization Platform integrating inventory control, AGV robot fleet management, dual pathfinding ($A^*$ and Dijkstra), smart replenishment recommendations, real-time Digital Twin synchronization, advanced operational analytics, and explainable decision support.

### 2. What problem does it solve?
It resolves operational latency, stockouts, uncoordinated AGV routing, lack of explainable inventory decisions, and data isolation in traditional warehouse management systems.

### 3. Why was this project selected?
Logistics hubs require deterministic, automated decision-making and real-time operational visibility while ensuring zero production data corruption.

### 4. What is novel about it?
- **Dual Algorithmic Pathfinding**: Comparative $A^*$ and Dijkstra routing with live obstacle avoidance.
- **Explainable Decision Support**: Deterministic, data-backed recommendations with action previews (`reason`, severity, suggested URLs).
- **Strict Read-Only Isolation**: Digital Twin, Analytics, and What-If Simulations evaluate snapshots without mutating production inventory or order tables.

### 5. What technologies are used?
- **Core Backend**: Python, FastAPI, SQLAlchemy ORM, Pydantic, Uvicorn.
- **Database**: PostgreSQL (Production SQL database), SQLite (isolated unit testing).
- **Asynchronous Task Queue**: Celery with Redis broker and result backend (fail-fast timeout configured).
- **Event Messaging**: Upstash Redis & CloudAMQP RabbitMQ.
- **Monitoring & Security**: Sentry, PyJWT, Bcrypt password hashing.
- **Frontend**: HTML5, Vanilla CSS3 (glassmorphism/responsive tokens), ES6 JavaScript, WebSockets / SSE.

### 6. Why is A* used?
$A^*$ utilizes a heuristic distance estimate ($h(n) = |x_1 - x_2| + |y_1 - y_2|$) combined with path cost ($g(n)$) to compute the shortest grid path efficiently, minimizing search space for AGV routing.

### 7. Why is Dijkstra used?
Dijkstra calculates guaranteed single-source shortest paths across non-uniform weighted grid edges without heuristic bias, providing an authoritative baseline to evaluate $A^*$ performance.

### 8. What is the difference between A* and Dijkstra?
- **Dijkstra**: Uninformed search ($f(n) = g(n)$); explores nodes equally in all directions until goal is reached.
- **A\***: Informed search ($f(n) = g(n) + h(n)$); uses Manhattan heuristic to prioritize nodes closer to the destination grid coordinates.

### 9. What is Smart Replenishment?
A decision workflow that combines historical stock movements, demand forecasts, safety stock levels, and reorder points to generate reorder recommendations. Recommendations require explicit operator approval to trigger inventory updates.

### 10. What is the Digital Twin?
A real-time, 2D visual layout of the warehouse grid that reflects authoritative database states (robot coordinates, rack occupancy, active routes). It performs ZERO writes to production tables.

### 11. What is Apache Spark?
*(Not implemented in this project codebase. Processed via Python/SQLAlchemy native queries).*

### 12. What is RFID?
*(Not implemented as physical hardware; inventory tracking operates via unique SKU barcoding and SQL primary key records).*

### 13. How are robots managed?
AGVs are tracked in the `robots` table with states (`AVAILABLE`, `MOVING`, `WORKING`, `CHARGING`, `FAILED`), battery percentages, and assigned warehouse zones.

### 14. How does task assignment work?
Tasks follow a strict state machine (`QUEUED` $\rightarrow$ `ASSIGNED` $\rightarrow$ `IN_PROGRESS` $\rightarrow$ `COMPLETED`). Intelligent dispatching evaluates robot availability, distance to pickup location, and battery level.

### 15. How does pathfinding work?
The route engine receives grid start and destination points, checks active `warehouse_obstacles`, executes $A^*$ or Dijkstra, returns step-by-step grid path coordinates, and logs distance, cost, and compute time in `robot_routes`.

### 16. How does inventory affect replenishment?
When `available_stock` $\le$ `safety_stock` or `reorder_threshold`, the replenishment engine flags critical reorder recommendations.

### 17. How does analytics work?
`backend/analytics_engine.py` executes SQL queries to calculate operational metrics (turnover, order fill rate, AGV utilization, low stock count). Missing data returns `"INSUFFICIENT DATA"`.

### 18. How does Decision Support work?
`backend/decision_support_engine.py` evaluates live WMS data to generate explainable recommendations (Why, Severity, Action Preview URL) and an Operational Health Score (0-100).

### 19. How does simulation work?
What-If analysis evaluates scenario parameters (`ROBOT_UNAVAILABLE`, `DEMAND_SURGE`, `ROUTE_BLOCKED`) on memory snapshots, leaving production tables untouched.

### 20. How is production data protected?
- Read-only constraints on Digital Twin, Analytics, and Decision Support.
- Session isolation for database transactions.
- Zero automatic background stock mutations.

### 21. How is authentication handled?
JWT (JSON Web Tokens) with HS256 signatures, token expiration handling, and bcrypt password hashing.

### 22. How does RBAC work?
User roles (`admin`, `manager`, `operator`, `viewer`) govern endpoint access. Privileged POST/PUT actions return `403 Forbidden` for unauthorized roles.

### 23. Why Redis?
Used as a high-speed in-memory message broker, task queue backend, and caching layer for real-time state broadcasts.

### 24. Why RabbitMQ?
Provides reliable enterprise message queuing for asynchronous background notifications and system events.

### 25. Why Celery?
Manages asynchronous background jobs (backup scheduling, health telemetry, notifications) without blocking main FastAPI API threads.

### 26. What are the limitations?
- Grid pathfinding is discrete 2D grid based.
- Decision support recommendations require human operator confirmation for operational execution.

### 27. What are future improvements?
- 3D WebGL Digital Twin rendering.
- Continuous multi-AGV collision resolution algorithms.
