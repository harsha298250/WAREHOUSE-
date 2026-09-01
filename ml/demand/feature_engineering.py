"""
ml/demand/feature_engineering.py

Builds family-level daily demand time series from the NeuroCipher
Store Sales Forecasting processed CSV files.

Data source: data/processed/store_sales_forecasting/
Files used:  train_processed.csv, oil_processed.csv

Output: dict[family_name -> pd.DataFrame]
        Each DataFrame has columns:
            date, daily_sales, day_of_week, month, week_of_year,
            days_since_start, rolling_mean_7d, promotion_ratio, oil_price
        Sorted chronologically. No future data leakage.
"""
import os
import logging
import pandas as pd
import numpy as np

from pathlib import Path

logger = logging.getLogger("warehouse.ml.demand")

# Absolute path relative to project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_PROC_DIR = os.path.join(str(_PROJECT_ROOT), "data", "processed", "store_sales_forecasting")
_TRAIN_FILE = os.path.join(_PROC_DIR, "train_processed.csv")
_OIL_FILE = os.path.join(_PROC_DIR, "oil_processed.csv")


def _load_oil_series() -> pd.Series:
    """Loads oil price series, forward-fills NaN. Returns pd.Series indexed by date string."""
    if not os.path.isfile(_OIL_FILE):
        try:
            from data_pipeline.provisioner import ensure_store_sales_dataset
            ensure_store_sales_dataset()
        except Exception:
            pass
    if not os.path.isfile(_OIL_FILE):
        logger.warning("oil_processed.csv not found — oil feature will be omitted.")
        return pd.Series(dtype=float)
    try:
        oil = pd.read_csv(_OIL_FILE, parse_dates=["date"])
        oil = oil.sort_values("date").drop_duplicates(subset=["date"])
        oil["dcoilwtico"] = oil["dcoilwtico"].ffill()
        oil.index = oil["date"].dt.strftime("%Y-%m-%d")
        return oil["dcoilwtico"]
    except Exception as e:
        logger.warning(f"Failed to load oil series: {e}")
        return pd.Series(dtype=float)


def build_family_series(
    train_path: str = _TRAIN_FILE,
    chunksize: int = 100_000,
) -> dict:
    """
    Reads train_processed.csv in chunks and aggregates to family × date level.

    Returns:
        dict[str -> pd.DataFrame]  — keyed by family name
        Each DataFrame columns: date(datetime), daily_sales, day_of_week, month,
            week_of_year, days_since_start, rolling_mean_7d, promotion_ratio, oil_price
    Raises:
        FileNotFoundError if train_processed.csv is missing.
    """
    if not os.path.isfile(train_path):
        try:
            from data_pipeline.provisioner import ensure_store_sales_dataset
            ensure_store_sales_dataset()
        except Exception:
            pass

    if not os.path.isfile(train_path):
        raise FileNotFoundError(f"train_processed.csv not found at {train_path}")

    logger.info(f"Building family demand series from {train_path} ...")

    # Chunked aggregation accumulators
    # We need: per (date, family) sum of sales and onpromotion counts + store counts
    agg_frames = []

    for chunk in pd.read_csv(train_path, chunksize=chunksize):
        # Normalise columns
        if "date" not in chunk.columns or "family" not in chunk.columns or "sales" not in chunk.columns:
            raise ValueError(f"Unexpected columns in train_processed.csv: {list(chunk.columns)}")

        chunk["date"] = pd.to_datetime(chunk["date"])
        chunk["sales"] = pd.to_numeric(chunk["sales"], errors="coerce").fillna(0.0)
        if "onpromotion" in chunk.columns:
            chunk["onpromotion"] = pd.to_numeric(chunk["onpromotion"], errors="coerce").fillna(0)
        else:
            chunk["onpromotion"] = 0

        grp = chunk.groupby(["date", "family"]).agg(
            daily_sales=("sales", "sum"),
            promo_stores=("onpromotion", "sum"),
            total_stores=("sales", "count"),
        ).reset_index()
        agg_frames.append(grp)

    if not agg_frames:
        raise ValueError("No data found in train_processed.csv")

    logger.info("Concatenating chunked aggregations ...")
    combined = pd.concat(agg_frames, ignore_index=True)

    # Second-level aggregation across chunks (handles date×family appearing in multiple chunks)
    combined = combined.groupby(["date", "family"]).agg(
        daily_sales=("daily_sales", "sum"),
        promo_stores=("promo_stores", "sum"),
        total_stores=("total_stores", "sum"),
    ).reset_index()

    combined["promotion_ratio"] = combined["promo_stores"] / combined["total_stores"].clip(lower=1)
    combined = combined.sort_values(["family", "date"]).reset_index(drop=True)

    # Load oil price (optional)
    oil_series = _load_oil_series()

    families = combined["family"].unique()
    logger.info(f"Found {len(families)} product families.")

    family_dfs: dict = {}
    global_start = combined["date"].min()

    for family in families:
        fdf = combined[combined["family"] == family].copy().sort_values("date").reset_index(drop=True)

        # Temporal features — derived from date only, no future leakage
        fdf["day_of_week"] = fdf["date"].dt.weekday          # 0=Mon
        fdf["month"] = fdf["date"].dt.month
        fdf["week_of_year"] = fdf["date"].dt.isocalendar().week.astype(int)
        fdf["days_since_start"] = (fdf["date"] - global_start).dt.days

        # Rolling mean (7-day, min_periods=1) — computed on chronological order
        fdf["rolling_mean_7d"] = fdf["daily_sales"].rolling(7, min_periods=1).mean()

        # Merge oil price by date string
        if not oil_series.empty:
            date_strs = fdf["date"].dt.strftime("%Y-%m-%d")
            fdf["oil_price"] = date_strs.map(oil_series).ffill().bfill()
        else:
            fdf["oil_price"] = np.nan

        fdf = fdf.rename(columns={"date": "date"})[
            ["date", "daily_sales", "day_of_week", "month", "week_of_year",
             "days_since_start", "rolling_mean_7d", "promotion_ratio", "oil_price"]
        ]
        family_dfs[family] = fdf

    logger.info(f"Feature engineering complete. Families: {list(family_dfs.keys())[:5]} ...")
    return family_dfs
