import pytest
import pandas as pd
import numpy as np
from ml.anomaly.demand_anomaly import detect_demand_anomalies, _build_anomaly_features


def test_anomaly_feature_engineering():
    """Verifies temporal feature building and rolling stats computation for anomaly detection."""
    dates = pd.date_range(start="2026-01-01", periods=10)
    sales = [10, 10, 10, 10, 10, 10, 10, 10, 10, 100]  # outlier at the end
    df = pd.DataFrame({"date": dates, "daily_sales": sales})

    fdf = _build_anomaly_features(df, target_col="daily_sales")

    assert "rolling_mean_7d" in fdf.columns
    assert "rolling_std_7d" in fdf.columns
    assert "deviation_from_mean" in fdf.columns
    assert "day_of_week_effect" in fdf.columns

    # Last row should have a positive deviation
    assert fdf["deviation_from_mean"].iloc[-1] > 0.0


def test_detect_demand_anomalies():
    """Verifies anomaly detection running using IsolationForest and normalized scoring."""
    dates = pd.date_range(start="2026-01-01", periods=20)
    sales = [float(i % 5 + 10) for i in range(20)]
    # Add a huge outlier spike
    sales[10] = 500.0

    df = pd.DataFrame({"date": dates, "daily_sales": sales, "promotion_ratio": [0.0]*20})
    family_dfs = {"TEST_FAMILY": df}

    res = detect_demand_anomalies(family_dfs=family_dfs, contamination=0.1, min_rows=5)

    assert res["status"] == "success"
    assert res["summary"]["total"] >= 1

    # Outlier spike at index 10 should be captured as an anomaly
    anoms = res["anomalies"]
    entities = [a["entity"] for a in anoms]
    assert "TEST_FAMILY" in entities

    # First anomaly should have high score and severe categorization
    top_anom = anoms[0]
    assert top_anom["anomaly_score"] >= 50
    assert top_anom["severity"] in ("HIGH", "CRITICAL")
