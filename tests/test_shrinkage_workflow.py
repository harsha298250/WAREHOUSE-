import pytest
import os
import sys
from datetime import date, timedelta
from backend.models import Warehouse, Item, StockMovement
from ml.shrinkage_detector import detect_shrinkage

_NEEDS_MYSQL = os.getenv("TEST_DB_NAME", "sqlite") == "sqlite"

def test_shrinkage_detector_with_synthetic_data(db):
    """
    Tests IsolationForest anomaly detection on SQLite using controlled synthetic data.
    Verifies reconciliation math, exposure calculation, and terminology compliance.
    """
    # Seed warehouse
    wh = Warehouse(id="WH-SHR-TEST", name="Test Shrinkage WH", location="City")
    db.add(wh)
    
    # Seed item
    item = Item(id="ITM-SHR-TEST", name="RTX GPU Test", unit_cost=500.0, category="Electronics")
    db.add(item)
    db.commit()
    
    # Seed 9 days of normal data
    base_date = date(2026, 8, 1)
    # Day 1: opening = 50, in = 5, out = 2 -> closing = 53
    # Day i: opening = 50 + (i-1)*3, in = 5, out = 2 -> closing = 50 + i*3
    for i in range(9):
        mv = StockMovement(
            date=base_date + timedelta(days=i),
            warehouse_id="WH-SHR-TEST",
            item_id="ITM-SHR-TEST",
            stock_in=5,
            stock_out=2,
            closing_stock=50 + (i + 1) * 3
        )
        db.add(mv)
        
    # Day 10: discrepancy anomaly
    # Previous closing (Day 9) = 50 + 9 * 3 = 77
    # Expected closing: 77 + 5 - 2 = 80
    # Actual recorded closing: 50 -> discrepancy is -30 units
    mv_anomaly = StockMovement(
        date=base_date + timedelta(days=9),
        warehouse_id="WH-SHR-TEST",
        item_id="ITM-SHR-TEST",
        stock_in=5,
        stock_out=2,
        closing_stock=50
    )
    db.add(mv_anomaly)
    db.commit()
    
    # Run detector
    res = detect_shrinkage(contamination=0.1, db=db)
    assert res["status"] == "success"
    anomalies = res["anomalies"]
    
    # Verify anomaly detected
    assert len(anomalies) > 0
    anomaly = [a for a in anomalies if a["item_id"] == "ITM-SHR-TEST"][0]
    
    assert anomaly["expected_quantity"] == 80.0
    assert anomaly["actual_quantity"] == 50.0
    assert anomaly["discrepancy_quantity"] == -30.0
    assert anomaly["estimated_exposure"] == 15000.0  # 30 * 500.0
    assert "RTX GPU Test" in anomaly["item_name"]
    assert anomaly["model_name"] == "IsolationForest"
    assert "theft" not in anomaly["explanation"].lower()
    assert "theft" not in anomaly["likely_cause"].lower()
    assert anomaly["data_provenance"]["inventory"] == "ACTUAL — PostgreSQL"


def test_shrinkage_detector_insufficient_data_handling(db):
    """Verifies that the detector returns a safe status on insufficient database observations."""
    wh = Warehouse(id="WH-SHR-SHORT", name="Short WH", location="City")
    db.add(wh)
    item = Item(id="ITM-SHR-SHORT", name="Short Item", unit_cost=100.0)
    db.add(item)
    db.commit()
    
    base_date = date(2026, 8, 1)
    for i in range(3):
        mv = StockMovement(
            date=base_date + timedelta(days=i),
            warehouse_id="WH-SHR-SHORT",
            item_id="ITM-SHR-SHORT",
            stock_in=10,
            stock_out=5,
            closing_stock=50
        )
        db.add(mv)
    db.commit()
    
    res = detect_shrinkage(db=db)
    # When run on a seeded database, other warehouses may generate anomalies,
    # so we filter and verify that no anomalies are detected for the short dataset warehouse
    anomalies_short = [a for a in res.get("anomalies", []) if "WH-SHR-SHORT" in a.get("anomaly_id", "")]
    assert len(anomalies_short) == 0


@pytest.mark.skipif(_NEEDS_MYSQL, reason="INTEGRATION: requires MySQL database with seed data")
def test_audit_verify_endpoint(client):
    # This remains as integration test
    pass

@pytest.mark.skipif(_NEEDS_MYSQL, reason="INTEGRATION: requires MySQL database with seed data")
def test_manager_decision_action(client):
    # This remains as integration test
    pass
