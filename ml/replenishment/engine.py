"""
ml/replenishment/engine.py

Data-driven replenishment recommendation engine for Phase 5 Smart Replenishment.

This engine generates RECOMMENDATIONS ONLY — it does NOT modify
production inventory levels, StockMovement records, or any operational WMS data.

Data sources:
    - PostgreSQL WMS tables: Inventory, Item (current stock, lead_time_days, safety_stock)
    - Order & OrderItem tables: historical customer demand analysis
    - ForecastResult table: latest forecast demand per entity/family
    - ABCClassification table: latest ABC class per item
"""
import logging
from datetime import datetime, timedelta, UTC
from typing import Optional, Dict, Any

from sqlalchemy import func
from sqlalchemy.orm import Session

logger = logging.getLogger("warehouse.ml.replenishment")


def _get_abc_class(db: Session, item_id: str, warehouse_id: Optional[str] = None) -> Optional[str]:
    """Returns the latest ABC class for an item from the ABCClassification table."""
    from backend.models import ABCClassification
    q = db.query(ABCClassification).filter(ABCClassification.item_id == str(item_id))
    if warehouse_id:
        q = q.filter(ABCClassification.warehouse_id == str(warehouse_id))
    row = q.order_by(ABCClassification.run_at.desc()).first()
    return row.abc_class if row else None


def _get_forecast_demand(db: Session, family: str, lead_time_days: int) -> Optional[float]:
    """Returns total forecast demand over lead_time_days from latest ForecastRun for the family."""
    from backend.models import ForecastResult, ForecastRun

    run = (
        db.query(ForecastRun)
        .filter(ForecastRun.grain.contains(family))
        .order_by(ForecastRun.created_at.desc())
        .first()
    )
    if not run:
        return None

    results = (
        db.query(ForecastResult)
        .filter(ForecastResult.run_id == run.run_id, ForecastResult.entity == family)
        .order_by(ForecastResult.forecast_date.asc())
        .limit(lead_time_days)
        .all()
    )

    if not results:
        return None

    total = sum(r.predicted_demand for r in results)
    return round(float(total), 2)


def _get_historical_daily_demand(db: Session, item_id: str, warehouse_id: Optional[str] = None, days: int = 30) -> Optional[float]:
    """Calculates average daily demand from historical Order & OrderItem records over the last N days."""
    from backend.models import Order, OrderItem

    cutoff = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=days)
    q = db.query(func.sum(OrderItem.requested_qty)).join(Order, Order.id == OrderItem.order_id).filter(
        OrderItem.item_id == str(item_id),
        Order.created_at >= cutoff
    )
    if warehouse_id:
        q = q.filter(Order.warehouse_id == warehouse_id)

    total_qty = q.scalar()
    if total_qty is not None and total_qty > 0:
        return round(float(total_qty) / float(days), 2)
    return None


def _get_incoming_stock(db: Session, item_id: str, warehouse_id: str) -> float:
    """Returns total pending incoming quantity from active REPLENISH tasks."""
    from backend.models import Task
    tasks = db.query(Task).filter(
        Task.warehouse_id == warehouse_id,
        Task.product_id == str(item_id),
        Task.task_type == "REPLENISH",
        Task.status.in_(["QUEUED", "PRIORITIZED", "ASSIGNED", "IN_PROGRESS"])
    ).all()
    incoming = 0.0
    for t in tasks:
        req = float(t.requested_quantity or 0)
        comp = float(t.completed_quantity or 0)
        incoming += max(0.0, req - comp)
    return incoming


def _determine_status(
    current_stock: float,
    reorder_point: float,
    abc_class: Optional[str],
    days_of_cover: Optional[float] = None
) -> tuple:
    """Returns (urgency, status) string tuple."""
    if (current_stock <= 0 and abc_class == "A") or (days_of_cover is not None and days_of_cover < 1.0 and current_stock <= reorder_point):
        return "URGENT_REORDER", "CRITICAL"
    elif current_stock <= reorder_point:
        return "REORDER_RECOMMENDED", "REORDER_REQUIRED"
    elif current_stock <= reorder_point * 1.5:
        return "MONITOR", "WATCH"
    else:
        return "NO_ACTION", "HEALTHY"


