# Smart Warehouse Platform — Final Feature Matrix

This matrix maps every major application feature, its categorization, data types, business values, and verification status.

| Feature Name | Category | UI Status | Data Type / Provenance | User Value | Reason | Test Status |
|---|---|---|---|---|---|---|
| **Dashboard** | Tier 1 (Core) | `KEEP` | `REAL DATABASE` / `CALCULATED` | High | High-level overview of current inventory, alerts, and performance metrics | `PASS` |
| **Warehouses** | Tier 1 (Core) | `KEEP` | `REAL DATABASE` | High | Location and coordinate registry configuration | `PASS` |
| **Inventory** | Tier 1 (Core) | `KEEP` | `REAL DATABASE` | High | Central catalog of items, categories, cost variables, and safety stock points | `PASS` |
| **Stock Movements** | Tier 1 (Core) | `KEEP` | `REAL DATABASE` | High | Log of daily inputs and outputs with automatic closing stock tracking | `PASS` |
| **AI Decision Center** | Tier 1 (Core) | `KEEP` | `CALCULATED` / `PREDICTED` | High | Manager Human-in-the-Loop reorder approvals and explanation logs | `PASS` |
| **Demand Forecasting** | Tier 1 (Core) | `KEEP` | `PREDICTED` | High | Out-of-sample demand forecasts with backtesting validations | `PASS` |
| **Shrinkage & Loss** | Tier 1 (Core) | `KEEP` | `CALCULATED` / `ESTIMATED` | High | Unsupervised anomaly isolation scanning and root-cause cluster patterns | `PASS` |
| **Transfer Advisor** | Tier 1 (Core) | `KEEP` | `ESTIMATED` / `CALCULATED` | High | Stock balancing optimization recommendations based on depot surpluses | `PASS` |
| **Reports** | Tier 1 (Core) | `KEEP` | `REAL DATABASE` | High | Export options for PDF, XLSX, and CSV stock sheets | `PASS` |
| **Authentication & RBAC**| Tier 1 (Core) | `KEEP` | `REAL DATABASE` | High | Secure login authorization and view boundaries based on server permissions | `PASS` |
| **PostgreSQL** | Tier 1 (Core) | `KEEP` | `REAL DATABASE` | High | Production database engine for storing application data | `PASS` |
| **Digital Twin** | Tier 2 (Differentiator) | `KEEP` | `REAL DATABASE` / `SIMULATED` | High | Visual 2D rack layout maps, utilizing simulated environmental telemetry | `PASS` |
| **What-If Simulator** | Tier 2 (Differentiator) | `KEEP` | `SIMULATED` | High | Crisis scenario models to evaluate inventory levels and stockout risks | `PASS` |
| **Query Assistant** | Tier 2 (Differentiator) | `KEEP` | `CALCULATED` | High | Natural language query assistant for catalog and stock operations | `PASS` |
| **Security Monitor** | Tier 2 (Differentiator) | `KEEP` | `CALCULATED` | Medium | Anomaly outlier scans on user access and login logs | `PASS` |
| **Alerts & Notifications**| Tier 2 (Differentiator) | `KEEP` | `REAL DATABASE` | Medium | Diagnostic statuses and system event email dispatch registers | `PASS` |
| **Cloud Backup** | Tier 3 (Supporting) | `KEEP` | `REAL DATABASE` / `SIMULATED` | Medium | Disaster-recovery db dumping, utilizing B2 local fallback storage | `PASS` |
| **System Health** | Tier 3 (Supporting) | `KEEP` | `REAL DATABASE` | Medium | Backend, Database, and SQS connectivity indicators | `PASS` |
| **Storage Cost Simulator**| Tier 4 (Optional) | `HIDE` | `SIMULATED` | Low | Cloud cost savings analysis based on storage tiering profiles | `PASS` |
| **Auto-scaling Simulator**| Tier 4 (Optional) | `HIDE` | `SIMULATED` | Low | Simulated capacity optimization charts based on API request loads | `PASS` |
| **Event Demand Calendar** | Tier 4 (Optional) | `HIDE` | `SYNTHETIC / DEMO` | Low | Demand calendars with simulated external event records | `PASS` |

---

## Terminology Reference Table
To align with strict academic honesty rules, the following terms are applied:
* `REAL DATABASE`: Sourced dynamically from PostgreSQL table records.
* `CALCULATED`: Sourced from algorithms running on dynamic database records.
* `PREDICTED`: Sourced from machine learning inference engines.
* `ESTIMATED`: Calculated using business model assumptions (e.g. costs/savings).
* `SIMULATED`: Generated via simulation models rather than hardware sensors or live integrations.
* `SYNTHETIC / DEMO`: Synthetic datasets used only for mock demonstration.
