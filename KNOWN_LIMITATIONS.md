# KNOWN_LIMITATIONS.md — Smart Warehouse Intelligence Platform

The following boundaries describe the scope of the current capstone implementation and explain how each could be scaled in subsequent operational versions.

---

## 1. Data & Sensing Limits

### A. Synthetic Demonstration Dataset
* **Current Boundary**: Initial database records (warehouses, items, daily transactions) are seeded programmatically via `backend/seed_demo_data.py` to allow immediate UI demos.
* **Future Work**: Connect the PostgreSQL layer directly to an enterprise Resource Planning (ERP) database (such as SAP or Oracle) or import active logs from an existing production inventory service.

### B. Simulated Telemetry (Environmental Conditions)
* **Current Boundary**: Digital Twin parameters like warehouse temperature, humidity, and active cooler statuses are marked as **SIMULATED** and rendered via heuristic formulas. No physical environmental hardware is connected.
* **Future Work**: Deploy microcontrollers (such as ESP32 or Raspberry Pi) reading DHT22 or TMP36 temperature sensors, transmitting telemetry payloads over MQTT/AMQP to a cloud broker (such as AWS IoT Core), and writing records to a time-series database (such as InfluxDB).

---

## 2. Analytics & Modeling Boundaries

### C. Forecast Engine Data Requirements
* **Current Boundary**: The ML demand forecasting engine (`ml/forecast.py`) requires a minimum sequence of historic stock movements (at least 7-14 days) to compile predictions. On newly created items with empty logs, it falls back to basic heuristics.
* **Future Work**: Introduce cold-start algorithms (such as category-average regression) or hybrid models incorporating macro market variables (e.g. inflation, seasonal calendar adjustments).

### D. Anomaly Flag Classifications
* **Current Boundary**: The IsolationForest detector in `ml/shrinkage_detector.py` flags numerical outliers. It cannot classify intent or confirm security violations (e.g. theft).
* **Future Work**: Correlate anomaly logs with access control check-ins, security CCTV timestamps, and logistics dispatch sheets to build a true risk-scoring matrix.

---

## 3. Automation & Ledgers

### E. Lack of Physical Warehouse Automation
* **Current Boundary**: System automation refers strictly to automated alert notifications, recommendation synthesis, and transaction recording. No physical conveyors, robotic sorting systems (AGVs), or PLCs are controlled.
* **Future Work**: Integrate standard industrial automation APIs (such as OPC-UA or Modbus TCP) to trigger sorting conveyors or physical door locks upon human ledger approval.

### F. Audit Ledger In-Memory Validation
* **Current Boundary**: The linear SHA-256 hash-chain checks are executed in-memory upon calling `/audit/verify`.
* **Future Work**: Deploy a distributed hyperledger (such as Hyperledger Fabric or Amazon QLDB) to replicate ledger logs across multiple immutable backup nodes.

---

## 4. Setup & Credentials

### G. Cloud Integrations and Credentials Prerequisites
* **Current Boundary**: Third-party services (Upstash Redis, CloudAMQP RabbitMQ, Sentry, Resend, Backblaze B2, Google Gemini API, and Google Sign-in OAuth) require active api keys and connection strings (`REDIS_URL`, `RABBITMQ_URL`, `SENTRY_DSN`, `RESEND_API_KEY`, `B2_APPLICATION_KEY_ID`, `GEMINI_API_KEY`, `GOOGLE_CLIENT_ID`) in `.env`. If credentials are absent, the application gracefully degrades to local fallback behaviors (such as in-memory state caching, logging emails locally, skipping cloud uploads, or falling back to rule-based offline chatbot) without crashing.
* **Future Work**: Establish automated client tenant registration via AWS Secrets Manager or Vault to configure client APIs dynamically on startup.

