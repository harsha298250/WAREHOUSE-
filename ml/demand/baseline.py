"""
ml/demand/baseline.py

Naive and Moving Average baseline predictors for chronological time series.
These are used for benchmark comparison against the TrendSeasonalityModel.

IMPORTANT: Both baselines respect the temporal boundary — they never
use any data from the validation/test period during prediction.
"""
import numpy as np
import pandas as pd


class NaiveBaseline:
    """
    Naive baseline: forecast = last observed training value.
    This is the most basic meaningful baseline for demand forecasting.
    """

    def __init__(self):
        self._last_value: float = 0.0
        self._fitted: bool = False

    def fit(self, train_df: pd.DataFrame, target_col: str = "daily_sales") -> "NaiveBaseline":
        """Fits on training data — simply records the last observed value."""
        if len(train_df) == 0:
            raise ValueError("NaiveBaseline.fit() called with empty training DataFrame.")
        self._last_value = float(train_df[target_col].iloc[-1])
        self._fitted = True
        return self

    def predict(self, steps: int) -> np.ndarray:
        """Returns an array of constant predictions = last training value."""
        if not self._fitted:
            raise RuntimeError("NaiveBaseline must be fitted before predicting.")
        return np.full(steps, self._last_value)


class MovingAverageBaseline:
    """
    Moving average baseline: forecast = mean of last `window` training observations.
    """

    def __init__(self, window: int = 7):
        if window < 1:
            raise ValueError("window must be >= 1.")
        self.window = window
        self._ma_value: float = 0.0
        self._fitted: bool = False

    def fit(self, train_df: pd.DataFrame, target_col: str = "daily_sales") -> "MovingAverageBaseline":
        """Computes trailing moving average over the last `window` training observations."""
        if len(train_df) == 0:
            raise ValueError("MovingAverageBaseline.fit() called with empty training DataFrame.")
        tail = train_df[target_col].tail(self.window)
        self._ma_value = float(tail.mean())
        self._fitted = True
        return self

    def predict(self, steps: int) -> np.ndarray:
        """Returns an array of constant predictions = moving average value."""
        if not self._fitted:
            raise RuntimeError("MovingAverageBaseline must be fitted before predicting.")
        return np.full(steps, self._ma_value)
