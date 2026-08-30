# Phase 18 — Security Architecture & Notification Blueprint

This document details the architecture, data models, rate-limiting rules, email alert routes, and templates implemented in Phase 18 to harden the Smart Warehouse WMS Platform.

---

## 1. Data Schema Architecture

```
+------------------+          +------------------------+
|      users       | <------+ |    security_events     |
+------------------+          +------------------------+
| id (PK)          |          | id (PK)                |
| username (Unique)|          | event_type (indexed)   |
| role             |          | severity (indexed)     |
| is_active        |          | status                 |
+------------------+          | actor_user_id (FK)     |
                              | target_user_id (FK)    |
                              | actor_username         |
                              | ip_address             |
                              | device / browser / os  |
                              | correlation_id         |
                              | audit_ledger_ref       |
                              | details (JSON)         |
                              | timestamp (indexed)    |
                              +------------------------+
```

### Table Structure (`security_events`)
- **Immutable Association**: `audit_ledger_ref` references `AuditLedger.id`, tying the filterable event record to the tamper-evident hash chain.
- **Traceability**: `correlation_id` ties sequential login flows together (e.g. `LOGIN_OTP_SENT` -> `LOGIN_OTP_SUCCESS`).
- **Context Parsing**: Device, browser, and OS are auto-extracted from HTTP request User-Agent strings.

---

## 2. Security Alerts & Email Blueprint

All alerts utilize the custom-styled responsive HTML wrapper templates sent via `backend/resend_client.py`.

### Email Routing Matrix

| Email Recipient | Purpose | Trigger Events |
|---|---|---|
| **User Email** (`User.email`) | Delivers confidential transaction verification tokens | `LOGIN_OTP_SENT` |
| **Admin Email** (`SECURITY_ALERT_EMAIL`) | Posture updates and critical alert escalations | `LOGIN_SUCCESS`, `LOGIN_FAILED`, `ROLE_CHANGED`, `ACCOUNT_ACTIVATED`, `ACCOUNT_DEACTIVATED` |

### Email Templates Layout
1. **Title Banner**: Color-coded by severity (INFO = `#10b981`, WARNING = `#f59e0b`, CRITICAL = `#dc2626`).
2. **Metadata Rows**: Key details like User, Device, Operating System, Browser, IP Address, Timestamp, and Event ID.
3. **Admin Alert Banner**: Interactive notice guiding investigations when unauthorized events occur.

---

## 3. Rate Limiting Rules & Security Constants

1. **OTP Rate Limiting**: Limit of **10 OTP codes per user per hour** (stored in Redis under `otp:ratelimit:{user_id}`).
2. **Fail-Open Policy**: If Redis is unreachable, the system falls back to allowing requests to prevent disruption, while logging the incident safely.
3. **Login OTP Expiry**: Set to **300 seconds (5 minutes)**.
4. **Brute Force Defense**: Maximum of **5 attempts** per OTP before the code is permanently destroyed in the database.
