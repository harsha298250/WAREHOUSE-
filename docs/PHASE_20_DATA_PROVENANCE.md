# Phase 20 Data Provenance Map — Smart Warehouse Intelligence Platform

This document outlines the source-of-truth mappings for all operational data types rendered inside the WMS frontend.

## 1. Authoritative Source-of-Truth Mapping

| Data Type | Authoritative Source | Derivation / Processing | UI Destination / Router | Status |
|---|---|---|---|---|
| **Inventory Stock** | PostgreSQL `StockMovement` table | Live aggregates matching latest dates | `/api/items` & `/apps/digital-twin` | **LIVE** |
| **Orders Lifecycle** | PostgreSQL `Order` & `OrderItem` | Live records and transition validations | `/api/orders` & `/orders` | **LIVE** |
| **Tasks & Priorities**| PostgreSQL `Task` | Priority-based dispatch queues | `/api/tasks` & `/tasks` | **LIVE** |
| **Robot Fleet States**| PostgreSQL `Robot` | Active battery & state mappings | `/api/robots` & `/robots` | **LIVE** |
| **Physical Warehouses**| PostgreSQL `Warehouse` | Location profiles and center coordinates | `/api/warehouses` | **LIVE** |
| **Financial Ledger** | PostgreSQL `Order` / `OrderItem` | Sum of prices, taxes, and transaction ledgers | `/api/analytics` & `/financials` | **LIVE** |
| **Demand Forecasts** | Model `ARIMA` / `Prophet` outputs | Evaluation metrics (MAE, RMSE, sMAPE) | `/api/forecast` & Forecasting UI | **MODEL OUTPUT** |
| **ABC Classifications**| Pareto Value calculation | Live sorted sales value percentages | `/api/analytics/abc` & ABC View | **DERIVED** |
| **Stock Anomalies** | ML Isolation Forest results | Incident log severity flags | `/api/anomalies` | **DERIVED** |
| **Replenishment** | Reorder points & Safety stock | safety stock checks & MOQ recommendations | `/api/replenishment` & Replenishment UI | **DERIVED** |
| **SimPy Simulation** | SimPy sandbox execution | Event logs, queue times, and resource contention | `/api/simulation/runs` & Simulation Lab | **SIMULATION** |
| **What-if Scenarios** | Parameterized stress tests | Comparison benchmarks vs base metrics | `/api/scenarios` & Scenario Lab | **SCENARIO** |
| **System Health** | Telemetry reachability checks | Direct database, Redis, RabbitMQ, and B2 ping tests | `/health` & System Health UI | **LIVE** |
| **Security Auditing** | PostgreSQL `AuditLedger` | Cryptographic SHA-256 hash chains | `/api/audit-log` & Audit Ledger | **LIVE** |

---

## 2. Data Flow Validation

Every endpoint verified above connects directly to real database records. There is no local state or cache acting as an independent source of truth for operational decisions. If database queries return empty results, the interface shows `INSUFFICIENT DATA` or `NO RECORDS FOUND`.
