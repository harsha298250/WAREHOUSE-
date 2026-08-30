# Failure Classification Matrix — Phase Fix 2

This matrix details the expected behavior and fallbacks for every possible failure scenario across our external dependencies.

| Dependency | Failure Mode | Impacted Action | Normalized Behavior | Fallback / Recovery Strategy |
| :--- | :--- | :--- | :--- | :--- |
| **Redis** | Timeout / Connection Failure | Cache reading / writing / OTP rate limits | Caching is bypassed; OTP rate-limiting fails open. | System queries PostgreSQL directly; `redis_available` is flagged false to fail fast. |
| | Authentication Failure | Connection initialization | Client initialization fails safely; logs warning. | System falls back to local memory and cache bypass. |
| **RabbitMQ** | Timeout / Connection Failure | Event routing / Message queues | Event publication fails; local warnings are logged. | Phase 22.5 asynchronous background daemon thread executes. WMS transaction is NOT rolled back. |
| | Authentication Failure | Connection initialization | Client initialization fails; logs warning. | System drops into bypass mode and tracks local events. |
| **Celery** | Worker Unavailable | Background task execution | Task cannot be queued in Celery. | Route handler catches queuing exceptions and falls back to thread/local async execution. |
| **Gemini API** | Timeout / Rate Limit | AI Assistant Chat queries | Returns error code (429/Timeout). | `ai_service.py` intercepts the error and returns local rule-based `offline_assistant_reply`. |
| | Malformed / Empty candidates | Response parsing | Candidate parsing raises Index / Key error. | `ai_service.py` bounds-checks the candidates list and returns the offline fallback. |
| **Open-Meteo** | Timeout / Connection Failure | Weather Dashboard Panel | Endpoint returns 503 Service Unavailable. | Frontend displays "Weather unavailable" panel. |
| | Malformed JSON | Weather response normalization | JSON parsing raises ValueError. | Intercepted in `weather_service.py` and treated as offline. |
| **Backblaze B2** | Connection / Upload / Read Failure | Automated / manual database backups | Backup verification fails. | Cloud storage falls back to locally saving logical sql backups. |
| **Google OAuth**| Provider Timeout / Token Mismatch | Google Sign-in login | Urllib token verification raises timeout/URLError. | Returns HTTP 401 Unauthorized; login fails safely. |
| **Sentry** | Connection Failure | Telemetry / Observability logs | SDK initialization fails. | Logged as warning; application continues running normally. |
