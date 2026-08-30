# Phase 17 Design System

This document registers design tokens to establish a professional "Modern Industrial SaaS Control Center" theme.

## 1. Color System Variables

```css
:root {
  /* Core Workspace Colors */
  --bg: #f8fafc;
  --surface: #ffffff;
  --surface-2: #f1f5f9;
  --border: #e2e8f0;
  
  /* Primary Accent & Brand */
  --primary: #4f46e5;         /* Indigo primary */
  --primary-dark: #3730a3;    /* Hover accent */
  --primary-light: #eef2ff;   /* Background active */
  
  /* Semantic Status Colors */
  --success: #10b981;         /* Green */
  --warning: #f59e0b;         /* Amber */
  --danger: #ef4444;          /* Red */
  --info: #3b82f6;            /* Blue */
  --simulation: #6366f1;      /* Purple/Indigo */
}
```

## 2. Navy Navigation Sidebar Colors

The left sidebar is locked to a dark navy industrial workspace scheme to preserve visual anchoring:

```css
:root {
  --sidebar-bg: #0f172a;       /* Deep Navy */
  --sidebar-border: #1e293b;
  --sidebar-text-muted: #94a3b8;
  --sidebar-text: #f8fafc;
  --sidebar-active-bg: #1e293b;
  --sidebar-active-text: #ffffff;
  --sidebar-section-color: #64748b;
}
```
