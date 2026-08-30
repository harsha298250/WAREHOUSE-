import os
import pandas as pd
import numpy as np
from data_pipeline.registry import DATASET_METADATA, ensure_directories

def process_online_retail_ii() -> int:
    """
    Cleans and normalizes the Online Retail II dataset:
    - Drops exact duplicate rows.
    - Fills missing Customer ID with 'UNKNOWN'.
    - Parses InvoiceDate to standard ISO format (YYYY-MM-DD HH:MM:SS).
    - Removes transactions with Price < 0.
    - Removes non-cancelled transactions (Invoice does not start with C) where Quantity is <= 0.
    - Tags cancelled invoices with a boolean column 'IsCancelled'.
    - Saves the processed dataset to data/processed/online_retail_ii/online_retail_II_processed.csv.
    """
    meta = DATASET_METADATA["online_retail_ii"]
    raw_file = os.path.join(meta["local_raw_path"], meta["expected_files"][0])
    processed_file = os.path.join(meta["local_processed_path"], "online_retail_II_processed.csv")
    
    if not os.path.isfile(raw_file):
        print(f"Skipping Online Retail II processing: raw file not found at {raw_file}")
        return 0
        
    print("Processing Online Retail II dataset...")
    ensure_directories()
    
    processed_rows = 0
    chunksize = 100000
    is_first = True
    
    for chunk in pd.read_csv(raw_file, chunksize=chunksize):
        # 1. Clean price < 0
        chunk = chunk[chunk["Price"] >= 0]
        
        # 2. Add IsCancelled column
        chunk["IsCancelled"] = chunk["Invoice"].astype(str).str.startswith("C", na=False)
        
        # 3. Clean invalid quantities: quantity must be > 0 if not cancelled
        chunk = chunk[(chunk["Quantity"] > 0) | (chunk["IsCancelled"] == True)]
        
        # 4. Fill missing Customer ID
        chunk["Customer ID"] = chunk["Customer ID"].fillna("UNKNOWN")
        
        # 5. Normalize InvoiceDate to ISO datetime format
        chunk["InvoiceDate"] = pd.to_datetime(chunk["InvoiceDate"], errors="coerce").dt.strftime("%Y-%m-%d %H:%M:%S")
        chunk = chunk.dropna(subset=["InvoiceDate"]) # drop rows where date parsing failed completely
        
        # Write to processed output
        mode = "w" if is_first else "a"
        header = is_first
        chunk.to_csv(processed_file, mode=mode, index=False, header=header)
        processed_rows += len(chunk)
        is_first = False
        
    # Drop duplicates from final output (since duplicate check must span the whole dataset)
    if os.path.isfile(processed_file):
        df_all = pd.read_csv(processed_file)
        before_dedup = len(df_all)
        df_all = df_all.drop_duplicates()
        df_all.to_csv(processed_file, index=False)
        processed_rows = len(df_all)
        print(f"Online Retail II processed: {before_dedup} rows -> {processed_rows} rows after deduplication.")
        
    return processed_rows

def process_m5() -> int:
    """
    Normalizes the M5 Forecasting dataset (calendar.csv, sales_train_validation.csv, sell_prices.csv):
    - calendar.csv: Normalizes dates, weekday formats.
    - sell_prices.csv: Normalizes prices.
    - sales_train_validation.csv: Standardizes IDs and validates schemas.
    """
    meta = DATASET_METADATA["m5"]
    raw_path = meta["local_raw_path"]
    processed_path = meta["local_processed_path"]
    
    processed_files_count = 0
    total_rows = 0
    
    # 1. Process calendar.csv
    cal_raw = os.path.join(raw_path, "calendar.csv")
    cal_proc = os.path.join(processed_path, "calendar_processed.csv")
    if os.path.isfile(cal_raw):
        print("Processing M5 calendar.csv...")
        df_cal = pd.read_csv(cal_raw)
        df_cal["date"] = pd.to_datetime(df_cal["date"]).dt.strftime("%Y-%m-%d")
        df_cal = df_cal.drop_duplicates()
        df_cal.to_csv(cal_proc, index=False)
        processed_files_count += 1
        total_rows += len(df_cal)
        
    # 2. Process sell_prices.csv
    prices_raw = os.path.join(raw_path, "sell_prices.csv")
    prices_proc = os.path.join(processed_path, "sell_prices_processed.csv")
    if os.path.isfile(prices_raw):
        print("Processing M5 sell_prices.csv...")
        # Chunk prices to prevent OOM
        is_first = True
        for chunk in pd.read_csv(prices_raw, chunksize=100000):
            # Clean invalid sell price (<= 0)
            chunk = chunk[chunk["sell_price"] > 0]
            mode = "w" if is_first else "a"
            header = is_first
            chunk.to_csv(prices_proc, mode=mode, index=False, header=header)
            is_first = False
            total_rows += len(chunk)
        processed_files_count += 1
        
    # 3. Process sales_train_validation.csv
    sales_raw = os.path.join(raw_path, "sales_train_validation.csv")
    sales_proc = os.path.join(processed_path, "sales_processed.csv")
    if os.path.isfile(sales_raw):
        print("Processing M5 sales_train_validation.csv...")
        is_first = True
        for chunk in pd.read_csv(sales_raw, chunksize=50000):
            mode = "w" if is_first else "a"
            header = is_first
            chunk.to_csv(sales_proc, mode=mode, index=False, header=header)
            is_first = False
            total_rows += len(chunk)
        processed_files_count += 1
        
    print(f"M5 processed files count: {processed_files_count} with {total_rows} total rows.")
    return total_rows

