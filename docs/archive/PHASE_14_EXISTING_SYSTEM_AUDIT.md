# Phase 14 Existing System Audit

This document serves as the repository audit for **Phase 14 — Google Gemini / AI Intelligence Integration**.

## 1. Existing AI Integration
- **Backend Router**: Located in [`backend/routers/ai_assistant.py`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/backend/routers/ai_assistant.py). It defines the POST `/ai/assistant` endpoint.
- **REST Client Calls**: The router makes synchronous REST calls via `httpx.Client()` to the Google Gemini API:
  `https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}`
- **Offline / Fallback Mode**: If `GEMINI_API_KEY` is not set in `.env`, the router degrades gracefully to a local offline chatbot logic helper (`offline_assistant_reply`) returning basic details for inventory, robot status, and discrepancies.
- **Frontend UI**: Integrated as a card in the **System Health** tab defined in [`frontend/js/system_health.js`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/frontend/js/system_health.js). It queries the API and appends chat bubbles.
- **SDK / Dependencies**: There is no dedicated Google Generative AI package in `requirements.txt`. The client uses HTTP REST calls via `httpx`.

## 2. central Model Configuration
The application reads settings from the `.env` file:
- `GEMINI_API_KEY` (used to authenticate requests)
- `GEMINI_MODEL` (defaults to `gemini-3.5-flash-lite`)

## 3. Reusable Backend Capabilities & Services
We can safely wrap the following existing components as read-only tools:
- **Inventory/WMS State**: Read-only queries to `db.query(Inventory)` and WMS tables.
- **Robots / Fleets**: Telemetry querying from the memory state cache (`active_robots` in `backend/routers/robots.py`).
- **Forecasting & ABC**: Analytical queries mapping Phase 9 tables (`demand_forecasts`, `abc_classifications`, `shrinkage_flags`).
- **Navigation (A*)**: Route planning via `calculate_manhattan_distance` and path planning checks.
- **Scheduler (OR-Tools)**: Task assignment optimization status.

## 4. Security & Permissions
- **RBAC**: User authorization roles are set (`admin`, `manager`, `operator`, `auditor`, `viewer`).
- **Enforcement Location**: Security must be enforced on the backend *inside* each tool function, completely independent of instructions passed to Gemini.

## 5. Identified Gaps
- **Centralized Registry**: AI tools are currently not registry-managed or schema-enforced.
- **Tool Calling Integration**: The REST client does not yet support the Gemini function-calling JSON format.
- **Dedicated Test Suite**: No test coverage for AI tools or prompt injection resistance exists.
- ** Observability & Auditing**: Latency and token metrics tracking is not present.
