# Shrinkage Anomaly Detection, AI Decision Center & Trust Ledger Workflow

This document defines the architectural specification for shrinkage anomaly detection, human-in-the-loop decisions, and tamper-evident SHA-256 audit logging in the **Smart Warehouse Intelligence Platform**.

---

## 🏗️ End-to-End System Architecture

```text
               MySQL Database
                     │
                     ▼
           Stock Movements Query
                     │
                     ▼
       IsolationForest Anomaly Detector
                     │
                     ▼
      Canonical Shrinkage Anomaly Schema
                     │
                     ▼
             AI Decision Center
                     │
                     ▼
        Explainable AI Recommendation
                     │
                     ▼
             Human Manager Review
              /      |      \
         APPROVE   MODIFY   REJECT
              \      |      /
               ▼     ▼     ▼
         Manager Decision Record
                     │
                     ▼
        Tamper-Evident Trust Ledger
                     │
                     ▼
       GET /audit/verify (SHA-256 Chain)
```

---

## 🛡️ Key Principles & Policy Compliance

### 1. Truthful Terminology (Zero Theft Accusations)
- **Policy**: Anomaly detection models cannot establish criminal intent or theft.
- **Terminology**: Labeled strictly as **"Potential Shrinkage Anomaly"** or **"Inventory Discrepancy Requiring Investigation"**. Never use "Theft Detected" or "Employee Stole Inventory".
- **Likely Causes**: Receiving discrepancy, stock adjustment, data entry lag, damaged goods, or unrecorded movement.

### 2. Monetary Exposure Calculation
- **Formula**: $\text{Estimated Exposure} = |\text{Discrepancy Quantity}| \times \text{Unit Cost}$
- If `unit_cost` is unavailable, exposure returns `null` with explanation.

### 3. Human-in-the-Loop Decisions (Not Automated Execution)
- Approving a recommendation records the **Manager Decision** in the database and Trust Ledger.
- System clearly communicates that real-world physical stock adjustments require manual field verification.

### 4. Server-Side RBAC Enforcement
- `POST /ai/recommendations/{rec_id}/action` requires `ADMIN` or `WAREHOUSE_MANAGER` role.
- `VIEWER` attempts return `403 Forbidden`.

---

## 🔒 Trust Ledger Hash-Chain Verification
- **Chain Structure**: Each decision record computes `hash = SHA256(timestamp + event_type + details + prev_hash)`.
- **Verification Endpoint**: `GET /audit/verify` iterates through all entries to verify chain continuity.
