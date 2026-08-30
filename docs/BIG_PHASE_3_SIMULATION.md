# BIG PHASE 3 SIMULATION ENGINE SPECIFICATION

This document describes the design and isolation mechanics of the SimPy discrete-event simulation engine in the Smart Warehouse Platform.

## 1. Engine Core
- Built on SimPy, managing queues for:
  - Order arrivals (order_arrival_process)
  - Task scheduler assignments (scheduler_process)
  - Robot transport movements (robot_process)
  - Charging lanes allocations (charging resource limits)

## 2. Environment Isolation Mechanics
> [!IMPORTANT]
> The simulation engine runs completely decoupled from production database mutations to protect real operational inventory:
> - Production inventory balances (`Inventory.on_hand`) are never written to by a simulation run.
> - Simulated picks and putaway operations are written as transient offsets inside `SimulationSnapshot.sim_inventory_delta`.
> - Active simulation sessions operate tick-by-tick using database transactions mapped to `digital_twin_simulations` and `simulation_snapshots` tables in isolation.
