"""
autoscaling_sim.py — Auto-scaling cost simulation, MySQL-backed.
"""
import pandas as pd
import numpy as np
from sqlalchemy import text
from backend.database import engine

COST_PER_INSTANCE_HOUR_USD = 0.05
REQUESTS_PER_INSTANCE_CAPACITY = 500


def simulate_autoscaling():
    df = pd.read_sql(text("""
        SELECT date, SUM(stock_in + stock_out) AS volume
        FROM stock_movements GROUP BY date ORDER BY date
    """), engine)
    if df.empty:
        return {"peak_instances_needed": 0, "avg_instances_autoscaled": 0,
                "monthly_cost_fixed_capacity_usd": 0, "monthly_cost_autoscaled_usd": 0,
                "estimated_savings_usd": 0, "estimated_savings_pct": 0, "daily_scaling_profile": []}

    df["est_requests"] = df["volume"] * 3
    df["required_instances"] = np.ceil(df["est_requests"] / REQUESTS_PER_INSTANCE_CAPACITY).clip(lower=1)

    peak_instances = int(df["required_instances"].max())
    autoscale_instance_hours = df["required_instances"].sum() * 24
    fixed_instance_hours = peak_instances * len(df) * 24

    autoscale_cost = autoscale_instance_hours * COST_PER_INSTANCE_HOUR_USD
    fixed_cost = fixed_instance_hours * COST_PER_INSTANCE_HOUR_USD
    savings = fixed_cost - autoscale_cost
    savings_pct = (savings / fixed_cost * 100) if fixed_cost > 0 else 0

    daily = df[["date", "est_requests", "required_instances"]].copy()
    daily["date"] = daily["date"].astype(str)

    return {
        "peak_instances_needed": peak_instances,
        "avg_instances_autoscaled": round(df["required_instances"].mean(), 2),
        "monthly_cost_fixed_capacity_usd": round(fixed_cost, 2),
        "monthly_cost_autoscaled_usd": round(autoscale_cost, 2),
        "estimated_savings_usd": round(savings, 2),
        "estimated_savings_pct": round(savings_pct, 1),
        "daily_scaling_profile": daily.to_dict(orient="records"),
    }
