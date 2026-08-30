"""
ml/demand/evaluate.py

Evaluation metrics for demand forecasting.

Metrics implemented:
    MAE   — Mean Absolute Error
    RMSE  — Root Mean Squared Error
    WAPE  — Weighted Absolute Percentage Error (sum |y-ŷ| / sum |y|)
    sMAPE — Symmetric Mean Absolute Percentage Error

All metrics are computed out-of-sample only (never on training data).

CRITICAL: This module asserts temporal integrity before any metric
computation. A ValueError is raised if training end >= validation start.
"""
import numpy as np
import pandas as pd
from ml.demand.baseline import NaiveBaseline, MovingAverageBaseline
from ml.demand.model import TrendSeasonalityModel


def _assert_no_leakage(train_df: pd.DataFrame, val_df: pd.DataFrame):
    """
    Asserts that the training window ends strictly before the validation window starts.
    Raises ValueError if temporal leakage is detected.
    """
    train_end = pd.to_datetime(train_df["date"].max())
    val_start = pd.to_datetime(val_df["date"].min())
    if train_end >= val_start:
        raise ValueError(
            f"DATA LEAKAGE DETECTED: train_end ({train_end.date()}) >= val_start ({val_start.date()}). "
            "Training and validation windows overlap. Aborting evaluation."
        )


def _compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """Computes MAE, RMSE, WAPE, sMAPE for a prediction array."""
    n = len(y_true)
    if n == 0:
        return {"mae": None, "rmse": None, "wape_pct": None, "smape_pct": None}

    mae = float(np.mean(np.abs(y_true - y_pred)))
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))

    sum_true = float(np.sum(np.abs(y_true)))
    wape_pct = float(np.sum(np.abs(y_true - y_pred)) / max(sum_true, 1e-6)) * 100.0

    denom = (np.abs(y_true) + np.abs(y_pred)) / 2.0
    denom = np.where(denom == 0, 1e-5, denom)
    smape_pct = float(np.mean(np.abs(y_true - y_pred) / denom)) * 100.0

    return {
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "wape_pct": round(wape_pct, 2),
        "smape_pct": round(smape_pct, 2),
    }