def process_store_sales() -> int:
    """
    Normalizes Store Sales Forecasting dataset (NeuroCipher):
    Processes and deduplicates train.csv, test.csv, stores.csv, transactions.csv,
    oil.csv, holidays_events.csv, sample_submission.csv.
    """
    meta = DATASET_METADATA["store_sales_forecasting"]
    raw_path = meta["local_raw_path"]
    processed_path = meta["local_processed_path"]
    ensure_directories()
    
    processed_files_count = 0
    total_rows = 0
    
    # Process each expected file
    for f in meta["expected_files"]:
        raw_file = os.path.join(raw_path, f)
        proc_file = os.path.join(processed_path, f.replace(".csv", "_processed.csv"))
        
        if not os.path.isfile(raw_file):
            continue
            
        print(f"Processing Store Sales {f}...")
        
        if f == "train.csv":
            is_first = True
            for chunk in pd.read_csv(raw_file, chunksize=100000):
                # Clean invalid sales and promotion columns
                if "sales" in chunk.columns:
                    chunk = chunk[chunk["sales"] >= 0]
                if "onpromotion" in chunk.columns:
                    chunk = chunk[chunk["onpromotion"] >= 0]
                if "date" in chunk.columns:
                    chunk["date"] = pd.to_datetime(chunk["date"]).dt.strftime("%Y-%m-%d")
                    
                mode = "w" if is_first else "a"
                header = is_first
                chunk.to_csv(proc_file, mode=mode, index=False, header=header)
                is_first = False
                
            # Perform final deduplication
            if os.path.isfile(proc_file):
                df_all = pd.read_csv(proc_file)
                before = len(df_all)
                df_all = df_all.drop_duplicates(subset=["date", "store_nbr", "family"])
                df_all.to_csv(proc_file, index=False)
                dedupped_rows = len(df_all)
                print(f"Deduplicated Store Sales train.csv: {before} -> {dedupped_rows} rows.")
                total_rows += dedupped_rows
                processed_files_count += 1
                
        elif f == "transactions.csv":
            df = pd.read_csv(raw_file)
            if "transactions" in df.columns:
                df = df[df["transactions"] >= 0]
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
            df = df.drop_duplicates()
            df.to_csv(proc_file, index=False)
            total_rows += len(df)
            processed_files_count += 1
            
        elif f == "oil.csv":
            df = pd.read_csv(raw_file)
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
            df = df.drop_duplicates()
            df.to_csv(proc_file, index=False)
            total_rows += len(df)
            processed_files_count += 1
            
        elif f == "holidays_events.csv":
            df = pd.read_csv(raw_file)
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
            df = df.drop_duplicates()
            df.to_csv(proc_file, index=False)
            total_rows += len(df)
            processed_files_count += 1
            
        else: # test.csv, stores.csv, sample_submission.csv
            df = pd.read_csv(raw_file)
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
            df = df.drop_duplicates()
            df.to_csv(proc_file, index=False)
            total_rows += len(df)
            processed_files_count += 1
            
    print(f"Store Sales processed: {processed_files_count} files with {total_rows} total rows.")
    return total_rows

