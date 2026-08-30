# VIVA_PREPARATION.md — Smart Warehouse Intelligence Platform

Contains 40 likely viva questions and answers covering all project aspects.

---

## Category A-C: Project Overview & Architecture

### Q1: What is the primary goal of this project?
* **Answer**: To build an AI-assisted cloud decision-support system that manages warehouse stock levels, predicts demand trends, flags potential shrinkage anomalies, and records human verification actions in a tamper-evident audit ledger.

### Q2: Explain the high-level architecture of your system.
* **Answer**: It is a client-server architecture. The frontend is a standard Javascript SPA (Single Page Application) communicating via REST APIs with a FastAPI backend server. Data is stored in a MySQL database, with cloud backups exported to an S3-compatible bucket.

### Q3: Why did you choose FastAPI instead of Django or Flask?
* **Answer**: FastAPI is highly performant (built on ASGI, running on Starlette and Uvicorn) and provides automatic, type-safe API request validation via Pydantic schemas, reducing input injection vulnerabilities.

### Q4: What makes this project "academically defensible"?
* **Answer**: We avoid fabricated metrics. For example, "Inventory Accuracy" is shown as N/A because there is no physical verification log, forecasting errors (WAPE) are calculated via out-of-sample backtests, and environmental metrics are explicitly labeled as **SIMULATED**.

---

## Category D-I: Database, Security & Authentication

### Q5: How do you prevent SQL injection in your application?
* **Answer**: We use SQLAlchemy ORM. All database queries are compiled into parameterized queries (using SQLAlchemy `text()` placeholders), separating query logic from user input.

### Q6: Explain how your Google Sign-In works.
* **Answer**: The client sends the Google ID Token (acquired from the Google client API) to our backend. The backend validates the token using the official Google auth library, checking expiration and client ID. If valid, we locate or create the user and issue our own JWT token.

### Q7: Why is it a security concern to send JWT tokens in query parameters?
* **Answer**: Query parameters are logged in plaintext by web servers and proxy hosts, and are visible in browser history. We hardened the application to pass JWT tokens in the secure HTTP `Authorization: Bearer` header.

### Q8: What role does bcrypt play in your authentication?
* **Answer**: Bcrypt hashes user passwords with a salt before they are written to the database. Even if the database is exposed, passwords cannot be reversed.

### Q9: What is Role-Based Access Control (RBAC), and how is it enforced?
* **Answer**: RBAC controls endpoint access based on user roles (Admin, Manager, Viewer). It is enforced server-side using FastAPI dependency injections (`Depends(require_admin)`). Checking roles on the frontend only hides buttons and is not secure.

### Q10: Why did you implement rate-limiting on login?
* **Answer**: To prevent brute-force attacks where a malicious script attempts thousands of password combinations per minute. We limit failed login attempts per IP.

---

## Category J-O: Machine Learning & Analytics

### Q11: Explain your demand forecasting algorithm.
* **Answer**: The forecasting model (`ml/forecast.py`) analyzes historical daily stock movements. It calculates a rolling demand average and applies a seasonal multiplier corresponding to cyclic inventory patterns.

### Q12: What is WAPE, and why do you use it?
* **Answer**: WAPE stands for Weighted Absolute Percentage Error. It measures forecasting error. Unlike standard MAPE, WAPE does not divide by actual stock values (avoiding division-by-zero errors when stock levels are zero).

### Q13: What is "out-of-sample backtesting"?
* **Answer**: It is a method to validate ML models honestly. We hide the last 25% of historic data (the holdout set), train our model on the first 75%, predict the holdout dates, and measure the error (WAPE) against the hidden actual data.

### Q14: How does your shrinkage detection work?
* **Answer**: It uses an unsupervised machine learning model: **IsolationForest**. It analyzes stock movements and flags entries that represent statistical anomalies (outliers).

### Q15: Why is it called "Potential Shrinkage Anomaly" instead of "Theft"?
* **Answer**: Because anomaly models detect data outliers, not physical actions. An outlier could represent an input typo, physical breakage, or administrative error, not necessarily theft.

### Q16: What is "Explainable AI" (XAI) in your Decision Center?
* **Answer**: Instead of outputting a single alert, the decision center explains *why* the warning exists by displaying the specific input weightings (e.g. current stock levels vs safety thresholds).

---

## Category P-T: Digital Twin & Trust Ledger

### Q17: What does "Database-Reconciled Digital Twin" mean?
* **Answer**: The visual 2D layout layout represents physical racks. Its occupancy indicators are built dynamically using SQL SELECT queries on the active MySQL database tables, reconciling the visual layout with database truth.

