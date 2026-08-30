# Phase 8.5 — Actual Dataset Installation & Verification Report

This report confirms the download status, raw file metrics, validation results, cleaning outcomes, and database logging status of the analytical datasets introduced for Phase 9 research.

---

## 1. Dataset Availability & Exact Files Downloaded

### Dataset 1: M5 Forecasting / Walmart
* **Availability**: **Absent** (Raw directories exist but are empty).
* **Downloaded Files**: None.
* **Reason**: Kaggle competition dataset requires manual authentication via Kaggle CLI or credentials setup. It cannot be downloaded automatically without personal credentials.
* **Manual Retrieval Guide**:
  1. Access the [Kaggle M5 Forecasting Accuracy Page](https://www.kaggle.com/c/m5-forecasting-accuracy/data).
  2. Authenticate and download `calendar.csv`, `sales_train_validation.csv`, and `sell_prices.csv`.
  3. Place them in the `data/raw/m5/` folder.

### Dataset 2: UCI Online Retail II
* **Availability**: **Fully Present** (Successfully downloaded and verified).
* **Downloaded Files**:
  * Raw: `data/raw/online_retail_ii/online_retail_II.csv` (Converted from extracted `online_retail_II.xlsx` spreadsheet).
  * Processed: `data/processed/online_retail_ii/online_retail_II_processed.csv`.
* **Raw File Size**: 95,917,576 bytes (~95.9 MB).
* **Processed File Size**: 100,391,184 bytes (~100.4 MB).
* **Raw Row Count**: 1,067,371 rows.
* **Raw Column Count**: 8 columns.
* **Cleaned Row Count**: 1,029,638 rows (after deduplication).
* **Raw Columns Headers**: `Invoice,StockCode,Description,Quantity,InvoiceDate,Price,Customer ID,Country`
* **Raw File Checksum (SHA-256)**: `c161f3e453e8f6d6ea864258742f472c21cb53400c0bac8da2d09985ab56f98e`
* **Transaction Date Range**: 2009-12-01 to 2011-12-09.

---

## 2. License & Provenance

### Walmart M5 Forecasting
* **Official Source**: [Kaggle Dataset](https://www.kaggle.com/c/m5-forecasting-accuracy)
* **Publisher**: Walmart / Kaggle
* **License/Terms**: Kaggle Competition Rules (No redistribution permitted; raw data remains excluded from Git via `.gitignore`).
* **DOI**: N/A
* **Intended Use**: Analytical demand forecasting research and walk-forward validation.
* **Known Limitations**: Daily aggregated department-level sales; does not represent live smart warehouse bin movements.

### UCI Online Retail II
* **Official Source**: [UCI ML Repository](https://archive.ics.uci.edu/dataset/502/online+retail+ii)
* **Publisher**: UCI Machine Learning Repository
* **License/Terms**: Creative Commons Attribution 4.0 International (CC BY 4.0) (Permits copying/redistributing in any medium).
* **DOI**: 10.24432/C5CG6D
* **Intended Use**: SKU pricing profiling, transaction anomaly detection, and ABC inventory classification.
* **Known Limitations**: Contains customer return cancellations (denoted by invoice numbers starting with 'C') and missing Customer ID values.

---

## 3. Validation & Ingestion Results

### Ingestion Validation Summary (Run 6 - Online Retail II):
* **Parsed Raw Records**: 1,067,371 rows
* **Deduplicated Records**: 1,029,638 rows
* **Missing Column Mapping**: None (0 missing columns).
* **Null Values Found**:
  * `Description`: 4,382
  * `Customer ID`: 235,151 (backfilled with `"UNKNOWN"`)
* **Duplicates Found**: 45,937 rows.
* **Date Range**: `2009-12-01` (Start) to `2011-12-09` (End).
* **Verification Status**: `WARNING` (due to expected returns/negative quantities/cancellations, but completed processing successfully).

---

## 4. PostgreSQL Metadata Status
Analytical data runs are registered in PostgreSQL as follows (queried from active database session):
* **`dataset_sources` Table**: Seeded with metadata definition entries for `m5` and `online_retail_ii`.
* **`dataset_import_runs` Table**: Logged run 6 for `online_retail_ii` with a status of `WARNING` and record count of `1,029,638`.
* **`dataset_validation_results` Table**: Seeded validation stats for run 6 showing `1,067,371` rows and `45,937` duplicates.

---

## 5. Testing Baseline Verification

* **Data Pipeline Tests**: All **7 tests** inside `tests/test_data_pipeline.py` passed successfully.
* **Backend Unit & Integration Tests**: All **253 tests** passed successfully.
* **Playwright E2E Browser Tests**: All **3 tests** passed successfully when uvicorn development server is active.
* **Operational Database Isolation**: Confirmed that running the pipeline does not modify or inject any records into operational WMS tables (such as `Inventory`, `Orders`, `Task`, `Robot`).

---

## 6. Dependency & Package Status

* **Available packages**: `numpy==2.4.4`, `pandas==3.0.2`, `scikit-learn==1.8.0`.
* **Phase 9 Readiness**: Packages like `xgboost`, `statsmodels`, `joblib`, and `scipy` are not yet installed and must be added to `requirements.txt` in Phase 9 if needed for ML modeling.

---

## 7. Problems Encountered & Fixes

1. **UCI Dataset ID Shift**: The UCI Machine Learning Repository changed the online retail dataset ID from `554` to `502`. Corrected download URL to `https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip`.
2. **Column Name Discrepancy**: The downloaded Online Retail II CSV contains a `"Price"` column, whereas `registry.py` and `process.py` expected `"UnitPrice"`. Corrected expected schema in [`data_pipeline/registry.py`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/data_pipeline/registry.py), validation in [`data_pipeline/validate.py`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/data_pipeline/validate.py), cleaning in [`data_pipeline/process.py`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/data_pipeline/process.py), and test fixtures in [`tests/test_data_pipeline.py`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/tests/test_data_pipeline.py) to use `"Price"`. The pipeline runs successfully.

---

## 8. Final Verdict

### **PHASE 9 NOT READY**

**Reason**: While the UCI Online Retail II dataset is fully downloaded, verified, and processed, the Walmart M5 Forecasting dataset raw files are still missing from the workspace due to Kaggle authentication restrictions. Models cannot be trained until the files are placed in `data/raw/m5/`.
