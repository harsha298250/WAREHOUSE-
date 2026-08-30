# Phase 15 Existing System Audit

This document serves as the repository audit for **Phase 15 — AI-Powered Scenario / What-If Intelligence Lab**.

## 1. What Already Exists
- **Models**: SQLAlchemy ORM models `Scenario`, `Experiment`, and `ExperimentRun` are fully defined in [`backend/models.py`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/backend/models.py).
- **APIs**: CRUD endpoints for creating, updating, duplicating, deleting, and running scenarios exist in [`backend/routers/scenarios.py`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/backend/routers/scenarios.py).
- **Background Worker**: `execute_experiment_task` is configured as a Celery background task (or background thread fallback) in [`backend/celery_app.py`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/backend/celery_app.py).
- **Simulation Engine**: `execute_single_repetition` in [`backend/experiment_runner.py`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/backend/experiment_runner.py) mirrors database models to an isolated SQLite file, applies scenario parameter overrides (blocked cells, fleet size, demand multiplier, failures), and runs tick-by-tick routing and assignments using A* and OR-Tools solvers.
- **Frontend Workspace**: Structured dashboard tabs in `frontend/js/scenario_lab.js` handle scenarios CRUD, experiment lists, charts, packing queue simulation, and SimPy runs history.

## 2. Reusable Components
- **Simulation Execution**: `execute_single_repetition` is fully complete and performs actual database isolation (SQLite temp file deleted on completion), keeping the live operational Postgres database completely non-mutated.
- **Algorithms**: OR-Tools assignment constraints, greedy heuristic prioritizations, A* path planning (standard and congestion-aware options) are fully reused.

## 3. What Needs Extension
- **AI Tool Integration**: The Gemini AI assistant layer (`GeminiService` in [`backend/services/ai_service.py`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/backend/services/ai_service.py)) needs new scenario tools registered so that users can query, trigger, and compare stressing scenarios in natural language.
- **Dedicated Test Suite**: A new comprehensive test suite `tests/test_phase15_scenarios.py` is needed to verify validations, isolation boundaries, and AI routing configurations.
