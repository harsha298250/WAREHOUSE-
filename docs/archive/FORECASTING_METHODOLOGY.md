# Outbound Demand Forecasting & Walk-Forward Validation Methodology

This document outlines the machine learning methodology, validation frameworks, metrics, and risk integration details for the demand forecasting system.

---

## 1. Forecasting Objective
The objective is to estimate the daily outbound demand volume of individual items across each warehouse. These predictions are used to calculate the lead-time demand, identify potential stockouts, and trigger human-in-the-loop reorder decisions.

## 2. Target Variable
The target variable is **Daily Outbound Demand (`stock_out`)** for a specific `(warehouse_id, item_id)` pair. This is a pure demand metrics prediction (labeled as `DEMAND FORECAST`), not inventory stock level.

## 3. Dataset Structure
Input data consists of daily transactional summaries from the `stock_movements` table. Missing transactions are zero-filled, and data is structured as a continuous chronological timeseries sorted by date.

## 4. Feature Engineering & Leakage Prevention
To prevent data leakage, features are computed using only past information:
* **Trend Regression Variable ($x$)**: Chronological index representing days from start.
* **Weekday Seasonality Index**: Average daily demand on day-of-week relative to overall average. Fits parameters *only* on training subsets.
* **Zero Shuffling**: Shuffling is disabled. Chronological timeseries splits are enforced.
* **No Future Leakage**: Models are fit exclusively on historical folds before scoring validation ranges.

## 5. Chronological Holdout Validation
For historical reporting, the dataset is split chronologically:
* **Training Window**: First 75% of observations.
* **Test Holdout Window**: Last 25% of observations.
Out-of-sample metrics are computed by evaluating predictions on this holdout subset.

## 6. Walk-Forward Backtesting (Rolling-Origin)
To simulate deployment performance, rolling walk-forward validation is executed:
* **Initial Training**: Min 10 observations or 60% of history.
* **Prediction Horizon**: 7 days ahead.
* **Origin Shift (Step)**: 7 days.
* **Iteration**: Move the training window forward by 7 days, fit parameters, predict the next 7 days, and repeat until the dataset is exhausted.
If history is under 17 days, the walk-forward evaluation skips gracefully and flags `INSUFFICIENT_DATA_FOR_WALK_FORWARD`.

## 7. Baseline Models
The model is validated against two baseline frameworks:
1. **Naive Baseline**: Forecast tomorrow equals the last observed actual demand.
2. **Moving Average Baseline**: Forecast equals the 7-day historical rolling average of demand.

## 8. Evaluation Metrics
We compute four quantitative out-of-sample metrics:
* **Mean Absolute Error (MAE)**:
  $$\text{MAE} = \frac{1}{N} \sum |y_i - \hat{y}_i|$$
* **Root Mean Squared Error (RMSE)**:
  $$\text{RMSE} = \sqrt{\frac{1}{N} \sum (y_i - \hat{y}_i)^2}$$
* **Weighted Absolute Percentage Error (WAPE)**:
  $$\text{WAPE} = \frac{\sum |y_i - \hat{y}_i|}{\sum |y_i|}$$
* **Symmetric Mean Absolute Percentage Error (sMAPE)**:
  $$\text{sMAPE} = \frac{100\%}{N} \sum \frac{|y_i - \hat{y}_i|}{(|y_i| + |\hat{y}_i|)/2}$$

## 9. Model vs. Baseline Comparison
We compare the Model WAPE and Baseline WAPE, calculating the **Relative WAPE Improvement**:
$$\text{Relative Improvement} = \frac{\text{WAPE}_{\text{baseline}} - \text{WAPE}_{\text{model}}}{\text{WAPE}_{\text{baseline}}} \times 100\%$$
If the model performs worse than the baseline, the relative improvement resolves to `0.0`, and the system notes that the model underperformed the baseline.

## 10. Forecast Uncertainty Range
Rather than a "95% Confidence Interval," the upper and lower forecast bands are labeled as the **Forecast Uncertainty Range** or **Estimated Forecast Range**. It is calculated from training residual standard deviation ($\sigma_{\text{resid}}$):
$$\text{Forecast Range}_h = \text{Forecast}_h \pm 1.28 \times \sigma_{\text{resid}} \times \sqrt{h}$$
This reflects error propagation over the forecast horizon $h$.

## 11. Forecast Reliability Score
The **Forecast Reliability Score (0–100 scale)** is a model-quality indicator:
* **Baseline Score**: Starts at $100 - \text{WAPE}$.
* **Deductions**:
  * $-20$ points for datasets under 15 days.
  * $-10$ points for datasets under 30 days.
  * $-15$ points if the Model WAPE exceeds the Moving Average Baseline WAPE.
  * $-10$ points if the demand coefficient of variation (std/mean) $> 1.5$.
The score is clamped between 10 and 99.

## 12. AI Decision Center Integration
The forecast feeds into the inventory reorder logic:
1. Current Inventory ($I_c$) is queried from MySQL.
2. Lead Time ($L$) is fetched from items registry.
3. Lead Time Demand ($D_L$) is calculated as the sum of forecasts over the next $L$ days.
4. Reorder Point ($RP$) is calculated as:
   $$RP = D_L + \text{Safety Stock}$$
5. If $I_c \le RP$, the AI Decision Center creates a `REORDER` recommendation with complete explanation details.

---

## 13. Limitations
* **Stationary Assumptive Bias**: Assumes historical trend and seasonality coefficients remain stable over the forecast horizon.
* **Exogenous Factors**: The model does not capture external promotional events, weather disruptions, or economic shifts.
* **Cold Starts**: Accuracy is degraded when SKUs have low historical transaction counts.
