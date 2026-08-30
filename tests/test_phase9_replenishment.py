import pytest
from sqlalchemy.orm import Session
from backend.models import (
    Inventory, Item, ForecastRun, ForecastResult,
    ABCClassification, ReplenishmentRecommendation
)
from ml.replenishment.engine import (
    run_replenishment_engine, _determine_status, _get_abc_class, _get_forecast_demand
)


def test_replenishment_status_rules():
    """Verifies urgency and status logic mappings based on stock levels and ABC tiers."""
    # Urgent Reorder: stock <= 0, Class A
    u, s = _determine_status(current_stock=0, reorder_point=50, abc_class="A")
    assert u == "URGENT_REORDER"

    # Reorder Recommended: stock <= reorder_point
    u, s = _determine_status(current_stock=30, reorder_point=50, abc_class="B")
    assert u == "REORDER_RECOMMENDED"

    # Monitor: reorder_point < stock <= 1.5 * reorder_point
    u, s = _determine_status(current_stock=60, reorder_point=50, abc_class="C")
    assert u == "MONITOR"

    # No Action: stock > 1.5 * reorder_point
    u, s = _determine_status(current_stock=100, reorder_point=50, abc_class="B")
    assert u == "NO_ACTION"


def test_replenishment_engine_insufficient_data(db: Session):
    """Verifies engine flags items with missing data fields as INSUFFICIENT_DATA."""
    # Seed warehouse
    from backend.models import Warehouse
    wh = db.query(Warehouse).filter(Warehouse.id == "WH-BLR-01").first()
    if not wh:
        wh = Warehouse(id="WH-BLR-01", name="BLR Test Wh", location="BLR")
        db.add(wh)
        
    # Seed a dummy item without lead time
    item = Item(id="TEST-ITEM-99", name="TEST-ITEM-99", unit_cost=5.0, safety_stock=10)
    db.add(item)
    
    # Add WMS inventory record
    inv = Inventory(warehouse_id="WH-BLR-01", item_id="TEST-ITEM-99", on_hand=15, reserved=0, available=15, damaged=0)
    db.add(inv)
    db.commit()

    res = run_replenishment_engine(db, warehouse_id="WH-BLR-01")

    assert res["status"] == "success"
    # Find our item's recommendation
    recs = res["recommendations"]
    target = next(r for r in recs if r["item_id"] == "TEST-ITEM-99")
    assert target["urgency"] == "INSUFFICIENT_DATA"
    assert "Missing required data" in target["reason"]

    # Assert no live inventory modifications were made
    db.refresh(inv)
    assert inv.available == 15  # unmodified
