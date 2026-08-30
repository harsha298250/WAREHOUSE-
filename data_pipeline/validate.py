import os
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, Tuple

from data_pipeline.registry import DATASET_METADATA, EXPECTED_COLUMNS, calculate_checksum, ensure_directories

def validate_m5_dataset() -> Tuple[str, Dict[str, Any]]:
    """
    Validates M5 Forecasting dataset.
    Since raw M5 is Kaggle-based, we look for calendar.csv, sales_train_validation.csv, and sell_prices.csv.
    """
    meta = DATASET_METADATA["m5"]
    raw_path = meta["local_raw_path"]
    expected_files = meta["expected_files"]
    
    report_lines = []
    report_lines.append("DATASET VALIDATION REPORT")
    report_lines.append("=" * 40)
    report_lines.append(f"Dataset: M5 Forecasting / Walmart")
    report_lines.append(f"Validation Timestamp: {datetime.now().isoformat()}")
    report_lines.append("")
    
    status = "PASS"
    issues = []
    stats = {
        "files_checked": {},
        "missing_values": {},
        "duplicate_count": 0,
        "invalid_records_count": 0,
        "rows_count": 0
    }
    
    # 1. Verify expected files exist
    for f in expected_files:
        full_path = os.path.join(raw_path, f)
        if not os.path.isfile(full_path):
            status = "FAIL"
            issues.append(f"Missing expected file: {f}")
            report_lines.append(f"File: {f} -> NOT FOUND")
            continue
            
        report_lines.append(f"File: {f} -> FOUND (Checksum: {calculate_checksum(full_path)[:12]}...)")
        
        # Validate schemas and scan in chunks to avoid OOM
        expected_cols = EXPECTED_COLUMNS["m5"][f]
        missing_cols = []
        rows = 0
        null_counts = {}
        duplicates = 0
        invalid_prices = 0
        
        try:
            # For sales_train_validation and sell_prices, read in chunks
            chunksize = 100000
            is_first = True
            
            for chunk in pd.read_csv(full_path, chunksize=chunksize):
                rows += len(chunk)
                
                # Check columns schema on first chunk
                if is_first:
                    is_first = False
                    for col in expected_cols:
                        if col not in chunk.columns:
                            missing_cols.append(col)
                            
                # Count missing values
                for col in chunk.columns:
                    n_null = int(chunk[col].isnull().sum())
                    if n_null > 0:
                        null_counts[col] = null_counts.get(col, 0) + n_null
                        
                # Validate prices in sell_prices
                if f == "sell_prices.csv" and "sell_price" in chunk.columns:
                    invalid_prices += int((chunk["sell_price"] <= 0).sum())
                    
            if missing_cols:
                status = "FAIL"
                issues.append(f"File {f} is missing expected columns: {missing_cols}")
                
            stats["files_checked"][f] = {
                "rows": rows,
                "missing_values": null_counts,
                "missing_columns": missing_cols,
                "invalid_prices": invalid_prices
            }
            stats["rows_count"] += rows
            
            report_lines.append(f"  Total Rows: {rows}")
            if null_counts:
                report_lines.append(f"  Missing values: {null_counts}")
            else:
                report_lines.append(f"  Missing values: None")
            if invalid_prices > 0:
                report_lines.append(f"  Invalid prices (<= 0): {invalid_prices}")
                status = "WARNING"
                issues.append(f"File {f} contains {invalid_prices} invalid price values <= 0")
                
        except Exception as e:
            status = "FAIL"
            issues.append(f"Failed to parse file {f}: {e}")
            report_lines.append(f"  Parsing Error: {e}")
            
        report_lines.append("-" * 40)
        
    report_lines.append(f"Status: {status}")
    if issues:
        report_lines.append("Issues Found:")
        for iss in issues:
            report_lines.append(f"  - {iss}")
    else:
        report_lines.append("Issues Found: None")
        
    report_text = "\n".join(report_lines)
    return report_text, {
        "status": status,
        "issues": issues,
        "stats": stats
    }

