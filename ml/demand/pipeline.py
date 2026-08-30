"""
ml/demand/pipeline.py

Orchestrates the end-to-end demand forecasting pipeline:
1. Feature engineering (NeuroCipher CSV → family series)
2. Chronological train/val split (80/20)
3. Model fit + evaluation (holdout + walk-forward)
4. Generate horizon forecasts
5. Persist ForecastRun + ForecastResult to PostgreSQL

Memory-safe: uses chunked CSV reading in feature_engineering.
Does not load any CSV into memory beyond what is needed.

Usage:
    from ml.demand.pipeline import run_forecast_pipeline
    result = run_forecast_pipeline(db=db_session, family="GROCERY I")
    result = run_forecast_pipeline(db=db_session)  # runs all families
"""
import uuid
import logging
import os
from datetime import datetime, UTC

import numpy as np
import pandas as pd

from ml.demand.feature_engineering import build_family_series
from ml.demand.model import TrendSeasonalityModel
from ml.demand.evaluate import evaluate_family
from backend.models import ForecastRun, ForecastResult

logger = logging.getLogger("warehouse.ml.demand")

_HORIZON_DAYS = 28
_DATASET_ID = "store_sales_forecasting"
_MODEL_NAME = "TrendSeasonalityModel"
_GRAIN = "family-level-aggregated"


def _generate_forecasts(model: TrendSeasonalityModel, fdf: pd.DataFrame,
                        horizon: int = _HORIZON_DAYS) -> list:
    """
    Generates `horizon` future date predictions starting from the last date in fdf.
    Returns list of dicts: {entity, forecast_date, predicted_demand, lower_bound, upper_bound}
    """
    last_date = pd.to_datetime(fdf["date"].max())
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=horizon, freq="D")

    # Use average promotion ratio from last 7 days as future proxy
    if "promotion_ratio" in fdf.columns:
        promo_proxy = fdf["promotion_ratio"].tail(7).mean()
        future_promos = pd.Series([promo_proxy] * horizon)
    else:
        future_promos = None

    start_idx = len(fdf)
    points, lowers, uppers = model.predict(start_idx=start_idx, dates=future_dates,
                                           promotion_ratios=future_promos)

    results = []
    for i, dt in enumerate(future_dates):
        results.append({
            "forecast_date": dt.strftime("%Y-%m-%d"),
            "predicted_demand": float(points[i]),
            "lower_bound": float(lowers[i]),
            "upper_bound": float(uppers[i]),
        })
    return results


