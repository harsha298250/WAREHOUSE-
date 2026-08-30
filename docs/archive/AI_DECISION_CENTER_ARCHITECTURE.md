# Production-Quality AI Decision Center Architecture

This document defines the architectural specification for the **Explainable AI Decision Center** in the Smart Warehouse Intelligence Platform.

---

## 🏗️ End-to-End Decision Architecture

```text
               MySQL Database
                     │
        ┌────────────┼────────────┐
        ↓            ↓            ↓
   Inventory     Movements    Warehouse
        │            │            │
        └─────┬──────┴─────┬──────┘
              ↓            ↓
          FORECAST      SHRINKAGE
          (ml/forecast) (ml/shrinkage)
              │            │
              └─────┬──────┘
                    ↓
              RISK ENGINE
                    ↓
           AI DECISION CENTER
                    │
        ┌───────────┼───────────┐
        ↓           ↓           ↓
     REORDER    INVESTIGATE  NO_ACTION
        │           │           │
        └───────────┼───────────┘
                    ↓
         CANONICAL EXPLAINABLE
            RECOMMENDATION
                    ↓
           HUMAN MANAGER REVIEW
            /       |       \
       APPROVE    MODIFY   REJECT
            \       |       /
             ▼      ▼      ▼
          SHA-256 TRUST LEDGER
```

---

## 🛡️ Key Principles & Policy Compliance

### 1. Canonical Recommendation Schema
Every recommendation follows a unified dictionary schema:
- `recommendation_id`, `item_id`, `item_name`, `warehouse_id`
- `recommendation_type`: `REORDER` | `STOCK_INVESTIGATION` | `STOCK_TRANSFER` | `STORAGE_OPTIMIZATION` | `NO_ACTION`
- `priority`: `CRITICAL` | `HIGH` | `MEDIUM` | `LOW`
- `priority_score`: 0–100 Recommendation Priority Score
- `forecast_reliability_score`: 0–100 backtested reliability score from Step 2 holdout WAPE
- `estimated_exposure`: Calculated as $\text{shortage\_qty} \times \text{unit\_cost}$ or $\text{discrepancy\_qty} \times \text{unit\_cost}$
- `evidence`, `reasoning`, `assumptions`, `data_sources`

### 2. Zero Arbitrary Formulas & Honest Scoring
- **No Arbitrary Formulas**: Removed ad-hoc math (e.g. `85 + x`).
- **Priority Score**: Operational score calculated from normalized operational signals (shortage ratio, lead-time pressure, anomaly severity).
- **Separation of Concepts**: `priority_score` (operational urgency) is strictly separated from `forecast_reliability_score` (backtest accuracy).

### 3. Human-in-the-Loop & Trust Ledger
- Admin/Manager decision actions (`APPROVE`, `MODIFY`, `REJECT`) preserve the original AI recommendation while recording manager intent and writing a SHA-256 hash-chained log entry to `AuditLedger`.
- `GET /ai/decision-history` provides complete audit trail verification.