def validate_online_retail_ii_dataset() -> Tuple[str, Dict[str, Any]]:
    """
    Validates UCI Online Retail II dataset.
    Looks for online_retail_II.csv in raw path.
    """
    meta = DATASET_METADATA["online_retail_ii"]
    raw_path = meta["local_raw_path"]
    expected_files = meta["expected_files"]
    
    report_lines = []
    report_lines.append("DATASET VALIDATION REPORT")
    report_lines.append("=" * 40)
    report_lines.append(f"Dataset: UCI Online Retail II")
    report_lines.append(f"Validation Timestamp: {datetime.now().isoformat()}")
    report_lines.append("")
    
    status = "PASS"
    issues = []
    stats = {
        "rows_count": 0,
        "duplicate_count": 0,
        "missing_values": {},
        "invalid_quantities": 0,
        "invalid_prices": 0,
        "min_date": None,
        "max_date": None
    }
    
    f = expected_files[0]
    full_path = os.path.join(raw_path, f)
    
    if not os.path.isfile(full_path):
        status = "FAIL"
        issues.append(f"Missing expected raw transaction file: {f}")
        report_lines.append(f"File: {f} -> NOT FOUND")
        report_lines.append(f"Status: {status}")
        return "\n".join(report_lines), {"status": status, "issues": issues, "stats": stats}
        
    report_lines.append(f"File: {f} -> FOUND (Checksum: {calculate_checksum(full_path)[:12]}...)")
    
    try:
        expected_cols = EXPECTED_COLUMNS["online_retail_ii"][f]
        missing_cols = []
        rows_count = 0
        null_counts = {}
        invalid_quantities = 0
        invalid_prices = 0
        min_date = None
        max_date = None
        
        # Read in chunks to compute statistics efficiently
        chunksize = 100000
        is_first = True
        
        for chunk in pd.read_csv(full_path, chunksize=chunksize):
            rows_count += len(chunk)
            
            # Schema column validation
            if is_first:
                is_first = False
                for col in expected_cols:
                    if col not in chunk.columns:
                        missing_cols.append(col)
                        
            # Null value validation
            for col in chunk.columns:
                n_null = int(chunk[col].isnull().sum())
                if n_null > 0:
                    null_counts[col] = null_counts.get(col, 0) + n_null
                    
            # Quantity validation: negative quantity is only valid if invoice starts with C (cancellation)
            if "Quantity" in chunk.columns and "Invoice" in chunk.columns:
                is_cancel = chunk["Invoice"].astype(str).str.startswith("C", na=False)
                invalid_q = int(((chunk["Quantity"] <= 0) & (~is_cancel)).sum())
                invalid_quantities += invalid_q
                
            # Price validation: price must be >= 0
            if "Price" in chunk.columns:
                invalid_p = int((chunk["Price"] < 0).sum())
                invalid_prices += invalid_p
                
            # Date range computation
            if "InvoiceDate" in chunk.columns:
                chunk_dates = pd.to_datetime(chunk["InvoiceDate"], errors="coerce").dropna()
                if not chunk_dates.empty:
                    c_min, c_max = chunk_dates.min(), chunk_dates.max()
                    if min_date is None or c_min < min_date:
                        min_date = c_min
                    if max_date is None or c_max > max_date:
                        max_date = c_max
                        
        # Check for duplicates on a subset sample or index if needed,
        # but for safety let's run a duplicate check by streaming or loading only key columns if needed.
        # Online Retail II duplicate check is fast on key columns:
        key_cols = ["Invoice", "StockCode", "InvoiceDate", "Customer ID"]
        df_keys = pd.read_csv(full_path, usecols=lambda c: c in key_cols)
        duplicate_count = int(df_keys.duplicated().sum())
        
        if missing_cols:
            status = "FAIL"
            issues.append(f"Missing columns: {missing_cols}")
            
        if invalid_quantities > 0:
            status = "WARNING"
            issues.append(f"Found {invalid_quantities} non-cancelled transactions with quantity <= 0")
            
        if invalid_prices > 0:
            status = "WARNING"
            issues.append(f"Found {invalid_prices} transactions with Price < 0")
            
        stats.update({
            "rows_count": rows_count,
            "duplicate_count": duplicate_count,
            "missing_values": null_counts,
            "invalid_quantities": invalid_quantities,
            "invalid_prices": invalid_prices,
            "min_date": min_date.strftime("%Y-%m-%d") if min_date else None,
            "max_date": max_date.strftime("%Y-%m-%d") if max_date else None
        })
        
        report_lines.append(f"  Rows: {rows_count}")
        report_lines.append(f"  Duplicates: {duplicate_count}")
        report_lines.append(f"  Missing values: {null_counts}")
        report_lines.append(f"  Invalid quantities (non-cancelled <= 0): {invalid_quantities}")
        report_lines.append(f"  Invalid prices (< 0): {invalid_prices}")
        report_lines.append(f"  Date Range: {stats['min_date']} to {stats['max_date']}")
        
    except Exception as e:
        status = "FAIL"
        issues.append(f"Failed to parse Online Retail II file: {e}")
        report_lines.append(f"  Parsing Error: {e}")
        
    report_lines.append(f"Status: {status}")
    if issues:
        report_lines.append("Issues Found:")
        for iss in issues:
            report_lines.append(f"  - {iss}")
    else:
        report_lines.append("Issues Found: None")
        
    report_text = "\n".join(report_lines)
    return report_text, {"status": status, "issues": issues, "stats": stats}

