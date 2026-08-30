"""
ml/shrinkage_insights.py — Root-cause clustering + cost-impact ranking based on real database records.
"""
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder
from sqlalchemy import text
from backend.database import engine


def build_shrinkage_insights(n_clusters: int = 4):
    """
    Groups flagged anomalies into root-cause clusters using KMeans.
    Ranks them by their actual database-reconciled cost exposure.
    """
    flags = pd.read_sql(text("SELECT * FROM shrinkage_flags"), engine)
    movements = pd.read_sql(text("""
        SELECT sm.date, sm.warehouse_id, sm.item_id, i.category, i.unit_cost
        FROM stock_movements sm JOIN items i ON sm.item_id = i.id
    """), engine)

    if flags.empty:
        return {"clusters": [], "top_by_cost": []}

    merged = flags.merge(movements, on=["date", "warehouse_id", "item_id"], how="left")
    merged["date"] = pd.to_datetime(merged["date"])
    merged["weekday"] = merged["date"].dt.day_name()
    
    # Use real database-reconciled quantities and cost exposures
    # discrepancy_quantity is already absolute/reconciled, and estimated_exposure is actual cost at risk
    merged["est_units_lost"] = merged["discrepancy_quantity"].fillna(0.0).abs()
    merged["est_cost_lost"] = merged["estimated_exposure"].fillna(0.0)

    top_by_cost = (
        merged.sort_values("est_cost_lost", ascending=False)
        .head(15)[["date", "warehouse_id", "item_id", "item_name", "category", "likely_cause", "est_cost_lost"]]
        .assign(date=lambda d: d["date"].dt.strftime("%Y-%m-%d"))
        .to_dict(orient="records")
    )

    le_wh, le_cat, le_wd = LabelEncoder(), LabelEncoder(), LabelEncoder()
    feat = pd.DataFrame({
        "warehouse": le_wh.fit_transform(merged["warehouse_id"]),
        "category": le_cat.fit_transform(merged["category"].fillna("Unknown")),
        "weekday": le_wd.fit_transform(merged["weekday"]),
        "deviation": merged["deviation_score"].abs(),
    })
    
    k = min(n_clusters, max(1, len(feat) // 3)) or 1
    if len(feat) >= k and k > 1:
        model = KMeans(n_clusters=k, random_state=42, n_init=10)
        merged["cluster"] = model.fit_predict(feat)
    else:
        merged["cluster"] = 0

    clusters = []
    for c, group in merged.groupby("cluster"):
        top_wh = group["warehouse_id"].mode().iloc[0] if not group.empty else "-"
        top_cat = group["category"].mode().iloc[0] if group["category"].notna().any() else "-"
        top_wd = group["weekday"].mode().iloc[0] if not group.empty else "-"
        total_cost = round(group["est_cost_lost"].sum(), 2)
        clusters.append({
            "cluster_id": int(c), "event_count": int(len(group)),
            "dominant_warehouse": top_wh, "dominant_category": top_cat, "dominant_weekday": top_wd,
            "total_estimated_cost_inr": total_cost,
            "pattern_summary": (
                f"{len(group)} events concentrated in {top_cat} at {top_wh}, "
                f"most common on {top_wd}s — estimated ₹{total_cost:,.0f} at risk."
            ),
        })
    clusters.sort(key=lambda c: c["total_estimated_cost_inr"], reverse=True)
    return {"clusters": clusters, "top_by_cost": top_by_cost}
