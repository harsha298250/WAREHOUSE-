# BIG PHASE 5 — UI & VIEW SWITCHER ARCHITECTURE

This document explains the frontend client-side navigation architecture, dynamic views injection, event handling, and data binding models.

---

## 1. Single Page View Switcher

The application shell provides client-side navigation using a lightweight JavaScript router implemented in `app.js`.

### Switch Flow
1. User triggers click on a sidebar/header menu item containing a `data-view` attribute.
2. The router updates the active navigation state class (`.active` visual styles in sidebar).
3. The content block `#main-content` is cleared, and the corresponding async load/render function is executed:
   - `renderDashboard(el)`
   - `renderItems(el)`
   - `renderOrders(el)`
   - etc.
4. The page title and subtitle metadata headers are updated.

---

## 2. API Contract & Data Binding

- All API communications flow through the thin wrapper defined in [api.js](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/frontend/js/api.js).
- Auth states and Bearer JWT tokens are stored in the browser's `localStorage` namespace (`wh_token`).
- Active warehouse filters are synchronized globally using the `#warehouse-select` dropdown, which triggers re-rendering of the active view on change.

---

## 3. Real-time Synchronization (SSE)

- Direct server-sent events (SSE) connect to `/digital-twin/sync` and `/notifications/stream`.
- Real-time updates update the state markers (active robot positions, alerts count) on-screen without requiring page reloads.
