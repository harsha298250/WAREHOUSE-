# Phase 3 Robotics Failure Matrix

This matrix describes the robotics failure modes, risk levels, and recovery behaviors.

| Failure Mode | Risk Level | Detection Mechanism | Safe Behavior / Recovery |
|--------------|------------|---------------------|--------------------------|
| **No eligible robot** | Medium | Auto-assignment returns empty candidate list | Task remains in `QUEUED` state; no dispatches are forced. |
| **Insufficient battery** | High | Estimated Manhattan distance energy check fails | Task rejected; robot remains `AVAILABLE` or auto-routed to `CHARGING`. |
| **Obstacle added during move** | High | Simulated obstacle on route path coordinates | Tick loop detects block, invalidates route, and triggers `PATH_REPLANNED` detour. |
| **Unreachable destination** | Medium | A* search returns `None` (open set empty) | Task transitions to `FAILED`, robot transitions back to `AVAILABLE`. |
| **Corridor Deadlock** | High | Wait tick counter exceeds 5 ticks | Robot status transitions to `PAUSED` and appends `DEADLOCK_DETECTED` ledger log. |
| **Robot goes OFFLINE** | High | Status set to `OFFLINE` during task | Active route invalidated, assigned task released and reset to `QUEUED`. |
| **Google OR-Tools failure** | Low | Import exception or solver timeout | Auto-assign engine transparently executes the greedy deterministic fallback. |
