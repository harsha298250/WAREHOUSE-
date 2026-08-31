# Smart Warehouse Management & Decision Support Platform (v3)

**Capstone Project — Cloud Computing & AI**  
**SIMATS Engineering — Logistics & Automation Systems**

---

## 1. Project Title & Overview
**Smart Warehouse Management, Autonomous AGV Routing, and Decision Support Platform**

This platform provides a complete cloud-native Warehouse Management System (WMS) integrating inventory control, AGV robot fleet management, dual pathfinding ($A^*$ and Dijkstra), smart replenishment decision support, real-time Digital Twin visual synchronization, operational health telemetry, and strict read-only analytical safeguards.

---

## 2. Problem Statement & Objectives
### Problem Statement
Modern logistics operations encounter four key challenges:
1. **Uncoordinated AGV Routing**: AGVs encounter deadlocks, suboptimal detours, and high traversal latency.
2. **Stockouts & Unexplained Inventory Decisions**: Traditional systems rely on static spreadsheets without clear lead-time or safety-stock evidence.
3. **Operational Visibility Gaps**: Facility managers lack real-time digital twin synchronization across warehouses.
4. **Data Corruption & Unauthorized Writes**: Automated analytics or simulation systems risk corrupting production inventory or database records.

### Objectives
- Build a multi-facility WMS backed by PostgreSQL with role-based access control (RBAC).
- Implement dual pathfinding algorithms ($A^*$ and Dijkstra) with obstacle avoidance and performance comparisons.
- Develop a read-only **Smart Replenishment** and **Decision Support Engine** exposing explainable recommendations ("Why?", severity, action URLs).
- Construct a real-time **2D Digital Twin** rendering warehouse grids and AGV telemetry without mutating production state.
- Establish an asynchronous background worker pipeline using Redis, RabbitMQ, and Celery for health monitoring and disaster recovery backups.

---

## 3. Technology Stack

| Technology | Purpose | Where Used | Why Used |
| :--- | :--- | :--- | :--- |
| **Python 3.12** | Core Programming Language | Backend API, ML & Engines | High productivity, extensive ecosystem for data and web APIs |
| **FastAPI** | Async REST API Framework | `backend/routers/` | High performance, automatic OpenAPI schema, native async support |
| **SQLAlchemy 2.0** | Object-Relational Mapping (ORM) | `backend/models.py`, DB queries | Safe SQL abstraction, session management, transaction safety |
| **PostgreSQL** | Primary Relational Database | Production Storage | ACID compliance, robust indexing, foreign key constraints |
| **SQLite** | In-Memory Testing Database | `tests/` Test Fixtures | Fast, isolated, zero-dependency unit and regression testing |
| **Celery** | Asynchronous Task Queue | `backend/celery_app.py` | Offloads background tasks (health, backups, notifications) from API |
| **Upstash Redis** | In-Memory Broker & Cache | Celery Broker / State Cache | Low-latency message broker and result storage |
| **CloudAMQP RabbitMQ** | Enterprise Message Broker | Event Notifications | Guaranteed message delivery and decoupling |
| **Sentry** | Error Telemetry & Tracing | `backend/sentry.py` | Real-time crash reporting and exception monitoring |
| **Resend** | Transactional Email API | `backend/notifications.py` | Cloud email notifications for critical alerts |
| **JavaScript (ES6)** | Frontend Logic | Web Interface | Lightweight native browser execution without framework bloat |
| **Vanilla CSS3** | Modern Glassmorphism Styling | Web UI Design Tokens | Sleek, responsive, high-performance UI components |

---

## 4. Implemented Algorithms

| Algorithm | Purpose | Input | Output | Where Used | Expected Benefit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **$A^*$ Pathfinding** | Optimal Grid Routing | Grid map, start `(x1,y1)`, goal `(x2,y2)`, active obstacles | Step-by-step path, distance, execution time | `backend/routers/pathfinding.py` | Minimizes search space using Manhattan distance heuristic $h(n)$ |
| **Dijkstra Pathfinding** | Guaranteed Shortest Path | Grid map, start `(x1,y1)`, goal `(x2,y2)`, active obstacles | Step-by-step path, distance, execution time | `backend/routers/pathfinding.py` | Provides unguided, exact baseline for routing comparison |
| **Smart Replenishment** | Reorder Recommendation | Stock on hand, safety stock, reorder point, lead time | Priority recommendation & reorder quantity | `ml/replenishment/engine.py` | Prevents stockouts by flagging reorder threshold breaches |
| **Operational Health Scoring** | Facility Risk Assessment | Stockouts, low battery AGVs, task queue backlog, incidents | 0–100 score, status (`HEALTHY`, `ATTENTION`, etc.) | `backend/decision_support_engine.py` | Provides single transparent operational health metric |
| **What-If Simulation** | Read-Only Impact Estimation | Scenario type (`ROBOT_UNAVAILABLE`, `DEMAND_SURGE`), parameters | Estimated latency, stockout impact | `backend/decision_support_engine.py` | Enables safe operational planning without database mutation |

---

## 5. System Architecture & Data Flow

