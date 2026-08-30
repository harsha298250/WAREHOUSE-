# Phase 15 AI Scenario Integration

This document outlines the Gemini Tool Calling schemas registered to enable natural language scenario stresses.

## 1. Registered Tools

- **`create_scenario`**: Generates a new scenario with specified fleet counts and load volumes.
- **`run_scenario_experiment`**: Queues execution repetitions in the background engine.
- **`get_scenario_result`**: Pulls status, logs, and aggregated metrics summaries.
- **`compare_scenarios`**: Reports variance diffs between two completed runs.
- **`compare_scenario_with_baseline`**: Audits stress metric variances against actual live baseline operational records.

## 2. Multi-Tool Reasoning Sequence
If a user asks: `"Would adding 3 robots help handle a 20% surge in order volume?"`
1. Gemini retrieves the live status using `get_warehouse_status`.
2. Gemini evaluates parameters and creates a custom scenario using `create_scenario`.
3. Gemini executes repetitions using `run_scenario_experiment`.
4. Gemini waits for status and queries KPIs via `get_scenario_result`.
5. Gemini audits variances against baseline using `compare_scenario_with_baseline`.
6. Gemini returns a detailed trade-off explanation of simulated outcomes.
