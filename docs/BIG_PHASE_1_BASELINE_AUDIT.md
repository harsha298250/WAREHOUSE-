# BIG_PHASE_1_BASELINE_AUDIT.md — Core Warehouse & Production Hardening

## 1. Baseline Inventory of Core WMS Modules

This audit evaluates the existing codebase for Core WMS features (Receiving, Quality Control, Putaway, Inventory, Transfers, Orders, Picking, Packing, Shipping, Returns, Damage, Reconciliation, and Auditing).

---

## 2. Module Verification Status

### A. Already Implemented (Verified & Safe)
* **Authentication & RBAC**: Session tokens, login lockout limits, and role boundaries (`admin`, `manager`, `operator`, `auditor`, `viewer`).
* **Warehouse Isolation**: Dynamic backend scoping based on `UserWarehouseAccess` mapping.
* **Basic Inventory**: `Inventory` table containing stock balances (`on_hand`, `reserved`, `available`) matching the core invariant: `available = on_hand - reserved`.
* **SELECT FOR UPDATE locks**: Serialized order allocations to prevent race conditions.
* **Audit Ledgers**: Secure, hash-chained `AuditLedger`, immutable `AccessLog`, and queryable `SecurityEvent` models.

---

### B. Partially Implemented (Requires Upgrade/Hardening)
* **Master Data**: 
  - `Warehouse` lacks dedicated configurations for zones (`receiving`, `storage`, `picking`, `quarantine`, `damaged`, etc.).
  - `WarehouseLocation` lacks capacity validation constraints during inventory putaway.
* **Inbound & Receiving**:
  - `IncomingShipment` handles basic incoming quantities, but lacks over-receiving blocks, partial receiving workflows, and discrepancy thresholds.
  - Multi-item incoming shipments are stored as individual single-item records.
* **Quality Control (QC)**:
  - QC status fields (`qc_result`) exist inside `IncomingShipment`, but there is no dedicated transaction to log inspector actions, reasons for rejection, and quarantine movement triggers.
* **Order Processing**:
  - Picking, packing, and shipping workflows exist, but require stricter sequence checking (e.g. preventing packing prior to complete picking, and shipping prior to packing).

---

### C. Missing (Needs Implementation)
* **Inventory Transfers**:
  - No models, APIs, or database schemas exist for same-warehouse or cross-warehouse Transfer Requests (`REQUESTED`, `APPROVED`, `IN_TRANSIT`, `RECEIVED`, `CANCELLED`).
* **Damage Handling**:
  - No dedicated table or operational workflow for logging damaged goods, quarantine movements, and write-off transactions.
* **Customer Returns**:
  - No database tables or lifecycle APIs exist for customer/supplier returns management (`REQUESTED`, `APPROVED`, `RECEIVED`, `RESTOCKED`, `QUARANTINED`, `DAMAGED`, `REJECTED`, `CLOSED`).

---

### D. Broken / Unsafe / Duplicate / Unnecessary
* **Unsafe**: Direct mathematical calculations previously used insecure `eval()` sandbox calculations. (Already hardened to a math-only AST parser in Phase 6).
* **Duplicate**: Handlers in router scopes occasionally duplicate permission checks instead of reusing standard FastAPI depends functions (e.g., duplicate JWT checks).
