"""
ml/anomaly/demand_anomaly.py

Dataset-level demand anomaly detection using IsolationForest.

Extends the same approach as ml/shrinkage_detector.py to NeuroCipher
family-level daily demand data.

Features used (derived from actual data only — no future leakage):
    daily_sales          — actual daily aggregated sales
    rolling_mean_7d      — 7-day rolling mean of sales
    rolling_std_7d       — 7-day rolling standard deviation
    deviation_from_mean  — daily_sales - rolling_mean_7d
    promotion_ratio      — fraction of stores running a promotion that day
    day_of_week_effect   — weekday index (sales / weekly_mean_by_weekday)

Severity classification (documented thresholds):
    CRITICAL: score >= 85 AND abs(deviation) > 3 * rolling_std
    HIGH:     score >= 70  OR abs(deviation) > 2 * rolling_std
    MEDIUM:   score >= 50
    LOW:      score < 50

Data source: data/processed/store_sales_forecasting/train_processed.csv
"""
import logging
from datetime import datetime, UTC

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

logger = logging.getLogger("warehouse.ml.anomaly")

_DATASET_ID = "store_sales_forecasting"
_MODEL_NAME = "IsolationForest"
_MODEL_VERSION = "1.0"


def _build_anomaly_features(fdf: pd.DataFrame, target_col: str = "daily_sales") -> pd.DataFrame:
    """
    Computes anomaly detection features for a single family series.
    All features are derived from past data only (no future leakage).
    """
    fdf = fdf.sort_values("date").reset_index(drop=True).copy()
    fdf["rolling_mean_7d"] = fdf[target_col].rolling(7, min_periods=1).mean()
    fdf["rolling_std_7d"] = fdf[target_col].rolling(7, min_periods=1).std().fillna(0.0)
    fdf["deviation_from_mean"] = fdf[target_col] - fdf["rolling_mean_7d"]

    # Weekday effect = sales / weekly mean by weekday
    if "day_of_week" not in fdf.columns:
        fdf["day_of_week"] = pd.to_datetime(fdf["date"]).dt.weekday
    wd_mean = fdf.groupby("day_of_week")[target_col].transform("mean")
    fdf["day_of_week_effect"] = fdf[target_col] / (wd_mean.clip(lower=1e-6))

    if "promotion_ratio" not in fdf.columns:
        fdf["promotion_ratio"] = 0.0

    return fdf


