# Phase 15 Security & Guardrails

This document registers safety guards built to secure the simulation and scenario calculations.

## 1. Parameters Guardrails & Sanitization
- **Repetitions Cap**: Limited between 1 and 10 to prevent resource exhaustion attacks.
- **Fleets Cap**: Fleet size configuration values must be bounded between 1 and 10 to limit CP-SAT matrix solving complexities.
- **Duration Cap**: Bounded simulation ticks bounds checks to avoid background execution threads starvation.
- **SQL Injection Prevention**: Safe parameter mappings instead of direct string concatenations inside DB queries.

## 2. RBAC Policies
- Only users with `admin` or `manager` roles possess write credentials to invoke `create_scenario` and `run_scenario_experiment` tools.
- `viewer` and `operator` roles are restricted to read-only tool invocations (`get_scenario_result`).
- Access validation happens independently inside the backend service registry prior to running queries.
