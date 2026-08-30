# Potential Shrinkage Anomaly Detection Methodology

This document outlines the machine learning methodology, mathematical models, and operational constraints for the IsolationForest-based potential shrinkage anomaly detection engine.

---

## 1. Problem Definition
The system identifies statistically unusual inventory movement patterns or recorded discrepancy events. These events are highlighted as "Potential Shrinkage Anomalies" for review, rather than confirmed theft or loss.

## 2. Data Source
The input consists of daily stock records from the `stock_movements` operational database table:
* `stock_in` (outbound receipt)
* `stock_out` (demand velocity)
* `closing_stock` (recorded end-of-day stock level)

## 3. Inventory Reconciliation Model
Expected Closing Stock ($T$) is calculated using the standard inventory identity:
$$\text{Expected Closing Stock}_T = \text{Closing Stock}_{T-1} + \text{Stock In}_T - \text{Stock Out}_T$$

The discrepancy quantity is then derived:
$$\text{Discrepancy Quantity}_T = \text{Recorded Closing Stock}_T - \text{Expected Closing Stock}_T$$

## 4. Feature Engineering
We extract 9 distinct operational features for every group:
1. `stock_in`: Inbound quantity.
2. `stock_out`: Outbound quantity.
3. `closing_stock`: End-of-day level.
4. `discrepancy`: Mathematical inventory mismatch.
5. `deviation`: Outbound velocity minus the 7-day rolling average.
6. `rolling_mean`: 7-day rolling average stock velocity.
7. `rolling_std`: 7-day rolling standard deviation of demand.
8. `movement_frequency`: Historical frequency of non-zero outbound days.
9. `inventory_turnover`: Stock velocity relative to closing stock level.

## 5. Model Configuration
* **Algorithm**: `sklearn.ensemble.IsolationForest`
* **Contamination**: `0.05` (assumed 5% nominal anomaly rate, customizable)
* **Random Seed**: `random_state=42` (ensures identical splits and predictions across runs)

## 6. Score Normalization
The IsolationForest decision function scores (ranging between -0.5 and +0.5) are normalized to a **0–100 Investigation Priority Score**:
$$\text{Priority Score} = \min\left(99, \max\left(10, \text{round}\left((0.25 - \text{decision\_score}) \times 140\right)\right)\right)$$
Higher scores represent greater statistical distance from normal operational profiles.

## 7. Severity Thresholds
Anomalies are categorized by model-based priority thresholds:
* **CRITICAL**: Priority Score $\ge 85$ and absolute discrepancy $\ge 15$ units.
* **HIGH**: Priority Score $\ge 70$ or absolute discrepancy $\ge 10$ units.
* **MEDIUM**: Priority Score $\ge 50$.
* **LOW**: Priority Score $< 50$.

## 8. Exposure Calculation
Monetary exposure represents the maximum asset value at risk:
$$\text{Estimated Exposure} = |\text{Discrepancy Quantity}| \times \text{Unit Cost}$$
If unit cost is missing or undefined, exposure resolves to `null`. No arbitrary scalar multiplier is applied.

## 9. Likely Cause Categories
* `UNUSUAL_OUTBOUND_ACTIVITY`: Discrepancy is negative with elevated outbound demand.
* `POSSIBLE_DAMAGE_OR_WASTAGE`: Discrepancy is negative with normal demand.
* `DATA_ENTRY_ERROR`: Negative closing stock or large positive discrepancy.
* `STOCK_RECONCILIATION_MISMATCH`: Mathematical mismatch between actual and expected logs.
* `UNKNOWN`: Default fallback.

## 10. Human-in-the-Loop & Trust Ledger
The model highlights candidates but never updates inventory balances or confirms theft automatically. The review workflow follows a mandatory human validation loop:
`OPEN` -> `UNDER_REVIEW` -> `APPROVED / REJECTED` -> `RESOLVED`.
Every state transition is signed cryptographically and written as an entry inside the tamper-evident hash-chained Audit Ledger.

---

## 11. Model Limitations
> [!IMPORTANT]
> **IsolationForest identifies statistically unusual inventory movement patterns. It does not establish theft or intentional loss.** 
> Mismatches may arise from scanner latency, unrecorded scraps, delayed check-ins, or transport delays. The model provides priority scoring for investigation teams, not legal proof.
