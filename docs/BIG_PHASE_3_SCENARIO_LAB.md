# BIG PHASE 3 SCENARIO LAB SPECIFICATION

This document outlines the user workflow and available scenarios in the Scenario Lab.

## 1. Scenario Configurations
- **BASELINE**: Normal warehouse operations under standard demand constraints.
- **HIGH_DEMAND**: Stress-test simulation with doubled order volumes and arrivals.
- **ROBOT_FAILURE**: Injects AGV breakdowns to evaluate task reassignment resilience.
- **CONGESTION**: Increases layout traffic density and pathing cost weight factors.
- **OBSTACLE_EVENT**: Injects physical blocks into routes to force A* detours.

## 2. What-If Comparisons & AI
- **Run History**: Compares two experiment metrics side-by-side (throughput, utilization, charging queues, detours).
- **Gemini Assistant Support**: Integrated AI assistant tools can fetch, describe, and compare runs directly for decision support.
