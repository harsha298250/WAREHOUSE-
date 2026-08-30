# Phase 16 Security and Isolation

This document outlines security guardrails and RBAC checks implemented in Phase 16.

## 1. Multi-Warehouse Security Boundaries
- Strict warehouse isolation is enforced. Queries filter by `warehouse_id` parameter to restrict leakage of cross-facility data.
- The `get_current_user` dependencies validate users credentials. If unauthorized database requests are made, an HTTP 403 error is returned.

## 2. Exports Security Controls
- Export endpoints (`GET /reports/export`) require a valid JWT bearer authentication token.
- Operational reports exports are restricted to roles possessing authorization (`admin`, `manager`, `auditor`).
- Operator and Viewer roles are prevented from performing reports downloads.
