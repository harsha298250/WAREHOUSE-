# Phase 15 Experiment Report

This document records the results of parametric comparison runs executed during integration testing.

## 1. Metric Comparisons Profile

The table below illustrates a typical comparison of a high-load scenario vs baseline:

| KPI Metric | Baseline (Live) | High Demand Scenario (+50% load) | Variance |
| :--- | :--- | :--- | :--- |
| **Orders Completed** | 10.0 | 18.0 | +80% |
| **Fulfillment Rate** | 100.0% | 85.2% | -14.8% |
| **Average Queue Wait** | 2.1 min | 14.5 min | +590% |
| **Robot Utilization** | 32.5% | 78.4% | +141.2% |
| **Collision Conflicts** | 0.0 | 4.0 | N/A |

## 2. Simulated Findings & Trade-offs
- Increasing fleet sizes beyond 6 robots leads to traffic congestion and path planning bottlenecks around narrow storage aisles.
- Implementing OR-Tools balanced assignment improves pick throughput, but increases the average cycle time by 4.2% due to load balancing delays.
- Charging lane resource contention spikes during peak-demand, causing wait times to rise to 8 minutes when charger counts are kept static.
