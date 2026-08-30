# Smart Warehouse Platform — PostgreSQL Migration Guide

This document describes the design, deployment steps, and rollback plans for migrating the database from MySQL to PostgreSQL.

---

## 1. Why PostgreSQL was Selected

PostgreSQL is a powerful, open-source object-relational database system. For this project, PostgreSQL offers several critical advantages:
* **Advanced Concurrency Control**: MVCC (Multi-Version Concurrency Control) provides superior performance for highly concurrent inventory read/write operations without locking tables.
* **Complex Query Optimization**: Better planner optimization for analytical reporting queries, such as live stock levels, forecast trend analyses, and digital twin reconciliation.
* **Strict Constraints & Typings**: Enhanced support for standard constraints, check parameters, and foreign key cascading.
* **PaaS Ecosystem Support**: Managed databases on cloud providers like Render.com are natively optimized for PostgreSQL, providing easy setup, automated clustering, scale-up options, and built-in replication.

---

## 2. Architecture Comparison

### Current MySQL Architecture
```
[Vanilla Frontend]
       ↓ (HTTP)
[FastAPI Server] (Runs locally or deployed)
       ↓ (SQLAlchemy ORM via PyMySQL)
[Local / Managed MySQL Database]
```

### Target PostgreSQL Architecture
```
[Vanilla Frontend]
       ↓ (HTTP)
[FastAPI Server] (Deployed on Render)
       ├── [Managed PostgreSQL Database] (For Users, Warehouses, Items, Stock Movements, etc.)
       └── [Backblaze B2 S3 Storage] (For Images, CSV Exports, and logical db backups)
```

---

## 3. Required Dependencies

The driver package `psycopg2-binary` has been added to `requirements.txt` to support connections:
```txt
psycopg2-binary==2.9.9
```

This binary package bundles standard compilation prerequisites (like `libpq` and `ssl`), making local installs and Docker/Render build stages fast and reliable.

---

## 4. Environment Variables Configuration

To run PostgreSQL, update your `.env` or Render environment configurations:

| Key | Description | Example Value |
|---|---|---|
| `DATABASE_URL` | SQLAlchemy connection URL (Primary configuration) | `postgresql://warehouse_app:secret@localhost:5432/warehouse_db` |
| `TARGET_DATABASE_URL` | Destination PostgreSQL URL (Used by migration script) | `postgresql://warehouse_app:secret@localhost:5432/warehouse_db` |

*Note: For backward compatibility, if `DATABASE_URL` is not set, the application defaults to standard local MySQL connection variables (`DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`).*

---

## 5. Local Schema and Database Migration

Follow these steps to migrate your local schema and transfer existing data:

### Step A: Start your local target PostgreSQL database
Ensure you have created the target database (e.g. `warehouse_db`) and user privileges.

### Step B: Run Alembic migrations to construct the target schema
In your shell, set the environment `DATABASE_URL` to point to your PostgreSQL target and run the upgrades:
```powershell
$env:DATABASE_URL="postgresql://warehouse_app:secret@localhost:5432/warehouse_db"
alembic upgrade head
```
This runs the full baseline schema configuration and tables without injecting dummy data.

### Step C: Execute the data migration script
Use the custom migration tool to copy all historical records (including JWT accounts, audit logs, and stock transactions) from SQLite/MySQL to PostgreSQL:
```powershell
python backend/migrate_to_postgres.py --source-url "sqlite:///./warehouse.db" --target-url "postgresql://warehouse_app:secret@localhost:5432/warehouse_db"
```
The script will copy data in strict topological order to respect foreign key constraint scopes, and automatically reset PostgreSQL auto-incrementing serial sequences afterwards.

### Step D: Validate the data
Verify the counts match perfectly:
```powershell
python backend/migrate_to_postgres.py --source-url "sqlite:///./warehouse.db" --target-url "postgresql://warehouse_app:secret@localhost:5432/warehouse_db" --verify-only
```

---

## 6. Docker Local Setup

To test the application locally running under Docker + PostgreSQL:
1. Modify `docker-compose.yml` to define a PostgreSQL service:
   ```yaml
   db:
     image: postgres:15
     container_name: warehouse_platform_db
     environment:
       POSTGRES_USER: warehouse_app
       POSTGRES_PASSWORD: password123
       POSTGRES_DB: warehouse_db
     ports:
       - "5432:5432"
   ```
2. Update your `.env` file to set `DATABASE_URL=postgresql://warehouse_app:password123@db:5432/warehouse_db`.
3. Rebuild and launch the containers:
   ```bash
   docker-compose up --build
   ```

---

## 7. Render Production Deployment Configuration

Render makes deploying a FastAPI + PostgreSQL web app extremely easy using a blueprint file (`render.yaml`).

### Environment Variables to Configure on Render Dashboard
All managed databases on Render provide a dynamic connection string. Make sure the following keys are set in your web service:
1. `DATABASE_URL`: Set dynamically from the PostgreSQL service.
2. `JWT_SECRET_KEY`: Automatically generated base64 key.
3. `GOOGLE_CLIENT_ID` & `GOOGLE_CLIENT_SECRET`: Your Google credentials.
4. `SMTP_USER` & `SMTP_PASSWORD`: Your Gmail SMTP configurations.
5. `AWS_ACCESS_KEY_ID` & `AWS_SECRET_ACCESS_KEY`: Backblaze S3 credentials.

---

## 8. Rollback Action Plan (Fallback to MySQL)

If any critical blocker is identified in the PostgreSQL service, you can return to MySQL immediately:
1. **Restore `.env` Configuration**: Remove the `DATABASE_URL` variable to let the app fall back to MySQL environment values, or set `DATABASE_URL=mysql+pymysql://...`.
2. **Reverse render.yaml**: Restore the individual MySQL connection parameters.
3. **Restart the Server**: Restart your uvicorn service. The application will instantly connect back to your intact MySQL database.
