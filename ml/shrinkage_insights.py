"""
ml/shrinkage_insights.py — Root-cause clustering + cost-impact ranking based on real database records.
"""
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder
from sqlalchemy import text
from backend.database import engine


def _safe_mode(series, fallback="-"):
    if series is None or series.empty or series.dropna().empty:
        return fallback
    m = series.dropna().mode()
    return str(m.iloc[0]) if not m.empty else fallback


def build_shrinkage_insights(n_clusters: int = 4, warehouse_id: str = None):
    """
    Groups flagged anomalies into root-cause clusters using KMeans.
    Ranks them by their actual database-reconciled cost exposure.
    """
    try:
        if warehouse_id:
            flags = pd.read_sql(text("SELECT * FROM shrinkage_flags WHERE warehouse_id = :wh"), engine, params={"wh": warehouse_id})
            movements = pd.read_sql(text("""
                SELECT sm.date, sm.warehouse_id, sm.item_id, i.name as item_name, i.category, i.unit_cost
                FROM stock_movements sm JOIN items i ON sm.item_id = i.id
                WHERE sm.warehouse_id = :wh
            """), engine, params={"wh": warehouse_id})
        else:
            flags = pd.read_sql(text("SELECT * FROM shrinkage_flags"), engine)
            movements = pd.read_sql(text("""
                SELECT sm.date, sm.warehouse_id, sm.item_id, i.name as item_name, i.category, i.unit_cost
                FROM stock_movements sm JOIN items i ON sm.item_id = i.id
            """), engine)

        if flags.empty:
            return {"clusters": [], "top_by_cost": []}

        # Convert date to string before joining
        flags["date_str"] = pd.to_datetime(flags["date"]).dt.strftime("%Y-%m-%d")
        if not movements.empty:
            movements["date_str"] = pd.to_datetime(movements["date"]).dt.strftime("%Y-%m-%d")
            merged = flags.merge(movements, on=["date_str", "warehouse_id", "item_id"], how="left", suffixes=("", "_mov"))
        else:
            merged = flags.copy()
            merged["item_name"] = merged.get("item_id", "Unknown Item")
            merged["category"] = "General"
            merged["unit_cost"] = 0.0

        if "item_name" not in merged.columns or merged["item_name"].dropna().empty:
            merged["item_name"] = merged["item_id"].astype(str)
        if "category" not in merged.columns or merged["category"].dropna().empty:
            merged["category"] = "General"

        merged["date"] = pd.to_datetime(merged["date"])
        merged["weekday"] = merged["date"].dt.day_name()
        
        merged["est_units_lost"] = merged.get("discrepancy_quantity", pd.Series(0.0)).fillna(0.0).abs()
        merged["est_cost_lost"] = merged.get("estimated_exposure", pd.Series(0.0)).fillna(0.0).abs()

        # Clean NaN values in string columns before dict conversion
        merged["item_name"] = merged["item_name"].fillna("Unknown Item").astype(str)
        merged["category"] = merged["category"].fillna("General").astype(str)
        merged["likely_cause"] = merged.get("likely_cause", pd.Series("Unexplained Discrepancy")).fillna("Unexplained Discrepancy").astype(str)
        merged["warehouse_id"] = merged.get("warehouse_id", pd.Series(warehouse_id or "WH-GENERAL")).fillna(warehouse_id or "WH-GENERAL").astype(str)

        cols_top = [c for c in ["date", "warehouse_id", "item_id", "item_name", "category", "likely_cause", "est_cost_lost"] if c in merged.columns]
        
        top_df = (
            merged.sort_values("est_cost_lost", ascending=False)
            .head(15)[cols_top]
            .assign(date=lambda d: pd.to_datetime(d["date"]).dt.strftime("%Y-%m-%d"))
        )
        
        # Convert NaN values to Python standard types to prevent JSON NaN serialization crash
        top_by_cost = []
        for row in top_df.to_dict(orient="records"):
            clean_row = {}
            for k, v in row.items():
                if pd.isna(v):
                    clean_row[k] = 0.0 if isinstance(v, (int, float)) else "-"
                else:
                    clean_row[k] = v
            top_by_cost.append(clean_row)

        le_wh, le_cat, le_wd = LabelEncoder(), LabelEncoder(), LabelEncoder()
        wh_col = merged["warehouse_id"]
        cat_col = merged["category"]
        wd_col = merged["weekday"].fillna("Monday").astype(str)
        dev_col = merged.get("deviation_score", pd.Series(1.0)).fillna(1.0).abs()

        feat = pd.DataFrame({
            "warehouse": le_wh.fit_transform(wh_col),
            "category": le_cat.fit_transform(cat_col),
            "weekday": le_wd.fit_transform(wd_col),
            "deviation": dev_col,
        })
        
        k = min(n_clusters, max(1, len(feat) // 3)) or 1
        if len(feat) >= k and k > 1:
            model = KMeans(n_clusters=k, random_state=42, n_init=10)
            merged["cluster"] = model.fit_predict(feat)
        else:
            merged["cluster"] = 0

        clusters = []
        for c, group in merged.groupby("cluster"):
            top_wh = _safe_mode(group.get("warehouse_id"), warehouse_id or "-")
            top_cat = _safe_mode(group.get("category"), "General")
            top_wd = _safe_mode(group.get("weekday"), "Monday")
            total_cost = round(float(group.get("est_cost_lost", pd.Series([0])).sum()), 2)
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
    except Exception as e:
        import logging
        logging.getLogger("warehouse.ml").error("Error in build_shrinkage_insights: %s", e)
        return {"clusters": [], "top_by_cost": [], "error": str(e)}

