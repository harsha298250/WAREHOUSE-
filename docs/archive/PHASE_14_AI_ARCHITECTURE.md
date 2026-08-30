# Phase 14 AI Assistant Architecture

This document details the software architecture, flow patterns, and integration boundaries of the WMS Intelligent Diagnostics assistant.

## 1. Flow Diagram

```mermaid
sequenceDiagram
    participant User as Operations Manager (UI)
    participant API as FastAPI Router (/ai/assistant)
    participant SVC as Gemini Service (ai_service.py)
    participant Gemini as Google Gemini REST API
    participant DB as PostgreSQL Database

    User->>API: Send chat prompt
    API->>API: Authenticate & check session
    API->>SVC: Delegate request details
    SVC->>Gemini: First Request (System prompt, tools schema, user query)
    alt Gemini requests Tool Call
        Gemini-->>SVC: JSON tool calls payload (e.g. get_robot_telemetry)
        SVC->>SVC: Validate arguments server-side
        SVC->>DB: Query read-only WMS telemetry
        DB-->>SVC: Telemetry JSON dataset
        SVC->>Gemini: Second Request (History + tool responses)
        Gemini-->>SVC: Response text explaining findings
    else Direct Answer (no tools)
        Gemini-->>SVC: Response text
    end
    SVC-->>API: Format structured response (text, tool calls, sources)
    API-->>User: Render chat bubble + tool badges + source credits
```

## 2. Centralized Model Orchestration
- **Service Layer**: Managed in [`backend/services/ai_service.py`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/backend/services/ai_service.py).
- **Graceful Fallback**: If the API key is not configured, the service routes requests to the local rule-based helper (`offline_assistant_reply`), preventing crashes and ensuring high system availability.
