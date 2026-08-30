# BIG PHASE 4 — PRODUCTION DEPLOYMENT ARCHITECTURE

This document describes the production deployment topology, communication paths, startup order, and failure behavior configurations.

---

## 1. Services & Responsibilities

### Frontend Static Assets
- **Responsibility**: Serves the user interface (HTML, CSS, Vanilla JS, Three.js) directly to user browsers.
- **Serving Path**: Mounted by FastAPI backend at `/` and `/static` via `StaticFiles`.

### Backend API Server
- **Responsibility**: FastAPI application handling all API routes (WMS operations, user auth, Digital Twin state, scenarios).
- **Process**: Starts via Uvicorn. Exposes port defined by the platform's `PORT` environment variable (defaults to `8000`).

### Celery Background Worker
- **Responsibility**: Independent worker process that handles long-running and scheduled tasks (emails, automated daily backups, heavy simulations).
- **Process**: Launched via `celery -A backend.celery_app.celery worker --loglevel=info`.

### PostgreSQL Database
- **Responsibility**: Transactional source of truth for WMS state, ledger movements, security logs, and users.
- **Port**: `5432`

### Redis Cache
- **Responsibility**: Stores cache entries for weather requests and temporary telemetry data.
- **Port**: `6379`

### RabbitMQ Broker
- **Responsibility**: Message broker handling routing between FastAPI backend and Celery workers.
- **Port**: `5672` (AMQP), `15672` (Management dashboard)

---

## 2. Communications & Topology

```
                  Client Browser (HTTPS)
                            │
                            ↓
                    FastAPI Backend (Uvicorn)
                            │
         ┌──────────────────┼──────────────────┐
         ↓                  ↓                  ↓
   PostgreSQL (5432)   Redis (6379)     RabbitMQ (5672)
                                               ↑
                                               │
                                         Celery Worker
```

---

## 3. Environment Variable Schema

| Variable | Scope | Purpose |
|---|---|---|
| `ENVIRONMENT` | All | `production` / `development` |
| `DATABASE_URL` | Web, Celery | PostgreSQL connection string |
| `REDIS_URL` | Web, Celery | Connection string for Redis cache |
| `RABBITMQ_URL` | Web, Celery | Connection broker string for RabbitMQ |
| `JWT_SECRET_KEY` | Web | Authentication hash secret |
| `CELERY_ENABLED` | Web | Set to `true` to delegate background jobs to Celery worker |
| `SENTRY_DSN` | Web, Celery | Error logging tracker DSN |

---

## 4. Startup & Dependencies Order
1. **Infrastructure (PostgreSQL, Redis, RabbitMQ)** must start first and report `healthy` states.
2. **FastAPI Backend (Web)**: On startup, runs `alembic upgrade head` to verify and migrate schema, then binds and launches Uvicorn.
3. **Celery Workers**: Launch independently and subscribe to the broker queues.

---

## 5. Failure Recovery Behavior

### PostgreSQL Outage
- **Behavior**: API routes returning database queries throw HTTP 500 errors. WMS requests are gated by transactional safety boundaries, preventing partial commits.

### Redis Cache Failure
- **Behavior**: The application catches connection exceptions and bypasses cache reads (falling back to direct queries or external weather APIs). **The core WMS remains fully operational.**

### RabbitMQ / Celery Worker Crash
- **Behavior**: FastAPI API remains completely available. Tasks continue to queue or fall back to internal backend threads (if `CELERY_ENABLED=false`).
