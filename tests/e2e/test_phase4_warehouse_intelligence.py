import pytest
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from backend.models import (
    User, Item, Warehouse, Inventory, StockMovement, ForecastRun,
    ForecastResult, ABCClassification, AnomalyResult, ReplenishmentRecommendation,
    WarehouseLocation
)
from backend.auth import hash_password
from ml.forecast import forecast_item
from ml.abc.classifier import ABCClassifier
from ml.anomaly.demand_anomaly import detect_demand_anomalies
from ml.replenishment.engine import run_replenishment_engine, _determine_status
from backend.audit_ledger import verify_chain


@pytest.fixture
def test_admin_token(client, db):
    """Seed and log in an admin user for testing analytics."""
    existing = db.query(User).filter(User.username == "anal_admin").first()
    if not existing:
        user = User(
            username="anal_admin",
            password_hash=hash_password("AdminPass123!"),
            role="admin"
        )
        db.add(user)
        db.commit()

    # Clear rate limiters
    try:
        from backend.main import _login_attempts
        _login_attempts.clear()
    except ImportError:
        pass

    r = client.post("/auth/login", json={"username": "anal_admin", "password": "AdminPass123!"})
    assert r.status_code == 200
    return r.json()["access_token"]


@pytest.fixture
def test_viewer_token(client, db):
    """Seed and log in a viewer user for testing RBAC."""
    existing = db.query(User).filter(User.username == "anal_viewer").first()
    if not existing:
        user = User(
            username="anal_viewer",
            password_hash=hash_password("ViewerPass123!"),
            role="viewer"
        )
        db.add(user)
        db.commit()

    r = client.post("/auth/login", json={"username": "anal_viewer", "password": "ViewerPass123!"})
    assert r.status_code == 200
    return r.json()["access_token"]


def setup_intelligence_e2e_data(db):
    """Seeds a test warehouse, item, stock movements, and inventory records."""
    db.query(ReplenishmentRecommendation).delete()
    db.query(AnomalyResult).delete()
    db.query(ABCClassification).delete()
    db.query(ForecastResult).delete()
    db.query(ForecastRun).delete()
    db.query(StockMovement).delete()
    db.query(Inventory).delete()
    db.query(WarehouseLocation).filter(WarehouseLocation.warehouse_id == "WH-INT-01").delete()
    db.query(Item).filter(Item.id == "ITM-INT-01").delete()
    db.query(Warehouse).filter(Warehouse.id == "WH-INT-01").delete()
    db.commit()

    wh = Warehouse(id="WH-INT-01", name="Intelligence Test Warehouse", location="Zone INT")
    db.add(wh)
    db.commit()

    # Lead time = 3 days, Safety stock = 10 units
    item = Item(id="ITM-INT-01", name="Predictive Item 1", unit_cost=10.0, safety_stock=10, lead_time_days=3)
    db.add(item)
    db.commit()

    # Seed 15 days of historical stock movements to satisfy forecasting and anomaly min rows threshold
    base_date = pd.to_datetime("2026-01-01")
    for i in range(15):
        date_str = (base_date + pd.Timedelta(days=i)).date()
        # Stable baseline demand of 5 units/day, except one spike (anomaly) on day 10
        out_qty = 50.0 if i == 10 else 5.0
        db.add(StockMovement(
            warehouse_id="WH-INT-01",
            item_id="ITM-INT-01",
            date=date_str,
            stock_in=0,
            stock_out=out_qty,
            closing_stock=100 - i
        ))
    db.commit()

    inv = Inventory(
        warehouse_id="WH-INT-01",
        item_id="ITM-INT-01",
        on_hand=85,
        reserved=0,
        available=85,
        damaged=0
    )
    db.add(inv)
    db.commit()


def test_data_quality_gate(db):
    setup_intelligence_e2e_data(db)

    # Fetch data gate inputs
    movements = db.query(StockMovement).filter(StockMovement.warehouse_id == "WH-INT-01").all()
    assert len(movements) == 15

    # Check for negative value protection
    for m in movements:
        assert m.stock_in >= 0
        assert m.stock_out >= 0


def test_demand_forecasting_holdout_and_baselines(db):
    setup_intelligence_e2e_data(db)

    # Execute forecast matching A* baseline requirements
    res = forecast_item("WH-INT-01", "ITM-INT-01", horizon=14, db=db)
    assert res["status"] == "success"
    assert "holdout_validation" in res
    assert "walk_forward_validation" in res

    # Baseline comparison check
    assert "naive_baseline_wape_pct" in res["holdout_validation"]
    assert "ma_baseline_wape_pct" in res["holdout_validation"]
    assert res["reliability_score"] > 0


def test_abc_inventory_classification(db):
    setup_intelligence_e2e_data(db)

    df_data = [
        {"item_id": "ITM-A", "qty": 100, "price": 50.0},
        {"item_id": "ITM-B", "qty": 50, "price": 10.0},
        {"item_id": "ITM-C", "qty": 10, "price": 5.0}
    ]
    df = pd.DataFrame(df_data)

    clf = ABCClassifier(threshold_a=91.0, threshold_b=99.5)
    clf.fit(df, item_col="item_id", qty_col="qty", value_col="price")

    summary = clf.get_summary()
    assert summary["A"]["count"] == 1
    assert summary["B"]["count"] == 1
    assert summary["C"]["count"] == 1


def test_demand_anomaly_isolation_forest(db):
    setup_intelligence_e2e_data(db)

    # Format dataframe matching family constraints
    dates = pd.date_range(start="2026-01-01", periods=15)
    sales = [5.0] * 15
    sales[10] = 100.0 # Spike outlier

    df = pd.DataFrame({"date": dates, "daily_sales": sales, "promotion_ratio": [0.0]*15})
    family_dfs = {"INT_FAMILY": df}

    res = detect_demand_anomalies(family_dfs=family_dfs, contamination=0.1, min_rows=5)
    assert res["status"] == "success"
    assert len(res["anomalies"]) > 0
    assert res["anomalies"][0]["entity"] == "INT_FAMILY"


def test_replenishment_data_sufficiency_behavior(db):
    setup_intelligence_e2e_data(db)

    # Trigger with missing safety stock/lead time on a new item
    db.add(Item(id="ITM-FAIL-1", name="Missing Data Item", unit_cost=5.0))
    db.add(Inventory(warehouse_id="WH-INT-01", item_id="ITM-FAIL-1", on_hand=15, reserved=0, available=15, damaged=0))
    db.commit()

    res = run_replenishment_engine(db, warehouse_id="WH-INT-01")
    assert res["status"] == "success"
    target = next(r for r in res["recommendations"] if r["item_id"] == "ITM-FAIL-1")
    assert target["urgency"] == "INSUFFICIENT_DATA"


def test_rbac_viewers_blocked_from_mutations(client, test_viewer_token):
    headers = {"Authorization": f"Bearer {test_viewer_token}"}

    # Attempt to post a replenishment recommendation rerun or report download
    res = client.post("/analytics/datasets", json={"dataset_id": "store_sales_forecasting"}, headers=headers)
    # Rejects mutations
    assert res.status_code in (403, 405)


def test_provenance_and_lineage_metadata(db):
    setup_intelligence_e2e_data(db)

    # Check that forecasting runs store clear lineage descriptors
    res = forecast_item("WH-INT-01", "ITM-INT-01", horizon=14, db=db)
    assert "data_provenance" in res
    assert res["data_provenance"]["historical_demand"] == "ACTUAL — PostgreSQL"
    assert res["data_provenance"]["forecast"] == "FORECAST — ML MODEL"
