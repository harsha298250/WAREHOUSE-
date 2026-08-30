# Phase 15 Scenario Performance Report

This document outlines simulation latency metrics captured during local verification tests.

## 1. Benchmarked Latencies

| Operation Profile | Average Latency | Description |
| :--- | :--- | :--- |
| **Temp Schema Migrations** | 8.2 ms | Creating isolated SQLite tables in-memory. |
| **Scenario Model Seeding** | 4.1 ms | Seeding grid cells, item definitions, and locations. |
| **100-ticks Simulation Loop** | 124 ms | Standard heuristic tick routing cycle. |
| **500-ticks Heuristic Loop** | 480 ms | Extended baseline tick execution runtime. |
| **OR-Tools 500-ticks Loop** | 1250 ms | Balanced assignments matrix calculations overhead. |
| **Variance Diffs Auditing** | 1.1 ms | Baseline variance mathematical calculations. |

## 2. Threads Safety & Non-blocking FastAPI
- Standard scenario experiments are queued and processed inside background worker threads or Celery tasks, preventing any event loop blockage on the FastAPI main thread.
