"""
transfer_optimizer.py — Multi-warehouse transfer optimization, MySQL-backed.
Finds cases where one warehouse's surplus can cover another's shortfall,
using each item's relative stock-to-safety-stock ratio across warehouses.
"""
import pandas as pd
from sqlalchemy import text
from backend.database import engine


def find_transfer_opportunities(item_id: str = None, top_n: int = 20):
    query = """
        SELECT sm.warehouse_id, sm.item_id, i.name AS item_name, i.category,
               i.unit_cost, i.safety_stock, sm.closing_stock
        FROM stock_movements sm
        JOIN items i ON sm.item_id = i.id
        JOIN (
            SELECT warehouse_id, item_id, MAX(date) AS max_date
            FROM stock_movements GROUP BY warehouse_id, item_id
        ) latest ON sm.warehouse_id = latest.warehouse_id
                AND sm.item_id = latest.item_id
                AND sm.date = latest.max_date
    """
    params = {}
    if item_id:
        query += " WHERE sm.item_id = :item_id"
        params["item_id"] = item_id
    df = pd.read_sql(text(query), engine, params=params)
    if df.empty:
        return []

    opportunities = []
    for iid, group in df.groupby("item_id"):
        if len(group) < 2:
            continue
        group = group.copy()
        group["ratio"] = group["closing_stock"] / group["safety_stock"].replace(0, 1)
        mean_ratio = group["ratio"].mean()

        surplus = group[group["ratio"] > mean_ratio * 1.25]
        deficit = group[group["ratio"] < mean_ratio * 0.8]
        if surplus.empty or deficit.empty:
            continue

        for _, d_row in deficit.iterrows():
            candidates = surplus[surplus["warehouse_id"] != d_row["warehouse_id"]].copy()
            if candidates.empty:
                continue
            candidates["excess"] = candidates["closing_stock"] - candidates["safety_stock"]
            best = candidates.sort_values("excess", ascending=False).iloc[0]

            deficit_gap = max(1, int(d_row["safety_stock"] - d_row["closing_stock"]))
            transfer_qty = int(min(max(1, best["excess"]), deficit_gap + d_row["safety_stock"] * 0.5))
            if transfer_qty <= 0:
                continue

            transfer_cost_per_unit = 8.0
            procurement_overhead_per_unit = 0.05 * d_row["unit_cost"]
            est_savings = round(transfer_qty * (procurement_overhead_per_unit - transfer_cost_per_unit), 2)

            opportunities.append({
                "item_id": iid, "item_name": d_row["item_name"], "category": d_row["category"],
                "from_warehouse": best["warehouse_id"], "to_warehouse": d_row["warehouse_id"],
                "transfer_qty": transfer_qty, "from_stock": int(best["closing_stock"]),
                "to_stock": int(d_row["closing_stock"]), "to_safety_stock": int(d_row["safety_stock"]),
                "estimated_savings_inr": est_savings,
                "reason": (
                    f"{d_row['warehouse_id']} holds {d_row['ratio']:.2f}x safety stock (below the "
                    f"{iid} network average of {mean_ratio:.2f}x) while {best['warehouse_id']} holds "
                    f"{best['ratio']:.2f}x — a transfer rebalances stock without a fresh purchase order."
                ),
            })

    opportunities.sort(key=lambda o: o["estimated_savings_inr"], reverse=True)
    return opportunities[:top_n]
