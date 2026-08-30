# BIG PHASE 5 — VISUAL REGRESSION CHECKS

This document records the visual regression sanity checks performed on core views.

---

## 1. Regression Checkpoints

| View Tested | Reference State | Current Render State | Findings |
|---|---|---|---|
| **Dashboard** | Slate cards grid | Match layout hierarchy | Renders cleanly in both light and dark modes. |
| **Inventory** | Stock tables, ABC labels | Match tables design | Align items and SKUs accurately. |
| **Orders** | Priority badge lists | Clear color styling | Contrast satisfies accessibility requirements. |
| **Pathfinding** | Grid route lines | Pulse animations | Lines draw routes correctly matching WMS coords. |
| **Digital Twin** | 3D visual obstacles | Rotated robot structures | Dynamic rotations function correctly. |

---

## 2. Playwright Screenshot Captures
- Screenshot checkpoints verify layout stability on failure conditions and prevent visual overlaps during theme switching.
