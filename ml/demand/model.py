"""
ml/demand/model.py

TrendSeasonalityModel — family-level demand forecasting model.

Architecture:
    1. Linear trend (numpy polyfit on training window)
    2. Weekday seasonality index (multiplicative, per day-of-week)
    3. Month seasonality index (multiplicative, per month)
    4. Promotion adjustment factor (additive, optional)

This is the same architecture as the existing ml/forecast.py `forecast_item()`
extended to work on external dataset family series rather than WMS stock_out data.

Model parameters are fully serializable to JSON — enabling reproducibility
without re-reading any CSV files.

Model selection rationale:
    - Matches existing project approach (consistency)
    - Fully explainable and auditable
    - No new dependencies beyond numpy/pandas (already in requirements.txt)
    - Practical: fits 33 families in < 5 minutes on dev hardware
    - No LSTM, Transformer, or external ML platform (per Phase 9 requirements)
"""
import json
import os
import logging
import numpy as np
import pandas as pd

logger = logging.getLogger("warehouse.ml.demand")

_MODELS_DIR = os.path.join("data", "models")


class TrendSeasonalityModel:
    """
    Trend + Weekday + Month Seasonality multiplicative model.

    Parameters saved to data/models/{family}.json for reproducibility.
    """

    def __init__(self, family: str):
        self.family = family
        self.slope: float = 0.0
        self.intercept: float = 0.0
        self.weekday_index: dict = {}     # {0..6 -> float}
        self.month_index: dict = {}       # {1..12 -> float}
        self.promotion_factor: float = 0.0
        self.train_mean: float = 0.0
        self.resid_std: float = 1.0
        self.train_length: int = 0
        self._fitted: bool = False

    def fit(self, train_df: pd.DataFrame, target_col: str = "daily_sales") -> "TrendSeasonalityModel":
        """
        Fits model parameters on training data.
        train_df must be sorted chronologically and must NOT include any validation data.
        """
        if len(train_df) < 5:
            raise ValueError(f"Insufficient training data for family '{self.family}' (need >= 5 rows).")

        y = train_df[target_col].values.astype(float)
        self.train_mean = float(np.mean(y)) if np.mean(y) > 0 else 1e-6
        self.train_length = len(train_df)

        # 1. Linear trend
        x = np.arange(len(train_df))
        self.slope, self.intercept = np.polyfit(x, y, 1)

        # 2. Weekday seasonality index
        train_df = train_df.copy()
        train_df["weekday"] = pd.to_datetime(train_df["date"]).dt.weekday
        wd_mean = train_df.groupby("weekday")[target_col].mean()
        self.weekday_index = {
            int(wd): float(v / max(self.train_mean, 1e-6))
            for wd, v in wd_mean.items()
        }

        # 3. Month seasonality index
        train_df["month"] = pd.to_datetime(train_df["date"]).dt.month
        mo_mean = train_df.groupby("month")[target_col].mean()
        self.month_index = {
            int(mo): float(v / max(self.train_mean, 1e-6))
            for mo, v in mo_mean.items()
        }

        # 4. Promotion factor: mean uplift when promotion_ratio > 0
        if "promotion_ratio" in train_df.columns:
            promo = train_df[train_df["promotion_ratio"] > 0]
            no_promo = train_df[train_df["promotion_ratio"] == 0]
            promo_mean = float(promo[target_col].mean()) if len(promo) > 0 else self.train_mean
            no_promo_mean = float(no_promo[target_col].mean()) if len(no_promo) > 0 else self.train_mean
            self.promotion_factor = max(0.0, promo_mean - no_promo_mean)

        # Residual standard deviation (for uncertainty bounds)
        fitted = self.intercept + self.slope * x
        self.resid_std = float(np.std(y - fitted)) if len(train_df) > 1 else 1.0

        self._fitted = True
        self._save_params()
        return self

    def predict(self, start_idx: int, dates: pd.DatetimeIndex,
                promotion_ratios: pd.Series = None) -> tuple:
        """
        Generates predictions for the given dates.

        Args:
            start_idx: index offset from training start (= len(train_df))
            dates: DatetimeIndex of dates to predict for
            promotion_ratios: optional Series of promotion_ratio values for those dates

        Returns:
            (point_forecasts, lower_bounds, upper_bounds) — all np.ndarray
        """
        if not self._fitted:
            raise RuntimeError("Model must be fitted before predicting.")

        points, lowers, uppers = [], [], []

        for h, dt in enumerate(dates):
            idx = start_idx + h
            wd = dt.weekday()
            mo = dt.month

            base = self.intercept + self.slope * idx
            wd_factor = self.weekday_index.get(wd, 1.0)
            mo_factor = self.month_index.get(mo, 1.0)

            val = max(0.0, base * wd_factor * mo_factor)

            # Promotion adjustment
            if promotion_ratios is not None and h < len(promotion_ratios):
                promo_r = float(promotion_ratios.iloc[h]) if hasattr(promotion_ratios, "iloc") else float(promotion_ratios[h])
                val += self.promotion_factor * promo_r

            # Uncertainty band: 1.28σ × √h (80% PI, widens with horizon)
            band = round(1.28 * self.resid_std * np.sqrt(h + 1), 2)

            points.append(round(max(0.0, val), 2))
            lowers.append(round(max(0.0, val - band), 2))
            uppers.append(round(val + band, 2))

        return np.array(points), np.array(lowers), np.array(uppers)

    def _save_params(self):
        """Saves model parameters to data/models/{family}.json for reproducibility."""
        os.makedirs(_MODELS_DIR, exist_ok=True)
        params = {
            "family": self.family,
            "slope": self.slope,
            "intercept": self.intercept,
            "weekday_index": self.weekday_index,
            "month_index": self.month_index,
            "promotion_factor": self.promotion_factor,
            "train_mean": self.train_mean,
            "resid_std": self.resid_std,
            "train_length": self.train_length,
        }
        path = os.path.join(_MODELS_DIR, f"{self.family.replace('/', '_')}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(params, f, indent=2)
        logger.debug(f"Saved model params to {path}")

    def get_params(self) -> dict:
        """Returns serializable parameter dictionary."""
        return {
            "slope": round(self.slope, 6),
            "intercept": round(self.intercept, 6),
            "weekday_index": {str(k): round(v, 4) for k, v in self.weekday_index.items()},
            "month_index": {str(k): round(v, 4) for k, v in self.month_index.items()},
            "promotion_factor": round(self.promotion_factor, 4),
            "train_mean": round(self.train_mean, 4),
            "resid_std": round(self.resid_std, 4),
        }
