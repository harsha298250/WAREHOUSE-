"""
data_pipeline/provisioner.py — Robust dataset provisioner and resolver for production deployments.

Ensures required processed dataset files exist using absolute paths relative to the project root.
If datasets are missing on clean production deployments (e.g. Render), provisions lightweight,
schema-compliant seed datasets so Forecasting, ABC Analysis, and Demand Anomaly detection function reliably.
"""
import os
import logging
from pathlib import Path
import pandas as pd
import numpy as np

logger = logging.getLogger("warehouse.provisioner")

# Resolve absolute paths relative to project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"


def ensure_store_sales_dataset():
    """Provisions store_sales_forecasting processed CSV files if missing."""
    ds_dir = PROCESSED_DIR / "store_sales_forecasting"
    os.makedirs(ds_dir, exist_ok=True)
    train_file = ds_dir / "train_processed.csv"
    oil_file = ds_dir / "oil_processed.csv"

    if not train_file.exists():
        logger.info("Provisioning seed train_processed.csv for store_sales_forecasting...")
        dates = pd.date_range(end=pd.Timestamp.now(), periods=180, freq="D")
        families = ["AUTOMOTIVE", "BEVERAGES", "BREAD/BAKERY", "CLEANING", "DAIRY", "GROCERY I", "POULTRY", "PRODUCE"]
        records = []
        np.random.seed(42)
        id_counter = 1
        for date_str in dates.strftime("%Y-%m-%d"):
            for fam in families:
                for store in [1, 2, 3]:
                    base_sales = np.random.uniform(50, 500)
                    onprom = int(np.random.choice([0, 1], p=[0.8, 0.2]))
                    records.append({
                        "id": id_counter,
                        "date": date_str,
                        "store_nbr": store,
                        "family": fam,
                        "sales": round(base_sales, 2),
                        "onpromotion": onprom,
                        "city": "Quito" if store == 1 else "Guayaquil",
                        "state": "Pichincha" if store == 1 else "Guayas",
                        "type": "A",
                        "cluster": 10
                    })
                    id_counter += 1
        df = pd.DataFrame(records)
        df.to_csv(train_file, index=False)
        logger.info("Provisioned %d rows into %s", len(df), train_file)

    if not oil_file.exists():
        logger.info("Provisioning seed oil_processed.csv for store_sales_forecasting...")
        dates = pd.date_range(end=pd.Timestamp.now(), periods=180, freq="D")
        records = []
        base_oil = 65.0
        for d in dates:
            base_oil += np.random.normal(0, 0.5)
            records.append({"date": d.strftime("%Y-%m-%d"), "dcoilwtico": round(max(30.0, base_oil), 2)})
        df = pd.DataFrame(records)
        df.to_csv(oil_file, index=False)
        logger.info("Provisioned %d rows into %s", len(df), oil_file)


def ensure_online_retail_dataset():
    """Provisions online_retail_ii processed CSV file if missing."""
    ds_dir = PROCESSED_DIR / "online_retail_ii"
    os.makedirs(ds_dir, exist_ok=True)
    csv_file = ds_dir / "online_retail_II_processed.csv"

    if not csv_file.exists():
        logger.info("Provisioning seed online_retail_II_processed.csv...")
        np.random.seed(42)
        dates = pd.date_range(end=pd.Timestamp.now(), periods=90, freq="D")
        stock_codes = ["85123A", "71053", "84406B", "84029G", "85099B", "22423", "47566", "20725"]
        descriptions = [
            "WHITE HANGING HEART T-LIGHT HOLDER", "WHITE METAL LANTERN", "CREAM CUPID HEARTS COAT HANGER",
            "KNITTED UNION FLAG HOT WATER BOTTLE", "JUMBO BAG RED RETROSPOT", "REGENCY CAKESTAND 3 TIER",
            "PARTY BUNTING", "LUNCH BAG RED RETROSPOT"
        ]
        records = []
        inv_id = 500000
        for date_str in dates.strftime("%Y-%m-%d %H:%M:%S"):
            for _ in range(15):
                idx = np.random.randint(0, len(stock_codes))
                qty = int(np.random.randint(1, 50))
                price = float(round(np.random.uniform(1.25, 18.50), 2))
                records.append({
                    "Invoice": str(inv_id),
                    "StockCode": stock_codes[idx],
                    "Description": descriptions[idx],
                    "Quantity": qty,
                    "InvoiceDate": date_str,
                    "Price": price,
                    "Customer ID": str(np.random.randint(12000, 18000)),
                    "Country": "United Kingdom",
                    "IsCancelled": False
                })
                inv_id += 1
        df = pd.DataFrame(records)
        df.to_csv(csv_file, index=False)
        logger.info("Provisioned %d rows into %s", len(df), csv_file)


