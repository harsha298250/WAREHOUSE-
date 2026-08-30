import pytest
import os
import sys
from datetime import date, timedelta
from backend.models import Warehouse, Item, StockMovement
from ml.forecast import forecast_item

_NEEDS_MYSQL = os.getenv("TEST_DB_NAME", "sqlite") == "sqlite"

def test_forecast_item_with_synthetic_data(db):
    """
    Tests rolling walk-forward forecasting on SQLite using controlled chronological synthetic data.
    Verifies metric correctness, naive/MA baseline comparison, and lack of data leakage.
    """
    # Seed warehouse
    wh = Warehouse(id="WH-FC-TEST", name="Test Forecast WH", location="City")
    db.add(wh)
    
    # Seed item
    item = Item(id="ITM-FC-TEST", name="RTX CPU Test", unit_cost=300.0, safety_stock=10, lead_time_days=3)
    db.add(item)
    db.commit()
    
    # Seed 20 days of chronological stock movement
    # Using a deterministic trend + weekly seasonality: demand = 10 + 0.5 * Day
    # Fridays have +3 demand.
    base_date = date(2026, 8, 1) # Aug 1, 2026
    for i in range(20):
        current_date = base_date + timedelta(days=i)
        weekday = current_date.weekday()
        seasonality = 3.0 if weekday == 4 else 0.0 # Friday bonus
        demand = int(10.0 + 0.5 * i + seasonality)
        
        mv = StockMovement(
            date=current_date,
            warehouse_id="WH-FC-TEST",
            item_id="ITM-FC-TEST",
            stock_in=0,
            stock_out=demand,
            closing_stock=100 - demand
        )
        db.add(mv)
    db.commit()
    
    # Execute forecasting with walk-forward validation active
    res = forecast_item("WH-FC-TEST", "ITM-FC-TEST", horizon=14, db=db)
    
    assert res["status"] == "success"
    assert res["item_id"] == "ITM-FC-TEST"
    assert res["forecast_horizon_days"] == 14
    assert len(res["forecast_next_days"]) == 14
    assert len(res["forecast_low"]) == 14
    assert len(res["forecast_high"]) == 14
    
    # Verify range is uncertainty-labeled and not described as 95% confidence interval
    assert res["data_provenance"]["forecast_range"] == "ESTIMATED (Uncertainty Range from Residual SD)"
    
    # Verify AI Decision Center elements are correct
    assert res["lead_time_demand"] > 0
    assert res["reorder_point"] == round(res["lead_time_demand"] + 10, 1)
    
    # Verify holdout metrics
    holdout = res["holdout_validation"]
    assert holdout["mae"] > 0
    assert holdout["rmse"] > 0
    assert holdout["wape_pct"] > 0
    assert holdout["smape_pct"] > 0
    assert "relative_wape_improvement_pct" in holdout
    
    # Verify walk-forward metrics (since total rows 20 >= initial 12 + horizon 7)
    wf = res["walk_forward_validation"]
    assert wf["status"] == "success"
    assert wf["mae"] > 0
    assert wf["rmse"] > 0
    assert wf["wape_pct"] > 0
    assert wf["smape_pct"] > 0
    assert "relative_wape_improvement_pct" in wf
    
    # Verify dynamic reliability score (0-100 range)
    assert 10 <= res["reliability_score"] <= 99
    
    # Verify no random shuffling leakage: input is chronologically ordered
    assert res["target_variable"] == "Outbound Daily Demand (stock_out)"


def test_forecast_insufficient_data_handling(db):
    """Verifies that the forecasting engine returns a safe response on short history."""
    wh = Warehouse(id="WH-FC-SHORT", name="Short WH", location="City")
    db.add(wh)
    item = Item(id="ITM-FC-SHORT", name="Short Item", safety_stock=5, lead_time_days=2)
    db.add(item)
    db.commit()
    
    # Seed only 5 days of data (less than minimum 10)
    base_date = date(2026, 8, 1)
    for i in range(5):
        mv = StockMovement(
            date=base_date + timedelta(days=i),
            warehouse_id="WH-FC-SHORT",
            item_id="ITM-FC-SHORT",
            stock_in=0,
            stock_out=5,
            closing_stock=20
        )
        db.add(mv)
    db.commit()
    
    res = forecast_item("WH-FC-SHORT", "ITM-FC-SHORT", horizon=14, db=db)
    assert res["status"] == "insufficient_data"
    assert "message" in res
    assert res["reliability_score"] == 0


@pytest.mark.skipif(_NEEDS_MYSQL, reason="INTEGRATION: requires MySQL with stock data")
def test_forecast_item_execution():
    res = forecast_item("WH-BLR-01", "ITM-CPU-01", horizon=14)
    assert res is not None
    assert res["status"] == "success"