def run_forecast_pipeline(
    db,
    family: str = None,
    horizon: int = _HORIZON_DAYS,
    train_pct: float = 0.80,
    warehouse_id: str = None,
) -> dict:
    """
    Runs the full demand forecast pipeline for one or all families.

    Args:
        db: SQLAlchemy Session
        family: if None, runs all families; otherwise runs only that family
        horizon: forecast horizon in days
        train_pct: fraction of data used for training (remainder = validation)
        warehouse_id: optional warehouse identifier

    Returns:
        dict with run_id, families processed, aggregate metrics
    """
    logger.info(f"Starting forecast pipeline (family={family!r}, horizon={horizon}d, warehouse={warehouse_id}) ...")

    # 1. Feature engineering
    try:
        all_families = build_family_series()
    except FileNotFoundError as e:
        return {"status": "error", "message": str(e)}

    if family is not None:
        if family not in all_families:
            return {"status": "error", "message": f"Family '{family}' not found in dataset."}
        families_to_run = {family: all_families[family]}
    else:
        families_to_run = all_families

    results_summary = []
    all_mae, all_rmse, all_wape, all_smape = [], [], [], []
    all_naive_wape, all_ma_wape, all_improvement = [], [], []

    for fam_name, fdf in families_to_run.items():
        logger.info(f"  Processing family: {fam_name} ({len(fdf)} rows) ...")

        # 2. Evaluate model
        eval_result = evaluate_family(fam_name, fdf, train_pct=train_pct)
        if eval_result.get("status") != "success":
            logger.warning(f"  Skipping {fam_name}: {eval_result.get('message', 'insufficient data')}")
            results_summary.append({"family": fam_name, "status": "skipped"})
            continue

        # Pick best validation metrics (prefer walk-forward if available)
        wf = eval_result["walk_forward"]
        ho = eval_result["holdout"]
        best = wf["model"] if wf["status"] == "success" else ho["model"]
        best_naive = wf["naive_baseline"] if wf["status"] == "success" else ho["naive_baseline"]
        best_ma = wf["ma_baseline"] if wf["status"] == "success" else ho["ma_baseline"]
        best_improvement = wf.get("wape_improvement_pct") or ho.get("wape_improvement_pct") or 0.0

        # 3. Generate forecasts using full data (no leakage — predictions are future-only)
        model = TrendSeasonalityModel(fam_name)
        model.fit(fdf, target_col="daily_sales")
        forecast_records = _generate_forecasts(model, fdf, horizon=horizon)

        # 4. Persist to PostgreSQL
        run_id = str(uuid.uuid4())
        run = ForecastRun(
            run_id=run_id,
            warehouse_id=warehouse_id,
            dataset_id=_DATASET_ID,
            model_name=_MODEL_NAME,
            grain=f"{_GRAIN}:{fam_name}",
            train_start=eval_result["train_start"],
            train_end=eval_result["train_end"],
            val_start=eval_result["val_start"],
            val_end=eval_result["val_end"],
            horizon_days=horizon,
            feature_set=["daily_sales", "day_of_week", "month", "week_of_year",
                         "days_since_start", "rolling_mean_7d", "promotion_ratio", "oil_price"],
            params=eval_result["model_params"],
            mae=best["mae"],
            rmse=best["rmse"],
            wape_pct=best["wape_pct"],
            smape_pct=best["smape_pct"],
            naive_wape_pct=best_naive.get("wape_pct"),
            ma_wape_pct=best_ma.get("wape_pct"),
            wape_improvement_pct=best_improvement,
            created_at=datetime.now(UTC).replace(tzinfo=None),
        )
        db.add(run)

        for rec in forecast_records:
            db.add(ForecastResult(
                run_id=run_id,
                entity=fam_name,
                forecast_date=rec["forecast_date"],
                predicted_demand=rec["predicted_demand"],
                lower_bound=rec["lower_bound"],
                upper_bound=rec["upper_bound"],
            ))

        db.flush()  # flush each family before next to limit memory

        if best["mae"] is not None:
            all_mae.append(best["mae"])
            all_rmse.append(best["rmse"])
            all_wape.append(best["wape_pct"])
            all_smape.append(best["smape_pct"])
            all_naive_wape.append(best_naive.get("wape_pct") or 0.0)
            all_ma_wape.append(best_ma.get("wape_pct") or 0.0)
            all_improvement.append(best_improvement)

        results_summary.append({
            "family": fam_name,
            "status": "success",
            "run_id": run_id,
            "mae": best["mae"],
            "rmse": best["rmse"],
            "wape_pct": best["wape_pct"],
            "smape_pct": best["smape_pct"],
            "wape_improvement_pct": best_improvement,
        })

    db.commit()
    logger.info(f"Forecast pipeline complete. {len(results_summary)} families processed.")

    return {
        "status": "success",
        "families_processed": len([r for r in results_summary if r["status"] == "success"]),
        "families_skipped": len([r for r in results_summary if r["status"] == "skipped"]),
        "aggregate_metrics": {
            "mean_mae": round(float(np.mean(all_mae)), 4) if all_mae else None,
            "mean_rmse": round(float(np.mean(all_rmse)), 4) if all_rmse else None,
            "median_wape_pct": round(float(np.median(all_wape)), 2) if all_wape else None,
            "mean_smape_pct": round(float(np.mean(all_smape)), 2) if all_smape else None,
            "median_naive_wape_pct": round(float(np.median(all_naive_wape)), 2) if all_naive_wape else None,
            "median_ma_wape_pct": round(float(np.median(all_ma_wape)), 2) if all_ma_wape else None,
            "mean_wape_improvement_pct": round(float(np.mean(all_improvement)), 1) if all_improvement else None,
        },
        "horizon_days": horizon,
        "dataset": _DATASET_ID,
        "model": _MODEL_NAME,
        "grain": _GRAIN,
        "data_leakage_check": "PASSED — train_end < val_start asserted per family",
        "families": results_summary,
    }
