# ☁️ Cloud MySQL Database Setup Guide

This guide walks you through migrating the Smart Warehouse Automation platform database connection from your local MySQL instance to a cloud-hosted MySQL provider (such as Aiven for MySQL or AWS RDS) securely.

---

## 🔑 Environment Configuration

To point your application to a cloud MySQL instance, you must configure the environment variables in your active `.env` file located in the project root:

```env
# ---------------- MySQL Connection Details ----------------
DB_HOST=your-cloud-db-endpoint.aivencloud.com
DB_PORT=12345
DB_NAME=defaultdb
DB_USER=avnadmin
DB_PASSWORD=your_cloud_password

# ---------------- SSL Configuration (Required) ----------------
# The absolute path to your downloaded database CA certificate (.pem file)
DB_SSL_CA=C:\Users\harsh\Downloads\warehouse_project_v3\warehouse_v3\ca.pem
```

---

## 🛡️ Setup Steps by Cloud Provider

### Option A: Aiven for MySQL (Recommended / Free Dev Tier Available)
1. Sign up/log in at [aiven.io](https://aiven.io/).
2. Create a new **MySQL** service (the free hobby/developer tier is sufficient).
3. On your Aiven service dashboard under **Connection Information**:
   * Copy the Host, Port, User, and Password into your `.env` file.
   * Click the link next to **CA Certificate** to download the `ca.pem` certificate.
4. Save the `ca.pem` file in your project directory (it is ignored by Git automatically via `*.pem` in `.gitignore`).
5. Paste the absolute path of `ca.pem` into the `DB_SSL_CA` field in your `.env` file.

### Option B: AWS RDS MySQL
1. Log in to your AWS Console and launch a MySQL DB instance under **Amazon RDS** (Free Tier eligible).
2. Download the global AWS RDS CA certificate bundle (`global-bundle.pem`) from the [AWS RDS Official SSL/TLS documentation](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.SSL.html).
3. Copy the RDS DB Endpoint (Host), Port, Database Name, Master Username, and Master Password into `.env`.
4. Save `global-bundle.pem` in your project folder, and point `DB_SSL_CA` to its absolute path.

---

## 🧱 Setup and Seeding the Cloud DB

To initialize your tables and seed rich Kaggle logistics data on your new cloud database, run the following commands sequentially:

```powershell
# 1. Create tables on the cloud database (includes connection retry mechanisms)
$env:PYTHONPATH = "."; python backend/init_db.py

# 2. Seed the database with high-fidelity logistics simulation dataset
$env:PYTHONPATH = "."; python backend/seed_demo_data.py
```

---

## 📴 Offline Development / Fallback to Local MySQL

The database configuration in `backend/database.py` is fully resilient and backward-compatible. To switch back to your local MySQL database:

1. Open your `.env` file.
2. Comment out or clear the cloud-specific variables and clear `DB_SSL_CA`:
   ```env
   # Local MySQL Fallbacks
   DB_HOST=localhost
   DB_PORT=3306
   DB_NAME=warehouse_db
   DB_USER=warehouse_app
   DB_PASSWORD=YOUR_SECURE_DB_PASSWORD
   DB_SSL_CA=
   ```
3. The server will automatically detect the empty `DB_SSL_CA` and connect to the local MySQL instance without using SSL arguments.
