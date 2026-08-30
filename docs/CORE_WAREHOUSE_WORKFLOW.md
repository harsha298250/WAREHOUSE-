# docs/CORE_WAREHOUSE_WORKFLOW.md — Core Warehouse Workflows

This document details the operational workflows for the core warehouse activities.

---

## 1. Quality Control & Putaway Workflow

```mermaid
graph TD
    Inbound[Expected Shipment] -->|Mark Received| Received[Received Shipment]
    Received -->|Verify Quantity| Verified[Verified Shipment]
    Verified -->|Inspector QC| QC{QC Check}
    QC -->|Passed Qty| Putaway[Putaway storage location]
    QC -->|Failed Qty| Quarantine[Auto-routed to Quarantine Location]
    Putaway -->|Capacity & Status Check| Storage[Stock added to Available Inventory]
```

---

## 2. Inventory Transfers Request Flow

```mermaid
sequenceDiagram
    autonumber
    Requester->>Backend: POST /wms/transfers (Source to Dest locations)
    Backend->>Database: Lock source inventory (SELECT FOR UPDATE)
    Backend->>Database: Increment reserved, decrement available
    Backend->>Database: Create TransferRequest (Status = REQUESTED)
    Manager->>Backend: POST /wms/transfers/{id}/approve
    Backend->>Database: Update Status = APPROVED
    Operator->>Backend: POST /wms/transfers/{id}/dispatch
    Backend->>Database: Deduct source on_hand & reserved (IN_TRANSIT)
    Operator->>Backend: POST /wms/transfers/{id}/receive
    Backend->>Database: Capacity check dest location
    Backend->>Database: Increment dest on_hand & available (RECEIVED)
```
