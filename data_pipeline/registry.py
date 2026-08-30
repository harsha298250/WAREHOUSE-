import os
import json
import hashlib
from typing import Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
METADATA_DIR = os.path.join(DATA_DIR, "metadata")

REGISTRY_PATH = os.path.join(METADATA_DIR, "dataset_registry.json")

# Metadata schemas for legimate external datasets
DATASET_METADATA = {
    "m5": {
        "dataset_name": "M5 Forecasting / Walmart",
        "official_source": "Kaggle",
        "source_url": "https://www.kaggle.com/c/m5-forecasting-accuracy",
        "version": "1.0",
        "access_download_date": "2026-08-21",
        "license": "Kaggle Competition Rules",
        "doi": "N/A",
        "publisher": "Walmart / Kaggle",
        "description": "Historical sales and demand forecasting research dataset from Walmart stores across multiple states (CA, TX, WI). Represents items, stores, calendar event indicators, and sell prices.",
        "intended_use": "Outbound sales/demand forecasting model research and walk-forward validation.",
        "known_limitations": "Aggregated daily-level sales by department/store; does not represent live smart warehouse bin movements.",
        "expected_files": [
            "calendar.csv",
            "sales_train_validation.csv",
            "sell_prices.csv"
        ],
        "local_raw_path": os.path.join(RAW_DIR, "m5"),
        "local_processed_path": os.path.join(PROCESSED_DIR, "m5")
    },
    "online_retail_ii": {
        "dataset_name": "UCI Online Retail II",
        "official_source": "UCI Machine Learning Repository",
        "source_url": "https://archive.ics.uci.edu/ml/datasets/Online+Retail+II",
        "version": "1.0",
        "access_download_date": "2026-08-21",
        "license": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
        "doi": "10.24432/C5CG6D",
        "publisher": "UCI Machine Learning Repository",
        "description": "Real transaction-level data containing all transactions occurring between 01/12/2009 and 09/12/2011 for a UK-based and registered non-store online retail.",
        "intended_use": "Customer transactions analysis, SKU pricing profiling, and ABC inventory optimization profiling.",
        "known_limitations": "Contains cancelled orders (denoted by Invoice codes starting with 'C'), missing CustomerIDs, and unit price adjustments.",
        "expected_files": [
            "online_retail_II.csv"  # Normal expected raw file
        ],
        "local_raw_path": os.path.join(RAW_DIR, "online_retail_ii"),
        "local_processed_path": os.path.join(PROCESSED_DIR, "online_retail_ii")
    },
    "store_sales_forecasting": {
        "dataset_name": "Store Sales Time Series Forecasting / NeuroCipher",
        "official_source": "Kaggle",
        "source_url": "https://www.kaggle.com/datasets/neurocipher/store-sales-time-series-forcasting",
        "version": "1.0",
        "access_download_date": "2026-08-21",
        "license": "Apache 2.0",
        "doi": "N/A",
        "publisher": "NeuroCipher / Kaggle",
        "description": "Store sales historical demand dataset from a Brazilian retailer. Features stores, transactions, oil prices, holiday event flags, and daily product family sales.",
        "intended_use": "Multi-store time series demand forecasting model research and product family analysis.",
        "known_limitations": "Protects retailer identity via masked sales values; subject to gaps in daily oil price reports.",
        "expected_files": [
            "train.csv",
            "test.csv",
            "stores.csv",
            "transactions.csv",
            "oil.csv",
            "holidays_events.csv",
            "sample_submission.csv"
        ],
        "local_raw_path": os.path.join(RAW_DIR, "store_sales_forecasting"),
        "local_processed_path": os.path.join(PROCESSED_DIR, "store_sales_forecasting")
    },
    "retail_sales_forecasting": {
        "dataset_name": "MLZC Compet '24 / Retail Demand Forecast",
        "official_source": "Kaggle",
        "source_url": "https://www.kaggle.com/datasets",
        "version": "2024",
        "access_download_date": "2026-08-21",
        "license": "CC BY-NC-SA 4.0",
        "doi": "N/A",
        "publisher": "MLZC / Kaggle",
        "description": "Historical multi-store retail sales, price changes, and discount histories used for demand forecasting models.",
        "intended_use": "Demand forecasting, price sensitivity analysis.",
        "known_limitations": "Anonymized items and store formats.",
        "expected_files": [
            "sales.csv",
            "online.csv",
            "stores.csv",
            "price_history.csv",
            "discounts_history.csv",
            "markdowns.csv",
            "catalog.csv",
            "actual_matrix.csv"
        ],
        "local_raw_path": os.path.join(RAW_DIR, "retail_sales_forecasting"),
        "local_processed_path": os.path.join(PROCESSED_DIR, "retail_sales_forecasting")
    }
}

