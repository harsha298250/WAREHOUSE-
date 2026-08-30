# Phase 14 Tool Catalog

This document registers the strict parameters schemas, descriptions, and RBAC roles authorized to execute each registry-backed tool.

## 1. Tool Catalog Summary

| Tool Name | Allowed Roles | Description | Arguments Schema |
| :--- | :--- | :--- | :--- |
| `get_warehouse_status` | `admin`, `manager`, `operator`, `auditor`, `viewer` | High-level summary of active robots, tasks, and inventory items. | `warehouse_id` (String) |
| `get_inventory_levels` | `admin`, `manager`, `operator`, `auditor`, `viewer` | Available, reserved, and damaged inventory level tables. | `warehouse_id` (String), `limit` (Int) |
| `get_robot_telemetry` | `admin`, `manager`, `operator`, `auditor` | Real-time coordinate positions, batteries, and operations state. | `warehouse_id` (String) |
| `get_active_tasks` | `admin`, `manager`, `operator` | Returns in-progress picker tasks and routing status. | `warehouse_id` (String) |
| `get_recent_anomalies` | `admin`, `manager`, `auditor` | Discrepancy deviation history and financial exposures. | `warehouse_id` (String) |
| `calculate_route_astar` | `admin`, `manager` | Calculates path coordinates and Manhattan distances between nodes. | `warehouse_id` (String), `robot_code` (String), `start_x` (Float), `start_y` (Float), `goal_x` (Float), `goal_y` (Float) |
