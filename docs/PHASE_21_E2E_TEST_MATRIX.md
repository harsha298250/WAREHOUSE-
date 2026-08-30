# Phase 21 End-to-End Test Matrix — Smart Warehouse Intelligence Platform

This document captures the verification matrix for all 30 integration workflows.

| Workflow ID | Workflow Description | Frontend View | API Path | Backend Component / Service | DB / Engine | Auth / RBAC | Audit Logged | Result |
|---|---|---|---|---|---|---|---|---|
| **WF-01** | User Authentication | Login Card / OTP | `/auth/login` | `security_service` | `User` / `OTPRecord` | YES | `SecurityEvent` | **PASS** |
| **WF-02** | Order to Fulfillment | Orders Dashboard | `/orders` / `/tasks` | `order_service` | `Order` / `Task` | YES | `AuditLedger` | **PASS** |
| **WF-03** | Incoming Shipments | Receiving View | `/shipments` | `wms_service` | `StockMovement` | YES | `AuditLedger` | **PASS** |
| **WF-04** | Inventory Management | Inventory Grid | `/inventory` | `wms_service` | `StockMovement` | YES | `AuditLedger` | **PASS** |
| **WF-05** | Robot Task Assignment | Robots Dashboard | `/robots/auto-assign` | `scheduler_service` | `Robot` / `Task` | YES | `AuditLedger` | **PASS** |
| **WF-06** | A* Pathfinding | Live Map | `/digital-twin/state` | `astar_pathfinder` | Grid cell matrix | YES | `RobotRoute` | **PASS** |
| **WF-07** | Collision Avoidance | Live Twin | `/digital-twin/state` | `collision_resolver` | Reservation matrix | YES | None | **PASS** |
| **WF-08** | Battery & Charge return | Map Telemetry | `/robots/status` | `battery_monitor` | `Robot` state | YES | `RobotTelemetry` | **PASS** |
| **WF-09** | OR-Tools CP-SAT | Health Dashboard | `/ai/scheduler/optimize` | `or_tools_scheduler` | CP-SAT solver | YES | None | **PASS** |
| **WF-10** | Step-by-Step Ticks | Live Twin | `/digital-twin/tick` | `simulation_tick` | Coordinate loop | YES | `RobotTelemetry` | **PASS** |
| **WF-11** | ARIMA Demand Forecast | Forecast View | `/forecast` | `forecasting_pipeline` | sqlite3/pandas | YES | `ForecastRun` | **PASS** |
| **WF-12** | ABC Pareto Analysis | Analytics View | `/wms/analytics/abc` | `abc_service` | sales aggregation | YES | `ABCClassification` | **PASS** |
| **WF-13** | Anomaly Detection | Anomalies Panel | `/wms/anomalies` | `isolation_forest` | ML models | YES | `AnomalyResult` | **PASS** |
| **WF-14** | Stock Replenishment | Replenishment UI | `/wms/replenishment` | `replenishment_calc` | Safety stock threshold | YES | `ReplenishRec` | **PASS** |
| **WF-15** | Dashboard KPI Aggregates | App Shell | `/wms/dashboard` | `analytics_service` | DB aggregates | YES | None | **PASS** |
| **WF-16** | CSV/PDF Export | Reports Page | `/reports/export` | `reporting_service` | pandas / reportlab | YES | None | **PASS** |
| **WF-17** | Digital Twin Live | Live Twin | `/digital-twin/state` | `digital_twin_state` | WMS Closing stock | YES | None | **PASS** |
| **WF-18** | Digital Twin Sim Mode | Simulation Lab | `/digital-twin/sim` | `simpy_simulator` | Isolated snapshot | YES | None | **PASS** |
| **WF-19** | SSE Synchronization | Live Twin | `/digital-twin/{wh}/sync` | `sse_sync_stream` | event queue | YES | None | **PASS** |
| **WF-20** | Gemini AI Grounding | Health Dashboard | `/api/chat` | `gemini_assistant` | Read-only tools | YES | `SecurityEvent` | **PASS** |
| **WF-21** | Scenario Lab Sandboxing | Scenario Lab | `/experiments` | `experiment_runner` | Isolated DB runs | YES | `Experiment` | **PASS** |
| **WF-22** | Simulation Lab Runs | Simulation Lab | `/simulation/runs` | `simpy_simulator` | Isolated DB runs | YES | `SimulationRun` | **PASS** |
| **WF-23** | Security Activity Log | Security Center | `/security/events` | `security_service` | `SecurityEvent` | YES | `SecurityEvent` | **PASS** |
| **WF-24** | Alerts & Notifications | System Alert | `/notifications` | `notification_service` | preference check | YES | `Notification` | **PASS** |
| **WF-25** | Cloud Integration fails | System Health | `/health` | `health_monitor` | pings (Redis/AMQP) | YES | None | **PASS** |
| **WF-26** | API RBAC Enforcement | App Shell | `/wms/*` | `rbac_guard` | Role check | YES | `SecurityEvent` | **PASS** |
| **WF-27** | Warehouse Isolation | App Shell | `/wms/warehouse/*` | `warehouse_isolation` | DB filtering query | YES | `SecurityEvent` | **PASS** |
| **WF-28** | Data Consistency check | Dashboard | `/wms/dashboard` | `analytics_service` | DB aggregates | YES | None | **PASS** |
| **WF-29** | Contract Mismatches | App Shell | `/wms/*` | `fastapi_validation` | Pydantic parser | YES | None | **PASS** |
| **WF-30** | UI Critical Path | Playwright E2E | browser | `playwright_tester` | browser UI rendering | YES | None | **PASS** |
