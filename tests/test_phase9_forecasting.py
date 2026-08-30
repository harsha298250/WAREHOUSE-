import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from ml.demand.feature_engineering import build_family_series
from ml.demand.baseline import NaiveBaseline, MovingAverageBaseline
from ml.demand.model import TrendSeasonalityModel
from ml.demand.evaluate import evaluate_family, _assert_no_leakage
from ml.demand.pipeline import run_forecast_pipeline


def test_no_leakage_assertion():
    """Verifies that _assert_no_leakage raises ValueError if splits overlap or are out of order."""
    dates_train = pd.date_range(start="2026-01-01", end="2026-01-10")
    dates_val_bad = pd.date_range(start="2026-01-09", end="2026-01-15")
    dates_val_good = pd.date_range(start="2026-01-11", end="2026-01-15")

    train_df = pd.DataFrame({"date": dates_train, "daily_sales": range(len(dates_train))})
    val_bad_df = pd.DataFrame({"date": dates_val_bad, "daily_sales": range(len(dates_val_bad))})
    val_good_df = pd.DataFrame({"date": dates_val_good, "daily_sales": range(len(dates_val_good))})

    # Should raise error for overlapping splits
    with pytest.raises(ValueError, match="DATA LEAKAGE DETECTED"):
        _assert_no_leakage(train_df, val_bad_df)

    # Should pass cleanly for chronologically distinct splits
    _assert_no_leakage(train_df, val_good_df)


def test_baseline_predictions():
    """Verifies Naive and Moving Average baseline predictions work correctly."""
    dates = pd.date_range(start="2026-01-01", periods=10)
    sales = [10, 12, 14, 16, 18, 20, 22, 24, 26, 50]  # last is 50
    df = pd.DataFrame({"date": dates, "daily_sales": sales})

    naive = NaiveBaseline().fit(df)
    ma = MovingAverageBaseline(window=3).fit(df)

    preds_naive = naive.predict(5)
    preds_ma = ma.predict(5)

    assert len(preds_naive) == 5
    assert np.all(preds_naive == 50)  # last value

    assert len(preds_ma) == 5
    # average of last 3: (24 + 26 + 50) / 3 = 33.3333
    assert np.allclose(preds_ma, 33.3333)


def test_model_fit_and_predict():
    """Verifies that TrendSeasonalityModel fits and generates forecasts within bounds."""
    dates = pd.date_range(start="2026-01-01", periods=30)
    sales = [float(i % 7 + 10) for i in range(30)]  # weekly pattern
    df = pd.DataFrame({
        "date": dates,
        "daily_sales": sales,
        "promotion_ratio": [0.1 if i % 2 == 0 else 0.0 for i in range(30)]
    })

    model = TrendSeasonalityModel(family="TEST_FAMILY")
    model.fit(df)

    assert model._fitted
    assert model.slope is not None
    assert model.intercept is not None
    assert len(model.weekday_index) == 7

    # Predict horizon
    future_dates = pd.date_range(start="2026-01-31", periods=7)
    promos = pd.Series([0.1] * 7)
    points, lowers, uppers = model.predict(start_idx=30, dates=future_dates, promotion_ratios=promos)

    assert len(points) == 7
    assert len(lowers) == 7
    assert len(uppers) == 7
    assert np.all(points >= 0.0)
    assert np.all(points >= lowers)
    assert np.all(uppers >= points)


def test_evaluate_family_insufficient_data():
    """Verifies that evaluate_family handles low observation counts safely."""
    dates = pd.date_range(start="2026-01-01", periods=10)
    df = pd.DataFrame({"date": dates, "daily_sales": range(10)})
    res = evaluate_family("SMALL_FAMILY", df)
    assert res["status"] == "INSUFFICIENT_DATA"
