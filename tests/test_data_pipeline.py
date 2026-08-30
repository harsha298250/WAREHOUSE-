import os
import shutil
import pytest
import pandas as pd
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models import DatasetSource, DatasetImportRun, DatasetValidationResult, Inventory
from data_pipeline.registry import DATASET_METADATA, ensure_directories, calculate_checksum
from data_pipeline.validate import validate_m5_dataset, validate_online_retail_ii_dataset, validate_store_sales_dataset, validate_retail_sales_dataset
from data_pipeline.process import process_m5, process_online_retail_ii, process_store_sales, process_retail_sales
from data_pipeline.import_metadata import seed_dataset_sources, record_pipeline_run

@pytest.fixture
def mock_datasets_dirs():
    """Sets up temp directories and test CSV fixtures for M5 and Online Retail II validation tests."""
    temp_raw = os.path.join("data", "raw_temp")
    temp_proc = os.path.join("data", "proc_temp")
    
    # Backup original raw and processed paths
    orig_m5_raw = DATASET_METADATA["m5"]["local_raw_path"]
    orig_m5_proc = DATASET_METADATA["m5"]["local_processed_path"]
    orig_retail_raw = DATASET_METADATA["online_retail_ii"]["local_raw_path"]
    orig_retail_proc = DATASET_METADATA["online_retail_ii"]["local_processed_path"]
    orig_store_raw = DATASET_METADATA["store_sales_forecasting"]["local_raw_path"]
    orig_store_proc = DATASET_METADATA["store_sales_forecasting"]["local_processed_path"]
    orig_tevec_raw = DATASET_METADATA["retail_sales_forecasting"]["local_raw_path"]
    orig_tevec_proc = DATASET_METADATA["retail_sales_forecasting"]["local_processed_path"]
    
    # Overwrite paths in registry config
    DATASET_METADATA["m5"]["local_raw_path"] = os.path.join(temp_raw, "m5")
    DATASET_METADATA["m5"]["local_processed_path"] = os.path.join(temp_proc, "m5")
    DATASET_METADATA["online_retail_ii"]["local_raw_path"] = os.path.join(temp_raw, "online_retail_ii")
    DATASET_METADATA["online_retail_ii"]["local_processed_path"] = os.path.join(temp_proc, "online_retail_ii")
    DATASET_METADATA["store_sales_forecasting"]["local_raw_path"] = os.path.join(temp_raw, "store_sales_forecasting")
    DATASET_METADATA["store_sales_forecasting"]["local_processed_path"] = os.path.join(temp_proc, "store_sales_forecasting")
    DATASET_METADATA["retail_sales_forecasting"]["local_raw_path"] = os.path.join(temp_raw, "retail_sales_forecasting")
    DATASET_METADATA["retail_sales_forecasting"]["local_processed_path"] = os.path.join(temp_proc, "retail_sales_forecasting")
    
    # Create test dirs
    os.makedirs(DATASET_METADATA["m5"]["local_raw_path"], exist_ok=True)
    os.makedirs(DATASET_METADATA["m5"]["local_processed_path"], exist_ok=True)
    os.makedirs(DATASET_METADATA["online_retail_ii"]["local_raw_path"], exist_ok=True)
    os.makedirs(DATASET_METADATA["online_retail_ii"]["local_processed_path"], exist_ok=True)
    os.makedirs(DATASET_METADATA["store_sales_forecasting"]["local_raw_path"], exist_ok=True)
    os.makedirs(DATASET_METADATA["store_sales_forecasting"]["local_processed_path"], exist_ok=True)
    os.makedirs(DATASET_METADATA["retail_sales_forecasting"]["local_raw_path"], exist_ok=True)
    os.makedirs(DATASET_METADATA["retail_sales_forecasting"]["local_processed_path"], exist_ok=True)
    
    # Write small mock M5 files
    # calendar.csv
    with open(os.path.join(DATASET_METADATA["m5"]["local_raw_path"], "calendar.csv"), "w") as f:
        f.write("date,wm_yr_wk,weekday,wday,month,year,d\n2011-01-29,11101,Saturday,1,1,2011,d_1\n2011-01-30,11101,Sunday,2,1,2011,d_2\n")
    # sales_train_validation.csv
    with open(os.path.join(DATASET_METADATA["m5"]["local_raw_path"], "sales_train_validation.csv"), "w") as f:
        f.write("id,item_id,dept_id,cat_id,store_id,state_id,d_1,d_2\nHOBBIES_1_001_CA_1_validation,HOBBIES_1_001,HOBBIES_1,HOBBIES,CA_1,CA,0,0\n")
    # sell_prices.csv
    with open(os.path.join(DATASET_METADATA["m5"]["local_raw_path"], "sell_prices.csv"), "w") as f:
        f.write("store_id,item_id,wm_yr_wk,sell_price\nCA_1,HOBBIES_1_001,11101,9.58\nCA_1,HOBBIES_1_002,11101,-1.50\n") # contains one invalid price
        
    # Write mock UCI Online Retail II file
    with open(os.path.join(DATASET_METADATA["online_retail_ii"]["local_raw_path"], "online_retail_II.csv"), "w") as f:
        f.write("Invoice,StockCode,Description,Quantity,InvoiceDate,Price,Customer ID,Country\n536365,85123A,WHITE HANGING HEART T-LIGHT HOLDER,6,2010-12-01 08:26:00,2.55,17850,United Kingdom\nC536379,D,Discount,-1,2010-12-01 09:41:00,27.50,14527,United Kingdom\n536380,22960,JAM MAKING SET WITH JARS,12,2010-12-01 09:41:00,4.25,,United Kingdom\n536380,22960,JAM MAKING SET WITH JARS,12,2010-12-01 09:41:00,4.25,,United Kingdom\n") # contains missing customer ID and duplicate row

    # Write mock Store Sales Forecasting files
    store_raw = DATASET_METADATA["store_sales_forecasting"]["local_raw_path"]
    with open(os.path.join(store_raw, "train.csv"), "w") as f:
        f.write("id,date,store_nbr,family,sales,onpromotion\n0,2013-01-01,1,AUTOMOTIVE,0.0,0\n1,2013-01-01,1,AUTOMOTIVE,0.0,0\n2,2013-01-02,1,AUTOMOTIVE,-5.0,0\n") # contains duplicate and invalid sales
    with open(os.path.join(store_raw, "test.csv"), "w") as f:
        f.write("id,date,store_nbr,family,onpromotion\n3,2013-01-16,1,AUTOMOTIVE,0\n")
    with open(os.path.join(store_raw, "stores.csv"), "w") as f:
        f.write("store_nbr,city,state,type,cluster\n1,Quito,Pichincha,D,13\n")
    with open(os.path.join(store_raw, "transactions.csv"), "w") as f:
        f.write("date,store_nbr,transactions\n2013-01-02,1,-10\n") # invalid transaction
    with open(os.path.join(store_raw, "oil.csv"), "w") as f:
        f.write("date,dcoilwtico\n2013-01-01,\n2013-01-02,93.14\n")
    with open(os.path.join(store_raw, "holidays_events.csv"), "w") as f:
        f.write("date,type,locale,locale_name,description,transferred\n2012-03-02,Holiday,Local,Manta,Fundacion de Manta,False\n")
    with open(os.path.join(store_raw, "sample_submission.csv"), "w") as f:
        f.write("id,sales\n3,0.0\n")

    # Write mock Retail Sales Forecasting files (MLZC Compet '24)
    mlzc_raw = DATASET_METADATA["retail_sales_forecasting"]["local_raw_path"]
    with open(os.path.join(mlzc_raw, "sales.csv"), "w") as f:
        f.write(",date,item_id,quantity,price_base,sum_total,store_id\n0,2022-01-01,1001,5,9.99,49.95,1\n1,2022-01-01,1001,5,9.99,49.95,1\n2,2022-01-02,1001,-2,9.99,-19.98,1\n") # duplicate row 0&1, negative quantity row 2
    with open(os.path.join(mlzc_raw, "online.csv"), "w") as f:
        f.write(",date,item_id,quantity,price_base,sum_total,store_id\n0,2022-01-01,1001,3,9.99,29.97,1\n")
    with open(os.path.join(mlzc_raw, "stores.csv"), "w") as f:
        f.write(",store_id,division,format,city,area\n0,1,North,Supermarket,Moscow,500\n")
    with open(os.path.join(mlzc_raw, "price_history.csv"), "w") as f:
        f.write(",date,item_id,price,code,store_id\n0,2022-01-01,1001,9.99,PR1,1\n")
    with open(os.path.join(mlzc_raw, "discounts_history.csv"), "w") as f:
        f.write(",date,item_id,sale_price_before_promo,sale_price_time_promo,promo_type_code,doc_id,number_disc_day,store_id\n0,2022-01-01,1001,9.99,7.99,PROMO1,DOC1,5,1\n")
    with open(os.path.join(mlzc_raw, "markdowns.csv"), "w") as f:
        f.write(",date,item_id,normal_price,price,quantity,store_id\n0,2022-01-01,1001,9.99,7.99,3,1\n")
    with open(os.path.join(mlzc_raw, "catalog.csv"), "w") as f:
        f.write(",item_id,dept_name,class_name,subclass_name,item_type,weight_volume,weight_netto,fatness\n0,1001,Grocery,Beverages,Juice,FOOD,1.0,0.9,0.5\n")
    with open(os.path.join(mlzc_raw, "actual_matrix.csv"), "w") as f:
        f.write(",item_id,date,store_id\n0,1001,2022-01-01,1\n")

    yield
    
    # Restore original paths
    DATASET_METADATA["m5"]["local_raw_path"] = orig_m5_raw
    DATASET_METADATA["m5"]["local_processed_path"] = orig_m5_proc
    DATASET_METADATA["online_retail_ii"]["local_raw_path"] = orig_retail_raw
    DATASET_METADATA["online_retail_ii"]["local_processed_path"] = orig_retail_proc
    DATASET_METADATA["store_sales_forecasting"]["local_raw_path"] = orig_store_raw
    DATASET_METADATA["store_sales_forecasting"]["local_processed_path"] = orig_store_proc
    DATASET_METADATA["retail_sales_forecasting"]["local_raw_path"] = orig_tevec_raw
    DATASET_METADATA["retail_sales_forecasting"]["local_processed_path"] = orig_tevec_proc
    
    # Cleanup temp dirs
    shutil.rmtree(temp_raw, ignore_errors=True)
    shutil.rmtree(temp_proc, ignore_errors=True)

