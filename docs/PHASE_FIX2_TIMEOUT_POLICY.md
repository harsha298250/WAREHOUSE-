# Centralized Timeout Policy — Phase Fix 2

This document details the centralized timeout policy implemented across all boundaries of the Smart Warehouse Platform.

## Centralized Timeout Parameters

All timeout configurations are centralized in [`backend/timeout_policy.py`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/backend/timeout_policy.py).

### Timeout Configurations

1. **Interactive Client Authentication & OAuth**
   - `OAUTH_TIMEOUT = 4.0` (seconds)
   - **Rationale**: Interactive sign-ins need to be highly responsive. Google tokeninfo requests must fail fast so that auth threads are not exhausted.

2. **Synchronous Weather Observations**
   - `WEATHER_TIMEOUT = 2.0` (seconds)
   - **Rationale**: Weather statistics are secondary dashboard enhancements. If Open-Meteo latency increases, we fail fast to keep the warehouse dashboard responsive.

3. **Redis Cache**
   - `REDIS_CONNECT_TIMEOUT = 2.0` (seconds)
   - `REDIS_SOCKET_TIMEOUT = 2.0` (seconds)
   - **Rationale**: Cache operations must be lightning fast. If Redis command operations block for more than 2 seconds, caching is bypassed in favor of direct database queries.

4. **RabbitMQ Messaging**
   - `RABBITMQ_CONNECT_TIMEOUT = 2.0` (seconds)
   - `RABBITMQ_SOCKET_TIMEOUT = 2.0` (seconds)
   - **Rationale**: WMS operational event publication should occur quickly. In case of network partitions, we fallback immediately to local log updates.

5. **AI Assistant Generation**
   - `GEMINI_TIMEOUT = 15.0` (seconds)
   - **Rationale**: Large language model token generation has higher inherent latency. A limit of 15 seconds allows for multi-tool calling loops to complete without timing out early under normal conditions.

6. **Transactional Emails (Resend)**
   - `RESEND_TIMEOUT = 8.0` (seconds)
   - **Rationale**: Email dispatch is done asynchronously or in background workers. 8 seconds allows Resend API connections to negotiate handshakes safely.

7. **Disaster Recovery Backups (B2/S3)**
   - `S3_CONNECT_TIMEOUT = 4.0` (seconds)
   - `S3_READ_TIMEOUT = 12.0` (seconds)
   - **Rationale**: Logical database snapshots require higher write and read limits due to content size. Larger values allow multi-megabyte streams to be fully committed.

8. **Diagnostic Health Checks**
   - `HEALTH_CHECK_TIMEOUT = 1.5` (seconds)
   - **Rationale**: Diagnostic dashboards must load instantly. One slow or offline service must never block the health check endpoint.
