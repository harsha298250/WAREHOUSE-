"""
ml/abc/classifier.py

Configurable ABC inventory classification.

Methodology:
    1. Calculate consumption value per item = total_qty × unit_value
    2. Sort items descending by consumption value
    3. Compute cumulative percentage contribution
    4. Assign class A / B / C based on configurable thresholds

Default thresholds:
    A: items whose cumulative value contribution <= threshold_a (default 80%)
    B: items from threshold_a to threshold_b (default 95%)
    C: remaining items

Thresholds are CONFIGURABLE — do not assume 80/20 or 75/25 are universally correct.

Works on any dataset:
    - WMS: item_id, stock_out qty, unit_cost
    - UCI Online Retail II: StockCode, Quantity, UnitPrice
    - MLZC: item_id, quantity, price_base
    - NeuroCipher: family, sales, 1.0

Results are persisted to the ABCClassification table with a source label.
"""
import logging
from datetime import datetime, UTC

import numpy as np
import pandas as pd

logger = logging.getLogger("warehouse.ml.abc")


class ABCClassifier:
    """
    Configurable ABC inventory classifier.

    Args:
        threshold_a: cumulative value % boundary for class A (default 80.0)
        threshold_b: cumulative value % boundary for class B (default 95.0)
                     Items beyond threshold_b are class C.
    """

    def __init__(self, threshold_a: float = 80.0, threshold_b: float = 95.0):
        if not (0 < threshold_a < threshold_b < 100):
            raise ValueError(
                f"Thresholds must satisfy 0 < threshold_a ({threshold_a}) "
                f"< threshold_b ({threshold_b}) < 100."
            )
        self.threshold_a = threshold_a
        self.threshold_b = threshold_b
        self._result_df: pd.DataFrame = None
        self._fitted: bool = False

    def fit(
        self,
        df: pd.DataFrame,
        item_col: str,
        qty_col: str,
        value_col: str,
        item_name_col: str = None,
    ) -> "ABCClassifier":
        """
        Fits the ABC classifier on the given DataFrame.

        Args:
            df: input data
            item_col: column name for item identifier
            qty_col: column name for quantity sold
            value_col: column name for unit value/price
            item_name_col: optional human-readable item name column

        Returns:
            self (for chaining)
        """
        if df.empty:
            logger.warning("ABCClassifier.fit() called with empty DataFrame — no classifications produced.")
            self._result_df = pd.DataFrame(columns=[
                "item_id", "item_name", "total_qty", "total_value",
                "pct_contribution", "cumulative_pct", "abc_class"
            ])
            self._fitted = True
            return self

        work = df[[item_col, qty_col, value_col]].copy()
        if item_name_col and item_name_col in df.columns:
            work["item_name"] = df[item_name_col].astype(str)
        else:
            work["item_name"] = work[item_col].astype(str)

        work[qty_col] = pd.to_numeric(work[qty_col], errors="coerce").fillna(0.0)
        work[value_col] = pd.to_numeric(work[value_col], errors="coerce").fillna(0.0)
        work["line_value"] = work[qty_col] * work[value_col]

        # Aggregate by item
        agg = work.groupby(item_col).agg(
            item_name=("item_name", "first"),
            total_qty=(qty_col, "sum"),
            total_value=("line_value", "sum"),
        ).reset_index().rename(columns={item_col: "item_id"})

        # Remove zero-value items (they cannot be meaningfully classified)
        agg = agg[agg["total_value"] > 0].copy()

        if agg.empty:
            logger.warning("All items have zero value — no ABC classifications produced.")
            self._result_df = agg
            self._fitted = True
            return self

        # Sort descending by value
        agg = agg.sort_values("total_value", ascending=False).reset_index(drop=True)

        total_value = agg["total_value"].sum()
        agg["pct_contribution"] = (agg["total_value"] / total_value * 100.0).round(4)
        agg["cumulative_pct"] = agg["pct_contribution"].cumsum().round(4)

        # Assign classes using configurable thresholds
        def _assign_class(cum_pct: float) -> str:
            if cum_pct <= self.threshold_a:
                return "A"
            elif cum_pct <= self.threshold_b:
                return "B"
            else:
                return "C"

        agg["abc_class"] = agg["cumulative_pct"].apply(_assign_class)

        self._result_df = agg
        self._fitted = True
        logger.info(
            f"ABC classification complete: "
            f"A={len(agg[agg['abc_class']=='A'])} items, "
            f"B={len(agg[agg['abc_class']=='B'])} items, "
            f"C={len(agg[agg['abc_class']=='C'])} items "
            f"(thresholds: A≤{self.threshold_a}%, B≤{self.threshold_b}%)"
        )
        return self

    def get_result_df(self) -> pd.DataFrame:
        """Returns the classified DataFrame."""
        if not self._fitted:
            raise RuntimeError("ABCClassifier must be fitted before calling get_result_df().")
        return self._result_df.copy()

    def get_summary(self) -> dict:
        """Returns a summary dict of A/B/C counts and values."""
        if not self._fitted:
            raise RuntimeError("ABCClassifier must be fitted before calling get_summary().")
        df = self._result_df
        result = {}
        for cls in ("A", "B", "C"):
            sub = df[df["abc_class"] == cls]
            result[cls] = {
                "count": len(sub),
                "total_value": round(float(sub["total_value"].sum()), 2),
                "total_qty": round(float(sub["total_qty"].sum()), 2),
                "pct_contribution": round(float(sub["pct_contribution"].sum()), 2),
            }
        result["thresholds"] = {"a": self.threshold_a, "b": self.threshold_b}
        result["total_items"] = len(df)
        return result

    def save_to_db(self, db, source: str, warehouse_id: str = None) -> int:
        """
        Persists classification results to the ABCClassification table.

        Args:
            db: SQLAlchemy Session
            source: label identifying the data source (e.g. 'wms', 'store_sales')
            warehouse_id: optional warehouse identifier

        Returns:
            number of rows saved
        """
        from backend.models import ABCClassification

        if not self._fitted:
            raise RuntimeError("ABCClassifier must be fitted before saving to DB.")

        df = self._result_df
        if df.empty:
            return 0

        run_at = datetime.now(UTC).replace(tzinfo=None)

        # Delete previous run for same source and warehouse to avoid unbounded table growth
        q = db.query(ABCClassification).filter(ABCClassification.source == source)
        if warehouse_id:
            q = q.filter(ABCClassification.warehouse_id == warehouse_id)
        else:
            q = q.filter(ABCClassification.warehouse_id.is_(None))
        q.delete()

        rows = []
        for _, row in df.iterrows():
            rows.append(ABCClassification(
                source=source,
                warehouse_id=warehouse_id,
                run_at=run_at,
                item_id=str(row["item_id"]),
                item_name=str(row.get("item_name", "")),
                total_qty=float(row["total_qty"]),
                total_value=float(row["total_value"]),
                pct_contribution=float(row["pct_contribution"]),
                cumulative_pct=float(row["cumulative_pct"]),
                abc_class=str(row["abc_class"]),
                threshold_a=self.threshold_a,
                threshold_b=self.threshold_b,
            ))

        db.bulk_save_objects(rows)
        db.commit()
        logger.info(f"Saved {len(rows)} ABC classifications to DB (source={source}, warehouse={warehouse_id}).")
        return len(rows)