def validate_store_sales_dataset() -> Tuple[str, Dict[str, Any]]:
    """
    Validates Store Sales Time Series Forecasting dataset by NeuroCipher.
    """
    meta = DATASET_METADATA["store_sales_forecasting"]
    raw_path = meta["local_raw_path"]
    expected_files = meta["expected_files"]
    
    report_lines = []
    report_lines.append("DATASET VALIDATION REPORT")
    report_lines.append("=" * 40)
    report_lines.append(f"Dataset: Store Sales Time Series Forecasting / NeuroCipher")
    report_lines.append(f"Validation Timestamp: {datetime.now().isoformat()}")
    report_lines.append("")
    
    status = "PASS"
    issues = []
    stats = {
        "files_checked": {},
        "missing_values": {},
        "duplicate_count": 0,
        "invalid_records_count": 0,
        "rows_count": 0,
        "min_date": None,
        "max_date": None
    }
    
    for f in expected_files:
        full_path = os.path.join(raw_path, f)
        if not os.path.isfile(full_path):
            status = "FAIL"
            issues.append(f"Missing expected file: {f}")
            report_lines.append(f"File: {f} -> NOT FOUND")
            continue
            
        report_lines.append(f"File: {f} -> FOUND (Checksum: {calculate_checksum(full_path)[:12]}...)")
        
        expected_cols = EXPECTED_COLUMNS["store_sales_forecasting"][f]
        missing_cols = []
        rows = 0
        null_counts = {}
        invalid_numeric = 0
        min_date = None
        max_date = None
        
        try:
            chunksize = 100000
            is_first = True
            
            for chunk in pd.read_csv(full_path, chunksize=chunksize):
                rows += len(chunk)
                
                if is_first:
                    is_first = False
                    for col in expected_cols:
                        if col not in chunk.columns:
                            missing_cols.append(col)
                            
                for col in chunk.columns:
                    n_null = int(chunk[col].isnull().sum())
                    if n_null > 0:
                        null_counts[col] = null_counts.get(col, 0) + n_null
                        
                # Perform numeric validation
                if f == "train.csv":
                    if "sales" in chunk.columns:
                        invalid_numeric += int((chunk["sales"] < 0).sum())
                    if "onpromotion" in chunk.columns:
                        invalid_numeric += int((chunk["onpromotion"] < 0).sum())
                    if "date" in chunk.columns:
                        chunk_dates = pd.to_datetime(chunk["date"], errors="coerce").dropna()
                        if not chunk_dates.empty:
                            c_min, c_max = chunk_dates.min(), chunk_dates.max()
                            if min_date is None or c_min < min_date:
                                min_date = c_min
                            if max_date is None or c_max > max_date:
                                max_date = c_max
                                
                elif f == "transactions.csv" and "transactions" in chunk.columns:
                    invalid_numeric += int((chunk["transactions"] < 0).sum())
                    
            if missing_cols:
                status = "FAIL"
                issues.append(f"File {f} is missing expected columns: {missing_cols}")
                
            stats["files_checked"][f] = {
                "rows": rows,
                "missing_values": null_counts,
                "missing_columns": missing_cols,
                "invalid_numeric": invalid_numeric
            }
            stats["rows_count"] += rows
            
            report_lines.append(f"  Total Rows: {rows}")
            if null_counts:
                report_lines.append(f"  Missing values: {null_counts}")
            else:
                report_lines.append(f"  Missing values: None")
            if invalid_numeric > 0:
                report_lines.append(f"  Invalid numeric values (< 0): {invalid_numeric}")
                status = "WARNING"
                issues.append(f"File {f} contains {invalid_numeric} negative numeric values")
                
            if min_date and max_date:
                stats["min_date"] = min_date.strftime("%Y-%m-%d")
                stats["max_date"] = max_date.strftime("%Y-%m-%d")
                report_lines.append(f"  Date Range: {stats['min_date']} to {stats['max_date']}")
                
        except Exception as e:
            status = "FAIL"
            issues.append(f"Failed to parse Store Sales file {f}: {e}")
            report_lines.append(f"  Parsing Error: {e}")
            
    # Calculate duplicates in train.csv specifically
    train_file = os.path.join(raw_path, "train.csv")
    if os.path.isfile(train_file):
        try:
            df_keys = pd.read_csv(train_file, usecols=["date", "store_nbr", "family"])
            duplicate_count = int(df_keys.duplicated().sum())
            stats["duplicate_count"] = duplicate_count
            report_lines.append(f"Train.csv Duplicates: {duplicate_count}")
            if duplicate_count > 0:
                status = "WARNING"
                issues.append(f"Found {duplicate_count} duplicate rows in train.csv")
        except Exception:
            pass
            
    report_lines.append(f"Status: {status}")
    if issues:
        report_lines.append("Issues Found:")
        for iss in issues:
            report_lines.append(f"  - {iss}")
    else:
        report_lines.append("Issues Found: None")
        
    report_text = "\n".join(report_lines)
    return report_text, {"status": status, "issues": issues, "stats": stats}

