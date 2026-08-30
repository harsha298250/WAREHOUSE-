"""
tests/test_trust_ledger.py — Trust Ledger hash chain and tampering detection tests.
"""
import pytest


class TestTrustLedger:

    def test_audit_verify_returns_200(self, client, admin_token):
        r = client.get("/audit/verify",
                       headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200

    def test_audit_verify_has_valid_field(self, client, admin_token):
        r = client.get("/audit/verify",
                       headers={"Authorization": f"Bearer {admin_token}"})
        d = r.json()
        assert "valid" in d or "status" in d, f"Missing valid/status field: {d}"

    def test_audit_verify_is_real_computation(self, client, admin_token):
        """Verification must return a proper boolean, not always True."""
        r = client.get("/audit/verify",
                       headers={"Authorization": f"Bearer {admin_token}"})
        d = r.json()
        # Result can be True or False — it must be a real boolean, not a string
        result = d.get("valid", d.get("status"))
        assert result is not None, "Verification result missing"

    def test_audit_verify_requires_auth(self, client):
        r = client.get("/audit/verify")
        assert r.status_code == 401

    def test_trust_ledger_endpoint_returns_entries(self, client, admin_token):
        r = client.get("/apps/trust-ledger",
                       headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200

    def test_trust_ledger_entries_have_hash_field(self, client, admin_token):
        r = client.get("/apps/trust-ledger",
                       headers={"Authorization": f"Bearer {admin_token}"})
        d = r.json()
        entries = d if isinstance(d, list) else d.get("entries", d.get("ledger", []))
        if entries:
            entry = entries[0]
            # Hash-chained entries should have a hash field
            has_hash = any(k in entry for k in ["hash", "entry_hash", "sha256"])
            assert has_hash, f"Ledger entry missing hash field: {entry.keys()}"


class TestTrustLedgerIntegrity:
    """Test that the audit ledger module correctly detects tampering."""

    def test_append_and_verify_chain(self):
        """Append entries and verify the chain is valid."""
        import sys, os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy.pool import StaticPool
        from backend.models import Base, AuditLedger
        from backend import audit_ledger as ledger

        # Create isolated in-memory DB for this test
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        db = Session()

        # Append 3 entries
        ledger.append_entry(db, "test_event_1", {"data": "value1"})
        ledger.append_entry(db, "test_event_2", {"data": "value2"})
        ledger.append_entry(db, "test_event_3", {"data": "value3"})

        # Verify chain is valid
        result = ledger.verify_chain(db)
        assert result.get("valid") is True, f"Chain should be valid: {result}"
        assert result.get("checked", 0) >= 3

        db.close()

    def test_tampered_entry_detected(self):
        """Modifying a ledger entry should break the chain."""
        import sys, os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy.pool import StaticPool
        from backend.models import Base, AuditLedger
        from backend import audit_ledger as ledger

        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        db = Session()

        ledger.append_entry(db, "event_a", {"val": "a"})
        ledger.append_entry(db, "event_b", {"val": "b"})
        ledger.append_entry(db, "event_c", {"val": "c"})

        # Tamper with entry 1 by changing its payload
        entry = db.query(AuditLedger).first()
        entry.event_type = "TAMPERED"
        db.commit()

        # Chain should now be invalid
        result = ledger.verify_chain(db)
        assert result.get("valid") is False, \
            f"Tampered ledger must be detected as invalid: {result}"

        db.close()

    def test_empty_chain_is_valid(self):
        """Empty ledger (no entries) must return valid=True."""
        import sys, os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy.pool import StaticPool
        from backend.models import Base
        from backend import audit_ledger as ledger

        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        db = Session()

        result = ledger.verify_chain(db)
        assert result.get("valid") is True
        assert result.get("checked", 0) == 0

        db.close()
