# Phase 14 Optional AI Deployment & Production Verification

This document details the configuration requirements, environment settings, and production compatibility verification for deploying the Smart Warehouse AI expansion to Render.

## 1. Environment Configuration Checklist

Configure the following settings in your Render environment dashboard:

- `GEMINI_API_KEY`: API Key for Google Gemini REST calls.
- `GEMINI_MODEL`: Defaults to `gemini-3.5-flash-lite`.
- `GEMINI_TEMPERATURE`: Defaults to `0.3`.
- `GEMINI_MAX_OUTPUT_TOKENS`: Defaults to `400`.
- `GEMINI_TIMEOUT`: Defaults to `15.0`.

## 2. Render Deployment Verification Status
All optional integrations are designed with fallback paths, ensuring that if external keys or connections fail, the core system continues operating stably.

| Capability | Config status | Live Verification | Remarks |
| :--- | :--- | :--- | :--- |
| **Thinking / Reasoning** | CONFIGURED | VERIFIED | Runs on model prompt instruction configurations. |
| **Multi-tool Agent** | CONFIGURED | VERIFIED | Evaluates loops in-memory. |
| **RAG / File Search** | CONFIGURED | VERIFIED | Scans local files inside the `docs/` folder. |
| **PDF Understanding** | CONFIGURED | VERIFIED | Read tools operate on file formats. |
| **Code Execution** | CONFIGURED | VERIFIED | Evaluated inside restricted python sandboxes. |
| **Google Search** | CONFIGURED | CONFIGURED — LIVE VERIFICATION PENDING | Mocked fallback returns search records. |
| **Google Maps** | CONFIGURED | CONFIGURED — LIVE VERIFICATION PENDING | Mocked fallback returns coordinates. |
| **Voice AI API** | CONFIGURED | VERIFIED | Endpoint decodes voice base64 queries. |
