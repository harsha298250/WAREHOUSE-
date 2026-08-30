# BIG PHASE 5 — DESIGN SYSTEM SPECIFICATION

This document outlines the visual standards, components, typography, layout rules, and token system designed to deliver a modern, industrial, and highly professional SaaS product experience.

---

## 1. Color Palette

The color palette is modeled directly after the **slate** palette in Tailwind / shadcn UI.

### Core Backgrounds & Surfaces
- **App Background**: `#f8fafc` (Light) / `#0b0f19` (Dark)
- **Primary Surface**: `#ffffff` (Light) / `#111827` (Dark)
- **Secondary Surface**: `#f1f5f9` (Light) / `#1e293b` (Dark)
- **Border color**: `#e2e8f0` (Light) / `#334155` (Dark)

### Accent & Status Indicators
- **Primary Accent**: `#4f46e5` (Light Indigo) / `#818cf8` (Dark Indigo)
- **Success Status**: `#10b981` (Green)
- **Warning Status**: `#f59e0b` (Amber)
- **Danger/Alert Status**: `#ef4444` (Red)
- **Info/Neutral Status**: `#3b82f6` (Blue)

---

## 2. Typography

- **Primary Font**: `Inter` (sans-serif) for general controls, labels, layout headers, and body text.
- **Monospace Font**: `JetBrains Mono` for IDs (SKUs, transaction IDs, coordinate pairs, system metrics).
- **Scale**:
  - `h1`: `24px`, bold, `tracking-tight`
  - `h2`: `18px`, semibold
  - `body`: `14px`
  - `small`: `12px`

---

## 3. Borders & Shadows

- **Border Radius**:
  - Small Controls (Inputs, Badges, Buttons): `6px` (`--radius-sm`)
  - Standard Cards / Overlays: `8px` (`--radius`)
  - Panels / Dialog Modals: `12px` (`--radius-lg`)
- **Box Shadows**:
  - Small elements: `0 1px 2px rgba(15, 23, 42, 0.04)`
  - Standard cards: `0 4px 12px rgba(15, 23, 42, 0.06)`
  - Overlays & Popups: `0 10px 25px rgba(15, 23, 42, 0.08)`

---

## 4. UI Elements Standard

### Buttons
- Height: `36px` (Default), `44px` (Large)
- Padding: `8px 16px`
- Transitions: `0.12s ease`

### Tables & Data Grids
- Padding: `12px` per row
- Border division: light bottom border (`1px solid var(--border)`)
- Hover highlight: background shifts to `var(--surface-2)` on row hover.

### Badges
- Semi-transparent fills with matching border and text colors for status (e.g. `bg-success-light`, `text-success` with green border).
