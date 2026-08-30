# Academic Viva Defense Preparation (Step 5)

This document provides clear, technically precise, and code-aligned answers to 22 critical defense questions to prepare for the academic presentation and viva examination.

---

### Q1: Why FastAPI?
* **Answer**: FastAPI offers native support for asynchronous handlers (`async/await`), automatic OpenAPI documentation generation, and robust request validation using Pydantic. It provides high execution performance, type safety, and clean separation of dependency injection compared to heavier frameworks like Django.

### Q2: Why MySQL?
* **Answer**: MySQL is a production-grade relational database engine that enforces strict schema structures, transaction boundaries (ACID compliant), foreign keys, and indexes. It is highly suitable for tracking inventory ledger balances where consistency and relational integrity are paramount.

### Q3: Why IsolationForest?
* **Answer**: Isolation Forest is an unsupervised tree-based algorithm that isolates anomalies rather than profiling normal data points. By partitioning features recursively, anomalies (which have shorter path lengths) are isolated near the root, making it highly effective for identifying multi-dimensional inventory deviations without requiring pre-labeled training data.

### Q4: Why forecasting?
* **Answer**: Anticipating future outbound demand is critical to preventing stockouts and overstocking. Evaluating expected lead-time demand enables the system to calculate dynamic reorder thresholds instead of relying on flat static baselines.

### Q5: Why chronological validation?
* **Answer**: Time-series data is chronologically dependent. Standard random train/test splits shuffle observations, causing future leakage (predicting past values using future information). Chronological validation preserves temporal ordering by training only on data prior to the target evaluation windows.

### Q6: Why WAPE?
* **Answer**: Weighted Absolute Percentage Error (WAPE) scales absolute errors relative to the total actual demand volume. Unlike MAPE, WAPE does not suffer from division-by-zero errors when daily actual demand is zero, making it highly reliable for sparse, low-volume inventory datasets.

### Q7: What is inventory shrinkage?
* **Answer**: Inventory shrinkage is the loss of physical stock between recorded entries and actual physical inventory counts. Mismatches may arise from damaged items, administrative data entry errors, log latency, or undocumented wastage.

### Q8: How is discrepancy calculated?
* **Answer**: Expected Closing Stock is derived from the previous day's closing balance plus stock-in minus stock-out. The discrepancy is then calculated as the recorded closing stock minus the expected closing stock.

### Q9: Why is the anomaly score not a probability?
* **Answer**: IsolationForest is an unsupervised model that measures statistical distance and path length outlier ranks. It is not a calibrated binary classifier and cannot represent the "probability of theft" or intent without a labeled target set.

### Q10: What is explainability?
* **Answer**: It is the method of exposing features, rolling baselines, absolute discrepancies, priority scores, and unit costs behind model decisions to human managers, allowing them to verify why a specific anomaly was flagged.

### Q11: What is the Digital Twin?
* **Answer**: The Digital Twin is a software representation of the physical warehouse state, mapping operational item inventories to spatial racks, calculating zone storage capacity limits, and highlighting active anomalies.

### Q12: What-If simulation?
* **Answer**: It is an isolated simulation sandbox that tests the impact of demand surges, supplier delays, and transport disruptions on reorder requirements without modifying the live database state.

### Q13: What is the AI Decision Center?
* **Answer**: It is the central decision-support module that synthesizes forecasting, discrepancy anomalies, and warehouse rules into advisory purchase recommendations.

### Q14: Why human-in-the-loop?
* **Answer**: The AI model flags candidates, but final approval and action authorization are restricted to authorized human managers, preventing automated errors from triggering incorrect orders.

### Q15: What is the Trust Ledger?
* **Answer**: It is a tamper-evident audit logging sequence that hashes and chains entries chronologically, allowing administrators to verify if any historical record has been altered.

### Q16: Why is it not blockchain?
* **Answer**: It is a centralized, single-node hash-chained ledger. It lacks decentralization, multi-node consensus algorithms, and distributed mining, which are key properties of blockchain.

### Q17: How is JWT secured?
* **Answer**: Tokens are signed using HMAC-SHA256 with a secret key loaded from the environment. They carry a 60-minute expiration limit, are passed in Authorization headers, and query parameter tokens are explicitly rejected.

### Q18: How does RBAC work?
* **Answer**: Server-side endpoints enforce role validation using FastAPI dependency injection (`require_admin`, `require_role`), matching claims against database-hashed user profiles.

### Q19: How are secrets protected?
* **Answer**: Secrets are stored in `.env` (ignored by git) and loaded as system environment variables in production. Hardcoded values have been fully cleaned from scripts and documents.

### Q20: How is the system deployed?
* **Answer**: The system is packaged into a hardened Docker container running as a non-root user (`appuser` UID 1001), executing Alembic migrations on startup, and ready for deployment on cloud hosts like Render.

### Q21: What are current limitations?
* **Answer**: Brute-force rate limiting and OTP registers operate process-local in-memory, requiring Redis for multi-instance deployments.
* **Forecast bias**: Relies on stationary demand trend assumptions.

### Q22: How would the system scale?
* **Answer**:
  1. Migrate in-memory session blocks to a shared Redis cache.
  2. Implement database read replicas.
  3. Deploy multi-container application groups behind a load balancer.