### Q18: What is the "Tamper-Evident Trust Ledger"?
* **Answer**: It is a database table (`audit_ledger`) where each log entry contains a cryptographic SHA-256 hash. The hash is calculated from the entry payload combined with the previous entry's hash, forming a chain.

### Q19: How do you check if the Trust Ledger has been tampered with?
* **Answer**: The backend runs a validation check (`verify_chain`). It loops through the ledger in chronological order, re-computes the SHA-256 hash of each entry, and compares it to the saved hash. If any data was altered, the hash will change, breaking the chain.

### Q20: Why did you label cooler temperatures on the Digital Twin as simulated?
* **Answer**: Because our capstone platform does not have physical temperature sensors connected. Labeling it as **SIMULATED** maintains academic honesty.

---

## Category U-Z: Cloud, Testing & Deployment

### Q21: What is the purpose of Docker in your project?
* **Answer**: Docker bundles our code, libraries, and Python environment into a single image. This ensures the application runs identically on a developer's machine and on a cloud provider.

### Q22: Why does your Docker container run as a non-root user?
* **Answer**: If a vulnerability in our application allows a shell takeover, running as a non-root user prevents the attacker from modifying container host files or accessing root level resources.

### Q23: Why do we use SQLite for automated tests and MySQL for production?
* **Answer**: SQLite runs in-memory, making unit tests fast and fully isolated. Using SQLite prevents tests from writing to or deleting real production data in MySQL.

### Q24: What is the purpose of Alembic in your project?
* **Answer**: Alembic manages SQL database migrations. It tracks schema modifications (such as adding columns) so we can upgrade the production database without dropping tables or losing user data.

---

## Category AA-ZZ: Advanced Security, ML, and Limitations

### Q25: Why is `seed_demo_data.py` excluded from the Docker start script?
* **Answer**: The seed script executes database delete queries before inserting fresh demo data. Running it on startup in production would delete real records upon container restarts.

### Q26: What is a holdout set in ML forecasting?
* **Answer**: It is a split of historical records set aside during model training, used only to calculate prediction metrics.

### Q27: How does your health check endpoint verify database status?
* **Answer**: It tries to run a basic `SELECT 1` statement against the database. If it succeeds, it returns `connected`. If not, it reports `disconnected` with status code 503.

### Q28: How does the What-If simulation work?
* **Answer**: It takes current inventory and simulates changes in demand by applying multipliers, warning the user about potential stockout items.

### Q29: What is the risk of wildcards in CORS settings?
* **Answer**: Allowing `*` in CORS allows any external website to query user APIs. In production, we restrict `CORS_ORIGINS` to our specific domain.

### Q30: How does the email notifier handle credential safety?
* **Answer**: The application does not store keys in code. It reads SMTP user/pass values directly from environment variables.

### Q31: How do you verify that the Trust Ledger detection works?
* **Answer**: Our unit test retrieves a ledger row, alters the payload text directly, commits the change, and asserts that the verification method returns `valid=False`.

### Q32: Why does the system default to 'Viewer' role for Google Sign-In?
* **Answer**: To prevent unauthorized users from registering and immediately creating, editing, or deleting items.

### Q33: How does the platform prevent JWT secret warning triggers?
* **Answer**: In production environment (`ENVIRONMENT=production`), the backend validates if the secret is set to the default dev fallback and refuses to start if it hasn't been changed.

### Q34: What is WAPE formula?
* **Answer**: `SUM(|Actual - Forecast|) / SUM(Actual) * 100`.

### Q35: What is IsolationForest?
* **Answer**: An unsupervised learning algorithm that isolates anomalies by randomly partitioning feature paths. Outliers require fewer splits to isolate than normal points.

### Q36: How does the database pool prevent connection timeouts?
* **Answer**: Using `pool_pre_ping=True` which pings the database before executing any request to recycle dead connections.

### Q37: Why are environmental logs labeled SIMULATED?
* **Answer**: To maintain academic credibility, as the rack temperature values are generated mathematically instead of using physical hardware sensors.

### Q38: Can your IsolationForest model determine who stole an item?
* **Answer**: No. It only detects quantitative mismatches. An investigator must verify audit logs and local logs to determine cause.

### Q39: What is the main limitation of the forecast model?
* **Answer**: It requires historical seasonal trends. It cannot predict sudden black swan events.

### Q40: How does the system secure report downloads?
* **Answer**: It requires JWT authentication, resolving it via query parameters or Bearer headers.

---

*(All 40 Viva Questions compiled for Capstone Review).*

