# Phase 17 Integration Map

This document tracks front-to-back REST APIs integration mappings across all modules.

## 1. REST Mappings & Contracts

| Frontend Action | API Path | HTTP Method | Remarks |
| :--- | :--- | :--- | :--- |
| **Get Overview KPIs** | `/analytics/overview` | GET | Consolidates cycle times, throughputs, stockout rates. |
| **Robot Performance** | `/analytics/robots` | GET | Telemetry summaries travel logs. |
| **ABC Distribution** | `/analytics/abc` | GET | Classifications classifications totals. |
| **Flagged Anomalies** | `/analytics/anomalies` | GET | Discrepancy lists exposure metrics. |
| **Replenishment Recommendations**| `/analytics/replenishment` | GET | Recommended quantities priorities. |
| **PDF Reports** | `/reports/export` | GET | Downloadable PDF reports binary stream. |
| **Trigger Forecasting** | `/analytics/forecasting/run`| POST | ML Horizon forecasting loop. |

## 2. Real-TimeSSE Stream
- Live robot positions and warehouse map changes are streamed via:
  `GET /digital-twin/{warehouse_id}/sync`
- Incremental Three.js modifications are applied inside `js/app.js` to ensure latency performance.
