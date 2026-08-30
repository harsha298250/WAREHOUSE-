# Phase 18 — Security Existing System Audit

This document outlines the structural audit of the pre-existing security, authentication, and notification components of the WMS platform, identifying how the Phase 18 Enterprise Security implementation was integrated without modifying core architectures.

---

## 1. What Pre-Existed (Audited & Reused)

| Component | DB Backed / Code File | Details / Reused For |
|---|---|---|
| **`OTPRecord`** | `backend/models.py` | ORM table with columns for `user_id`, `purpose`, `code_hash`, `expires_at`, `attempts`, `max_attempts`, and `consumed_at`. Reused as operational store for login verification codes. |
| **`_create_db_otp()`** | `backend/routers/auth.py` | Generates a 6-digit random code, hashes it with bcrypt, and persists to DB. Reused unchanged for Login OTP. |
| **`_verify_db_otp()`** | `backend/routers/auth.py` | Handles attempt counting, expiry check, password hash verification, and single-use consumption. Reused unchanged. |
| **`AuditLedger`** | `backend/models.py` | SHA-256 hash-chained immutable audit log. Linked to security events via `audit_ledger_ref`. |
| **`UserSession`** | `backend/models.py` | Tracks user agent, IP, login method, and `revoked_at` status. Integrated with session revocation endpoint. |
| **`resend_client.py`** | `backend/resend_client.py` | Resend SDK integration with a local console fallback (mock mode) when API keys are absent. Used for sending branded HTML emails. |

---

## 2. Identified Gaps & How They Were Filled

1. **Single-Factor Login**: Standard login only validated username/password.
   - *Resolution*: Implemented optional `LOGIN_OTP` verification flow gated by `LOGIN_OTP_REQUIRED` environment variable.
2. **Missing Rich Metadata**: Pre-existing `AccessLog` only logged minimal fields (username, action, IP).
   - *Resolution*: Created the `SecurityEvent` model to track detailed device, browser, OS, correlation IDs, and severity classifications.
3. **No Login Alerts**: Administrators were not alerted when users logged in or performed critical operations.
   - *Resolution*: Added `send_login_alert_email()` and `send_role_change_alert()` dispatches to alert security administrators of high-impact events.
4. **No Security Dashboard Interface**: No UI existed to monitor security posture.
   - *Resolution*: Added `Security Activity` section in the sidebar with category filters, date filters, user search, and an event details slide drawer.
