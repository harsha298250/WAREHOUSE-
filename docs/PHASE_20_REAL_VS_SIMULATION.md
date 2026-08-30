# Phase 20 Real vs. Simulation Labeling Standards

This document establishes the labeling and storage conventions for separating live database facts from simulated/hypothetical run metrics.

## 1. Visual Labeling Conventions

To prevent operational confusion, every interface must display one of the following labels to clarify the nature of the data:

* **LIVE**: Real-world records fetched directly from active PostgreSQL schemas (e.g., active orders, actual stock inventory, and current robot heartbeat states).
* **SIMULATION**: Sandbox SimPy events and run outputs (e.g. simulated bottlenecks, throughput runs, and low-battery events).
* **SCENARIO**: hypothetical "what-if" stress tests (such as simulating a peak demand surge).
* **EXTERNAL DATA**: real-time feeds fetched from external APIs (such as Google OAuth metadata or OpenWeather weather stats).
* **INSUFFICIENT DATA**: explicitly displayed when needed variables or histories are missing from the backend.

---

## 2. Database & Operational Isolation

* **Mutations Guard**: Simulation runs are executed within isolated database sandboxes. They must never mutate, delete, or append to active production tables (like `Inventory`, `Orders`, `Tasks`, or `Robot`).
* **Tool Grounding**: The Gemini AI Operations Assistant retrieves tool data strictly from read-only functions. It cannot modify operational data or invent values if queries return empty responses.
