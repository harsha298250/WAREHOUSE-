# Phase 15 Scenario Lab Architecture

This document maps the implementation details of the scenario orchestration layers.

## 1. Sequence & Data Flow

```mermaid
sequenceDiagram
    User ->> Scenario Lab UI: Define parameters / text prompt
    Scenario Lab UI ->> FastAPI Scenario API: Request scenario creation
    FastAPI Scenario API ->> Scenario Validation Layer: Verify parameters limit
    Scenario Validation Layer ->> Scenario Engine: Apply parameters in-memory
    Scenario Engine ->> Isolated SQLite Temp DB: Seed schema & items
    Scenario Engine ->> SimPy Simulation: Run execution tick loop
    SimPy Simulation ->> Scenario Engine: Aggregate operational metrics
    Scenario Engine ->> PostgreSQL WMS DB: Write scenario history metadata
    Scenario Engine ->> Scenario Lab UI: Return metrics & charts
    Scenario Lab UI ->> Gemini Service: Request AI explanation of results
```

## 2. Sandbox DB Isolation
- A temp SQLite database file is created at runtime inside system temp directory:
  `sqlite:///{db_path}`
- Operational schema is migrated dynamically onto the temp database.
- After simulation completion, the temp database session is closed, the connection pool disposed, and the SQLite file deleted.
- Live WMS database tables (orders, tasks, robots) are strictly read-only and never mutated.
