# Smart Warehouse Inventory Analytics and Decision Support System Using AI and Cloud Computing

SIMATS Engineering | Capstone Project — Cloud Computing & AI
H. Harshavardhan (192511171), Chintha Abhilash Reddy (192525462) — Team 4

---

## 1. Project Title
**Smart Warehouse Inventory Analytics and Decision Support System Using AI and Cloud Computing**

---

## 2. Problem Statement
Modern logistics and supply chain networks face three critical challenges:
1. **Inefficient Decision Support**: Inventory managers rely on static spreadsheets, leading to stockouts or costly overstocking due to lack of explainable forecasting.
2. **Inventory Discrepancy (Shrinkage)**: Loss from administrative errors, damage, or unrecorded events goes unnoticed, silently inflating costs.
3. **Data Integrity & Compliance**: Access logs and operational records can be manipulated offline in database systems, making audits unreliable.

---

## 3. Objectives
* Design a **Cloud-Based Warehouse Analytics** platform reconciling physical stock levels with relational database structures.
* Deploy statistical ML forecasting with **Out-of-Sample Backtesting (WAPE)** to assure model reliability.
* Apply unsupervised anomaly detection (**IsolationForest**) to isolate potential shrinkage discrepancies.
* Construct a **Tamper-Evident Hash-Chained Audit Ledger** to log verification histories.
* Enforce robust, server-side role constraints and secure OAuth SSO sessions.

---

## 4. Key Features
- **Executive Analytics Dashboard**: Consolidates 8 database-sourced KPI cards, alert banners, and trend graphs.
- **Database-Reconciled Digital Twin**: Interactive 2D layout rendering warehouse occupancy grids.
- **Explainable AI Decision Center**: Presents forecast-driven stock alerts alongside interactive evidence breakdowns.
- **Human-in-the-Loop Workflow**: Allows managers to approve, reject, or modify recommendations.
- **Tamper-Evident Ledger**: A linear cryptographic SHA-256 block chain securing event verification logs.
- **Cloud Storage Adapter**: Automates database backups to S3-compatible cloud storage.

---

## 5. System Architecture

The data flows from operational transactions to ML prediction, manager review, and cryptographic logging:

```
[Single Page Client SPA]
          ↓ (REST API / JWT Session)
   [FastAPI Service]
     ├─ [JWT / Google OAuth SSO]
     ├─ [PostgreSQL Operational DB]
     ├─ [ML Analytics (forecast / IsolationForest)]
     ├─ [SHA-256 Hash Chain Signer]
     └─ [S3/B2 Backup Object Adapter]
```

---

## 6. Technology Stack
* **Frontend**: HTML5, Vanilla CSS3 (Sleek dark/light theme, custom glassmorphism components), Vanilla JavaScript (ES6), Lucide Icons, Chart.js.
* **Backend**: FastAPI (Python), Uvicorn ASGI Server, Pydantic (data validation).
* **Database**: PostgreSQL, SQLAlchemy 2.0 (ORM), Alembic (migrations), SQLite (isolated unit testing).
* **Machine Learning**: Scikit-Learn (IsolationForest anomalies), Pandas, Numpy.
* **Security & Cloud**: PyJWT, Google Auth Library, Boto3 (AWS S3/Backblaze B2), SMTP, Upstash Redis, CloudAMQP RabbitMQ, Celery, Sentry, Resend, Google Gemini API REST.

---

## 7. Database Architecture
The platform is backed by a structured relational schema in PostgreSQL:
- `users`: Stores login records, bcrypt password hashes, and user roles (`admin`, `manager`, `viewer`).
- `warehouses` & `items`: Metadata tables defining storage terminals and product parameters.
- `stock_movements`: Log of inventory additions, deductions, and current closing stock.
- `ai_recommendations`: Operational recommendations list (PENDING, APPROVED, REJECTED).
- `audit_ledger`: SHA-256 linear chain records backing the trust verification system.
- `access_log`: Logs logins and admin events for access anomaly analysis.

---

## 8. AI/ML Components
1. **Demand Forecasting (`ml/forecast.py`)**: Uses historical daily movement statistics combined with seasonal multipliers. Evaluated using out-of-sample backtesting on the last 25% of data.
2. **Shrinkage Anomaly Detection (`ml/shrinkage_detector.py`)**: Unsupervised IsolationForest model flagging sudden, unrecorded discrepancies between actual stock levels and recorded actions.

---

## 9. Digital Twin Explanation
The **Database-Reconciled Digital Twin** displays warehouse bay grids using a dynamic HTML5 Canvas. Rack grid colors adjust based on SQL stock queries:
* Green: Adequate Stock
* Orange: Warning
* Red: Critical Reorder required
Environmental telemetry (such as temperatures) is explicitly labeled as **SIMULATED** to clarify the boundaries of the sensor implementation.

