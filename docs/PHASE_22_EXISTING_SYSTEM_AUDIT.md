# Phase 22 Existing System Audit — Smart Warehouse Intelligence Platform

## 1. Core Performance Architecture

### 1.1 Database Connection Pooling
* **Configuration**: Defined inside [database.py](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/backend/database.py).
  * `pool_size`: 10 connections.
  * `max_overflow`: 20 connections.
  * `pool_recycle`: 1800 seconds (30 minutes).
  * `pool_timeout`: 30 seconds.
* **Failover Design**: Re-pings active connections (`pool_pre_ping=True`) to drop stale database handles safely.

### 1.2 Redis Caching
* **Configuration**: Set up inside [redis_client.py](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/backend/redis_client.py) with a `3.0s` connection/socket timeout.
* **Bypass Design**: If Redis fails to ping on startup or during a runtime get/set/delete operation, the client logs a warning and marks `redis_available = False`. Caching routines cleanly return `None` or `False` (fail-safe bypass), query execution falls back to the authoritative PostgreSQL database, and the system continues running without throwing unhandled exceptions.

### 1.3 RabbitMQ Event Broker
* **Configuration**: Mapped in [mq_client.py](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/backend/mq_client.py) with 3 connection attempts, a 2s retry delay, and a `3.0s` socket timeout.
* **Bypass Design**: If RabbitMQ is unavailable, `publish_event` intercepts delivery errors and logs the event category and JSON payload locally to standard output.
* **Resilience**: Employs publisher acknowledgements (`confirm_delivery()`) and routes failed messages to a Dead Letter Exchange (`dlx.warehouse_events`) and queue (`dlq.warehouse_events`).

### 1.4 Celery Task Queue
* **Configuration**: Uses RabbitMQ as the message broker and Upstash Redis as the result backend. Celery tasks (e.g. ARIMA forecasts, logical backups, anomaly scoring) run asynchronously. If RabbitMQ is unreachable, Celery tasks fallback to synchronous execution inside daemon threads to prevent background task starvation.

### 1.5 Gemini AI Assistant
* **Configuration**: Connects to the Google Gemini model.
* **Resilience**: If model quotas are exhausted or connections timeout, the assistant router handles the error gracefully, returns structured grounding errors, and refuses to fabricate fake operational counts or numbers.

### 1.6 Digital Twin & SSE Sync
* **Configuration**: Serves client sync packets over `/digital-twin/{warehouse_id}/sync` using Server-Sent Events (SSE).
* **Resilience**: Implements connection disconnect heartbeats. If the connection drops, the frontend transitions through `RECONNECTING` and `STALE` states before retrying.
