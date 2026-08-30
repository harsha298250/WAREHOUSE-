"""
storage_tiering.py — Cost-aware cloud storage tiering simulation, MySQL-backed.
"""
import pandas as pd
from sqlalchemy import text
from backend.database import engine

RATES_PER_GB_MONTH = {"hot": 0.023, "cool": 0.010, "cold": 0.004}
BYTES_PER_ROW = 220


def simulate_tiering(hot_days=30, cool_days=90):
    df = pd.read_sql(text("SELECT date FROM stock_movements"), engine)
    if df.empty:
        return {"policy": "", "row_counts_by_tier": {}, "estimated_gb_by_tier": {},
                "monthly_cost_naive_all_hot_usd": 0, "monthly_cost_tiered_usd": 0,
                "estimated_savings_pct": 0,
                "production_scale_projection": {"assumption": "no data yet",
                                                 "monthly_cost_naive_all_hot_usd": 0,
                                                 "monthly_cost_tiered_usd": 0,
                                                 "estimated_monthly_savings_usd": 0}}

    df["date"] = pd.to_datetime(df["date"])
    latest = df["date"].max()
    df["age_days"] = (latest - df["date"]).dt.days

    def tier_of(age):
        if age <= hot_days:
            return "hot"
        elif age <= cool_days:
            return "cool"
        return "cold"

    df["tier"] = df["age_days"].apply(tier_of)
    tier_counts = df["tier"].value_counts().to_dict()

    gb_per_tier = {t: (tier_counts.get(t, 0) * BYTES_PER_ROW) / (1024 ** 3) for t in RATES_PER_GB_MONTH}
    tiered_cost = sum(gb_per_tier[t] * RATES_PER_GB_MONTH[t] for t in RATES_PER_GB_MONTH)
    total_gb = sum(gb_per_tier.values())
    naive_cost = total_gb * RATES_PER_GB_MONTH["hot"]
    savings = naive_cost - tiered_cost
    savings_pct = (savings / naive_cost * 100) if naive_cost > 0 else 0

    scale_factor = (500 * 50 * 365 * 3) / max(len(df), 1)
    naive_cost_scaled = naive_cost * scale_factor
    tiered_cost_scaled = tiered_cost * scale_factor

    return {
        "policy": f"hot <= {hot_days}d, cool <= {cool_days}d, cold > {cool_days}d",
        "row_counts_by_tier": tier_counts,
        "estimated_gb_by_tier": {k: round(v, 6) for k, v in gb_per_tier.items()},
        "monthly_cost_naive_all_hot_usd": round(naive_cost, 6),
        "monthly_cost_tiered_usd": round(tiered_cost, 6),
        "estimated_monthly_savings_usd": round(savings, 6),
        "estimated_savings_pct": round(savings_pct, 1),
        "production_scale_projection": {
            "assumption": "500 SKUs x 50 warehouses x 3 years of daily logs",
            "monthly_cost_naive_all_hot_usd": round(naive_cost_scaled, 2),
            "monthly_cost_tiered_usd": round(tiered_cost_scaled, 2),
            "estimated_monthly_savings_usd": round(naive_cost_scaled - tiered_cost_scaled, 2),
        },
    }
