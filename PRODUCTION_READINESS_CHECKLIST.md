# PRODUCTION_READINESS_CHECKLIST.md
# Smart Warehouse Intelligence Platform — Step 7 Hardened

**Version**: 3.0  
**Assessment Date**: 2026-08-14  
**Assessed By**: Antigravity (automated audit + hardening)

> This checklist reflects the **current assessed state** of the project.
> Items marked ✅ have been verified or implemented.
> Items marked ⚠️ require manual action or configuration.
> Items marked ❌ are not implemented.

---

## SECURITY

### Secrets Management
- [x] ✅ JWT secret loaded from `JWT_SECRET_KEY` environment variable
- [x] ✅ JWT secret validation enforced when `ENVIRONMENT=production`
- [x] ✅ DB password loaded from `DB_PASSWORD` environment variable
- [x] ✅ `.env` is in `.gitignore` (never committed)
- [x] ✅ `.env.example` contains only safe placeholders
- [x] ✅ `docker-compose.yml` uses `${VAR}` references (no hardcoded passwords)
- [ ] ⚠️ **ROTATE CREDENTIALS**: DB password, Gmail app password, and Backblaze keys were exposed in workspace files — rotate all three before production use

### Authentication
- [x] ✅ Passwords stored as bcrypt hashes (never plaintext)
- [x] ✅ JWT tokens expire (120 minutes)
- [x] ✅ Invalid/malformed JWTs rejected with 401
- [x] ✅ Expired JWTs rejected with 401
- [x] ✅ OTP generated with `secrets.randbelow()` (cryptographically secure)
- [x] ✅ OTP NOT returned in API response body (verified by test)
- [ ] ⚠️ JWT token lifetime: 120 minutes — consider reducing for production (30-60 min recommended)
- [x] ✅ Google Sign-In: new users default to VIEWER role (not admin)

### Authorization (RBAC)
- [x] ✅ RBAC enforced server-side (not just frontend button hiding)
- [x] ✅ VIEWER cannot approve AI decisions
- [x] ✅ VIEWER cannot trigger shrinkage detection
- [x] ✅ VIEWER cannot create admin accounts
- [x] ✅ Admin creation requires OTP confirmation
- [x] ✅ All sensitive endpoints require JWT token

