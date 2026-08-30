import os
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import argparse
import logging
from datetime import datetime, timezone
from sqlalchemy import create_engine, MetaData, Table, inspect, text
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("postgres_migration")

TABLES_ORDER = [
    "users",
    "warehouses",
    "items",
    "stock_movements",
    "shrinkage_flags",
    "ai_recommendations",
    "audit_ledger",
    "access_log",
    "recovery_credentials",
    "recovery_codes",
    "backup_records"
]

SERIAL_TABLES = [
    "users",
    "stock_movements",
    "shrinkage_flags",
    "ai_recommendations",
    "audit_ledger",
    "access_log",
    "recovery_credentials",
    "recovery_codes",
    "backup_records"
]


def run_migration():
    parser = argparse.ArgumentParser(description="Migrate Smart Warehouse Database to PostgreSQL")
    parser.add_argument("--source-url", help="Source Database URL (SQLite or MySQL)", default=None)
    parser.add_argument("--target-url", help="Target PostgreSQL Database URL", default=None)
    parser.add_argument("--verify-only", action="store_true", help="Compare row counts without writing data")
    parser.add_argument("--skip-clean", action="store_true", help="Do not truncate target tables before insertion")
    args = parser.parse_args()

    # Determine source database URL
    source_url = args.source_url or os.getenv("DATABASE_URL")
    if not source_url:
        # Fallback constructor for default MySQL
        db_user = os.getenv("DB_USER", "warehouse_app")
        db_pass = os.getenv("DB_PASSWORD", "")
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "3306")
        db_name = os.getenv("DB_NAME", "warehouse_db")
        source_url = f"mysql+pymysql://{db_user}:{quote_plus(db_pass)}@{db_host}:{db_port}/{db_name}"

    # Normalize source prefix
    if source_url.startswith("postgres://"):
        source_url = source_url.replace("postgres://", "postgresql://", 1)
    elif source_url.startswith("mysql://") and not source_url.startswith("mysql+pymysql://"):
        source_url = source_url.replace("mysql://", "mysql+pymysql://", 1)

    # Determine target database URL
    target_url = args.target_url or os.getenv("TARGET_DATABASE_URL")
    if not target_url and not args.verify_only:
        logger.error("Target PostgreSQL Database URL is required. Pass --target-url or set TARGET_DATABASE_URL env var.")
        sys.exit(1)

    if target_url and target_url.startswith("postgres://"):
        target_url = target_url.replace("postgres://", "postgresql://", 1)

    logger.info("Initializing Database Engines...")
    logger.info(f"Source DB: {source_url.split('@')[-1] if '@' in source_url else source_url}")
    
    src_engine = create_engine(source_url)
    
    if args.verify_only:
        if not target_url:
            logger.info("No target URL specified. Running source database verification checks only.")
            src_metadata = MetaData()
            src_metadata.reflect(bind=src_engine)
            for table_name in TABLES_ORDER:
                if table_name in src_metadata.tables:
                    t = src_metadata.tables[table_name]
                    with src_engine.connect() as conn:
                        cnt = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
                    logger.info(f"Source Table '{table_name}': {cnt} records")
            sys.exit(0)

    logger.info(f"Target DB: {target_url.split('@')[-1] if '@' in target_url else target_url}")
    tgt_engine = create_engine(target_url)

    # Reflect metadata
    src_metadata = MetaData()
    src_metadata.reflect(bind=src_engine)

    tgt_metadata = MetaData()
    tgt_metadata.reflect(bind=tgt_engine)

    # Check that all tables exist in source and target
    missing_src = [t for t in TABLES_ORDER if t not in src_metadata.tables]
    missing_tgt = [t for t in TABLES_ORDER if t not in tgt_metadata.tables]

    if missing_src:
        logger.warning(f"Tables missing in Source database: {missing_src}")
    if missing_tgt:
        logger.error(f"Tables missing in Target database (Did you run 'alembic upgrade head'?): {missing_tgt}")
        sys.exit(1)

    if args.verify_only:
        logger.info("--- ROW COUNT COMPARISON ---")
        row_counts_match = True
        for table_name in TABLES_ORDER:
            with src_engine.connect() as s_conn, tgt_engine.connect() as t_conn:
                s_cnt = s_conn.execute(text(f'SELECT COUNT(*) FROM "{table_name}"')).scalar()
                t_cnt = t_conn.execute(text(f'SELECT COUNT(*) FROM "{table_name}"')).scalar()
                diff = s_cnt - t_cnt
                status = "MATCH" if diff == 0 else "MISMATCH"
                if diff != 0:
                    row_counts_match = False
                logger.info(f"Table '{table_name}': Source={s_cnt} | Target={t_cnt} | Diff={diff} ({status})")
        
        # Verify trust ledger hash chain integrity on target
        if "audit_ledger" in tgt_metadata.tables:
            from backend.audit_ledger import verify_chain
            from sqlalchemy.orm import sessionmaker
            TgtSession = sessionmaker(bind=tgt_engine)
            db = TgtSession()
            try:
                res = verify_chain(db)
                if res["valid"]:
                    logger.info("Trust Ledger chain verified on target database: INTEGRITY VALID")
                else:
                    logger.error(f"Trust Ledger chain verification FAILED on target database: broken at entry index {res['broken_at']}")
                    row_counts_match = False
            except Exception as audit_err:
                logger.error(f"Could not verify trust ledger: {audit_err}")
            finally:
                db.close()

        if row_counts_match:
            logger.info("Verification Complete: All row counts match successfully.")
            sys.exit(0)
        else:
            logger.warning("Verification Complete: Some row count mismatches exist.")
            sys.exit(1)

    # Clean target tables in reverse order of foreign key relationships
    if not args.skip_clean:
        logger.info("Cleaning target PostgreSQL tables (Cascading Truncation)...")
        with tgt_engine.begin() as conn:
            for table_name in reversed(TABLES_ORDER):
                try:
                    conn.execute(text(f'TRUNCATE TABLE "{table_name}" CASCADE;'))
                    logger.info(f"Truncated target table: '{table_name}'")
                except Exception as clean_err:
                    logger.warning(f"Truncate failed for '{table_name}' (will delete instead): {clean_err}")
                    conn.execute(text(f'DELETE FROM "{table_name}";'))

    # Copy data table by table
    logger.info("Starting Data Copy to PostgreSQL...")
    for table_name in TABLES_ORDER:
        src_table = Table(table_name, src_metadata, autoload_with=src_engine)
        tgt_table = Table(table_name, tgt_metadata, autoload_with=tgt_engine)

        with src_engine.connect() as src_conn:
            rows = src_conn.execute(src_table.select()).fetchall()
        
        if not rows:
            logger.info(f"Table '{table_name}': Source is empty. Skipping.")
            continue

        insert_data = [dict(row._mapping) for row in rows]
        
        logger.info(f"Copying {len(insert_data)} rows for table '{table_name}'...")
        chunk_size = 500
        with tgt_engine.begin() as tgt_conn:
            for idx in range(0, len(insert_data), chunk_size):
                chunk = insert_data[idx:idx + chunk_size]
                tgt_conn.execute(tgt_table.insert(), chunk)

    # Reset PostgreSQL Serial Sequences
    logger.info("Synchronizing PostgreSQL serial sequences...")
    with tgt_engine.begin() as conn:
        for table_name in SERIAL_TABLES:
            try:
                # Check sequence name
                seq_res = conn.execute(text(f"SELECT pg_get_serial_sequence('\"{table_name}\"', 'id')")).scalar()
                if seq_res:
                    # Query max id
                    max_id = conn.execute(text(f'SELECT MAX(id) FROM "{table_name}"')).scalar()
                    if max_id is not None:
                        conn.execute(text(f"SELECT setval('{seq_res}', {max_id})"))
                        logger.info(f"Reset sequence '{seq_res}' to {max_id}")
                    else:
                        conn.execute(text(f"SELECT setval('{seq_res}', 1, false)"))
                        logger.info(f"Reset sequence '{seq_res}' to baseline 1")
            except Exception as seq_err:
                logger.warning(f"Could not reset sequence for table '{table_name}': {seq_err}")

    logger.info("Data Migration completed successfully.")
    
    # Run verification count comparison
    logger.info("Verifying record counts...")
    all_match = True
    for table_name in TABLES_ORDER:
        with src_engine.connect() as s_conn, tgt_engine.connect() as t_conn:
            s_cnt = s_conn.execute(text(f'SELECT COUNT(*) FROM "{table_name}"')).scalar()
            t_cnt = t_conn.execute(text(f'SELECT COUNT(*) FROM "{table_name}"')).scalar()
            diff = s_cnt - t_cnt
            if diff != 0:
                all_match = False
            logger.info(f"Verification '{table_name}': Source={s_cnt} | Target={t_cnt} | Diff={diff}")

    if all_match:
        logger.info("PostgreSQL Database Migration Verified: SUCCESS")
    else:
        logger.error("PostgreSQL Database Migration Row Counts MISMATCH. Please inspect logs.")


if __name__ == "__main__":
    run_migration()