---

## 10. AI Decision Center
Provides a single review panel for all recommendations. It lists:
* Recommendation title (e.g. "Critical Stockout Warning")
* Priority Score (computed programmatically from lead time and deficit)
* Evidence factors (numerical criteria in plain English)

---

## 11. Human-in-the-Loop Workflow
Recommendations require a human action:
1. **Approve**: Backend generates a synchronized transaction entry in `stock_movements`.
2. **Reject**: Flags the alert as processed without taking action.
3. **Modify**: Allows stock levels adjustment.
Every decision updates the `ai_recommendations` state machine and writes a record to the Trust Ledger.

---

## 12. Trust Ledger
Backs compliance using linear cryptography. Each row stores a SHA-256 hash computed as:
`Hash_N = SHA256(Record_N_Payload + Hash_{N-1})`
Modifying any database record directly breaks the chain, causing `/audit/verify` to fail.

---

## 13. Cloud Integration
* **Backblaze B2 Storage**: Uploads daily database logical backup snapshots to Backblaze B2 with size and checksum checks.
* **Upstash Redis**: Handles forecast caching and Celery results.
* **CloudAMQP RabbitMQ**: Event-driven queuing backend.
* **Sentry**: FastAPI error logging.
* **Resend**: Transactional email dispatch.
* **Google Gemini API**: WMS Operational explainers.
* **Google OAuth**: Single Sign-on integration.

---

## 14. Security
- **Bcrypt**: All local user passwords are salted and hashed.
- **Server-Side RBAC**: Authorization checks occur at endpoint dependencies (e.g. `/run-shrinkage-detection` checks for admin).
- **Hardened JWTs**: Token signatures validation and expiries (120 minutes) are strictly enforced in production.
- **2FA OTP**: Required when creating new admin accounts.

---

## 15. Testing
* **Isolated Pytest Suite**: Full suite of unit and integration tests run on an isolated, transactional in-memory SQLite database, avoiding database pollution.
* **Smoke Testing**: 23 GET/POST API validations run against the active service instance.

---

## 16. Deployment
* **Docker Container**: Multi-stage build running under a non-root `appuser` (UID 1001) for privilege restriction.
* **Render**: Configured with live health checks (`GET /health`) and production settings in `render.yaml`.

---

## 17. Data Source & Provenance
* The application runs on a **Synthetic Demonstration Dataset** initialized dynamically for demonstrations.
* Telemetry sensor values are marked as **SIMULATED**.
* Dashboard KPI metrics are labeled: `ACTUAL — PostgreSQL`, `FORECAST — ML Model`, or `CALCULATED`.

---

## 18. Known Limitations
- Environmental conditions are mathematically simulated (no physical IoT sensors).
- Seeding data is destructive and should only be run in local/development modes.
- Google OAuth and SMTP alerts require external credentials configured in `.env` to operate.
- Ledger validation is in-memory at request time rather than distributed.

---

## 19. Local Setup
1. **Database Setup**:
   ```sql
   CREATE DATABASE warehouse_db;
   CREATE USER postgres WITH PASSWORD 'YOUR_SECURE_DB_PASSWORD';
   GRANT ALL PRIVILEGES ON DATABASE warehouse_db TO postgres;
   ```
2. **Python Setup**:
   ```bash
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your database password
   ```
3. **Initialize & Run**:
   ```bash
   python backend/init_db.py
   python backend/seed_demo_data.py  # Local dev only
   uvicorn backend.main:app --reload
   ```

---

## 20. Environment Variables
See `.env.example` for the complete list. Essential variables:
* `ENVIRONMENT`: `development` or `production`
* `DATABASE_URL`: Connection URL for your PostgreSQL server
* `JWT_SECRET_KEY`: Cryptographic signing key

---

## 21. API Overview
- `POST /auth/login` - Authenticate & obtain JWT
- `GET /analytics/dashboard` - Consolidated KPI metrics
- `GET /inventory/{id}` - Retrieve current warehouse inventory
- `GET /forecast/{wh}/{item}` - Run forecast & backtesting
- `GET /audit/verify` - Check hash-chain integrity
- `POST /ai/recommendations/{id}/action` - Record decision

---

## 22. Demo Workflow
1. Log in as `admin`.
2. Inspect consolidated KPIs on the Executive Dashboard.
3. Open the Digital Twin layout grid.
4. Review low-stock forecasts and backtest WAPE.
5. In AI Decision Center, click **Approve** on a recommendation.
6. Verify that a block was appended to the **Trust Ledger** and run the validation integrity scanner.