def evaluate_family(
    family: str,
    fdf: pd.DataFrame,
    train_pct: float = 0.80,
    target_col: str = "daily_sales",
    ma_window: int = 7,
) -> dict:
    """
    Evaluates TrendSeasonalityModel vs Naive and MA baselines on a single family series.

    Uses:
    1. Chronological holdout: 80% train / 20% validation
    2. Walk-forward backtesting: step=7, eval_horizon=7

    Args:
        family: product family name
        fdf: feature DataFrame for this family (from feature_engineering.build_family_series)
        train_pct: fraction of data to use for training
        target_col: name of demand column
        ma_window: moving average window size

    Returns:
        dict with holdout metrics, walk-forward metrics, and model params
    """
    if len(fdf) < 20:
        return {
            "status": "INSUFFICIENT_DATA",
            "family": family,
            "rows": len(fdf),
            "message": "Minimum 20 daily observations required for evaluation.",
        }

    fdf = fdf.sort_values("date").reset_index(drop=True)
    n_train = max(10, int(len(fdf) * train_pct))
    train_df = fdf.iloc[:n_train].copy()
    val_df = fdf.iloc[n_train:].copy()

    # --- Temporal leakage assertion ---
    _assert_no_leakage(train_df, val_df)

    y_true = val_df[target_col].values

    # --- Fit model ---
    model = TrendSeasonalityModel(family=family)
    model.fit(train_df, target_col=target_col)

    val_dates = pd.to_datetime(val_df["date"])
    promo_ratios = val_df.get("promotion_ratio", None)
    y_model, _, _ = model.predict(start_idx=n_train, dates=val_dates, promotion_ratios=promo_ratios)

    # --- Baselines ---
    naive = NaiveBaseline().fit(train_df, target_col)
    ma = MovingAverageBaseline(window=ma_window).fit(train_df, target_col)
    y_naive = naive.predict(len(val_df))
    y_ma = ma.predict(len(val_df))

    holdout_model = _compute_metrics(y_true, y_model)
    holdout_naive = _compute_metrics(y_true, y_naive)
    holdout_ma = _compute_metrics(y_true, y_ma)

    ma_wape = holdout_ma["wape_pct"] or 0.0
    model_wape = holdout_model["wape_pct"] or 0.0
    wape_improvement = round(
        max(0.0, (ma_wape - model_wape) / max(ma_wape, 1e-5)) * 100.0, 1
    ) if ma_wape > 0 else 0.0

    # --- Walk-forward backtesting ---
    wf_actuals, wf_model_preds, wf_naive_preds, wf_ma_preds = [], [], [], []
    init_size = max(14, int(len(fdf) * 0.6))
    step = 7
    eval_h = 7
    wf_status = "success"

    if len(fdf) >= init_size + eval_h:
        origin = init_size
        while origin + eval_h <= len(fdf):
            t_sub = fdf.iloc[:origin].copy()
            v_sub = fdf.iloc[origin:origin + eval_h].copy()

            # Leakage check on each fold
            _assert_no_leakage(t_sub, v_sub)

            m_sub = TrendSeasonalityModel(family=f"{family}_wf")
            m_sub.fit(t_sub, target_col)
            v_dates = pd.to_datetime(v_sub["date"])
            pr_sub = v_sub.get("promotion_ratio", None)
            preds_sub, _, _ = m_sub.predict(origin, v_dates, pr_sub)

            n_sub = NaiveBaseline().fit(t_sub, target_col)
            ma_sub = MovingAverageBaseline(window=ma_window).fit(t_sub, target_col)

            wf_actuals.extend(v_sub[target_col].values)
            wf_model_preds.extend(preds_sub)
            wf_naive_preds.extend(n_sub.predict(eval_h))
            wf_ma_preds.extend(ma_sub.predict(eval_h))
            origin += step
    else:
        wf_status = "INSUFFICIENT_DATA_FOR_WALK_FORWARD"

    if wf_actuals:
        wf_model_m = _compute_metrics(np.array(wf_actuals), np.array(wf_model_preds))
        wf_naive_m = _compute_metrics(np.array(wf_actuals), np.array(wf_naive_preds))
        wf_ma_m = _compute_metrics(np.array(wf_actuals), np.array(wf_ma_preds))
        wf_ma_wape = wf_ma_m["wape_pct"] or 0.0
        wf_model_wape = wf_model_m["wape_pct"] or 0.0
        wf_improvement = round(
            max(0.0, (wf_ma_wape - wf_model_wape) / max(wf_ma_wape, 1e-5)) * 100.0, 1
        ) if wf_ma_wape > 0 else 0.0
    else:
        wf_model_m = wf_naive_m = wf_ma_m = {"mae": None, "rmse": None, "wape_pct": None, "smape_pct": None}
        wf_improvement = 0.0

    return {
        "status": "success",
        "family": family,
        "rows": len(fdf),
        "train_rows": n_train,
        "val_rows": len(val_df),
        "train_start": str(train_df["date"].min().date()),
        "train_end": str(train_df["date"].max().date()),
        "val_start": str(val_df["date"].min().date()),
        "val_end": str(val_df["date"].max().date()),
        "holdout": {
            "model": holdout_model,
            "naive_baseline": holdout_naive,
            "ma_baseline": holdout_ma,
            "wape_improvement_pct": wape_improvement,
        },
        "walk_forward": {
            "status": wf_status,
            "model": wf_model_m,
            "naive_baseline": wf_naive_m,
            "ma_baseline": wf_ma_m,
            "wape_improvement_pct": wf_improvement,
        },
        "model_params": model.get_params(),
        "data_leakage_check": "PASSED — train_end < val_start asserted",
    }
