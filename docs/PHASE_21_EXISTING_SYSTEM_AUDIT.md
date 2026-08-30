# Phase 21 Existing System Audit — Smart Warehouse Intelligence Platform

## 1. Scope & Objective

This document audits the existing testing framework, fixtures, mocks, and coverage across all previous verification phases (Phases 11 to 20).

---

## 2. Test Suite Inventory

The codebase contains a comprehensive regression suite located under the [tests/](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/tests/) folder, comprising **66 files** and **350 passing tests**.

### 2.1 Database & Security Fixtures
* **File**: [conftest.py](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/tests/conftest.py).
* **Key Components**:
  * `db`: Automatically yields an isolated SQLite in-memory database mapping all SQLAlchemy declarative bases, preventing tests from writing to live production PostgreSQL.
  * `client`: FastAPI `TestClient` initialized with the test DB dependency overrides.
  * `seed_test_users`: Automatically registers default admin (`test_admin`), manager (`test_manager`), operator (`test_operator`), auditor (`test_auditor`), and viewer (`test_viewer`) accounts with hashed credentials.
  * `admin_token`, `viewer_token`: Yield valid, signed JWT access tokens with correct role scopes.

### 2.2 Security, Hardening & Auth Tests
* **File**: [test_auth.py](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/tests/test_auth.py) & [test_rbac_security.py](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/tests/test_rbac_security.py).
  * *Coverage*: Password hashing validations, JWT login, OTP verification limits, rate limiting checks, and direct RBAC endpoint blocks.
* **File**: [test_security_hardening.py](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/tests/test_security_hardening.py) & [test_persistence_hardening.py](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/tests/test_persistence_hardening.py).
  * *Coverage*: secure headers (XSS, HSTS), rate-limiting headers, SQLite transactions, rollback blocks on failures, and isolation maps.

### 2.3 Cloud & Core Services
* **File**: [test_phase18_cloud_services.py](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/tests/test_phase18_cloud_services.py).
  * *Coverage*: Backblaze B2 HeadBucket checks, Upstash Redis latency check, CloudAMQP worker status, Sentry event triggering, and Google OAuth callbacks.

### 2.4 E2E Browser Testing
* **Folder**: [tests/e2e/test_playwright.py](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/tests/e2e/test_playwright.py).
  * *Coverage*: Playwright testing for authentication flow (login/logout redirections), responsive drawers closing, sidebar navigation views (Dashboard, Orders, Inventory, Health), and Gemini AI chat Assistant inputs.

---

## 3. Mock Services & Test Isolation

* **AI assistant**: Grounded queries inside tests are routed to local mocks or mock transcription dictionaries to ensure tests do not require API quotas or fail if OpenAI/Gemini servers are offline.
* **Resend email alerts**: Mocked via `mock_send_email_alert` fixture, validating message contents locally without triggering external SMTP servers.
* **OpenWeather map API**: Mapped to standard mock HTTP responders to test temperature normalization routines and caching behavior.