```text
                                +-----------------------------------+
                                |     Single Page App (Web UI)      |
                                +-----------------------------------+
                                                  | REST API / JWT
                                                  v
+---------------------------------------------------------------------------------------------------+
|                                          FastAPI Backend                                          |
|                                                                                                   |
|  +--------------------+  +----------------------+  +---------------------+  +------------------+  |
|  | Authentication     |  | WMS & Core Logic     |  | Pathfinding Engine  |  | Digital Twin     |  |
|  | (JWT / RBAC)       |  | (Warehouse, Items,   |  | (A* & Dijkstra)     |  | (Read-Only State)|  |
|  |                    |  |  Orders, Tasks, AGVs)|  |                     |  |                  |  |
|  +--------------------+  +----------------------+  +---------------------+  +------------------+  |
|            |                        |                         |                      |            |
|  +---------------------------------------------------------------------------------------------+  |
|  |                     Decision Support & Analytics Engine (Read-Only)                         |  |
|  +---------------------------------------------------------------------------------------------+  |
+---------------------------------------------------------------------------------------------------+
       |                                      |                                      |
       v                                      v                                      v
+--------------+                      +---------------+                      +---------------+
| PostgreSQL   |                      | Redis / Celery|                      | System Health |
| Database     |                      | Task Queue    |                      | Telemetry     |
+--------------+                      +---------------+                      +---------------+
```

---

## 6. Database Schema & Entities

- `users`: User credentials, bcrypt password hash, role (`admin`, `manager`, `operator`, `viewer`).
- `warehouses`: Warehouse metadata (ID, name, city, latitude, longitude).
- `warehouse_locations`: Grid storage locations (zone, aisle, rack, shelf, X/Y coordinates).
- `items`: Product catalog (SKU, name, unit cost, safety stock, reorder threshold).
- `inventory`: Stock levels per warehouse location (on hand, reserved, available, damaged).
- `orders` & `order_items`: Order status tracking (`CREATED`, `PROCESSING`, `SHIPPED`, `CANCELLED`).
- `tasks`: Work items (`PICK`, `REPLENISH`, `TRANSFER`) following a strict state machine (`QUEUED` $\rightarrow$ `ASSIGNED` $\rightarrow$ `IN_PROGRESS` $\rightarrow$ `COMPLETED`).
- `robots`: AGV fleet state tracking (`AVAILABLE`, `WORKING`, `CHARGING`, `FAILED`), battery level, location coordinates.
- `robot_routes`: Pathfinding execution logs (algorithm used, distance, cost, time ms).
- `system_incidents`: Health and incident logging.

---

## 7. Major System Modules

1. **Authentication & RBAC**: JWT token creation, expiration, role checking (`admin` full access, `manager` approvals, `operator` execution, `viewer` read-only).
2. **WMS Core**: Complete lifecycle management for warehouses, items, locations, stock movements, and customer orders.
3. **Task & Robot Management**: State-machine driven task queues with intelligent AGV dispatch based on proximity and battery level.
4. **Dual Pathfinding ($A^*$ & Dijkstra)**: Interactive route calculation with live obstacle avoidance and side-by-side performance metrics.
5. **Smart Replenishment**: Lead-time aware inventory reorder recommendations with human-in-the-loop approval workflows.
6. **Real-Time Digital Twin**: 2D grid rendering of facility state, robot positions, and rack occupancy.
7. **Advanced Analytics**: Operational KPIs, inventory turnover, order fulfillment efficiency, and exportable reports.
8. **Decision Support & What-If Simulation**: Explainable priority recommendations with "Why?" reasons and isolated What-If scenario estimates.
9. **System Health & Telemetry**: `/system/health` status reporting for DB, Redis, Celery, and email integrations.

---

## 8. Environment Configuration

Copy `.env.example` to `.env` and set required environment variables:

```env
# Application Core
ENVIRONMENT=production
DEBUG=false
JWT_SECRET_KEY=<your_jwt_secret_key>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/warehouse_db

# Asynchronous Task Queue & Messaging
REDIS_URL=redis://localhost:6379/0
RABBITMQ_URL=amqp://guest:guest@localhost:5672//
CELERY_ENABLED=true

# External Services (Optional)
SENTRY_DSN=<your_sentry_dsn>
RESEND_API_KEY=<your_resend_api_key>
```

---

## 9. Installation & Local Setup

```bash
# 1. Clone or open repository
cd warehouse_v3

# 2. Create virtual environment and install dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Initialize database migrations
alembic upgrade head

# 4. Seed initial demonstration data
python -m backend.seed_demo_data

# 5. Start dev backend server
python start_dev_server.py
# Server running at: http://localhost:8000
```

---

## 10. Test Execution & Regression Results

Run the complete test suite across Phases 4 to 11 (185 tests):

```bash
pytest tests/test_phase11_decision_support.py tests/test_phase10_final_validation.py tests/test_phase9_advanced_analytics.py tests/test_phase8_digital_twin_visualization.py tests/test_phase7_smart_replenishment.py tests/test_phase6_dynamic_pathfinding.py tests/test_phase5_intelligent_assignment.py tests/test_phase4_integration_flow.py -v
```

### Verification Result
- **Total Tests**: **185 Passed**, 0 Failed, 0 Skipped (100% pass rate)
- **Data Safety**: Confirmed **ZERO** unauthorized production database mutations.

---

## 11. Known Limitations & Future Roadmap
- Pathfinding operates on discrete 2D grid coordinates; continuous 3D spatial dynamics are planned for future revisions.
- Decision support recommendations are strictly advisory and require human operator confirmation for production execution.
