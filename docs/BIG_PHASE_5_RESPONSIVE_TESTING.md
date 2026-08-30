# BIG PHASE 5 — RESPONSIVE LAYOUT VERIFICATION

This document outlines the layout behavior, media queries, and mobile/tablet viewport adaptations.

---

## 1. Supported Viewports & Resolutions

| Device Class | Minimum Width | Sidebar Behavior | Content Adjustments |
|---|---|---|---|
| **Large Desktop** | `1440px` | Permanent Sidebar | Full multi-column dashboard, detailed inventory tables. |
| **Standard Laptop** | `1280px` / `1024px` | Permanent Sidebar | Fluid grids adapt to 3-column / 2-column card structures. |
| **Tablet View** | `768px` | Drawer menu | Sidebar transitions to drawer mode triggered by top menu button. |
| **Mobile View** | `390px` | Drawer menu | Single-column stack layouts. Heavy elements (3D Digital Twin) hide coordinate grids and show list cards. |

---

## 2. Horizontal Page Overflow Prevention
- Body and HTML tags enforce `max-width: 100vw; overflow-x: hidden`.
- Playwright tests verify that the document scroll width is always less than or equal to the client viewport width on all device classes.
