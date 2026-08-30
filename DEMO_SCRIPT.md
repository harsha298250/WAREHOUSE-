# DEMO_SCRIPT.md — Smart Warehouse Intelligence Platform

An 8–12 minute step-by-step faculty demonstration guide.

---

## Demo Step Overview

```
1. Authenticate (JWT/OAuth)
        ↓
2. Inspect KPI Dashboard
        ↓
3. View Digital Twin Layout
        ↓
4. Load Demand Forecast
        ↓
5. Check Shrinkage Anomalies
        ↓
6. AI Decisions & Approval
        ↓
7. Verify Trust Ledger
        ↓
8. Run What-If Simulation
```

---

## Step-by-Step Script

### Step 1: Authentication & Entry (1.5 Minutes)
* **What to do**:
  1. Open the login page (`http://localhost:8000`).
  2. Log in using admin credentials (`admin` / `Admin@123`).
  3. Show the sidebar navigation loading.
* **What to say**:
  > "I will begin by logging in as an administrator. The application uses server-side JWT authentication. Every subsequent API request passes this token in the header. We also support Google Sign-In SSO, which automatically assigns a safe 'Viewer' role to new users, preventing unauthorized database edits."
* **Why it matters**: Demonstrates security hardening, server-side RBAC, and standard OAuth integration.

---

### Step 2: Consolidated Executive Dashboard (2 Minutes)
* **What to do**:
  1. Show the main dashboard view.
  2. Point out the KPI cards: **Inventory Value**, **Warehouse Utilization**, **Forecast Error**, and **Audit Ledger Status**.
  3. Scroll down to show the **Priority Alerts** pane.
* **What to say**:
  > "This is our database-synchronized dashboard. Every KPI is computed dynamically from actual MySQL transactions. To maintain academic honesty, notice that 'Inventory Accuracy' is explicitly marked as 'N/A' because the database does not contain physical verification count records. Instead of fabricating a fake 99% metric, we document the coverage gap honestly."
* **Why it matters**: Highlights database reconciliation, honest reporting, and consolidated operational visibility.

---

### Step 3: Database-Reconciled Digital Twin (1.5 Minutes)
* **What to do**:
  1. Click **Digital Twin** in the sidebar.
  2. Hover over the racks to display the stock levels.
  3. Hover over the temperature sensor overlay to show the simulated environment feeds.
* **What to say**:
  > "Next, I will open the Database-Reconciled Digital Twin. This view queries the current stock counts in MySQL and maps them to a visual rack layout. The layout utilization matches the database in real-time. Notice the environmental values: they are clearly labeled as **SIMULATED** since no physical hardware telemetry is active."
* **Why it matters**: Visualizes physical layout utilizing real SQL queries while declaring simulated values honestly.

---

### Step 4: Out-of-Sample Demand Forecasting (1.5 Minutes)
* **What to do**:
  1. Navigate to the **Forecast** page (or click an item in the dashboard's stockout list).
  2. Show the 14-day demand forecast chart.
  3. Focus on the metric card: **Backtest WAPE (79.3%)**.
* **What to say**:
  > "Here is the 14-day demand forecasting screen. We do not claim perfect predictive accuracy. The system programmatically measures forecast error using out-of-sample holdout backtesting on the last 25% of historic data. This yields a transparent, mathematically computed WAPE (Weighted Absolute Percentage Error), which is visible on the KPI card."
* **Why it matters**: Demonstrates academic rigor in forecasting validation rather than hardcoding fake success metrics.

---

### Step 5: Potential Shrinkage Anomalies (1.5 Minutes)
* **What to do**:
  1. Click **Loss Investigation** (or Shrinkage page).
  2. Point out the list of flagged outliers.
  3. Highlight the label: **Potential Shrinkage Anomaly**.
* **What to say**:
  > "Our security layer monitors inventory deviations using an IsolationForest outlier model. Outliers are classified as 'Potential Shrinkage Anomalies'. We avoid calling this 'Theft' because ML can only detect numerical discrepancies, not legal intent."
* **Why it matters**: Demonstrates statistical classification and honest labeling of security events.

---

### Step 6: AI Decision Center & Trust Ledger Verification (2 Minutes)
* **What to do**:
  1. Navigate to the **AI Decision Center** in the sidebar.
  2. Review a pending recommendation (e.g. "Low Stock Warning").
  3. Explain the "Evidence Factor Breakdown" cards.
  4. Click **Approve**.
  5. Go to the **Trust Ledger** view.
  6. Point out the newly appended block showing status `APPROVED` with its SHA-256 hash.
  7. Click the **Run Ledger Verification** button.
* **What to say**:
  > "We use a human-in-the-loop workflow. AI recommendations are explainable, displaying input factor weightings. When I click 'Approve', the backend updates the database and writes a record to the tamper-evident audit ledger. Let's run the integrity verification: it recalculates the linear SHA-256 hash chains of all records to verify that no database values have been modified offline."
* **Why it matters**: Shows the complete flow: AI -> Explainable recommendations -> Human Choice -> Tamper-Evident Ledger sync.
