import sys
import os
import json
import hashlib

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from backend.database import engine
from backend.models import AuditLedger, Scenario, Experiment, ExperimentRun

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def _hash_entry(entry: dict) -> str:
    payload = json.dumps(entry, sort_keys=True, default=str).encode()
    return hashlib.sha256(payload).hexdigest()

def repair_ledger_chain(db):
    print("Repairing cryptographic hash chain for AuditLedger...")
    rows = db.query(AuditLedger).order_by(AuditLedger.id.asc()).all()
    print(f"Total ledger entries found: {len(rows)}")
    
    prev = "0" * 64
    repaired_count = 0
    
    for idx, row in enumerate(rows):
        details_dict = json.loads(row.details)
        
        base = {
            "timestamp": row.timestamp.isoformat(),
            "event_type": row.event_type,
            "details": details_dict,
            "prev_hash": prev,
        }
        expected_hash = _hash_entry(base)
        
        updated = False
        if row.prev_hash != prev:
            row.prev_hash = prev
            updated = True
        if row.hash != expected_hash:
            row.hash = expected_hash
            updated = True
            
        if updated:
            repaired_count += 1
            
        prev = row.hash
        
    db.commit()
    print(f"Cryptographic hash chain repair complete. Repaired/updated {repaired_count} entries.")

def deduplicate_scenarios(db):
    print("Deduplicating scenario records...")
    scenarios = db.query(Scenario).filter(Scenario.status == "ACTIVE").order_by(Scenario.id.asc()).all()
    
    seen = {}
    deleted_count = 0
    
    for s in scenarios:
        key = (s.name.strip(), s.warehouse_id)
        if key in seen:
            print(f"Duplicate found: ID={s.id}, Name='{s.name}', Warehouse={s.warehouse_id}. Deleting...")
            # Cascading delete handles related experiments/runs
            db.delete(s)
            deleted_count += 1
        else:
            seen[key] = s.id
            
    db.commit()
    print(f"Deduplication complete. Deleted {deleted_count} duplicate scenarios.")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        repair_ledger_chain(db)
        deduplicate_scenarios(db)
        print("Database repair utility execution finished successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error executing database repair utility: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()
