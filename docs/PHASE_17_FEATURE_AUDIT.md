# Phase 17 Feature Audit

This document inventories the visible UI capabilities of the Smart Warehouse platform.

## 1. Feature Classifications

| Feature Name | View Identifier | Classification | Remarks |
| :--- | :--- | :--- | :--- |
| **Executive Dashboard** | `dashboard` | WORKING | Standard cards, Digital Twin frame, alerts feed. |
| **Orders View** | `orders` | WORKING | Filterable order tables, status columns. |
| **Inventory View** | `items` | WORKING | SKUs list, stock levels, ABC classes. |
| **Tasks View** | `tasks` | WORKING | Task priority lists and logs. |
| **Robots View** | `robots` | WORKING | Status list, details drawers, battery monitoring. |
| **Digital Twin** | `digital-twin` | WORKING | Three.js rendering, live SSE updates. |
| **Forecasting** | `demand-forecast`| WORKING | Horizonal demand predictions charts. |
| **ABC Analysis** | `abc` | WORKING | ABC Pareto distributions. |
| **Anomalies** | `anomalies` | WORKING | Discrepancies logs and exposures. |
| **Replenishment** | `ai-decision-center`| WORKING| Reorder recommendations list. |
| **Scenario Lab** | `what-if-simulator`| WORKING | Custom fleets configurations stress testing. |
| **Simulation Lab** | `experiments` | WORKING | Discrete-event SimPy parameters runs. |
| **Reports** | `timeline` | WORKING | Exports matching CSV, Excel, and PDF formats. |

## 2. Feature Cleanups
- Ensure all navigation links point to valid views.
- Clean up duplicate charts and unify spacing and card styles across all modules.
