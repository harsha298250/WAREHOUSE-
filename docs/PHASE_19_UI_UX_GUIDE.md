# Phase 19 UI/UX Guide — Smart Warehouse Intelligence Platform

## 1. Design System Architecture

The application UI utilizes a unified, componentized design system. All visual components rely on CSS variables declared in the `:root` pseudo-class (and overridden inside `body.dark-mode`).

### 1.1 Color Tokens
* **Backgrounds**: `--bg` (`#f8fafc` in light mode, `#0b0f19` in dark mode).
* **Surfaces**:
  * `--surface` (`#ffffff` / `#111827`): main dashboard panels and modal dialogs.
  * `--surface-2` (`#f1f5f9` / `#1e293b`): field inputs, sub-menus, and select fields.
  * `--surface-3` (`#e2e8f0` / `#0f172a`): separators and grid borders.
* **Text**:
  * `--text` (`#0f172a` / `#f8fafc`): primary headers, table text, and active choices.
  * `--text-muted` (`#475569` / `#94a3b8`): body descriptions and metadata.
  * `--text-faint` (`#64748b` / `#64748b`): secondary timestamps, placeholders, and disabled labels.
* **Accents**: `--primary` (`#4f46e5` / `#818cf8`) and `--accent` (`#6366f1`).
* **Status Badges**:
  * **Success (Green)**: `--success` (`#10b981`).
  * **Warning (Amber)**: `--warning` (`#f59e0b`).
  * **Danger/Critical (Red)**: `--danger` (`#ef4444`).
  * **Info (Blue)**: `--info` (`#3b82f6`).

### 1.2 Spacing & Radii
* `--radius-sm` (6px): buttons, small input selectors, and badge tags.
* `--radius` (8px): standard input controls and action buttons.
* `--radius-lg` (12px): dashboard card panels, modal dialogs, and detail drawers.

---

## 2. Page Loading & Template Injection

Page rendering is driven by `navigate(view)` in [app.js](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/frontend/js/app.js).
1. **Teardown**: Any active polling interval (`dtPollInterval`), SSE streams, and Three.js orbit controls are disposed cleanly.
2. **Skeleton Loader**: Injects a dashboard skeleton (`skeletonDashboard()`) or a table skeleton (`skeletonTable()`) to prevent sudden layout shifts.
3. **Template Rendering**: Asynchronously queries the backend and executes the page renderer (e.g. `renderDashboard()`).
4. **Icons**: Generates SVG assets using `lucide.createIcons()`.
