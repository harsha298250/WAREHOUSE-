"""
audit_ledger.py — Tamper-evident audit trail, now backed by PostgreSQL.
Each entry stores the SHA-256 hash of the previous entry (hash-chained,
like a simplified blockchain). Altering a past row breaks the chain and
verify_chain() detects exactly where.
"""
import hashlib
import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.models import AuditLedger


def _hash_entry(entry: dict) -> str:
    payload = json.dumps(entry, sort_keys=True, default=str).encode()
    return hashlib.sha256(payload).hexdigest()


def append_entry(db: Session, event_type: str, details: dict):
    prev = db.query(AuditLedger).order_by(AuditLedger.id.desc()).first()
    prev_hash = prev.hash if prev else "0" * 64

    ts = datetime.now(timezone.utc).replace(tzinfo=None).replace(microsecond=0)  # match PostgreSQL TIMESTAMP precision exactly
    base = {"timestamp": ts.isoformat(), "event_type": event_type, "details": details, "prev_hash": prev_hash}
    entry_hash = _hash_entry(base)

    row = AuditLedger(
        timestamp=ts, event_type=event_type, details=json.dumps(details),
        prev_hash=prev_hash, hash=entry_hash,
    )
    db.add(row)
    db.commit()
    try:
        db.refresh(row)
    except Exception:
        pass
    return row







def read_ledger(db: Session, limit: int = 50):
    rows = db.query(AuditLedger).order_by(AuditLedger.id.desc()).limit(limit).all()
    return list(reversed(rows))


def verify_chain(db: Session):
    rows = db.query(AuditLedger).order_by(AuditLedger.id.asc()).all()
    prev = "0" * 64
    for i, row in enumerate(rows):
        base = {
            "timestamp": row.timestamp.isoformat(), "event_type": row.event_type,
            "details": json.loads(row.details), "prev_hash": row.prev_hash,
        }
        expected = _hash_entry(base)
        if row.prev_hash != prev or row.hash != expected:
            return {"valid": False, "checked": i, "broken_at": row.id}
        prev = row.hash
    return {"valid": True, "checked": len(rows), "broken_at": None}
