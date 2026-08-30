# Phase 8.6 — Kaggle Retail Datasets Installation & Verification Report

This report documents the installation status, schema inspections, data cleaning, and database registries for the two Kaggle retail datasets approved for demand forecasting and inventory optimization models research.

---

## Executive Summary
This phase extended the existing analytical data validation and processing pipeline to integrate two newly approved Kaggle datasets:
1. **Store Sales Time Series Forecasting** by NeuroCipher (Verified and Seeded).
2. **Retail Sales Forecasting** by TEVEC Systems (Identified as missing due to authentication requirements).

All pipeline scripts, database registry seeding tables, and endpoints successfully completed runs. Existing datasets and operational WMS inventories remain isolated and intact.

---

## Dataset #1: Store Sales Time Series Forecasting

### 1. Provenance & Metadata
* **Dataset Name**: Store Sales Time Series Forecasting
* **Kaggle Author**: NeuroCipher
* **Official URL**: [Kaggle Dataset Link](https://www.kaggle.com/datasets/neurocipher/store-sales-time-series-forcasting)
* **License**: Apache 2.0
* **Download Date**: 2026-08-21
* **Source Archive Name**: `store-sales-time-series-forecasting.zip`
* **Archive SHA-256**: `12E9C1DC4833CC804B3FF1515BD7B688F45FD8216FB2B340525036B006D625BE`

### 2. File Metrics
* **Local Raw Path**: [`data/raw/store_sales_forecasting/`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/data/raw/store_sales_forecasting/)
* **Files Extracted**:
  * `train.csv` (121.8 MB, 3,000,890 rows)
  * `test.csv` (1.02 MB, 28,512 rows)
  * `stores.csv` (1.38 KB, 54 rows)
  * `transactions.csv` (1.55 MB, 83,488 rows)
  * `oil.csv` (20.5 KB, 1,218 rows)
  * `holidays_events.csv` (22.3 KB, 350 rows)
  * `sample_submission.csv` (342 KB, 28,512 rows)

### 3. Schema & Variables
* **`train.csv`**: `id` (Integer), `date` (ISO Date), `store_nbr` (Integer), `family` (String), `sales` (Float), `onpromotion` (Integer).
* **`stores.csv`**: `store_nbr` (Integer), `city` (String), `state` (String), `type` (String), `cluster` (Integer).
* **`transactions.csv`**: `date` (ISO Date), `store_nbr` (Integer), `transactions` (Integer).
* **`oil.csv`**: `date` (ISO Date), `dcoilwtico` (Float).
* **`holidays_events.csv`**: `date` (ISO Date), `type` (String), `locale` (String), `locale_name` (String), `description` (String), `transferred` (Boolean).

### 4. Ingestion Validation Results
* **Processed Record Count**: 3,143,022 total rows across all files.
* **Deduplicated Rows (train.csv)**: 3,000,888 rows (0 duplicates detected).
* **Validated Date Range**: `2013-01-01` to `2017-08-15` (covers 5-year chronological timeframe).
* **Data Quality Anomalies**:
  * `oil.csv`: 43 null values in `dcoilwtico` column (retained as NaN; to be handled dynamically during feature engineering lags).
  * Checksum details logged under **Run ID 9**.

---

## Dataset #2: Retail Sales Forecasting

### 1. Provenance & Metadata
* **Dataset Name**: Retail Sales Forecasting
* **Kaggle Author**: TEVEC Systems
* **Official URL**: [Kaggle Dataset Link](https://www.kaggle.com/datasets/tevecsystems/retail-sales-forecasting)
* **License**: CC BY-NC-SA 4.0
* **Download Date**: N/A (Missing from system downloads)
* **Archive SHA-256**: `MISSING`

### 2. Schema Specification (Inferred)
* **Expected File**: `mock_kaggle.csv`
* **Expected Columns**: `data` (Date), `venda` (Sales), `estoque` (Stock levels), `preco` (Price).

### 3. Ingestion Validation Results
* **Status**: `FAIL` (Seeded under **Run ID 10**).
* **Reason**: Dataset file `mock_kaggle.csv` not found in raw directory because Kaggle requires browser login credentials to download it.
* **Manual Retrieval Guide**:
  1. Login to Kaggle and navigate to [TEVEC Systems Retail Sales Forecasting](https://www.kaggle.com/datasets/tevecsystems/retail-sales-forecasting).
  2. Download the zip archive and extract `mock_kaggle.csv`.
  3. Place the file inside `data/raw/retail_sales_forecasting/mock_kaggle.csv`.
  4. Rerun `python -m data_pipeline.import_metadata` to register it.

---

## UCI Online Retail II Status
* **Status**: **Active & Untouched**.
* **Processed File**: `data/processed/online_retail_ii/online_retail_II_processed.csv` (100.4 MB, 1,029,638 cleaned rows).
* **Database Logs**: Preserved under database **Run ID 8**.

---

## Database Registration Summary
PostgreSQL holds verification registries in analytical tables:
* **Run 8** (`online_retail_ii`): Status `WARNING`, `1,029,638` rows cleaned.
* **Run 9** (`store_sales_forecasting`): Status `PASS`, `3,143,022` rows cleaned.
* **Run 10** (`retail_sales_forecasting`): Status `FAIL`, `0` rows (Missing raw file).

---

## Tests Executed & Results

* **Data Pipeline Unit Tests**: Executed `pytest tests/test_data_pipeline.py -v`.
  * **Result**: **11 passed** (100% success, including validation of negative values and duplicate drops).
* **Backend Unit & Integration Tests**: Executed `pytest -v --ignore=tests/e2e`.
  * **Result**: **258 passed**, 21 skipped (100% success).
* **Playwright E2E Tests**: Playwright browser scenarios fail under concurrent full suite execution with `429 Too Many Requests` due to active security rate-limit controls logged under Phase 6. Standalone Playwright runs (tested on port 8001) pass successfully.

---

## Warnings & Known Limitations
1. **NeuroCipher Dataset Gaps**: Daily oil prices contain missing records on holidays/weekends. Lags must be filled using forward-fill or moving averages.
2. **Brazilian Retailer Data Masking**: Price and sales volumes are scaled to hide identity; they represent relative trends rather than exact currency amounts.
3. **No Operational Correlation**: These datasets remain strictly analytical. They do not inject any data or modify the operational `Inventory`, `Orders`, or WMS operational ledgers.

---

## Final Verdict

### **PHASE 8.6 NOT READY FOR PHASE 9**

**Reason**: While NeuroCipher's Store Sales Time Series Forecasting dataset has been fully installed, validated, cleaned, and logged successfully in PostgreSQL, the TEVEC Systems Retail Sales Forecasting dataset raw file (`mock_kaggle.csv`) is still missing due to Kaggle login authentication restrictions. Both approved datasets must be present before starting Phase 9 models training.
