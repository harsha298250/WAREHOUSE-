# External Service Audit Report — Phase Fix 2

This document contains a comprehensive audit of all external service boundaries in the Smart Warehouse Platform, mapping their locations, timeout policies, fallbacks, and security considerations.

## Audit Matrix

| Service | Call Location | Timeout (Connect / Read / Write) | Retry Policy | Failure Behavior | Can Block WMS? | Can Fabricate Data? | Security Concern | Recommended Action |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **PostgreSQL** | `backend/database.py` | 30.0s Pool acquisition | None (interactive connection pools) | Connection failures raise DB exceptions immediately. | Yes (critical source of truth) | No | Database passwords / credentials leak | Use connection pool limits and pre-pings; keep credentials strictly in environment. |
| **Redis** | `backend/redis_client.py` | 2.0s / 2.0s / 2.0s | None (fail open) | Connection/timeout error deactivates Redis cache runtime flags and queries PostgreSQL directly. | No | No | Cache poisoning / credentials leak | Centralize Redis socket timeouts and bypass redundant pings. |
| **RabbitMQ** | `backend/mq_client.py` | 2.0s connection & socket | 3 retries (normal), 1 (fast reconnect) | Skips RabbitMQ message publishing, falls back to logging locally, and flags client offline. | No (isolated via background thread & mocks) | No | Plaintext credentials in URLs | Centralize timeouts and use fast reconnection parameter (1 attempt, 1s timeout) in health checks. |
| **Celery** | `backend/celery_app.py` | 5.0s broker, 300s task limit | 3 retries on transient errors (exponential backoff) | Queuing failures fallback to synchronous local background daemon threads. | No (fully isolated from routes) | No | Celery broker URL secrets | Verify task queuing timeouts and fallback behaviors. |
| **Gemini API** | `backend/services/ai_service.py` | 15.0s overall | None (rule-based fallback) | Catching connection exceptions invokes the rule-based local assistant fallback. | No | No | API Key exposure | Centralize timeouts and bounds-check empty candidate responses. |
| **Open-Meteo** | `backend/weather_service.py` | 2.0s connection & read | None (cached for 15m) | Raises RuntimeError; route handler catches it and returns 503 Service Unavailable. | No | No | None (public API) | Set strict connection timeouts and display weather unavailable correctly. |
| **Backblaze B2 / S3** | `backend/cloud_storage.py` | 4.0s connect / 12.0s read | None (logs local fallback backup) | Cloud upload failures fall back to local disk storage backups. | No | No | `verify=False` insecure SSL bypass | Enforce certificate validation (`verify=True`) and specify timeouts in boto3 Config. |
| **Google OAuth** | `backend/routers/auth.py` | 4.0s token exchange | None (unauthenticated error) | Token verification failure raises 401 Unauthorized. | No | No | Access Token leaks / audience mismatches | Enforce interactive-speed oauth timeouts. |
| **Sentry** | `backend/sentry.py` | SDK defaults | None | Sentry SDK initialization failures log error; business transactions continue. | No | No | Sentry DSN key leak | Keep Sentry DSN configuration separate and secure. |
