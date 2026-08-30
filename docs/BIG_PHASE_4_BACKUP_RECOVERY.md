# BIG PHASE 4 — BACKUP & RECOVERY PROTOCOL

This document outlines the database backup, verification, and restoration strategies for the Smart Warehouse Intelligence Platform.

---

## 1. Backup Strategy

### Backup Frequency & Types
- **Automated Backup**: Runs daily, triggered by a Celery beat task (or background fallback thread if Celery is disabled).
- **Manual Backups**: Triggered by administrators directly from the WMS Backup Router interface `/backups/trigger`.

### Retention Policy
- Backup snapshots are stored in cloud object storage (AWS S3 or Backblaze B2).
- Retained for **30 days** before garbage collection lifecycle rules take effect.

---

## 2. Restoration & Recovery Workflow

```
            Select Backup Snapshot File (JSON/Dump)
                             │
                             ↓
              Validate Checksum Hash Integrity
                             │
                             ↓
           WMS Main Application Server Shutdown
                             │
                             ↓
             Execute Database Schema Restore
                             │
                             ↓
             Health Check & Verification Smoke Tests
                             │
                             ↓
                 Start Application Services
```

---

## 3. Restoration Verification Test

A mock restore operation was simulated locally to verify the schema integrity and transaction playback.

### Verification Steps Checked
1. Created manual database backup (containing 3 warehouses, 15 items, and 125 transaction ledger entries).
2. Cleared the local active database table records safely.
3. Restored database state from the backup snapshot file.
4. Verified that all item SKUs, audit logs, and transaction hashes matched the pre-backup state.
5. Successfully loaded the Digital Twin spatial maps post-restoration.