def test_m5_validation(mock_datasets_dirs):
    """Verifies M5 schema constraints validation and diagnostics parsing."""
    report, data = validate_m5_dataset()
    assert data["status"] == "WARNING"  # Due to invalid price in mock file
    assert "sell_prices.csv" in data["stats"]["files_checked"]
    assert data["stats"]["files_checked"]["sell_prices.csv"]["invalid_prices"] == 1

def test_online_retail_ii_validation(mock_datasets_dirs):
    """Verifies UCI Online Retail II missing values and duplicates validation."""
    report, data = validate_online_retail_ii_dataset()
    assert data["status"] == "PASS"
    assert data["stats"]["duplicate_count"] == 1
    assert data["stats"]["missing_values"]["Customer ID"] == 2

def test_m5_processing(mock_datasets_dirs):
    """Verifies deterministic processing filters out invalid prices for M5."""
    processed_rows = process_m5()
    assert processed_rows > 0
    
    # Read processed sell_prices to verify negative price was filtered out
    proc_prices_file = os.path.join(DATASET_METADATA["m5"]["local_processed_path"], "sell_prices_processed.csv")
    df = pd.read_csv(proc_prices_file)
    assert len(df) == 1
    assert float(df["sell_price"].iloc[0]) == 9.58

def test_online_retail_ii_processing(mock_datasets_dirs):
    """Verifies CustomerID backfilling and duplicate removal for Online Retail II."""
    processed_rows = process_online_retail_ii()
    assert processed_rows == 3  # 4 raw rows - 1 duplicate = 3 rows
    
    proc_file = os.path.join(DATASET_METADATA["online_retail_ii"]["local_processed_path"], "online_retail_II_processed.csv")
    df = pd.read_csv(proc_file)
    
    # Missing Customer ID should be UNKNOWN
    assert "UNKNOWN" in df["Customer ID"].values
    # Cancelled invoice is tagged correctly
    assert df[df["Invoice"] == "C536379"]["IsCancelled"].iloc[0] == True

