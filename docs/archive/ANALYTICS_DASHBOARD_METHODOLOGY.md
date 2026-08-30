# Analytics Dashboard Methodology

## Overview

This document defines the exact formula, data source, and limitations for every KPI shown in the Executive Analytics Dashboard (`GET /analytics/dashboard`).

**Endpoint**: `GET /analytics/dashboard?warehouse_id={optional}`  
**Authentication**: JWT Bearer token required  
**Data Mode**: `DATABASE_SYNCHRONIZED` — not real-time; refreshed on each page load

---

## KPI Definitions

### 1. Total Inventory Value

**Formula**:
```
inventory_value = SUM(closing_stock × unit_cost)
                  WHERE unit_cost IS NOT NULL AND unit_cost > 0
```

**Source**: MySQL `stock_movements` JOIN `items`  
**Coverage**: Only items where `unit_cost` is configured in the `items` table  
**Note**: Items without a configured unit cost are **excluded** from the total and counted separately in `inventory_value_note`  
**Limitation**: Does not account for shrinkage, write-offs, or in-transit inventory

---

### 2. Warehouse Utilization

**Formula**:
```
warehouse_utilization_pct = total_occupied_units / total_capacity_units × 100

Where:
  total_occupied_units = SUM(closing_stock) across all items in scope
  total_capacity_units = count(warehouses) × 500 units (configurable capacity constant)
```

**Source**: MySQL `stock_movements` (latest closing stock per item per warehouse)  
**Note**: Capacity constant of 500 units per warehouse is a system-level default. If actual racking capacity is measured physically, this should be updated in the Warehouse table.  
**Limitation**: Physical racking structure not modeled; this is a units-based approximation

---

### 3. Stockout Risk Items

**Formula**:
```
stockout_risk_items = count(items where needs_reorder = True)
```

**Source**: `ml/forecast.py` — 14-day Holt-Winters holdout-backtested forecast  
**Detail**:
- `needs_reorder = True` when `current_stock < reorder_point`
- `reorder_point = safety_stock + lead_time_demand`
- Risk levels: `CRITICAL` if `current_stock < safety_stock`, else `HIGH`

**Limitation**: Forecast accuracy depends on historical data availability. Items with fewer than 10 data points use simplified rolling average.

---

### 4. Shrinkage Exposure

**Formula**:
```
shrinkage_exposure = SUM(discrepancy × unit_cost)
                     FOR each active anomaly where unit_cost > 0
```

**Source**: `ml/shrinkage_detector.py` — IsolationForest anomaly detection  
**Labeling**: Described as "Potential Shrinkage Anomaly" — **NOT confirmed loss**  
**Limitation**: IsolationForest flags statistical outliers only. Exposure is estimated, not verified against physical counts.

---

### 5. Forecast Error (WAPE)

**Formula**:
```
forecast_error_wape = MEDIAN(WAPE_per_item)

Where:
  WAPE = 100 × SUM(|actual - forecast|) / SUM(actual)
  Computed on 25% chronological holdout (last quarter of data per item)
```

**Source**: Out-of-sample holdout backtest in `ml/forecast.py`  
**Interpretation**: Lower is better. < 20% = good, 20-30% = acceptable, > 30% = poor  
**Note**: This is the **median across all items** with sufficient historical data. Items without holdout data are excluded.  
**Limitation**: WAPE can be high for items with very low actual demand (denominator effect)

---

### 6. Open AI Decisions

**Formula**:
```
open_ai_decisions = count(AIRecommendation WHERE status = 'PENDING')
```

**Source**: MySQL `ai_recommendations` table  
**Note**: Counts all PENDING recommendations regardless of warehouse filter (global manager queue)

---

### 7. Inventory Accuracy

**Status**: **N/A — not calculated**

**Why**:
```
inventory_accuracy = 1 - |system_quantity - verified_quantity| / verified_quantity
```
This requires a **verified physical count** in the database. No such data currently exists.

Displaying a fabricated inventory accuracy percentage would be academically dishonest and operationally misleading. The dashboard explicitly shows `N/A` with an explanation note.

---

### 8. Active Anomalies

**Formula**:
```
active_anomalies = count(anomalies) from detect_shrinkage()
```

**Source**: `ml/shrinkage_detector.py` IsolationForest model  
**Note**: All anomalies are labeled "Potential" — not confirmed shrinkage

---

## Operational Health Score

**Not implemented**. An overall Operational Health Score was considered but not implemented because:
- Combining heterogeneous KPIs (WAPE, utilization, anomaly count, AI decisions) into a single score requires weights that are inherently arbitrary
- Such a score could create a false sense of security if individual critical alerts are masked by high scores elsewhere
- The Priority Alerts section provides a more honest, actionable alternative

---

## Alerts

Alerts are generated from KPI thresholds:

| Condition | Level | Action |
|---|---|---|
| `current_stock < safety_stock` for any item | CRITICAL | AI Decision Center |
| `needs_reorder = True` for any item | HIGH | AI Decision Center |
| Active shrinkage anomalies exist | HIGH or CRITICAL | AI Decision Center |
| Any warehouse utilization > 85% | MEDIUM | Digital Twin |
| Any PENDING AI decisions exist | MEDIUM | AI Decision Center |
| Trust Ledger chain broken | CRITICAL | Audit Log |

---

## Data Freshness

- The dashboard is refreshed on **each page load** (manual synchronization)
- Data is **not real-time streaming** — it reflects the state of the MySQL database at the time of the API call
- All KPIs are labeled with a `generated_at` timestamp (UTC ISO 8601)
- The dashboard header shows: `🗄️ DATABASE-SYNCHRONIZED · Last generated: {timestamp}`

---

## Filters

### Warehouse Filter
- `GET /analytics/dashboard?warehouse_id=WH-BLR-01`
- Filters inventory, utilization, stockout risks, shrinkage anomalies, and trend to the specified warehouse
- AI Decision counts are global (not filtered by warehouse in PENDING query)

### Item Filter
- Not implemented at dashboard level — per-item analysis is available via the AI Decision Center and Forecast views

### Date Filter
- The inventory trend shows the last 30 days of stock movements
- KPIs reflect current state (no time filter applicable to `current_stock`, `active_anomalies`, etc.)

---

## Data Limitations

| Limitation | Impact |
|---|---|
| No physical verification data | Inventory Accuracy cannot be computed |
| Unit cost not set on some items | Inventory Value and Shrinkage Exposure are partial |
| Forecast requires ≥ 8 data points | Items with less history use simplified model |
| IsolationForest anomaly detection | Statistical only — not confirmed loss |
| Warehouse capacity is a fixed constant | Utilization is approximate |
| No real-time data streaming | Dashboard reflects DB state at load time |

---

## Terminology

| Term | Meaning |
|---|---|
| ACTUAL | Real MySQL database values |
| ESTIMATED | Computed from model output (e.g., shrinkage exposure) |
| CALCULATED | Derived from a documented formula (e.g., utilization) |
| N/A | Data required for calculation is unavailable |
| SIMULATED | Not from real database (only applies to Digital Twin sensors) |
| Potential Shrinkage Anomaly | IsolationForest flag — not confirmed theft or loss |