def run_replenishment_engine(db: Session, warehouse_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Runs the replenishment recommendation engine across WMS inventory items.
    Updates existing recommendation records in-place (idempotently) without destroying status.
    """
    from backend.models import Inventory, Item, ReplenishmentRecommendation
    from backend.settings import get_settings

    settings_data = get_settings(db)
    global_low_stock_thresh = float(settings_data.get("low_stock_thresh", 10))
    global_reorder_point = float(settings_data.get("reorder_point", 20))
    global_safety_stock = float(settings_data.get("safety_stock", 5))

    inv_q = db.query(Inventory)
    if warehouse_id:
        inv_q = inv_q.filter(Inventory.warehouse_id == warehouse_id)
    inventory_records = inv_q.all()

    if not inventory_records:
        return {
            "status": "insufficient_data",
            "message": "No inventory records found in WMS.",
            "recommendations": [],
            "summary": {},
        }

    now = datetime.now(UTC).replace(tzinfo=None)
    recommendations = []
    counts = {"NO_ACTION": 0, "MONITOR": 0, "REORDER_RECOMMENDED": 0,
              "URGENT_REORDER": 0, "INSUFFICIENT_DATA": 0}

    for inv in inventory_records:
        item: Item = inv.item
        if not item:
            continue

        item_id = str(inv.item_id)
        item_name = item.name or item_id
        wh_id = str(inv.warehouse_id)
        current_stock = float(inv.available if inv.available is not None else (inv.quantity or 0.0))
        lead_time_days = item.lead_time_days or 7  # Fallback default lead time 7 days if missing
        safety_stock = float(item.safety_stock) if (item.safety_stock is not None and item.safety_stock > 0) else global_safety_stock
        item_reorder_thresh = float(item.reorder_threshold) if (hasattr(item, 'reorder_threshold') and item.reorder_threshold is not None and item.reorder_threshold > 0) else global_reorder_point

        # ABC class lookup
        abc_class = _get_abc_class(db, item_id, wh_id)

        # Incoming stock accounting from active REPLENISH tasks
        incoming_stock = _get_incoming_stock(db, item_id, wh_id)

        # Forecast demand lookup (with historical demand fallback)
        forecast_demand = None
        if item_name:
            for family_guess in [item_name.upper(), "GROCERY I"]:
                fd = _get_forecast_demand(db, family_guess, lead_time_days)
                if fd is not None:
                    forecast_demand = fd
                    break

        hist_daily_demand = _get_historical_daily_demand(db, item_id, wh_id, days=30)
        if forecast_demand is None and hist_daily_demand is not None:
            forecast_demand = round(hist_daily_demand * lead_time_days, 2)

        missing = []
        if forecast_demand is None and hist_daily_demand is None and not item_reorder_thresh:
            missing.append("demand_data")

        if missing:
            urgency = "INSUFFICIENT_DATA"
            status = "INSUFFICIENT_DATA"
            data_quality = "INSUFFICIENT_DATA"
            reason = "Insufficient historical demand or forecast data available. Cannot compute reorder point."
            reorder_point = None
            recommended_qty = 0.0
            days_of_cover = None
            stock_out_risk = "UNAVAILABLE"
        else:
            daily_demand = (forecast_demand / lead_time_days) if (forecast_demand and lead_time_days > 0) else (hist_daily_demand or 0.0)
            calculated_rp = round(float(forecast_demand) + safety_stock, 2) if forecast_demand is not None else 0.0
            reorder_point = max(calculated_rp, item_reorder_thresh)

            # Days of cover calculation
            if daily_demand > 0:
                days_of_cover = round(current_stock / daily_demand, 1)
            else:
                days_of_cover = None

            # Stock-out risk calculation
            if days_of_cover is not None:
                if days_of_cover < lead_time_days:
                    stock_out_risk = "HIGH"
                elif days_of_cover < lead_time_days * 1.5:
                    stock_out_risk = "MEDIUM"
                else:
                    stock_out_risk = "LOW"
            else:
                stock_out_risk = "LOW"

            urgency, status = _determine_status(current_stock, reorder_point, abc_class, days_of_cover)

            # Recommended quantity calculation accounting for incoming stock
            projected_avail = current_stock + incoming_stock
            if projected_avail <= reorder_point:
                target_stock = reorder_point + (daily_demand * 7.0 if daily_demand > 0 else 10.0)
                recommended_qty = max(0.0, round(target_stock - projected_avail, 2))
            else:
                recommended_qty = 0.0

            data_quality = "COMPLETE" if (abc_class and forecast_demand is not None) else "PARTIAL"

            # Explainable natural-language reason
            reason_parts = []
            if urgency == "URGENT_REORDER":
                reason_parts.append(f"CRITICAL: Stock ({current_stock:.0f}) is severely low or depleted.")
            elif urgency == "REORDER_RECOMMENDED":
                reason_parts.append(f"Stock ({current_stock:.0f}) ≤ Reorder Point ({reorder_point:.0f}).")
            elif urgency == "MONITOR":
                reason_parts.append(f"Stock ({current_stock:.0f}) approaching Reorder Point ({reorder_point:.0f}).")
            else:
                reason_parts.append(f"Stock ({current_stock:.0f}) is healthy above Reorder Point ({reorder_point:.0f}).")

            fd_text = f"{forecast_demand:.0f}" if forecast_demand is not None else "N/A"
            reason_parts.append(f"Lead-time demand: {fd_text} units ({lead_time_days} days).")
            if safety_stock > 0:
                reason_parts.append(f"Safety stock: {safety_stock:.0f}.")
            if incoming_stock > 0:
                reason_parts.append(f"Incoming stock: {incoming_stock:.0f}.")
            if days_of_cover is not None:
                reason_parts.append(f"Days of cover: {days_of_cover}d.")
            reason = " ".join(reason_parts)

        # Idempotent record lookup/update
        existing_rec = db.query(ReplenishmentRecommendation).filter(
            ReplenishmentRecommendation.item_id == item_id,
            ReplenishmentRecommendation.warehouse_id == wh_id
        ).first()

        if existing_rec:
            # Preserve human decision status if already approved/rejected/completed
            if existing_rec.status not in ("APPROVED", "REJECTED", "COMPLETED"):
                existing_rec.status = status
            existing_rec.current_stock = current_stock
            existing_rec.forecast_demand = forecast_demand
            existing_rec.lead_time_days = lead_time_days
            existing_rec.safety_stock = safety_stock
            existing_rec.reorder_point = reorder_point
            existing_rec.recommended_qty = recommended_qty
            existing_rec.abc_class = abc_class
            existing_rec.urgency = urgency
            existing_rec.reason = reason
            existing_rec.data_quality = data_quality
            existing_rec.created_at = now
            rr = existing_rec
        else:
            rr = ReplenishmentRecommendation(
                item_id=item_id,
                item_name=item_name,
                warehouse_id=wh_id,
                current_stock=current_stock,
                forecast_demand=forecast_demand,
                lead_time_days=lead_time_days,
                safety_stock=safety_stock,
                reorder_point=reorder_point,
                recommended_qty=recommended_qty,
                abc_class=abc_class,
                urgency=urgency,
                status=status,
                reason=reason,
                data_quality=data_quality,
                created_at=now,
            )
            db.add(rr)

        counts[urgency] = counts.get(urgency, 0) + 1
        recommendations.append({
            "id": rr.id,
            "item_id": item_id,
            "item_name": item_name,
            "warehouse_id": wh_id,
            "current_stock": current_stock,
            "forecast_demand": forecast_demand,
            "lead_time_days": lead_time_days,
            "safety_stock": safety_stock,
            "reorder_point": reorder_point,
            "recommended_qty": recommended_qty,
            "incoming_stock": incoming_stock,
            "days_of_cover": days_of_cover,
            "stock_out_risk": stock_out_risk,
            "abc_class": abc_class,
            "urgency": urgency,
            "status": rr.status,
            "reason": reason,
            "data_quality": data_quality,
        })

    db.commit()

    urgent = counts["URGENT_REORDER"]
    reorder = counts["REORDER_RECOMMENDED"]
    logger.info(
        f"Replenishment engine complete: {len(recommendations)} items processed. "
        f"Urgent: {urgent}, Reorder: {reorder}."
    )

    return {
        "status": "success",
        "items_processed": len(recommendations),
        "summary": counts,
        "data_provenance": {
            "current_stock": "ACTUAL — PostgreSQL WMS (inventories table)",
            "historical_demand": "ACTUAL — PostgreSQL WMS (orders & order_items tables)",
            "lead_time_days": "ACTUAL — PostgreSQL WMS (items table)",
            "safety_stock": "ACTUAL — PostgreSQL WMS (items table)",
            "forecast_demand": "FORECAST / HISTORICAL — TrendSeasonalityModel & WMS orders",
            "abc_class": "CALCULATED — ABCClassifier",
            "reorder_point": "CALCULATED — lead_time_demand + safety_stock",
            "incoming_stock": "ACTUAL — Active WMS REPLENISH tasks",
            "inventory_not_modified": "TRUE — recommendations only",
        },
        "recommendations": recommendations,
    }

