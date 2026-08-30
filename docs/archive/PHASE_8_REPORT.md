# Phase 8 — Legitimate External Datasets & Data Pipeline Report

This report summarizes the design, implementation, and verification findings for the introduction of legitimate external datasets and the analytical data validation/processing pipeline.

---

## A. What Was Inspected
* **FastAPI Backend Routers**: Evaluated the routing schema for potential endpoints configuration and located `/analytics/overview` as the mount pattern.
* **SQLAlchemy Database Models**: Inspected [`backend/models.py`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/backend/models.py) to assess how to safely structure analytical dataset runs tables without corrupting live inventory.
* **Frontend Routing & Design Layout**: Reviewed index.html navigation and `app.js` navigation hooks.
* **Existing Tests Framework**: Evaluated conftest.py base setups and verified transactional rollbacks strategy.

---

## B. Datasets Used & Provenance

### 1. Walmart M5 Forecasting Dataset
* **Dataset Name**: M5 Forecasting / Walmart
* **Official Source**: Kaggle
* **Reference URL**: [Kaggle M5 Forecasting Accuracy](https://www.kaggle.com/c/m5-forecasting-accuracy)
* **Version**: 1.0
* **Access/Download Date**: 2026-08-21
* **License**: Kaggle Competition Rules
* **DOI**: N/A
* **Original Publisher**: Walmart Inc. / Kaggle
* **Description**: Historical daily unit sales by store and department, calendar event tags, and weekly sell prices.
* **Intended Use**: Outbound sales demand model research and walk-forward verification.
* **Known Limitations**: Daily aggregated department-level sales; does not represent live smart warehouse bin movements.

### 2. UCI Online Retail II
* **Dataset Name**: UCI Online Retail II
* **Official Source**: UCI Machine Learning Repository
* **Reference URL**: [Online Retail II on UCI](https://archive.ics.uci.edu/ml/datasets/Online+Retail+II)
* **Version**: 1.0
* **Access/Download Date**: 2026-08-21
* **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
* **DOI**: 10.24432/C5CG6D
* **Original Publisher**: UCI Machine Learning Repository
* **Description**: Real transaction-level UK online retail store transactions.
* **Intended Use**: Analytical SKU clustering and ABC inventory prioritization profiling.
* **Known Limitations**: Contains customer returns/cancellations (denoted by Invoice codes starting with 'C') and missing Customer ID values.

---

## C. Raw/Processed Folder Structure
Massive raw datasets are ignored by Git via `.gitignore`. The registry layout is configured as follows:
```
data/
    raw/
        m5/                     <- Local location for calendar.csv, sales_train_validation.csv, sell_prices.csv
        online_retail_ii/       <- Local location for online_retail_II.csv

    processed/
        m5/                     <- Cleaned processed M5 CSVs
        online_retail_ii/       <- Cleaned processed Online Retail II CSV

    metadata/
        dataset_registry.json   <- Central SHA-256 and metadata definition parameters
```

---

## D. Deterministic Cleaning & Normalization Rules

### 1. UCI Online Retail II
* **CustomerID Backfilling**: Instead of dropping rows, missing Customer IDs are backfilled with `'UNKNOWN'` to preserve aggregate sales quantities.
* **Returns Identification**: Retains cancelled/returned transactions (Invoice starting with 'C') but tags them with a boolean attribute `IsCancelled = True`.
* **Sanity Checks**: Discards transactions with negative prices (`UnitPrice < 0`) or non-cancelled transaction quantities <= 0.
* **Timestamp Formatting**: Normalizes `InvoiceDate` to `YYYY-MM-DD HH:MM:SS` ISO standard.
* **Duplicates Filter**: Drops exact duplicate rows from the final file.

### 2. Walmart M5 Forecasting
* **Pricing Sanity**: Discards records with invalid sell prices (`sell_price <= 0`).
* **Timestamp Formatting**: Formats calendar dates to `YYYY-MM-DD` ISO standard.

---

## E. PostgreSQL Database Integration
Registered new tables to hold application metadata and import execution results:
* `dataset_sources`: Seeded with fixed registry entries.
* `dataset_import_runs`: Stores imports timestamps, record count, execution status (`SUCCESS` / `FAILED`), and file SHA-256 checksums.
* `dataset_validation_results`: Stores row counts, missing column/null mappings, duplicate counts, and validation text logs.

---

## F. Files Changed
* [`backend/models.py`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/backend/models.py): Added analytical datasets tables.
* [`backend/routers/analytics.py`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/backend/routers/analytics.py): Implemented the secure `/analytics/datasets` endpoint.
* [`frontend/index.html`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/frontend/index.html): Added "Datasets" navigation sidebar link.
* [`frontend/js/api.js`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/frontend/js/api.js): Added the `getDatasets` API helper.
* [`frontend/js/app.js`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/frontend/js/app.js): Implemented datasets metadata rendering panel inside `renderDatasets(el)`.
* [`data_pipeline/registry.py`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/data_pipeline/registry.py): [NEW] Ingestion registry config.
* [`data_pipeline/validate.py`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/data_pipeline/validate.py): [NEW] Data checks diagnostics.
* [`data_pipeline/process.py`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/data_pipeline/process.py): [NEW] Preprocessing cleaning operations.
* [`data_pipeline/import_metadata.py`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/data_pipeline/import_metadata.py): [NEW] Registry DB seeding and runs logger.
* [`tests/test_data_pipeline.py`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/tests/test_data_pipeline.py): [NEW] Pipeline verification test cases.

---

## G. Testing & Verification Evidence

### 1. Ingestion Pipeline Verification
Running the pipeline locally outputs:
```
Seeding dataset sources into database...

=== Ingesting M5 Forecasting ===
Recording import run for dataset: m5...
Logged import run 1 and validation result for m5 successfully.

=== Ingesting UCI Online Retail II ===
Recording import run for dataset: online_retail_ii...
Logged import run 2 and validation result for online_retail_ii successfully.
```

### 2. Unit and Integration Test Counts
Executed data pipeline tests verifying duplicate filtering, date parsing, column counts, and database metadata seeding:
* Run command: `pytest tests/test_data_pipeline.py -v`
* Result: **7 Passed** (100% success).

Executed full integration regression suite:
* Run command: `pytest -v --ignore=tests/e2e` (ignoring E2E tests requiring live servers)
* Result: **253 Passed** (0 failures, 21 skipped).

### 3. Browser E2E Playwright Tests
Executed E2E browser tests:
* Run command: `pytest tests/test_playwright_scenarios.py tests/test_playwright_accessibility_responsive.py tests/test_playwright_system_health.py -v`
* Result: **3 Passed** (100% success).

---

## H. Phase 9 Carry-Forward Items
* Implementation of actual walk-forward demand forecasting models using the processed calendar, sales, and sell prices datasets.
* Implementation of the inventory ABC classification model based on cumulative sales value metrics.
* Implementation of the transaction anomaly scoring algorithm using Isolation Forest workflows.
* Replenishment order optimization calculations based on forecasts and safety stocks.