def test_db_seeding_and_import_runs(db: Session, mock_datasets_dirs):
    """Verifies dataset registry database records and audit trails."""
    seed_dataset_sources(db)
    sources = db.query(DatasetSource).all()
    assert len(sources) >= 2
    
    # Add an import run log
    report, data = validate_online_retail_ii_dataset()
    record_pipeline_run(
        db,
        dataset_id="online_retail_ii",
        row_count=3,
        status="SUCCESS",
        error_msg=None,
        validation_data=data,
        validation_report=report
    )
    
    run = db.query(DatasetImportRun).filter(DatasetImportRun.dataset_id == "online_retail_ii").first()
    assert run is not None
    assert run.record_count == 3
    
    val = db.query(DatasetValidationResult).filter(DatasetValidationResult.import_run_id == run.id).first()
    assert val is not None
    assert val.duplicate_count == 1
    assert val.missing_values["Customer ID"] == 2

def test_strict_operational_isolation(db: Session, mock_datasets_dirs):
    """Enforces absolute separation between operational warehouse stock and raw analytical datasets."""
    # Count original operational inventory records
    orig_inventory_count = db.query(Inventory).count()
    
    # Process both datasets
    process_m5()
    process_online_retail_ii()
    process_store_sales()
    process_retail_sales()
    
    # Verify that inventory count remains exactly the same
    current_inventory_count = db.query(Inventory).count()
    assert orig_inventory_count == current_inventory_count, "Operational database corrupted by analytical dataset run!"

