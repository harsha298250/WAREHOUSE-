import pytest
import pandas as pd
from ml.abc.classifier import ABCClassifier


def test_abc_classification_logic():
    """Verifies cumulative percentage contribution and class assignments with custom thresholds."""
    data = [
        {"item_id": "ITM-A", "qty": 10, "price": 100},  # Value = 1000 (80%)
        {"item_id": "ITM-B", "qty": 5, "price": 40},    # Value = 200 (16%)
        {"item_id": "ITM-C", "qty": 2, "price": 25},    # Value = 50 (4%)
    ]
    df = pd.DataFrame(data)

    # Thresholds: A <= 80%, B <= 96%, C > 96%
    clf = ABCClassifier(threshold_a=80.0, threshold_b=96.0)
    clf.fit(df, item_col="item_id", qty_col="qty", value_col="price")

    result = clf.get_result_df()
    assert len(result) == 3

    # ITM-A should be class A (80% <= 80%)
    row_a = result[result["item_id"] == "ITM-A"].iloc[0]
    assert row_a["abc_class"] == "A"
    assert row_a["cumulative_pct"] == 80.0

    # ITM-B should be class B (96% <= 96%)
    row_b = result[result["item_id"] == "ITM-B"].iloc[0]
    assert row_b["abc_class"] == "B"
    assert row_b["cumulative_pct"] == 96.0

    # ITM-C should be class C (100% > 96%)
    row_c = result[result["item_id"] == "ITM-C"].iloc[0]
    assert row_c["abc_class"] == "C"
    assert row_c["cumulative_pct"] == 100.0


def test_abc_empty_data_handling():
    """Verifies ABCClassifier gracefully returns empty results on empty inputs."""
    clf = ABCClassifier(threshold_a=80.0, threshold_b=95.0)
    clf.fit(pd.DataFrame(), item_col="item_id", qty_col="qty", value_col="price")

    result = clf.get_result_df()
    assert result.empty
    summary = clf.get_summary()
    assert summary["total_items"] == 0
    assert summary["A"]["count"] == 0