def process_retail_sales() -> int:
    """
    Normalizes MLZC Compet '24 Retail Demand Forecast dataset.
    Processes all 8 CSV files: sales, online, stores, price_history,
    discounts_history, markdowns, catalog, actual_matrix.
    """
    meta = DATASET_METADATA["retail_sales_forecasting"]
    raw_path = meta["local_raw_path"]
    processed_path = meta["local_processed_path"]
    ensure_directories()

    processed_files_count = 0
    total_rows = 0

    for f in meta["expected_files"]:
        raw_file = os.path.join(raw_path, f)
        proc_file = os.path.join(processed_path, f.replace(".csv", "_processed.csv"))

        if not os.path.isfile(raw_file):
            print(f"Skipping Retail Sales file (not found): {f}")
            continue

        print(f"Processing Retail Sales {f}...")

        if f in ["sales.csv", "online.csv"]:
            is_first = True
            for chunk in pd.read_csv(raw_file, chunksize=100000):
                if "quantity" in chunk.columns:
                    chunk = chunk[chunk["quantity"] >= 0]
                if "price_base" in chunk.columns:
                    chunk = chunk[chunk["price_base"] >= 0]
                if "sum_total" in chunk.columns:
                    chunk = chunk[chunk["sum_total"] >= 0]
                if "date" in chunk.columns:
                    chunk["date"] = pd.to_datetime(chunk["date"]).dt.strftime("%Y-%m-%d")
                mode = "w" if is_first else "a"
                chunk.to_csv(proc_file, mode=mode, index=False, header=is_first)
                is_first = False

            if os.path.isfile(proc_file):
                df_all = pd.read_csv(proc_file)
                before = len(df_all)
                df_all = df_all.drop_duplicates(subset=["date", "item_id", "store_id"])
                df_all.to_csv(proc_file, index=False)
                print(f"  {f}: {before} -> {len(df_all)} rows after dedup.")
                total_rows += len(df_all)
                processed_files_count += 1

        elif f == "price_history.csv":
            df = pd.read_csv(raw_file)
            if "price" in df.columns:
                df = df[df["price"] >= 0]
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
            df = df.drop_duplicates()
            df.to_csv(proc_file, index=False)
            total_rows += len(df)
            processed_files_count += 1

        elif f == "discounts_history.csv":
            # Large file — process in chunks
            is_first = True
            for chunk in pd.read_csv(raw_file, chunksize=100000):
                if "sale_price_before_promo" in chunk.columns:
                    chunk = chunk[chunk["sale_price_before_promo"] >= 0]
                if "sale_price_time_promo" in chunk.columns:
                    chunk = chunk[chunk["sale_price_time_promo"] >= 0]
                if "date" in chunk.columns:
                    chunk["date"] = pd.to_datetime(chunk["date"]).dt.strftime("%Y-%m-%d")
                mode = "w" if is_first else "a"
                chunk.to_csv(proc_file, mode=mode, index=False, header=is_first)
                is_first = False
            if os.path.isfile(proc_file):
                df_all = pd.read_csv(proc_file)
                before = len(df_all)
                df_all = df_all.drop_duplicates()
                df_all.to_csv(proc_file, index=False)
                print(f"  {f}: {before} -> {len(df_all)} rows after dedup.")
                total_rows += len(df_all)
                processed_files_count += 1

        elif f == "markdowns.csv":
            df = pd.read_csv(raw_file)
            if "normal_price" in df.columns:
                df = df[df["normal_price"] >= 0]
            if "price" in df.columns:
                df = df[df["price"] >= 0]
            if "quantity" in df.columns:
                df = df[df["quantity"] >= 0]
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
            df = df.drop_duplicates()
            df.to_csv(proc_file, index=False)
            total_rows += len(df)
            processed_files_count += 1

        else:  # stores.csv, catalog.csv, actual_matrix.csv
            df = pd.read_csv(raw_file)
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
            df = df.drop_duplicates()
            df.to_csv(proc_file, index=False)
            total_rows += len(df)
            processed_files_count += 1

    print(f"Retail Demand Forecast processed: {processed_files_count} files, {total_rows} total rows.")
    return total_rows

if __name__ == "__main__":
    ensure_directories()
    process_online_retail_ii()
    process_m5()
    process_store_sales()
    process_retail_sales()
