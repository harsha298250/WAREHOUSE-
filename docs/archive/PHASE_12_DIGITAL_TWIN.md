# Phase 12 Digital Twin Documentation

This document describes the design, implementation, and integration of the 3D Digital Twin visualization layer.

## 1. Architecture
The 3D Digital Twin operates completely in the frontend, leveraging WebGL and Three.js, and polling the backend's `/digital-twin/{id}/state` endpoint to update physical entity representations dynamically.

```
PostgreSQL (DB)
      ↓
Digital Twin REST APIs (`/state` / `/heatmap` / `/events`)
      ↓
Frontend polling (every 2s) & Dimension Toggle Selector
      ↓
WebGLRenderer & Three.js Scene
      ↓
Inspectable 3D Entities (Robots, Racks, Charging pads, Paths)
```

## 2. Coordinate Transformation System
The WMS coordinate system uses a 1-indexed integers grid matching the physical layout (12 cols x 5 rows). The Three.js scene uses a right-handed system centered around the origin `(0, 0, 0)`.

**Mapping Formula**:
- **Three.js X** = `(WMS X - 6.5) * 10`
- **Three.js Z** = `(WMS Y - 3.0) * 10`
- **Three.js Y** (Elevation) = 
  - Floor plate top = `0.0`
  - Robots y-position = `0.1` (bases elevated to `y=0.5`, domes to `y=1.75`)
  - Racks y-position = `0.1` (racks are cubes of height 10)
  - Charging pads y-position = `0.1` (glowing sphere status lights at `y=0.6`)
  - Obstacles y-position = `4.0` (boxes of height 8)
  - Lines/Paths y-position = `0.5`

## 3. Live Mode vs Simulation Mode
- **LIVE Mode**: Pulls live PostgreSQL operations state (observation mode) showing current physical telemetry and queues.
- **SIMULATION Mode**: Triggered during a SimPy run, polling active simulated snapshots and replaying movement coordinates and events stream without database mutations.

## 4. Resource & Memory Management
To avoid memory leaks, calling `destroyThreeEngine` (triggered when navigating away or switching to 2D view) recursively disposes of geometries, materials, textures, removes click listeners, and cancels the `requestAnimationFrame` render loop.
