# Phase 12 Existing System Audit: Digital Twin Expansion

This audit documents the existing assets, architectures, and integration points for the 3D Digital Twin expansion.

## 1. Existing Digital Twin & 2D Warehouse Map
- **Location**: `frontend/js/app.js` (`renderDigitalTwin` and `drawDTSpatialMap`).
- **Implementation**: The existing Digital Twin is a **2D SVG-based grid system** (`#dt-svg-canvas`).
- **Layers**: SVG `<g>` groups representing:
  - Grid cells (`#dt-g-grid`)
  - Heatmap overlay (`#dt-g-heatmap`)
  - Active routes (`#dt-g-routes`)
  - Trailed path points (`#dt-g-trails`)
  - Robots (`#dt-g-robots`)
  - Blocked obstacles (`#dt-g-obstacles`)
- **Interaction**: Lightweight selection listeners for cells/robots that load details into the `#dt-inspector-body` element.

## 2. Existing 3D and Three.js Code
- **Status**: **None**. There is currently no Three.js library loaded, and no WebGL or 3D renderer setup exists in the frontend. 
- **Required Library**: Three.js needs to be loaded via a standard CDN script tag in `frontend/index.html` (e.g., `https://unpkg.com/three@0.158.0/build/three.min.js` and `https://unpkg.com/three@0.158.0/examples/js/controls/OrbitControls.js`).

## 3. Existing Warehouse Coordinates
- **Layout Size**: 12 columns (X) by 5 rows (Y).
- **Coordinate Values**: 1-indexed integers (e.g., `x = 1` to `12`, `y = 1` to `5`).
- **Cell Mapping**:
  - Docks/Receiving: `row = 5`, `col = 1, 2`.
  - Charging Stations: `row = 5`, `col = 11, 12`.
  - Racks/Racks: `row = 1, 3`, `col = 2` to `11`.
  - Aisles (traversable): All other cells.
- **Three.js Conversion Design**:
  - **WMS X** → **Three.js X** (scaled by a factor of 10)
  - **WMS Y** → **Three.js Z** (scaled by a factor of 10)
  - **WMS Elevation (height)** → **Three.js Y** (constant base for floor, racks elevated)

## 4. Existing Robot Representation
- **Real Robots**: Read from `robots` array returned by `/digital-twin/{wh}/state`. Code split to show ID suffix (e.g., `RB-BLR-01` → `01`).
- **Battery**: Field `battery_level` (0-100%).
- **States**: `AVAILABLE`, `MOVING`, `PICKING`, `RETURNING`, `WAITING`, `CHARGING`, `FAILED`.

## 5. Existing APIs
- **GET `/digital-twin/{warehouse_id}/state`**: Full state (grid structure, robot statuses, locations, paths, tasks).
- **GET `/digital-twin/{warehouse_id}/events`**: Event stream logs.
- **GET `/digital-twin/{warehouse_id}/heatmap`**: Heatmap overlay metric grid.
- **GET `/simulation/runs/{run_id}/metrics`**: Completed SimPy simulation logs/KPIs.

## 6. Limitations & Integration Points
- **WebGL Fallback**: If WebGL/Three.js fails to initialize, the app must gracefully fall back to the existing 2D SVG map canvas.
- **Simulation View**: The 3D Digital Twin must render the playback coordinates of robots during a completed SimPy simulation run.
- **Data Mutation Isolation**: Front-end controls must remain strictly read-only and telemetry-focused. No direct DB modification allowed.
