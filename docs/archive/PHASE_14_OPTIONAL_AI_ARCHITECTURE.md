# Phase 14 Optional AI Architecture

This document registers the architecture of the **Google Gemini Optional Capabilities** extension.

## 1. Sequence & Event Flow

```mermaid
sequenceDiagram
    participant User as User
    participant Router as API Router (/ai/voice or /ai/assistant)
    participant Agent as Multi-Tool Agent Loop (ai_service.py)
    participant Registry as Tool Registry
    participant Gemini as Google Gemini API

    User->>Router: Send query / simulated audio stream
    Router->>Agent: Delegate message
    loop Sequential Agent reasoning (up to 3 iterations)
        Agent->>Gemini: Current context + conversation history
        Gemini-->>Agent: Request Tool Calls (e.g. search docs + read document)
        Agent->>Registry: Execute registered tool (check RBAC + parameters)
        Registry-->>Agent: JSON results
        Agent->>Agent: Record result to conversation history
    end
    Agent->>Gemini: Request final explanation
    Gemini-->>Agent: Text explaining findings
    Agent-->>Router: Combined answer, tool details, source credits
    Router-->>User: Structured response
```

## 2. Integrated Optional Capabilities
- **Thinking / Reasoning**: Instructs Gemini to perform step-by-step reasoning over JSON WMS datasets, verifying metrics before writing text output.
- **Multi-tool Reasoning**: Evaluates sequential dependencies (e.g., getting warehouse anomalies, then checking manuals for safety SOP rules).
- **File Search / RAG**: Simple local document scanning inside the `docs/` folder, separating document truths from PostgreSQL state databases.
- **Document Understanding**: Read tools returning previews of warehouse SOP files.
- **Sandbox Code Execution**: Restricts evaluation to mathematical operations, blocking imports, FS commands, and database logins.
- **Google Search Grounding**: Integrates industry automation research context.
- **Google Maps Grounding**: Integrates logistics coordinates facilities mapping.
- **Voice AI API**: Adds `/ai/voice` route to process voice base64 streams.
