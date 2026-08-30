# Legitimate Analytical Datasets Documentation

This document describes the external, public datasets introduced in Phase 8 for research, demand forecasting model training, and analytical model validation.

> [!IMPORTANT]
> **Strict Operational Separation Statement**
> External datasets are used strictly for research, analytics and ML preparation. They do NOT represent the live warehouse's operational inventory and never corrupt or overwrite the production PostgreSQL database.

---

## 1. Dataset Registry

### Dataset A: M5 Forecasting / Walmart
* **Official Source**: Kaggle - M5 Forecasting - Accuracy
* **Source URL**: [M5 Forecasting on Kaggle](https://www.kaggle.com/c/m5-forecasting-accuracy)
* **License**: Kaggle Competition Rules
* **Publisher**: Walmart / Kaggle
* **DOI**: N/A
* **Description**: Daily unit sales data by item and store (departments, category, state CA/TX/WI) accompanied by calendar event flags and pricing details.
* **Intended Use**: Outbound demand/sales forecasting research and backtest validation.
* **Known Limitations**: Aggregated daily-level store sales; does not represent live, bin-level real-time warehouse robotic movements.

### Dataset B: UCI Online Retail II
* **Official Source**: UCI Machine Learning Repository
* **Source URL**: [Online Retail II on UCI](https://archive.ics.uci.edu/ml/datasets/Online+Retail+II)
* **DOI**: [10.24432/C5CG6D](https://doi.org/10.24432/C5CG6D)
* **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
* **Publisher**: UCI Machine Learning Repository
* **Description**: All transactions occurring between 01/12/2009 and 09/12/2011 for a UK-based registered non-store online retail.
* **Intended Use**: Retail transaction analysis, SKU pricing profiling, and ABC inventory optimization research.
* **Known Limitations**: Includes cancellations (invoice code starting with 'C'), missing Customer IDs, and adjustments.

---

## 2. Ingestion & Downloading Instructions

To prevent storing large datasets in Git, raw files are ignored by `.gitignore`.

### UCI Online Retail II
Run the download helper to automatically download and extract:
```bash
# This downloads and extracts the Online Retail II CSV into data/raw/online_retail_ii/
python -m data_pipeline.import_metadata
```
If the automatic script fails due to network constraints:
1. Download the zip file from [UCI Online Retail II](https://archive.ics.uci.edu/static/public/554/online+retail+ii.zip).
2. Extract `online_retail_II.csv` to `data/raw/online_retail_ii/online_retail_II.csv`.

### M5 Forecasting
Due to Kaggle login restrictions:
1. Access [M5 Forecasting Competition](https://www.kaggle.com/c/m5-forecasting-accuracy/data).
2. Download `calendar.csv`, `sales_train_validation.csv`, and `sell_prices.csv`.
3. Extract and place these files in `data/raw/m5/`.

---

## 3. Data Validation & Processing Pipeline

### Pipeline Flow
```
Raw Dataset File -> validation.py -> process.py -> import_metadata.py -> PostgreSQL Runs Log
```

### Deterministic Cleaning Rules
1. **Deduplication**: Exact duplicates are removed from both datasets.
2. **Missing Customer IDs**: Fills missing Customer IDs with `'UNKNOWN'` (does not drop the transactions to preserve sales volume aggregates).
3. **Invalid Prices/Quantities**: Filters out negative prices (`UnitPrice < 0`) and non-cancelled quantities (`Quantity <= 0` when invoice is not a return).
4. **Cancelled Invoices**: Retains returns (starting with 'C') but flags them via boolean column `IsCancelled`.
5. **ISO Date Normalization**: Standardizes transaction date strings to `YYYY-MM-DD HH:MM:SS`.

---

## 4. Reproducing Ingestion

Run the complete pipeline validation and cleaning:
```bash
# Set Python path
$env:PYTHONPATH="."

# Run validation and cleaning metadata import
python -m data_pipeline.import_metadata
```
This inserts metadata entries, SHA-256 checksums, and validation counts into `dataset_sources`, `dataset_import_runs`, and `dataset_validation_results` tables in PostgreSQL.