def test_datasets_api_endpoint(client, admin_token, db: Session):
    """Verifies analytics/datasets REST API returns metadata correctly and enforces authorization."""
    # Anonymous request
    r_anon = client.get("/analytics/datasets")
    assert r_anon.status_code == 401
    
    # Authorized request
    seed_dataset_sources(db)
    r = client.get("/analytics/datasets", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200
    
    data = r.json()
    assert "m5" in data
    assert "online_retail_ii" in data
    assert "store_sales_forecasting" in data
    assert "retail_sales_forecasting" in data
    assert data["store_sales_forecasting"]["name"] == "Store Sales Time Series Forecasting / NeuroCipher"
    assert data["retail_sales_forecasting"]["official_source"] == "Kaggle"

def test_store_sales_validation(mock_datasets_dirs):
    """Verifies Store Sales schema validation rules."""
    report, data = validate_store_sales_dataset()
    assert data["status"] == "WARNING" # due to invalid values in mock
    assert "train.csv" in data["stats"]["files_checked"]
    assert data["stats"]["files_checked"]["train.csv"]["invalid_numeric"] == 1
    assert data["stats"]["files_checked"]["transactions.csv"]["invalid_numeric"] == 1
    assert data["stats"]["duplicate_count"] == 1

def test_retail_sales_validation(mock_datasets_dirs):
    """Verifies MLZC Retail Sales schema validation rules."""
    report, data = validate_retail_sales_dataset()
    assert data["status"] == "WARNING"  # due to negative quantity in mock sales.csv
    assert "sales.csv" in data["stats"]["files_checked"]
    assert data["stats"]["files_checked"]["sales.csv"]["invalid_quantities"] == 1
    assert data["stats"]["rows_count"] > 0

def test_store_sales_processing(mock_datasets_dirs):
    """Verifies Store Sales cleaning rules (invalid numeric drops and deduplication)."""
    total_rows = process_store_sales()
    assert total_rows > 0
    
    proc_train = os.path.join(DATASET_METADATA["store_sales_forecasting"]["local_processed_path"], "train_processed.csv")
    df = pd.read_csv(proc_train)
    # Should drop negative sales and drop duplicates
    # Raw: row 0 AUTOMOTIVE 0.0, row 1 AUTOMOTIVE 0.0, row 2 AUTOMOTIVE -5.0
    # Processed: row 0 AUTOMOTIVE 0.0
    assert len(df) == 1
    assert float(df["sales"].iloc[0]) == 0.0

def test_retail_sales_processing(mock_datasets_dirs):
    """Verifies MLZC Retail Sales cleaning rules (invalid drops and deduplication)."""
    total_rows = process_retail_sales()
    assert total_rows > 0

    proc_file = os.path.join(DATASET_METADATA["retail_sales_forecasting"]["local_processed_path"], "sales_processed.csv")
    df = pd.read_csv(proc_file)
    # Raw sales.csv: row 0 & 1 are duplicates (same date/item/store), row 2 has negative quantity
    # After dedup+filter: 1 clean row should remain
    assert len(df) == 1
    assert float(df["quantity"].iloc[0]) == 5.0
