# docs/PHASE_9_VIVA_PREPARATION.md — Viva Preparation Guide

This document prepares you for technical viva defense questions regarding architecture, algorithms, database logic, AI controls, and security implementations.

---

## 1. Project Overview & Architecture

### Q1: What is the core problem solved by this system?
**A**: It coordinates warehouse operations (orders, reservations, tasks) with robotic grid routing and advanced decision intelligence (time-series forecasting, anomaly detection, replenishment) while explaining findings through a secure, non-mutating AI assistant.

### Q2: Explain the database source-of-truth flow.
**A**: PostgreSQL is the single source of truth for all operational states. Caching layers (Redis), messaging channels (RabbitMQ/Celery), and visualization frontends (Three.js/SSE) act as secondary read/write pipes. The AI assistant never mutates database states.

---

## 2. Algorithm Details

### Q3: How is task assignment formulated and optimized?
**A**: We use Google OR-Tools CP-SAT solver to formulate task scheduling. It assigns queued picking/packing tasks to available robots in the warehouse. If the solver fails, timing out, or is infeasible, the system falls back to a deterministic greedy distance heuristic.

### Q4: Explain the pathfinding A* algorithm details.
**A**:
- **Movement**: 4-direction orthogonal movements.
- **Heuristic**: Manhattan distance ($|x_1 - x_2| + |y_1 - y_2|$).
- **Zoning Weights**: Floor = 1.0, Danger/High-Risk = 5.0, Restricted = 10.0, Congestion/Collision = 15.0.

### Q5: How are demand anomalies detected?
**A**: We use an **Isolation Forest** model from Scikit-Learn. It isolates sales anomalies by recursively splitting features (rolling sales volume, prices, time aggregates). Outliers are labeled and persisted in PostgreSQL.

---

## 3. Database & Concurrency

### Q6: Why is SELECT FOR UPDATE locking required?
**A**: Multiple users/orders concurrently try to reserve items from the same limited inventory. By using `with_for_update()`, PostgreSQL locks the matching inventory rows in a transaction, preventing race-conditions, double-deductions, or negative stock states.

### Q7: What is the inventory invariant equation?
**A**: `available = on_hand - reserved`. Any inventory reservation must atomically increment `reserved` and decrement `available`.

---

## 4. AI Guardrails (Gemini)

### Q8: How do you prevent Gemini from hallucinating or mutating data?
**A**: Gemini is restricted to read-only tool calling. The tools (`get_executive_kpis`, `get_abc_analytics`, etc.) query verified PostgreSQL records. The backend checks authorization and warehouse mappings, so Gemini cannot bypass database rules.

### Q9: Explain prompt-injection defense.
**A**: Input messages are scanned for keywords (ignore previous instructions, override, pretend, bypass). More importantly, the backend enforces tool authorization schemas and user-warehouse mapping keys, so adversarial overrides fail backend checks.
