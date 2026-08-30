# Phase 16 KPI Definitions

This document details WMS operational KPI formulas and measurement bounds.

## 1. Key Metrics & Formulas

| KPI Metric | Definition | Mathematical Formula | Data Source |
| :--- | :--- | :--- | :--- |
| **Fulfillment Rate** | Ratio of fully picked and completed orders to total orders received. | `completed_orders / total_orders * 100.0` | `orders` table |
| **Robot Utilization** | Average active operational duration of picker robots. | `active_time / available_time * 100.0` | `robots` (telemetry events) |
| **Stockout Rate** | Percent of unique items experiencing zero available stock. | `stockout_items / total_items * 100.0` | `inventory` table |
| **Forecast Error (WAPE)** | Weight absolute percentage error. | `sum(abs(actual - predicted)) / sum(actual)` | `forecast_results` |
| **Throughput** | Count of completed and dispatched shipments. | `count(orders.status == 'COMPLETED')` | `orders` table |
| **Average Pick Duration** | Average time from task start to completion. | `avg(tasks.completed_at - tasks.started_at)` | `tasks` table |