def ensure_mlzc_dataset():
    """Provisions retail_sales_forecasting (MLZC) processed CSV files if missing."""
    ds_dir = PROCESSED_DIR / "retail_sales_forecasting"
    os.makedirs(ds_dir, exist_ok=True)
    sales_file = ds_dir / "sales_processed.csv"
    catalog_file = ds_dir / "catalog_processed.csv"

    if not sales_file.exists():
        logger.info("Provisioning seed sales_processed.csv for MLZC dataset...")
        np.random.seed(42)
        dates = pd.date_range(end=pd.Timestamp.now(), periods=60, freq="D")
        items = ["SKU_MLZC_001", "SKU_MLZC_002", "SKU_MLZC_003", "SKU_MLZC_004", "SKU_MLZC_005"]
        records = []
        for d in dates.strftime("%Y-%m-%d"):
            for item in items:
                qty = int(np.random.randint(10, 200))
                price = float(round(np.random.uniform(9.99, 49.99), 2))
                records.append({
                    "date": d,
                    "item_id": item,
                    "quantity": qty,
                    "price_base": price
                })
        df = pd.DataFrame(records)
        df.to_csv(sales_file, index=False)
        logger.info("Provisioned %d rows into %s", len(df), sales_file)

    if not catalog_file.exists():
        logger.info("Provisioning seed catalog_processed.csv for MLZC dataset...")
        cat_df = pd.DataFrame([
            {"item_id": "SKU_MLZC_001", "dept_name": "Electronics & Sensors"},
            {"item_id": "SKU_MLZC_002", "dept_name": "Industrial Components"},
            {"item_id": "SKU_MLZC_003", "dept_name": "Packaging Supplies"},
            {"item_id": "SKU_MLZC_004", "dept_name": "Safety & Apparel"},
            {"item_id": "SKU_MLZC_005", "dept_name": "Automotive Hardware"}
        ])
        cat_df.to_csv(catalog_file, index=False)
        logger.info("Provisioned %d catalog rows into %s", len(cat_df), catalog_file)


def ensure_m5_dataset():
    """Provisions m5 processed CSV files if missing."""
    ds_dir = PROCESSED_DIR / "m5"
    os.makedirs(ds_dir, exist_ok=True)
    sales_file = ds_dir / "sales_train_validation_processed.csv"

    if not sales_file.exists():
        logger.info("Provisioning seed sales_train_validation_processed.csv for M5...")
        np.random.seed(42)
        items = ["HOBBIES_1_001", "HOBBIES_1_002", "HOUSEHOLD_1_001", "FOODS_1_001"]
        records = []
        for item in items:
            row = {"id": f"{item}_CA_1_validation", "item_id": item, "dept_id": item.rsplit("_", 2)[0], "cat_id": item.split("_")[0], "store_id": "CA_1", "state_id": "CA"}
            for day in range(1, 91):
                row[f"d_{day}"] = int(np.random.poisson(lam=5))
            records.append(row)
        df = pd.DataFrame(records)
        df.to_csv(sales_file, index=False)
        logger.info("Provisioned %d rows into %s", len(df), sales_file)


def ensure_all_datasets_provisioned():
    """Main entrypoint to ensure all production dataset files exist."""
    try:
        ensure_store_sales_dataset()
        ensure_online_retail_dataset()
        ensure_mlzc_dataset()
        ensure_m5_dataset()
        logger.info("Dataset provisioning check complete — all processed dataset files verified.")
    except Exception as e:
        logger.error("Dataset provisioning failed: %s", e)
