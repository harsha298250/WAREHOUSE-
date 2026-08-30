# Database-Reconciled Digital Twin Architecture

This document defines the architectural specification for the **Cloud-Based Database-Reconciled Digital Twin** in the Smart Warehouse Intelligence Platform.

---

## 🏗️ Data Flow & Provenance Architecture

```text
               MySQL Database
                     │
         ┌───────────┴───────────┐
         │                       │
  stock_movements              items
   (closing_stock)         (safety_stock)
         │                       │
         └───────────┬───────────┘
                     │
                     ▼
       Database-Reconciled Digital Twin
                     │
      ┌──────────────┼──────────────┐
      │              │              │
Inventory      Warehouse      Environmental
Reconciliation   Structure      Telemetry
(MYSQL ✓)       (MYSQL ✓)    (SIMULATED ⚠)
```

---

## 🛡️ Key Principles & Policy Compliance

### 1. Zero Fake Inventory Fallbacks
- **Rule**: Stock counts are strictly queried from MySQL `stock_movements.closing_stock`.
- **Database Failure Behavior**: If MySQL fails or has no records, returns `"data_mode": "DATABASE_UNAVAILABLE"`, `"message": "Digital Twin inventory data could not be loaded."`. No hardcoded fallback stock dictionaries allowed.

### 2. Explicit Data Provenance Metadata
Every API response contains:
```json
"data_provenance": {
  "inventory": "REAL_DATABASE (MySQL stock_movements)",
  "warehouse_structure": "REAL_DATABASE (MySQL items & warehouses)",
  "environmental_telemetry": "SIMULATED TELEMETRY (Sensor Array A-4)"
}
```

### 3. Operational Status Thresholds
- `OVER_CAPACITY`: Utilization $\ge 100\%$
- `HIGH_UTILIZATION`: Utilization $\ge 85\%$
- `LOW_STOCK`: Closing stock $\le$ safety stock
- `SHRINKAGE_INVESTIGATION`: Active open shrinkage anomaly flagged by `detect_shrinkage()`
- `NORMAL`: Standard operating parameters.
