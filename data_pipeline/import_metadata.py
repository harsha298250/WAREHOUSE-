import os
import json
from datetime import datetime
from sqlalchemy.orm import Session

from backend.database import SessionLocal, engine
from backend.models import DatasetSource, DatasetImportRun, DatasetValidationResult, Base
from data_pipeline.registry import DATASET_METADATA, REGISTRY_PATH, save_registry, ensure_directories
from data_pipeline.validate import validate_m5_dataset, validate_online_retail_ii_dataset, validate_store_sales_dataset, validate_retail_sales_dataset
from data_pipeline.process import process_m5, process_online_retail_ii, process_store_sales, process_retail_sales

def seed_dataset_sources(db: Session):
    """Seeds static metadata definitions into the dataset_sources table."""
    Base.metadata.create_all(bind=engine)
    print("Seeding dataset sources into database...")
    for key, data in DATASET_METADATA.items():
        existing = db.query(DatasetSource).filter(DatasetSource.id == key).first()
        if existing:
            # Update values
            existing.name = data["dataset_name"]
            existing.official_source = data["official_source"]
            existing.source_url = data["source_url"]
            existing.version = data["version"]
            existing.license = data["license"]
            existing.doi = data["doi"]
            existing.publisher = data["publisher"]
            existing.description = data["description"]
            existing.intended_use = data["intended_use"]
            existing.known_limitations = data["known_limitations"]
        else:
            source = DatasetSource(
                id=key,
                name=data["dataset_name"],
                official_source=data["official_source"],
                source_url=data["source_url"],
                version=data["version"],
                license=data["license"],
                doi=data["doi"],
                publisher=data["publisher"],
                description=data["description"],
                intended_use=data["intended_use"],
                known_limitations=data["known_limitations"]
            )
            db.add(source)
    db.commit()

def record_pipeline_run(db: Session, dataset_id: str, row_count: int, status: str, error_msg: str, validation_data: dict, validation_report: str):
    """Logs the import run and validation results to the database."""
    print(f"Recording import run for dataset: {dataset_id}...")
    
    # 1. Calculate raw file checksums to record
    meta = DATASET_METADATA[dataset_id]
    checksums = []
    for f in meta["expected_files"]:
        full_path = os.path.join(meta["local_raw_path"], f)
        if os.path.isfile(full_path):
            from data_pipeline.registry import calculate_checksum
            checksums.append(f"{f}:{calculate_checksum(full_path)[:12]}")
    raw_checksum = "; ".join(checksums) if checksums else "MISSING"

    # 2. Add run record
    run = DatasetImportRun(
        dataset_id=dataset_id,
        import_timestamp=datetime.now(),
        record_count=row_count,
        status=status,
        raw_checksum=raw_checksum,
        processing_version="1.0",
        error_message=error_msg
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    # 3. Add validation record
    val_status = validation_data.get("status", "FAIL")
    val_stats = validation_data.get("stats", {})
    
    # Format missing values count per column
    missing_vals = val_stats.get("missing_values", {})
    
    val_res = DatasetValidationResult(
        import_run_id=run.id,
        status=val_status,
        rows_count=val_stats.get("rows_count", 0),
        missing_values=missing_vals,
        duplicate_count=val_stats.get("duplicate_count", 0),
        invalid_records_count=val_stats.get("invalid_quantities", 0) + val_stats.get("invalid_prices", 0),
        date_range_start=val_stats.get("min_date"),
        date_range_end=val_stats.get("max_date"),
        validation_report=validation_report
    )
    db.add(val_res)
    db.commit()
    print(f"Logged import run {run.id} and validation result for {dataset_id} successfully.")

def run_import_pipeline():
    """Main execution engine for the data import and validation pipeline."""
    ensure_directories()
    save_registry()
    
    db = SessionLocal()
    try:
        # Step 1: Seed Metadata sources
        seed_dataset_sources(db)
        
        # Step 2: Validate M5 Forecasting
        print("\n=== Ingesting M5 Forecasting ===")
        m5_report, m5_data = validate_m5_dataset()
        m5_rows = 0
        m5_status = m5_data["status"]
        m5_error = None
        
        if m5_status != "FAIL":
            try:
                m5_rows = process_m5()
            except Exception as e:
                m5_status = "FAILED"
                m5_error = str(e)
                print(f"M5 processing failed: {e}")
        else:
            m5_error = "Validation failed: missing expected raw files."
            
        record_pipeline_run(db, "m5", m5_rows, m5_status, m5_error, m5_data, m5_report)
        
        # Step 3: Validate UCI Online Retail II
        print("\n=== Ingesting UCI Online Retail II ===")
        retail_report, retail_data = validate_online_retail_ii_dataset()
        retail_rows = 0
        retail_status = retail_data["status"]
        retail_error = None
        
        if retail_status != "FAIL":
            try:
                retail_rows = process_online_retail_ii()
            except Exception as e:
                retail_status = "FAILED"
                retail_error = str(e)
                print(f"Online Retail II processing failed: {e}")
        else:
            retail_error = "Validation failed: missing expected raw files."
            
        record_pipeline_run(db, "online_retail_ii", retail_rows, retail_status, retail_error, retail_data, retail_report)
        
        # Step 4: Validate Store Sales Time Series Forecasting
        print("\n=== Ingesting Store Sales Time Series Forecasting ===")
        store_report, store_data = validate_store_sales_dataset()
        store_rows = 0
        store_status = store_data["status"]
        store_error = None
        
        if store_status != "FAIL":
            try:
                store_rows = process_store_sales()
            except Exception as e:
                store_status = "FAILED"
                store_error = str(e)
                print(f"Store Sales processing failed: {e}")
        else:
            store_error = "Validation failed: missing expected raw files."
            
        record_pipeline_run(db, "store_sales_forecasting", store_rows, store_status, store_error, store_data, store_report)
        
        # Step 5: Validate Retail Sales Forecasting (TEVEC)
        print("\n=== Ingesting Retail Sales Forecasting (TEVEC) ===")
        tevec_report, tevec_data = validate_retail_sales_dataset()
        tevec_rows = 0
        tevec_status = tevec_data["status"]
        tevec_error = None
        
        if tevec_status != "FAIL":
            try:
                tevec_rows = process_retail_sales()
            except Exception as e:
                tevec_status = "FAILED"
                tevec_error = str(e)
                print(f"Retail Sales processing failed: {e}")
        else:
            tevec_error = "Validation failed: missing expected raw files."
            
        record_pipeline_run(db, "retail_sales_forecasting", tevec_rows, tevec_status, tevec_error, tevec_data, tevec_report)
        
    finally:
        db.close()

if __name__ == "__main__":
    run_import_pipeline()
