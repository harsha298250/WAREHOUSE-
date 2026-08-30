# Phase 15 Supported Scenario Types

This document outlines the supported scenario profiles validated in the Scenario Lab.

## 1. Supported Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `robot_count` | Integer | 3 | Number of active robots deployed in the simulated fleet. |
| `robot_speed` | Float | 1.0 | Speed multiplier of simulated picker robots. |
| `order_volume` | Integer | 5 | Starting count of orders queued for simulation picker tasks. |
| `order_arrival_rate` | Integer | 50 | Frequency ticks between dynamic simulation orders generation. |
| `blocked_cells` | List[List[int]] | `[]` | Cell coordinate lists to mark as obstacles/blocked aisles on A* maps. |
| `failure_tick` | Integer | 100 | Tick number to inject robot OFFLINE status failure events. |

## 2. Supported Scenarios
- **Robot Fleet Scenario**: Altering count and speed multipliers to measure idle rates and completions.
- **Demand Load Scenario**: Surging order quantities to identify queue bottle-necks and backlog hours.
- **Routing & Obstacles Scenario**: Injecting blocked grid cell lists to evaluate path length deviations and replanning counts.
