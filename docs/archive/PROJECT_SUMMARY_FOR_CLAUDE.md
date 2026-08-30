# 📦 Cloud-Based Smart Warehouse Automation and Inventory Analytics Platform (v3)

> **Prompt Context**: Copy and paste this document into Claude to ask for architectural feedback, code optimization, security audit, and feature expansion ideas.

---

## 🚀 1. Project Overview & Objective

This platform is a **Cloud Computing Capstone Project** for Smart Warehouse Automation & Inventory Analytics. It integrates a real **MySQL relational database**, **JWT-based authentication**, **Google Sign-In SSO**, **2FA Email OTP Passkey verification for Admin creation**, **tamper-evident SHA-256 audit ledgers**, **ML-driven demand forecasting & shrinkage detection**, **AWS S3 / Backblaze B2 cloud backup**, and a **responsive Single Page Application (SPA)** dashboard.

---

## 🛠️ 2. Tech Stack

- **Backend**: Python 3.14, FastAPI, SQLAlchemy ORM, PyJWT, Bcrypt, Pydantic, Pandas, NumPy, Scikit-learn
- **Database**: MySQL Server 8.0 (`warehouse_db`)
- **Frontend**: HTML5, CSS3 (Vanilla Design System with Dark/Light Mode), JavaScript (ES6+ SPA), Chart.js, Leaflet Maps
- **Alerts & Integrations**: SMTP Email (Gmail App Password), Twilio SMS API, AWS S3 / Backblaze B2 Storage (`boto3`)
- **DevOps / Deployment**: Docker, Docker Compose (`docker-compose.yml`), Render (`render.yaml`)

---

## 📁 3. Codebase Structure

```
warehouse_v3/
├── backend/
│   ├── main.py              # FastAPI app, API routes, JWT auth, Admin creation, Reports export
│   ├── database.py          # SQLAlchemy MySQL connection pooling & session management
│   ├── models.py            # ORM models (User, Warehouse, Item, StockMovement, ShrinkageFlag, AccessLog, Ledger)
│   ├── auth.py              # Bcrypt hashing, JWT generation, OAuth2 bearer dependency, require_admin
│   ├── schemas.py           # Pydantic request & response schemas
│   ├── audit_ledger.py      # Tamper-evident SHA-256 hash-chained audit ledger
│   ├── notifications.py     # Real SMTP Email & Twilio SMS notification dispatchers
│   ├── cloud_storage.py     # AWS S3 / Backblaze B2 backup and snapshot management
│   ├── reports.py           # ReportLab PDF, OpenPyXL Excel, CSV report generator engine
│   ├── init_db.py           # Database tables creation & initial admin bootstrap
│   └── seed_demo_data.py    # Realistic Kaggle-style logistics dataset seeder (1,050 movements, 5 WHs)
│
├── frontend/
│   ├── index.html           # Single Page Application HTML (Login, App Shell, Modals, OTP Verification)
│   ├── css/style.css        # Responsive design system, CSS variables, dark/light theme, animation rules
│   └── js/
│       ├── api.js           # API fetch client wrapper with automatic JWT header handling
│       ├── app.js           # Core SPA navigation, Dashboard charts, Stock recording, Admin OTP workflow
│       └── apps.js          # Launcher apps logic (Loss Investigation, Smart Transfer, Storage Optimizer, etc.)
│
├── ml/
│   ├── forecast.py          # 14-day demand forecasting (Trend + Seasonality model)
│   ├── shrinkage_detector.py # Isolation Forest & Z-score shrinkage anomaly detection
│   ├── shrinkage_insights.py # Root-cause clustering & cost-ranking for theft/loss incidents
│   ├── transfer_optimizer.py # Inter-warehouse stock rebalancing advisor
│   ├── access_anomaly.py    # Security access anomaly detection on user activity logs
│   ├── storage_tiering.py   # Cloud S3/Standard vs Glacier cost tiering optimizer
│   ├── autoscaling_sim.py   # Fixed vs Auto-scaling cloud infrastructure cost simulator
│   ├── nl_query.py          # Natural language database Q&A assistant
│   ├── event_calendar.py    # Festival & seasonal demand multiplier adjustments
│   └── alert_notifier.py    # Automated daily digest message generator
│
├── Dockerfile               # Containerization spec
├── docker-compose.yml       # MySQL + FastAPI orchestration spec
├── render.yaml              # Cloud deployment specification
├── requirements.txt         # Python dependencies
├── README.md                # Project documentation & viva setup guide
└── .env.example             # Environment configuration template
```

---

## 🔒 4. Key Security & Architecture Features

1. **Authentication & Authorization**:
   - Standard Username/Password with Bcrypt hashing.
   - Google Account SSO (`/auth/google-login`).
   - Role-based Access Control (`admin` vs `user` permissions).

2. **2FA Email OTP Verification for Admin Creation**:
   - Adding a new Administrator requires initiating a request (`POST /admin/request-add-admin`).
   - Generates a 6-digit one-time passkey (OTP) valid for 10 minutes.
   - Dispatches an SMTP Email to `harsha200797@gmail.com`.
   - Creation is finalized only after verifying the 6-digit OTP (`POST /admin/confirm-add-admin`).

3. **Tamper-Evident SHA-256 Audit Ledger**:
   - Every system mutation (warehouse creation, item addition, admin creation) creates a hash-chained block (`previous_hash` + `payload` -> `current_hash`).
   - Re-checking the chain flags any direct manual database tampering.

4. **Analytics & Cloud Optimization**:
   - Inter-warehouse transfer suggestions to minimize purchase orders.
   - Cloud S3 Storage Tiering optimization (Standard vs Infrequent Access vs Glacier).
   - Server Auto-Scale Simulator to analyze cloud host cost efficiency.

---

## ❓ Prompts You Can Ask Claude

Copy this entire file and paste it into Claude along with one of these prompt questions:

### 1. Code Optimization & Refactoring
> *"Here is the codebase structure and architecture for my Smart Warehouse Automation platform. Please review the architecture and suggest 5 high-impact performance optimizations and refactoring improvements for the FastAPI backend and Vanilla JS frontend."*

### 2. Security Audit & Improvements
> *"Please conduct a security audit on my auth flow (JWT, Google SSO, 2FA Email OTP, Audit Ledger). What potential vulnerabilities exist and how can I harden the system for production deployment?"*

### 3. Feature Expansion & AI Enhancements
> *"What novel cloud computing or machine learning features can I add to this warehouse platform to impress my capstone review panel? Suggest 3 advanced features with code examples."*

### 4. Database & Microservices Scaling
> *"How can I transition this monolithic FastAPI + MySQL warehouse app into a scalable microservices / serverless architecture on AWS (Lambda, ECS, RDS Aurora, SQS)?"*
