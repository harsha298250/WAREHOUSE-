# Phase 17 UI/UX Architecture

This document registers navigation hierarchies and workspace layout models.

## 1. Global Shell Structure
The application structure enforces three main view components:
- **Left Sidebar**: locks grouped modules navigation (Operations, Intelligence, Simulation, Management, and System).
- **Top Header**: displays global search, breadcrumbs, notifications count, currency selections, and warehouse context.
- **Content Area**: embeds the active workspace view dynamically based on navigation tabs selections.

```
+-------------------------------------------------------------+
|  WAREHOUSE OS  |  Dashboard / Context Header     (Select)   |
+----------------+--------------------------------------------+
|  Operations    |                                            |
|  - Dashboard   |                                            |
|  - Inventory   |              Main content                  |
|  - Robots      |               Workspace                    |
|  Intelligence  |                                            |
|  - Forecasting |                                            |
+----------------+--------------------------------------------+
```

## 2. Dynamic View Injection
The App Router handles view switching dynamically inside [`frontend/js/app.js`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/frontend/js/app.js) by intercepting `data-view` attributes from navigation items.
- Only authorized views are displayed based on roles.
- Unauthorized pages show a clean access denied state.
