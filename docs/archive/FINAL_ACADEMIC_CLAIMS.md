# FINAL_ACADEMIC_CLAIMS.md — Smart Warehouse Intelligence Platform

This document outlines the strict academic terminology and boundary definitions adopted to maintain technical honesty and academic credibility during reviews, submissions, and demonstrations.

---

## 1. Terminology Cross-Reference

| Topic | Draft / Colloquial Term | Academic / Honest Term | Rationale / Evidence |
|---|---|---|---|
| **Dataset** | "Real-world Kaggle database" / "Live warehouse log" | **Synthetic Demonstration Dataset** | The dataset is programmatically initialized with demo records (`seed_demo_data.py`) and allows manual edits. No actual proprietary warehouse records are used. |
| **Data Processing**| "Big Data / Hadoop architecture" | **Cloud-Based Warehouse Analytics** / **Scalable Warehouse Analytics** | The architecture is standard relational (MySQL + SQLAlchemy) built on lightweight cloud hosting. It does not run distributed MapReduce, Spark, or Hadoop. |
| **Digital Twin** | "Real-time IoT telemetry twin" | **Database-Reconciled Digital Twin** / **Cloud-Based Digital Twin** | Environmental variables (e.g. rack temperature) are marked as **SIMULATED**. The visual warehouse layout is derived directly from the MySQL database tables. |
| **Artificial Intelligence** | "Fully autonomous AI operator" / "Flawless optimization model" | **AI-Assisted Decision Support System** / **Decision Priority Index** | The model recommends actions (reorder, inspect, adjust layout) based on heuristics and ML. All actions require a human manager to approve, modify, or reject. |
| **Shrinkage Anomaly** | "Theft detection ledger" / "Confirmed fraud alerts" | **Potential Shrinkage Anomaly** / **Inventory Discrepancy Requiring Investigation** | The IsolationForest model detects standard numerical deviations in daily movements. It cannot classify legal intent or prove criminal theft. |
| **Audit Ledger** | "Blockchain trust network" | **Tamper-Evident Hash-Chained Audit Ledger** | The ledger chains events linearly via SHA-256 hashes (`AuditLedger` table), providing tamper detection. It is not a distributed peer-to-peer blockchain. |
| **Warehouse Automation**| "Fully automated robotic terminal" | **Automated Analysis, Alerts, and Workflow Recording** | The platform automates recommendation synthesis, notification dispatches, and ledger logging. No physical robots, PLCs, or conveyors are present. |
| **ML Forecast** | "Statistical probability of stockout" | **Forecast Reliability Score** / **Estimated Forecast Range** / **Decision Priority Score** | Demand forecasting uses WAPE and regression metrics. Stockout risks are prioritizing indexes, not strict mathematical probabilities. |
| **Financial Impact** | "Real-world cash savings" | **Estimated Impact** | All savings or efficiency figures are projections computed from user-defined unit costs and estimated holding fees. |

---

## 2. Correct Formulation Examples (To Use During Viva)

### Example 1: The Digital Twin
* **Do NOT say**: "The Digital Twin monitors the temperature of the physical racks in real time."
* **DO say**: "The twin displays a database-reconciled map of stock levels, while environmental parameters are labeled as **SIMULATED** to demonstrate how real IoT sensor feeds would integrate."

### Example 2: The Audit Ledger
* **Do NOT say**: "We deployed a blockchain node to make the data impossible to hack."
* **DO say**: "We implemented a tamper-evident hash-chained audit ledger. Each log entry stores the SHA-256 hash of the previous record, allowing standard verification algorithms to immediately detect any offline SQL modifications."

### Example 3: The Demand Forecast
* **Do NOT say**: "Our AI predicts future stock levels with 100% accuracy."
* **DO say**: "Our forecasting engine generates a 14-day estimated demand range. The reliability of this forecast is audited using out-of-sample holdout backtesting, yielding an honest, computed median WAPE."