def detect_demand_anomalies(
    family_dfs: dict = None,
    contamination: float = 0.05,
    min_rows: int = 14,
    target_col: str = "daily_sales",
) -> dict:
    """
    Detects demand anomalies across all product families.

    Args:
        family_dfs: dict[family -> DataFrame] from feature_engineering.build_family_series().
                    If None, builds it from the processed CSV automatically.
        contamination: expected fraction of anomalies (default 5%)
        min_rows: minimum rows per family to run detection
        target_col: demand column name

    Returns:
        dict with anomalies list and summary
    """
    if family_dfs is None:
        from ml.demand.feature_engineering import build_family_series
        try:
            family_dfs = build_family_series()
        except FileNotFoundError as e:
            return {"status": "insufficient_data", "anomalies": [], "summary": {}, "error": str(e)}

    all_anomalies = []

    for family, fdf in family_dfs.items():
        if len(fdf) < min_rows:
            logger.debug(f"Skipping family '{family}' — only {len(fdf)} rows (min {min_rows}).")
            continue

        try:
            fdf = _build_anomaly_features(fdf, target_col)
        except Exception as e:
            logger.warning(f"Feature engineering failed for family '{family}': {e}")
            continue

        feature_cols = [
            target_col, "rolling_mean_7d", "rolling_std_7d",
            "deviation_from_mean", "promotion_ratio", "day_of_week_effect"
        ]
        feat_df = fdf[feature_cols].copy()
        feat_df = feat_df.replace([np.inf, -np.inf], np.nan).fillna(0.0)

        # Drop zero-variance columns to prevent IsolationForest crash
        active_cols = [c for c in feature_cols if feat_df[c].std() > 1e-5]
        if len(active_cols) < 2:
            active_cols = [target_col, "rolling_mean_7d"]

        model = IsolationForest(contamination=contamination, random_state=42)
        preds = model.fit_predict(feat_df[active_cols])
        scores_raw = model.decision_function(feat_df[active_cols])

        fdf["is_flagged"] = preds == -1
        fdf["decision_score"] = scores_raw

        flagged = fdf[fdf["is_flagged"]].copy()

        for _, row in flagged.iterrows():
            decision_val = float(row["decision_score"])
            # Normalize to 0-100 (same formula as shrinkage_detector.py)
            priority_score = int(min(99, max(10, round((0.25 - decision_val) * 140))))

            sales_val = float(row[target_col])
            rolling_mean = float(row["rolling_mean_7d"])
            rolling_std = float(row["rolling_std_7d"])
            deviation = float(row["deviation_from_mean"])
            abs_dev = abs(deviation)

            # Severity classification (documented thresholds)
            if priority_score >= 85 and abs_dev > 3 * max(rolling_std, 1e-6):
                severity = "CRITICAL"
            elif priority_score >= 70 or abs_dev > 2 * max(rolling_std, 1e-6):
                severity = "HIGH"
            elif priority_score >= 50:
                severity = "MEDIUM"
            else:
                severity = "LOW"

            # Reason classification
            if sales_val > rolling_mean + 2 * rolling_std:
                reason = "DEMAND_SPIKE"
            elif sales_val < max(0, rolling_mean - 2 * rolling_std):
                reason = "DEMAND_DROP"
            elif float(row.get("promotion_ratio", 0)) > 0.5 and sales_val < rolling_mean:
                reason = "PROMOTION_UNDERPERFORMANCE"
            else:
                reason = "STATISTICAL_OUTLIER"

            date_str = pd.to_datetime(row["date"]).strftime("%Y-%m-%d") if "date" in row.index else "unknown"

            features_json = {
                "daily_sales": round(sales_val, 2),
                "rolling_mean_7d": round(rolling_mean, 2),
                "rolling_std_7d": round(rolling_std, 2),
                "deviation_from_mean": round(deviation, 2),
                "promotion_ratio": round(float(row.get("promotion_ratio", 0)), 3),
                "day_of_week": int(row.get("day_of_week", -1)),
            }

            all_anomalies.append({
                "dataset_id": _DATASET_ID,
                "entity": family,
                "date": date_str,
                "anomaly_score": priority_score,
                "is_anomaly": True,
                "severity": severity,
                "reason": reason,
                "features_json": features_json,
                "model_name": _MODEL_NAME,
                "model_version": _MODEL_VERSION,
            })

    # Sort by score descending
    all_anomalies.sort(key=lambda x: x["anomaly_score"], reverse=True)

    by_severity = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for a in all_anomalies:
        by_severity[a["severity"]] = by_severity.get(a["severity"], 0) + 1

    return {
        "status": "success",
        "anomalies": all_anomalies,
        "summary": {
            "total": len(all_anomalies),
            "by_severity": by_severity,
            "families_analyzed": len(family_dfs),
            "model": _MODEL_NAME,
            "contamination": contamination,
        },
    }


def save_anomalies_to_db(db, result: dict, warehouse_id: str = None) -> int:
    """Saves demand anomaly results to the AnomalyResult table."""
    from backend.models import AnomalyResult

    anomalies = result.get("anomalies", [])
    if not anomalies:
        return 0

    # Replace previous results for this dataset and warehouse
    q = db.query(AnomalyResult).filter(AnomalyResult.dataset_id == _DATASET_ID)
    if warehouse_id:
        q = q.filter(AnomalyResult.warehouse_id == warehouse_id)
    else:
        q = q.filter(AnomalyResult.warehouse_id.is_(None))
    q.delete()

    now = datetime.now(UTC).replace(tzinfo=None)
    rows = []
    for a in anomalies:
        rows.append(AnomalyResult(
            dataset_id=a["dataset_id"],
            warehouse_id=warehouse_id,
            entity=a["entity"],
            date=a["date"],
            anomaly_score=a["anomaly_score"],
            is_anomaly=True,
            severity=a["severity"],
            reason=a["reason"],
            features_json=a["features_json"],
            model_name=a["model_name"],
            model_version=a["model_version"],
            created_at=now,
        ))

    db.bulk_save_objects(rows)
    db.commit()
    logger.info(f"Saved {len(rows)} demand anomalies to DB (warehouse={warehouse_id}).")
    return len(rows)
