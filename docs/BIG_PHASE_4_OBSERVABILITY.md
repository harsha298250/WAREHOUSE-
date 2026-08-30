# BIG PHASE 4 — OBSERVABILITY & LOGGING SPECIFICATION

This document outlines the structured logging, Sentry error tracking, and Prometheus metrics configuration.

---

## 1. Structured Logging Policy

All logs output to the stdout/stderr console using a standardized layout format:
`%(asctime)s [%(levelname)s] %(name)s: %(message)s`

### Log Metadata Context
- **Correlation Request ID**: Embedded inside request headers via `X-Request-ID` and retrieved via `request.state.request_id` in unhandled exceptions.
- **Warehouse ID**: Included in all analytics and operational transaction messages.
- **User ID**: Logged safely for RBAC actions.

### Data Privacy Restrictions
- **Strict Prohibition**: Logging of raw passwords, JWT keys, Google Client Secrets, OTP codes, or full OAuth tokens is strictly blocked to prevent leakage in log aggregators.

---

## 2. Error Tracking & Monitoring

### Sentry Error Tracking
- Integrated inside `backend/sentry.py`. Catches FastAPI uncaught exceptions, database connectivity timeouts, and background worker failures.
- Environment and release tags are added dynamically.

### Prometheus API Metrics
- **HTTP_REQUESTS_TOTAL**: Counter tracking request counts by method, endpoint path, and response status code.
- **HTTP_REQUEST_DURATION**: Histogram tracking API path response latency.
- Scraped via the `/metrics` endpoint.