def validate_retail_sales_dataset() -> Tuple[str, Dict[str, Any]]:
    """
    Validates MLZC Compet '24 Retail Demand Forecast dataset.
    """
    meta = DATASET_METADATA["retail_sales_forecasting"]
    raw_path = meta["local_raw_path"]
    expected_files = meta["expected_files"]
    
    report_lines = []
    report_lines.append("DATASET VALIDATION REPORT")
    report_lines.append("=" * 40)
    report_lines.append(f"Dataset: MLZC Compet '24 / Retail Demand Forecast")
    report_lines.append(f"Validation Timestamp: {datetime.now().isoformat()}")
    report_lines.append("")
    
    status = "PASS"
    issues = []
    stats = {
        "files_checked": {},
        "missing_values": {},
        "duplicate_count": 0,
        "invalid_quantities": 0,
        "invalid_prices": 0,
        "rows_count": 0,
        "min_date": None,
        "max_date": None
    }
    
    for f in expected_files:
        full_path = os.path.join(raw_path, f)
        if not os.path.isfile(full_path):
            status = "FAIL"
            issues.append(f"Missing expected file: {f}")
            report_lines.append(f"File: {f} -> NOT FOUND")
            continue
            
        report_lines.append(f"File: {f} -> FOUND (Checksum: {calculate_checksum(full_path)[:12]}...)")
        
        expected_cols = EXPECTED_COLUMNS["retail_sales_forecasting"][f]
        missing_cols = []
        rows = 0
        null_counts = {}
        invalid_quantities = 0
        invalid_prices = 0
        min_date = None
        max_date = None
        
        try:
            chunksize = 100000
            is_first = True
            
            for chunk in pd.read_csv(full_path, chunksize=chunksize):
                rows += len(chunk)
                
                if is_first:
                    is_first = False
                    for col in expected_cols:
                        if col not in chunk.columns:
                            missing_cols.append(col)
                            
                for col in chunk.columns:
                    n_null = int(chunk[col].isnull().sum())
                    if n_null > 0:
                        null_counts[col] = null_counts.get(col, 0) + n_null
                        
                # Perform numeric validation
                if f in ["sales.csv", "online.csv"]:
                    if "quantity" in chunk.columns:
                        invalid_quantities += int((chunk["quantity"] < 0).sum())
                    if "price_base" in chunk.columns:
                        invalid_prices += int((chunk["price_base"] < 0).sum())
                    if "sum_total" in chunk.columns:
                        invalid_prices += int((chunk["sum_total"] < 0).sum())
                    if "date" in chunk.columns:
                        chunk_dates = pd.to_datetime(chunk["date"], errors="coerce").dropna()
                        if not chunk_dates.empty:
                            c_min, c_max = chunk_dates.min(), chunk_dates.max()
                            if min_date is None or c_min < min_date:
                                min_date = c_min
                            if max_date is None or c_max > max_date:
                                max_date = c_max
                                
                elif f == "price_history.csv" and "price" in chunk.columns:
                    invalid_prices += int((chunk["price"] < 0).sum())
                    
                elif f == "discounts_history.csv":
                    if "sale_price_before_promo" in chunk.columns:
                        invalid_prices += int((chunk["sale_price_before_promo"] < 0).sum())
                    if "sale_price_time_promo" in chunk.columns:
                        invalid_prices += int((chunk["sale_price_time_promo"] < 0).sum())
                        
                elif f == "markdowns.csv":
                    if "normal_price" in chunk.columns:
                        invalid_prices += int((chunk["normal_price"] < 0).sum())
                    if "price" in chunk.columns:
                        invalid_prices += int((chunk["price"] < 0).sum())
                    if "quantity" in chunk.columns:
                        invalid_quantities += int((chunk["quantity"] < 0).sum())
                        
            if missing_cols:
                status = "FAIL"
                issues.append(f"File {f} is missing expected columns: {missing_cols}")
                
            stats["files_checked"][f] = {
                "rows": rows,
                "missing_values": null_counts,
                "missing_columns": missing_cols,
                "invalid_quantities": invalid_quantities,
                "invalid_prices": invalid_prices
            }
            stats["rows_count"] += rows
            stats["invalid_quantities"] += invalid_quantities
            stats["invalid_prices"] += invalid_prices
            
            # Map nulls to global stats dictionary
            for col, count in null_counts.items():
                stats["missing_values"][f"{f}:{col}"] = count
                
            report_lines.append(f"  Total Rows: {rows}")
            if null_counts:
                report_lines.append(f"  Missing values: {null_counts}")
            else:
                report_lines.append(f"  Missing values: None")
            if invalid_quantities > 0 or invalid_prices > 0:
                report_lines.append(f"  Invalid values: Quantities={invalid_quantities}, Prices={invalid_prices}")
                status = "WARNING"
                issues.append(f"File {f} contains negative numeric values")
                
            if min_date and max_date:
                stats["min_date"] = min_date.strftime("%Y-%m-%d")
                stats["max_date"] = max_date.strftime("%Y-%m-%d")
                report_lines.append(f"  Date Range: {stats['min_date']} to {stats['max_date']}")
                
        except Exception as e:
            status = "FAIL"
            issues.append(f"Failed to parse Retail Sales file {f}: {e}")
            report_lines.append(f"  Parsing Error: {e}")
            
    # Calculate duplicates in sales.csv specifically
    sales_file = os.path.join(raw_path, "sales.csv")
    if os.path.isfile(sales_file):
        try:
            # Let's read in chunks or subset
            df_keys = pd.read_csv(sales_file, usecols=["date", "item_id", "store_id"])
            duplicate_count = int(df_keys.duplicated().sum())
            stats["duplicate_count"] = duplicate_count
            report_lines.append(f"sales.csv Duplicates: {duplicate_count}")
            if duplicate_count > 0:
                status = "WARNING"
                issues.append(f"Found {duplicate_count} duplicate rows in sales.csv")
        except Exception as e:
            print(f"Error checking duplicates in sales.csv: {e}")
            
    report_lines.append(f"Status: {status}")
    if issues:
        report_lines.append("Issues Found:")
        for iss in issues:
            report_lines.append(f"  - {iss}")
    else:
        report_lines.append("Issues Found: None")
        
    report_text = "\n".join(report_lines)
    return report_text, {"status": status, "issues": issues, "stats": stats}

if __name__ == "__main__":
    ensure_directories()
    m5_report, m5_res = validate_m5_dataset()
    retail_report, retail_res = validate_online_retail_ii_dataset()
    print("M5 Forecasting Validation:")
    print(m5_report)
    print("\n" + "="*50 + "\n")
    print("Online Retail II Validation:")
    print(retail_report)