# Validation expected columns
EXPECTED_COLUMNS = {
    "m5": {
        "calendar.csv": ["date", "wm_yr_wk", "weekday", "wday", "month", "year", "d"],
        "sales_train_validation.csv": ["id", "item_id", "dept_id", "cat_id", "store_id", "state_id"], # dynamic sales columns d_1, d_2...
        "sell_prices.csv": ["store_id", "item_id", "wm_yr_wk", "sell_price"]
    },
    "online_retail_ii": {
        "online_retail_II.csv": ["Invoice", "StockCode", "Description", "Quantity", "InvoiceDate", "Price", "Customer ID", "Country"]
    },
    "store_sales_forecasting": {
        "train.csv": ["id", "date", "store_nbr", "family", "sales", "onpromotion"],
        "test.csv": ["id", "date", "store_nbr", "family", "onpromotion"],
        "stores.csv": ["store_nbr", "city", "state", "type", "cluster"],
        "transactions.csv": ["date", "store_nbr", "transactions"],
        "oil.csv": ["date", "dcoilwtico"],
        "holidays_events.csv": ["date", "type", "locale", "locale_name", "description", "transferred"],
        "sample_submission.csv": ["id", "sales"]
    },
    "retail_sales_forecasting": {
        "sales.csv": ["Unnamed: 0", "date", "item_id", "quantity", "price_base", "sum_total", "store_id"],
        "online.csv": ["Unnamed: 0", "date", "item_id", "quantity", "price_base", "sum_total", "store_id"],
        "stores.csv": ["Unnamed: 0", "store_id", "division", "format", "city", "area"],
        "price_history.csv": ["Unnamed: 0", "date", "item_id", "price", "code", "store_id"],
        "discounts_history.csv": ["Unnamed: 0", "date", "item_id", "sale_price_before_promo", "sale_price_time_promo", "promo_type_code", "doc_id", "number_disc_day", "store_id"],
        "markdowns.csv": ["Unnamed: 0", "date", "item_id", "normal_price", "price", "quantity", "store_id"],
        "catalog.csv": ["Unnamed: 0", "item_id", "dept_name", "class_name", "subclass_name", "item_type", "weight_volume", "weight_netto", "fatness"],
        "actual_matrix.csv": ["Unnamed: 0", "item_id", "date", "store_id"]
    }
}

def calculate_checksum(file_path: str) -> str:
    """Calculates SHA-256 checksum of a file."""
    if not os.path.isfile(file_path):
        return ""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256.update(byte_block)
    return sha256.hexdigest()

def ensure_directories():
    """Ensures all raw, processed, and metadata directories exist."""
    dirs_to_make = [
        RAW_DIR, PROCESSED_DIR, METADATA_DIR,
        os.path.join(RAW_DIR, "m5"), os.path.join(RAW_DIR, "online_retail_ii"),
        os.path.join(RAW_DIR, "store_sales_forecasting"), os.path.join(RAW_DIR, "retail_sales_forecasting"),
        os.path.join(PROCESSED_DIR, "m5"), os.path.join(PROCESSED_DIR, "online_retail_ii"),
        os.path.join(PROCESSED_DIR, "store_sales_forecasting"), os.path.join(PROCESSED_DIR, "retail_sales_forecasting")
    ]
    for d in dirs_to_make:
        os.makedirs(d, exist_ok=True)

def save_registry():
    """Saves the metadata definitions to the metadata registry JSON file."""
    ensure_directories()
    # Update checksums dynamically for any files that exist
    for key, meta in DATASET_METADATA.items():
        checksums = {}
        raw_path = meta["local_raw_path"]
        for f in meta["expected_files"]:
            full_path = os.path.join(raw_path, f)
            if os.path.isfile(full_path):
                checksums[f] = calculate_checksum(full_path)
        meta["file_checksums"] = checksums
    
    # Write to file
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(DATASET_METADATA, f, indent=4)
