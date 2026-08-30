# Phase 16 AI Decision Support

This document explains the Gemini Tool Calling mappings enabling natural-language decision support queries.

## 1. Analytics Tool Registry

- **`get_executive_kpis`**: Returns consolidated dashboard KPIs.
- **`get_order_analytics`**: Returns cycle duration averages.
- **`get_inventory_analytics`**: Returns ABC classes and turnover metrics.
- **`get_robot_analytics`**: Returns telemetry active/charging fleet stats.
- **`get_forecast_analytics`**: Returns MAE/RMSE demand forecast error percentages.
- **`get_anomaly_analytics`**: Returns shrinkage flags list and total exposure in INR.
- **`get_replenishment_analytics`**: Returns recommended reorder thresholds.
- **`get_simulation_analytics`**: Returns SimPy completions history.
- **`get_scenario_analytics`**: Returns what-if parametric runs logs.
- **`get_bottleneck_analysis`**: Compiles queue time and aisle collision diagnostics.

## 2. Multi-Tool Explanations Workflow
If a manager asks: `"Why did pick times increase this week?"`
1. Gemini calls `get_bottleneck_analysis` to identify robot queue delays.
2. Gemini calls `get_robot_analytics` to check fleet battery charging contentions.
3. Gemini isolates the underlying root causes (e.g. high congestion around aisle 2).
4. Gemini presents observations, inferences, and suggests a Phase 15 What-If fleet simulation.
