"""
nl_query.py — Natural-language query interface, MySQL-backed.
Lightweight rule-based intent + entity parser (no external API/keys needed).
"""
import pandas as pd
from sqlalchemy import text
from backend.database import engine
from ml.forecast import forecast_item
from ml.shrinkage_insights import build_shrinkage_insights


def _extract_warehouse(nl_text: str):
    nl = nl_text.lower()
    df = pd.read_sql(text("SELECT id, name, location FROM warehouses"), engine)
    for _, row in df.iterrows():
        candidates = [row["id"].lower(), row["name"].lower()]
        if row["location"]:
            candidates.append(row["location"].lower())
        for c in candidates:
            if c and c in nl:
                return row["id"]
    return None


def answer_query(nl_text: str):
    text_l = nl_text.lower()
    wh = _extract_warehouse(nl_text)

    if "shrinkage" in text_l or "theft" in text_l or "loss" in text_l:
        insights = build_shrinkage_insights()
        clusters = insights["clusters"]
        if wh:
            clusters = [c for c in clusters if c["dominant_warehouse"] == wh]
        if not clusters:
            return {"intent": "shrinkage_query", "answer": "No significant shrinkage patterns found for that scope."}
        top = clusters[0]
        return {"intent": "shrinkage_query", "answer": top["pattern_summary"], "data": clusters[:3]}

    if any(k in text_l for k in ["reorder", "restock", "running out", "low stock"]):
        if not wh:
            return {"intent": "reorder_query", "answer": "Please mention a warehouse name or location so I can check reorder needs."}
        items = pd.read_sql(text("SELECT DISTINCT item_id FROM stock_movements WHERE warehouse_id = :wh"),
                             engine, params={"wh": wh})
        needing = []
        for iid in items["item_id"]:
            r = forecast_item(wh, iid)
            if r and r["needs_reorder"]:
                needing.append(r["item_name"])
        if not needing:
            return {"intent": "reorder_query", "answer": f"No items currently need reordering at {wh}."}
        return {
            "intent": "reorder_query",
            "answer": f"{len(needing)} item(s) need reordering at {wh}: {', '.join(needing[:8])}" + ("..." if len(needing) > 8 else ""),
            "data": needing,
        }

    if "stock" in text_l and wh:
        df = pd.read_sql(text("""
            SELECT SUM(closing_stock) total FROM stock_movements sm
            JOIN (SELECT warehouse_id, item_id, MAX(date) md FROM stock_movements
                  WHERE warehouse_id = :wh GROUP BY warehouse_id, item_id) latest
            ON sm.warehouse_id = latest.warehouse_id AND sm.item_id = latest.item_id AND sm.date = latest.md
        """), engine, params={"wh": wh})
        total = df["total"].iloc[0] or 0
        return {"intent": "stock_query", "answer": f"{wh} currently holds {int(total):,} total units across all SKUs."}

    return {
        "intent": "unrecognized",
        "answer": "I can answer questions about reorder needs, stock levels, and shrinkage patterns — "
                   "try e.g. 'which items in Chennai need reordering' or 'show shrinkage in Bengaluru'.",
    }
