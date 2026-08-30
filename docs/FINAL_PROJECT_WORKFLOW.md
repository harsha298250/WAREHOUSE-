# docs/FINAL_PROJECT_WORKFLOW.md — End-to-End Business Workflows

This document outlines the core business operations workflows.

---

## 1. WMS Order Processing Workflow

```mermaid
sequenceDiagram
    autonumber
    actor U as User / Client
    participant API as FastAPI Backend
    participant DB as PostgreSQL
    participant T as Task Scheduler
    participant R as Robot Engine

    U->>API: Place Order (Items + Quantities)
    API->>DB: Begin Transaction & lock rows (SELECT FOR UPDATE)
    alt Stock Available
        DB-->>API: Row updates succeed (Reserved count incremented)
        API->>DB: Create order in RESERVED state
        API->>DB: Commit Transaction
        API->>T: Spawn Pick Task
        T->>R: Run OR-Tools Assignment
        R->>DB: Update Robot assigned_task_id
        API-->>U: Order placed successfully (HTTP 201)
    else Stock Insufficient
        API->>DB: Rollback / Partial reservation applied
        API->>DB: Create order in INVENTORY_SHORTAGE state
        API-->>U: Shortage registered (HTTP 201/200)
    end
```

---

## 2. Inventory Receiving & Putaway Workflow
1. **ASN Registration**: Supplier submits an Advanced Shipping Notice. An expected shipment quantity is registered in PostgreSQL.
2. **Quality Control Check**: Inspector runs verification checks against received quantities. Discrepancies are logged in the movement ledgers.
3. **Location Allocation**: Backend selects the optimal storage rack based on zoning heuristics.
4. **Transaction Putaway**: Inventory quantities are shifted from receiving zones to storage racks. An entry is appended to `InventoryMovementLedger`.