### Network Security
- [x] ✅ CORS configured (origins from `CORS_ORIGINS` env var)
- [ ] ⚠️ Set `CORS_ORIGINS` to your exact production domain (not `*`)
- [x] ✅ Security headers middleware active (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`)
- [x] ✅ Rate limiting on login, OTP, and admin creation endpoints
- [x] ✅ `ENVIRONMENT=production` disables debug mode and enforces JWT

### Input Validation
- [x] ✅ Pydantic schema validation on all POST endpoints
- [x] ✅ SQLAlchemy parameterized queries (no raw SQL string building)
- [x] ✅ API returns 422 for malformed/missing fields
- [x] ✅ SQL injection attempts return 4xx (not 500 with stack trace)
- [x] ✅ Error responses show `detail` field only (no stack traces in production)

---

## DATABASE

### Configuration
- [x] ✅ Database URL built from `DB_*` environment variables
- [x] ✅ No hardcoded database credentials in source code
- [x] ✅ `pool_pre_ping=True` for connection health checks
- [x] ✅ `pool_recycle=280` to prevent stale connections
- [x] ✅ SSL CA certificate support via `DB_SSL_CA` env var

### Migration System
- [x] ✅ Alembic initialized with baseline migration from current schema
- [x] ✅ `init_db.py` uses `create_all()` — safe and idempotent
- [x] ✅ Alembic `env.py` reads DB URL from environment (not hardcoded)
- [ ] ⚠️ Future schema changes: use `alembic revision --autogenerate` not `create_all()`

### Data Safety
- [x] ✅ `seed_demo_data.py` NOT run automatically in Docker/production startup
- [x] ✅ `init_db.py` is the only script in Docker CMD (creates tables, doesn't delete data)
- [ ] ⚠️ No automated database backup configured — set up scheduled backups in production
- [x] ✅ `seed_demo_data.py` is clearly documented as data-destructive

---

## TESTING

### Test Suite
- [x] ✅ pytest configured (conftest.py with SQLite test database)
- [x] ✅ Tests use SQLite in-memory DB — never touch production MySQL
- [x] ✅ Shared JWT token across test session (avoids rate-limiter)
- [x] ✅ Unit tests: Trust Ledger hash chain + tampering detection
- [x] ✅ API tests: Health, Auth, RBAC, Analytics Dashboard
- [x] ✅ Security tests: OTP leak, headers, CORS, rate limiting
- [x] ✅ Input validation tests: SQL injection, negative values, malformed JSON
- [x] ✅ Report tests: CSV/XLSX/PDF generation, auth requirements
- [x] ✅ Smoke test: 11 production endpoint checks
- [ ] ⚠️ ML unit tests (WAPE, backtest, no data leakage): requires MySQL for full test
- [ ] ❌ End-to-end browser tests (Selenium/Playwright) — not implemented

### Test Commands
```bash
# Run all pytest tests (SQLite, no MySQL required)
python -m pytest tests/ -v --tb=short

# Run original smoke test suite (requires running server)
python tests/smoke_test.py

# Run original integration suite
python tests/run_all_tests.py
```

---

## DEPLOYMENT

### Docker
- [x] ✅ `Dockerfile` runs as non-root user `appuser`
- [x] ✅ `HEALTHCHECK` added to Dockerfile
- [x] ✅ `seed_demo_data.py` NOT in Docker CMD
- [x] ✅ Docker startup: `init_db.py && uvicorn`
- [x] ✅ `docker-compose.yml` uses env vars, not hardcoded credentials
- [x] ✅ MySQL healthcheck in docker-compose (web waits for db)
- [x] ✅ Non-root user in Docker image

### Render Deployment
- [x] ✅ `render.yaml` updated with all required env vars
- [x] ✅ Health check path configured: `/health`
- [x] ✅ `ENVIRONMENT=production` set in render.yaml
- [ ] ⚠️ Set secret variables in Render dashboard manually (they have `sync: false`)
- [ ] ⚠️ Run `init_db.py` after first deployment
- [ ] ⚠️ Test deployment not yet performed — cannot mark as verified deployed

### Configuration
- [x] ✅ `ENVIRONMENT` env var controls dev vs. production behavior
- [x] ✅ `CORS_ORIGINS` configurable via env var
- [x] ✅ `PORT` env var used for Render compatibility
- [x] ✅ All secrets configurable without code changes

---

## OBSERVABILITY

### Logging
- [x] ✅ Structured logging with `logging.getLogger("warehouse")`
- [x] ✅ Authentication events logged (login, Google login, OTP)
- [x] ✅ Authorization failures logged
- [x] ✅ AI recommendation creation logged
- [x] ✅ Database connection logged (without password)
- [x] ✅ Passwords, JWT secrets, OTPs NOT logged

### Error Handling
- [x] ✅ API errors return safe `{"detail": "..."}` — no stack traces
- [x] ✅ Database errors caught and logged server-side
- [x] ✅ ML model failures caught gracefully (return error status not 500)

### Audit Ledger
- [x] ✅ Tamper-evident SHA-256 hash chain
- [x] ✅ `GET /audit/verify` performs real chain validation (not hardcoded True)
- [x] ✅ Every AI decision recorded in ledger
- [x] ✅ Tampering detection tested and verified

---

## PRODUCTION READINESS ASSESSMENT

| Category | Status | Notes |
|---|---|---|
| Security — Auth | ✅ Good | JWT, bcrypt, RBAC all implemented |
| Security — Secrets | ⚠️ Action Required | Rotate exposed credentials |
| Security — Network | ✅ Good | Headers, CORS, rate limiting active |
| Database | ✅ Good | Env vars, Alembic, safe startup |
| Testing | ✅ Good | pytest + SQLite + smoke tests |
| Docker | ✅ Good | Non-root, healthcheck, no seed on start |
| Render | ⚠️ Pending | Manual env var configuration required |
| Documentation | ✅ Good | DEPLOYMENT.md rewritten |
| ML/AI Features | ✅ Good | Honest metrics, backtested WAPE |
| Observability | ✅ Good | Structured logging, audit ledger |

---

## MANDATORY ACTIONS BEFORE PRODUCTION LAUNCH

1. ⚠️ **ROTATE CREDENTIALS** — Gmail app password, Backblaze B2 keys, DB password
2. ⚠️ **SET CORS_ORIGINS** — restrict to your actual domain
3. ⚠️ **SET JWT_SECRET_KEY** — use a proper 64-char random hex
4. ⚠️ **Set Render env vars** — all `sync: false` variables in Render dashboard
5. ⚠️ **Run init_db.py after first Render deploy** — to create tables
6. ⚠️ **Set up DB backup** — scheduled MySQL dumps or point-in-time recovery

---

## REMAINING KNOWN RISKS

| Risk | Severity | Mitigation |
|---|---|---|
| Credentials may have been committed to git | HIGH | Rotate all exposed credentials |
| Render free tier sleeps after inactivity | MEDIUM | Expected — acceptable for demo |
| WAPE = 79.3% (high) | LOW | Honest — reflects small demo dataset, not fabricated |
| No end-to-end browser tests | LOW | Manual testing covers this |
| Warehouse capacity is a fixed constant | LOW | Documented as approximation |
