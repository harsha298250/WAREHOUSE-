# Phase 16 Data Provenance

This document maps analytics metrics directly to their authoritative source columns in PostgreSQL.

## 1. Provenance Source Register

| Metric | Source Table | Source Attributes | Logic Type |
| :--- | :--- | :--- | :--- |
| **Completed Orders** | `orders` | `status == 'COMPLETED'` | COUNT |
| **Stockout Rate** | `inventory` | `available <= 0` | COUNT / TOTAL RATIO |
| **Total SKU Value** | `inventory` join `items` | `on_hand * unit_cost` | SUM |
| **Robot Utilization** | `robots` | `utilization_percent` | AVERAGE |
| **Shrinkage Exposure** | `shrinkage_flags` | `estimated_exposure` | SUM |
| **Reorder Recommendations** | `replenishment_recommendations`| `recommended_qty` | SELECT |
| **Simulated Duration** | `digital_twin_simulations` | `tick_count` | AVERAGE |

## 2. Fabricated-Data Audit Findings
- Zero default placeholders, random seeds, or dummy metrics are generated.
- When query intervals are empty, the dashboard defaults to reporting `INSUFFICIENT DATA` or falls back to live database summaries.
