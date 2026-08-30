# BIG PHASE 3 3D DIGITAL TWIN SPECIFICATION

This document outlines the detailed specifications of the 3D Digital Twin visualization layer updated in Big Phase 3.

## 1. 3D Spatial Entities Specification

### Coordinates Alignment
- **2D/3D Mapping Formula**:
  - `Three.js X` = `(WMS X - 6.5) * 10`
  - `Three.js Z` = `(WMS Y - 3.0) * 10`
  - `Three.js Y` = `0.1` (Elevation offset)
- **Cell Scale**: Standard cells are represented in a `10 x 10` layout grid.

### Physical Floor Assets
- **Storage Racks**: Cube wireframe geometry of size `8 x 10 x 8` representing rack frames, plus solid boxes inside color-coded based on safety/health metrics.
- **Charging Lanes**: Cylinder pad representing charger contacts, and glowing status light sphere above it.
- **Docks/Receiving Pads**: Rendered as transparent green floor panels.
- **Shipping/Packing Pads**: Rendered as transparent blue floor panels.

### Robotics Representation
- Renders as a composite group containing:
  - Base cylinder (`metalness: 0.8, roughness: 0.2`)
  - Dome warning indicator cylinder (`emissiveIntensity: 0.5`)
  - Battery capacity box scaling on the X-axis
- Dome color states:
  - `AVAILABLE`/`IDLE`: Green (`0x10b981`)
  - `MOVING`: Cyan (`0x06b6d4`)
  - `PICKING`/`RETURNING`: Amber (`0xf59e0b`)
  - `FAILED`/`OFFLINE`: Red (`0xef4444`)
  - `WAITING`: Dark Red (`0xeb4034`)
  - `CHARGING`: Orange (`0xffa500`)

## 2. Dynamic Telemetry & Micro-Animations

### Heading Orientation
- Computes `Math.atan2(dx, dz)` in real-time to align robot mesh groups with their target navigation heading.

### Pulsating Indicators
- Dome warnings flash quickly during `WAITING`, `FAILED`, or low battery conditions using sine-based emissive light multipliers.
- Active path line opacities breathe using a sine wave, representing flowing routes.
- Charging indicators blink dynamically to show active energy transfers.
