# Phase 16 Reporting Capabilities

This document registers the layout properties, headers, and profiles supported by the WMS export router.

## 1. Supported Report Types

- **Executive Warehouse Report**: Consolidated operational KPI summary.
- **Operations Report**: Task throughput and average picking duration.
- **Inventory Report**: SKU stock levels, reserved units, and ABC classes.
- **Robot Performance Report**: Telemetry travel distance, tasks completed, and battery logs.
- **Forecast Report**: Horizon predictions vs actual demand WAPE values.
- **Anomaly Report**: Shrimp flag logs and exposure totals.
- **Replenishment Report**: Reorder point alerts and safety stock recommended quantities.
- **Simulation Report**: SimPy discrete-event runs completion stats.

## 2. Export Formats
- **PDF**: Page numbering, corporate color formattingHex (#0F172A), and clean margins.
- **Excel**: Auto-adjusting grid layout worksheets containing an *Executive Summary* tab.
- **CSV**: Text-comma lists suitable for third-party spreadsheet ingestion.
