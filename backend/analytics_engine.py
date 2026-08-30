import logging
import statistics
import secrets
from datetime import datetime, date, timedelta, UTC
from typing import Dict, Any, List, Optional
from sqlalchemy import text, func, and_
from sqlalchemy.orm import Session

from backend.models import (
    Order, OrderItem, OrderEvent, PackingRecord, Shipment,
    Inventory, Item, StockMovement, ShrinkageFlag,
    Task, TaskEvent, Robot, RobotTelemetryEvent, RobotRoute,
    DigitalTwinSimulation, SimulationEvent, SimulationSnapshot,
    AIRecommendation, BackupRecord, Notification
)

logger = logging.getLogger("warehouse.analytics")

def get_date_range(period: str, start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Calculates start and end datetime bounds based on the period filter."""
    now = datetime.now(UTC).replace(tzinfo=None)
    
    if period == "today":
        start = datetime(now.year, now.month, now.day, 0, 0, 0)
        end = datetime(now.year, now.month, now.day, 23, 59, 59)
    elif period == "7d":
        start = now - timedelta(days=7)
        end = now
    elif period == "30d":
        start = now - timedelta(days=30)
        end = now
    elif period == "90d":
        start = now - timedelta(days=90)
        end = now
    elif period == "custom" and start_date and end_date:
        try:
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
        except ValueError:
            start = now - timedelta(days=30)
            end = now
    else:
        # Default fallback to 30d
        start = now - timedelta(days=30)
        end = now
        
    return start, end


def calculate_abc_distribution(
    db: Session,
    warehouse_id: Optional[str],
    threshold_a: float = 75.0,
    threshold_b: float = 95.0,
) -> Dict[str, Any]:
    """
    Performs ABC inventory analysis based on consumption value (stock_out * unit_cost).
    Classifies SKUs into A (top threshold_a%), B (next threshold_b%), and C (remaining).
    """
    query_items = db.query(Item).all()
    consumption = []
    total_val = 0.0

    for item in query_items:
        # Sum historical stock_out movements
        move_query = db.query(func.sum(StockMovement.stock_out))
        if warehouse_id:
            move_query = move_query.filter(StockMovement.warehouse_id == warehouse_id)
        move_query = move_query.filter(StockMovement.item_id == item.id)
        qty = float(move_query.scalar() or 0.0)
        
        val = qty * float(item.unit_cost or 0.0)
        consumption.append({
            "item_id": item.id,
            "item_name": item.name,
            "qty": qty,
            "value": val,
            "unit_cost": item.unit_cost
        })
        total_val += val

    if total_val == 0.0:
        # Fallback using unit_cost * 10
        for c in consumption:
            c["value"] = float(c["unit_cost"] or 0.0) * 10.0
            total_val += c["value"]

    consumption.sort(key=lambda x: x["value"], reverse=True)

    cumulative_val = 0.0
    a_count, b_count, c_count = 0, 0, 0
    a_val, b_val, c_val = 0.0, 0.0, 0.0
    a_qty, b_qty, c_qty = 0.0, 0.0, 0.0
    
    item_classifications = {}
    
    for c in consumption:
        cumulative_val += c["value"]
        cum_pct = (cumulative_val / total_val * 100.0) if total_val > 0 else 0.0

        if cum_pct <= threshold_a:
            classification = "A"
            a_count += 1
            a_val += c["value"]
            a_qty += c["qty"]
        elif cum_pct <= threshold_b:
            classification = "B"
            b_count += 1
            b_val += c["value"]
            b_qty += c["qty"]
        else:
            classification = "C"
            c_count += 1
            c_val += c["value"]
            c_qty += c["qty"]
            
        item_classifications[c["item_id"]] = classification

    return {
        "summary": {
            "A": {"count": a_count, "value": round(a_val, 2), "qty": a_qty},
            "B": {"count": b_count, "value": round(b_val, 2), "qty": b_qty},
            "C": {"count": c_count, "value": round(c_val, 2), "qty": c_qty},
            "thresholds": {"a": threshold_a, "b": threshold_b}
        },
        "item_classifications": item_classifications
    }


def compute_order_analytics(db: Session, warehouse_id: Optional[str], start: datetime, end: datetime) -> Dict[str, Any]:
    """Computes order cycle times, completion rate, SLA targets, and counts."""
    order_q = db.query(Order).filter(Order.created_at.between(start, end))
    if warehouse_id:
        order_q = order_q.filter(Order.warehouse_id == warehouse_id)
        
    orders = order_q.all()
    total_orders = len(orders)
    
    completed_orders = [o for o in orders if o.status in ("COMPLETED", "DELIVERED", "SHIPPED")]
    cancelled_orders = [o for o in orders if o.status == "CANCELLED"]
    exception_orders = [o for o in orders if o.status in ("FAILED", "RETURNED", "EXCEPTIONAL")]
    
    # Completion Rate = Completed / (Total - Cancelled)
    denominator = total_orders - len(cancelled_orders)
    completion_rate = (len(completed_orders) / denominator * 100.0) if denominator > 0 else 100.0
    
    cycle_times = []
    pick_durations = []
    pack_durations = []
    ship_durations = []
    on_time_count = 0
    sla_hours_threshold = 48.0 # Standard WMS cycle time expectation SLA

    for o in completed_orders:
        events = db.query(OrderEvent).filter(OrderEvent.order_id == o.id).order_by(OrderEvent.timestamp).all()
        if not events:
            # Fallback to updated_at - created_at
            dur = (o.updated_at - o.created_at).total_seconds() / 3600.0
            cycle_times.append(dur)
            if dur <= sla_hours_threshold:
                on_time_count += 1
            continue
            
        start_time = o.created_at
        end_time = events[-1].timestamp
        
        order_cycle = (end_time - start_time).total_seconds() / 3600.0
        cycle_times.append(order_cycle)
        if order_cycle <= sla_hours_threshold:
            on_time_count += 1
            
        # Try to find specific pick/pack/ship task durations for this order
        tasks = db.query(Task).filter(Task.order_id == o.id, Task.status == "COMPLETED").all()
        for t in tasks:
            if t.started_at and t.completed_at:
                dur_mins = (t.completed_at - t.started_at).total_seconds() / 60.0
                if t.task_type == "PICK":
                    pick_durations.append(dur_mins)
                elif t.task_type == "PACK":
                    pack_durations.append(dur_mins)
                elif t.task_type == "SHIP":
                    ship_durations.append(dur_mins)

    avg_cycle = statistics.mean(cycle_times) if cycle_times else None
    avg_pick = statistics.mean(pick_durations) if pick_durations else None
    avg_pack = statistics.mean(pack_durations) if pack_durations else None
    avg_ship = statistics.mean(ship_durations) if ship_durations else None
    on_time_rate = (on_time_count / len(completed_orders) * 100.0) if completed_orders else 100.0
    cancellation_rate = (len(cancelled_orders) / total_orders * 100.0) if total_orders > 0 else 0.0
    exception_rate = (len(exception_orders) / total_orders * 100.0) if total_orders > 0 else 0.0

    return {
        "throughput": {"value": len(completed_orders), "unit": "orders", "data_quality": "DATABASE_SYNCHRONIZED"},
        "completion_rate": {"value": round(completion_rate, 1), "unit": "percent", "data_quality": "DATABASE_SYNCHRONIZED"},
        "avg_cycle_time_hours": {"value": round(avg_cycle, 1) if avg_cycle is not None else None, "unit": "hours", "data_quality": "DATABASE_SYNCHRONIZED" if cycle_times else "INSUFFICIENT DATA"},
        "avg_pick_time_minutes": {"value": round(avg_pick, 1) if avg_pick is not None else None, "unit": "minutes", "data_quality": "DATABASE_SYNCHRONIZED" if pick_durations else "INSUFFICIENT DATA"},
        "avg_pack_time_minutes": {"value": round(avg_pack, 1) if avg_pack is not None else None, "unit": "minutes", "data_quality": "DATABASE_SYNCHRONIZED" if pack_durations else "INSUFFICIENT DATA"},
        "avg_ship_time_minutes": {"value": round(avg_ship, 1) if avg_ship is not None else None, "unit": "minutes", "data_quality": "DATABASE_SYNCHRONIZED" if ship_durations else "INSUFFICIENT DATA"},
        "on_time_rate": {"value": round(on_time_rate, 1), "unit": "percent", "data_quality": "DATABASE_SYNCHRONIZED"},
        "cancellation_rate": {"value": round(cancellation_rate, 1), "unit": "percent", "data_quality": "DATABASE_SYNCHRONIZED"},
        "exception_rate": {"value": round(exception_rate, 1), "unit": "percent", "data_quality": "DATABASE_SYNCHRONIZED"}
    }


def compute_inventory_analytics(db: Session, warehouse_id: Optional[str], start: datetime, end: datetime) -> Dict[str, Any]:
    """Computes inventory stock numbers, turnover metrics, ABC values and capacity utilization."""
    inv_query = db.query(Inventory)
    if warehouse_id:
        inv_query = inv_query.filter(Inventory.warehouse_id == warehouse_id)
        
    records = inv_query.all()
    on_hand = sum(r.on_hand for r in records)
    reserved = sum(r.reserved for r in records)
    available = sum(r.available for r in records)
    damaged = sum(r.damaged for r in records)
    
    # Calculate stockout rates and low stock item count
    stockout_count = 0
    low_stock_count = 0
    overstock_count = 0
    total_value = 0.0
    damaged_value = 0.0
    overstock_value = 0.0
    cost_data_available = True
    missing_cost_items = 0
    
    for r in records:
        if r.available <= 0:
            stockout_count += 1
            
        item = r.item
        if item:
            cost = item.unit_cost or 0.0
            if cost <= 0:
                missing_cost_items += 1
                
            total_value += r.on_hand * cost
            damaged_value += r.damaged * cost
            
            if r.available < (item.reorder_threshold or 20):
                low_stock_count += 1
                
            # Overstock is defined as having available stock > safety_stock * 3
            overstock_limit = (item.safety_stock or 10) * 3
            if r.available > overstock_limit:
                overstock_count += 1
                overstock_value += (r.available - overstock_limit) * cost

    if (missing_cost_items == len(records) and len(records) > 0) or len(records) == 0:
        cost_data_available = False

    stockout_rate = (stockout_count / len(records) * 100.0) if records else 0.0
    
    # Inventory Turnover Ratio = Total stock_out quantity in period / average inventory in period
    move_query = db.query(func.sum(StockMovement.stock_out)).filter(StockMovement.date.between(start.date(), end.date()))
    if warehouse_id:
        move_query = move_query.filter(StockMovement.warehouse_id == warehouse_id)
    total_out_qty = float(move_query.scalar() or 0.0)
    
    avg_inventory_qty = on_hand if on_hand > 0 else 1.0
    inventory_turnover = total_out_qty / avg_inventory_qty
    
    # Total moves volume
    move_volume_query = db.query(
        func.sum(StockMovement.stock_in),
        func.sum(StockMovement.stock_out)
    ).filter(StockMovement.date.between(start.date(), end.date()))
    if warehouse_id:
        move_volume_query = move_volume_query.filter(StockMovement.warehouse_id == warehouse_id)
    in_sum, out_sum = move_volume_query.first()
    receiving_volume = int(in_sum or 0)
    shipping_volume = int(out_sum or 0)
    
    abc_data = calculate_abc_distribution(db, warehouse_id)

    return {
        "on_hand": {"value": on_hand, "unit": "units", "data_quality": "DATABASE_SYNCHRONIZED"},
        "reserved": {"value": reserved, "unit": "units", "data_quality": "DATABASE_SYNCHRONIZED"},
        "available": {"value": available, "unit": "units", "data_quality": "DATABASE_SYNCHRONIZED"},
        "damaged": {"value": damaged, "unit": "units", "data_quality": "DATABASE_SYNCHRONIZED"},
        "stockout_rate": {"value": round(stockout_rate, 1), "unit": "percent", "data_quality": "DATABASE_SYNCHRONIZED"},
        "low_stock_count": {"value": low_stock_count, "unit": "SKUs", "data_quality": "DATABASE_SYNCHRONIZED"},
        "overstock_count": {"value": overstock_count, "unit": "SKUs", "data_quality": "DATABASE_SYNCHRONIZED"},
        "inventory_value": {"value": round(total_value, 2) if cost_data_available else None, "unit": "INR", "data_quality": "DATABASE_SYNCHRONIZED" if cost_data_available else "NOT AVAILABLE"},
        "damaged_value": {"value": round(damaged_value, 2) if cost_data_available else None, "unit": "INR", "data_quality": "DATABASE_SYNCHRONIZED" if cost_data_available else "NOT AVAILABLE"},
        "overstock_value": {"value": round(overstock_value, 2) if cost_data_available else None, "unit": "INR", "data_quality": "DATABASE_SYNCHRONIZED" if cost_data_available else "NOT AVAILABLE"},
        "inventory_turnover": {"value": round(inventory_turnover, 2), "unit": "ratio", "data_quality": "DATABASE_SYNCHRONIZED"},
        "receiving_volume": {"value": receiving_volume, "unit": "units", "data_quality": "DATABASE_SYNCHRONIZED"},
        "shipping_volume": {"value": shipping_volume, "unit": "units", "data_quality": "DATABASE_SYNCHRONIZED"},
        "abc_distribution": abc_data["summary"]
    }


def compute_task_analytics(db: Session, warehouse_id: Optional[str], start: datetime, end: datetime) -> Dict[str, Any]:
    """Computes task KPIs, average durations, retry metrics, priority weight distributions."""
    task_q = db.query(Task).filter(Task.created_at.between(start, end))
    if warehouse_id:
        task_q = task_q.filter(Task.warehouse_id == warehouse_id)
        
    tasks = task_q.all()
    total_tasks = len(tasks)
    
    completed = [t for t in tasks if t.status == "COMPLETED"]
    failed = [t for t in tasks if t.status == "FAILED"]
    pending = [t for t in tasks if t.status in ("QUEUED", "ASSIGNED", "IN_PROGRESS")]
    cancelled = [t for t in tasks if t.status == "CANCELLED"]
    
    comp_denom = len(completed) + len(failed)
    completion_rate = (len(completed) / comp_denom * 100.0) if comp_denom > 0 else 100.0
    failure_rate = (len(failed) / comp_denom * 100.0) if comp_denom > 0 else 0.0
    
    # Task timings
    durations = []
    queue_times = []
    overdue_high_priority = 0
    
    for t in tasks:
        if t.started_at and t.completed_at:
            durations.append((t.completed_at - t.started_at).total_seconds() / 60.0)
        if t.started_at and t.created_at:
            queue_times.append((t.started_at - t.created_at).total_seconds() / 60.0)
            
        if t.priority in ("HIGH", "CRITICAL") and t.status != "COMPLETED":
            if t.due_at and t.due_at < datetime.now(UTC).replace(tzinfo=None):
                overdue_high_priority += 1

    avg_duration = statistics.mean(durations) if durations else None
    avg_queue = statistics.mean(queue_times) if queue_times else None
    
    # Breakdown by type
    by_type = {}
    for t in tasks:
        by_type[t.task_type] = by_type.get(t.task_type, 0) + 1
        
    # Breakdown by priority
    by_priority = {}
    for t in tasks:
        by_priority[t.priority] = by_priority.get(t.priority, 0) + 1
        
    # Priority performance
    durations_by_prio = {}
    for p in ("LOW", "MEDIUM", "HIGH", "CRITICAL"):
        p_durs = [
            (t.completed_at - t.started_at).total_seconds() / 60.0
            for t in tasks if t.priority == p and t.started_at and t.completed_at
        ]
        durations_by_prio[p] = round(statistics.mean(p_durs), 1) if p_durs else None

    return {
        "tasks_created": {"value": total_tasks, "unit": "tasks", "data_quality": "DATABASE_SYNCHRONIZED"},
        "tasks_completed": {"value": len(completed), "unit": "tasks", "data_quality": "DATABASE_SYNCHRONIZED"},
        "tasks_pending": {"value": len(pending), "unit": "tasks", "data_quality": "DATABASE_SYNCHRONIZED"},
        "tasks_failed": {"value": len(failed), "unit": "tasks", "data_quality": "DATABASE_SYNCHRONIZED"},
        "tasks_cancelled": {"value": len(cancelled), "unit": "tasks", "data_quality": "DATABASE_SYNCHRONIZED"},
        "completion_rate": {"value": round(completion_rate, 1), "unit": "percent", "data_quality": "DATABASE_SYNCHRONIZED"},
        "failure_rate": {"value": round(failure_rate, 1), "unit": "percent", "data_quality": "DATABASE_SYNCHRONIZED"},
        "avg_duration_minutes": {"value": round(avg_duration, 1) if avg_duration is not None else None, "unit": "minutes", "data_quality": "DATABASE_SYNCHRONIZED" if durations else "INSUFFICIENT DATA"},
        "avg_queue_time_minutes": {"value": round(avg_queue, 1) if avg_queue is not None else None, "unit": "minutes", "data_quality": "DATABASE_SYNCHRONIZED" if queue_times else "INSUFFICIENT DATA"},
        "overdue_high_priority": {"value": overdue_high_priority, "unit": "tasks", "data_quality": "DATABASE_SYNCHRONIZED"},
        "by_type": by_type,
        "by_priority": by_priority,
        "avg_duration_by_priority": durations_by_prio
    }


def compute_robot_analytics(db: Session, warehouse_id: Optional[str], start: datetime, end: datetime) -> Dict[str, Any]:
    """Computes robot fleet utilization, active/charging times, battery consumption and distance metrics."""
    robots_q = db.query(Robot)
    if warehouse_id:
        robots_q = robots_q.filter(Robot.warehouse_id == warehouse_id)
        
    robots = robots_q.all()
    
    if not robots:
        return {
            "fleet_size": {"value": 0, "unit": "robots", "data_quality": "DATABASE_SYNCHRONIZED"},
            "avg_utilization": {"value": None, "unit": "percent", "data_quality": "INSUFFICIENT DATA"},
            "comparison": []
        }
        
    utilization_list = [r.utilization_percent for r in robots]
    avg_utilization = statistics.mean(utilization_list) if utilization_list else 0.0
    
    # Active, Idle, Charging breakdown based on telemetry events
    # We fetch positions and telemetry logs in the period
    comparison = []
    for r in robots:
        t_events = db.query(RobotTelemetryEvent).filter(
            RobotTelemetryEvent.robot_id == r.id,
            RobotTelemetryEvent.timestamp.between(start, end)
        ).all()
        
        # Telemetry-based counts
        charging_events = sum(1 for e in t_events if e.event_type == "CHARGING_STARTED")
        battery_drops = [e.battery for e in t_events if e.event_type == "BATTERY_UPDATED"]
        avg_battery = statistics.mean(battery_drops) if battery_drops else r.battery_level
        
        comparison.append({
            "robot_code": r.robot_code,
            "name": r.name,
            "status": r.status,
            "utilization_percent": r.utilization_percent,
            "tasks_completed": r.total_tasks_completed,
            "distance_travelled": round(r.total_distance, 1),
            "failures": r.failure_count,
            "avg_battery": round(avg_battery, 1)
        })

    return {
        "fleet_size": {"value": len(robots), "unit": "robots", "data_quality": "DATABASE_SYNCHRONIZED"},
        "avg_utilization": {"value": round(avg_utilization, 1), "unit": "percent", "data_quality": "DATABASE_SYNCHRONIZED"},
        "comparison": comparison
    }


def compute_routing_analytics(db: Session, warehouse_id: Optional[str], start: datetime, end: datetime) -> Dict[str, Any]:
    """Computes routing computation metrics, replanning frequency, and spatial congestion alerts."""
    routes_q = db.query(RobotRoute).filter(RobotRoute.created_at.between(start, end))
    if warehouse_id:
        routes_q = routes_q.filter(RobotRoute.warehouse_id == warehouse_id)
        
    routes = routes_q.all()
    route_count = len(routes)
    
    avg_distance = statistics.mean([r.distance for r in routes]) if routes else None
    avg_cost = statistics.mean([r.cost for r in routes]) if routes else None
    replanned_count = sum(1 for r in routes if r.status == "REPLANNED")
    
    # Calculate congestion events from SimulationEvents (contains warnings of obstacles or collision avoidances)
    sim_events_q = db.query(SimulationEvent).filter(SimulationEvent.real_timestamp.between(start, end))
    if warehouse_id:
        sim_events_q = sim_events_q.filter(SimulationEvent.warehouse_id == warehouse_id)
        
    events = sim_events_q.all()
    collision_avoided = sum(1 for e in events if e.event_type == "COLLISION_AVOIDED")
    robot_waiting = sum(1 for e in events if e.event_type == "ROBOT_WAITING")
    obstacle_count = sum(1 for e in events if e.event_type == "OBSTACLE_CREATED")

    return {
        "route_count": {"value": route_count, "unit": "routes", "data_quality": "DATABASE_SYNCHRONIZED"},
        "avg_route_length": {"value": round(avg_distance, 1) if avg_distance is not None else None, "unit": "cells", "data_quality": "DATABASE_SYNCHRONIZED" if routes else "INSUFFICIENT DATA"},
        "avg_route_cost": {"value": round(avg_cost, 1) if avg_cost is not None else None, "unit": "cost_weight", "data_quality": "DATABASE_SYNCHRONIZED" if routes else "INSUFFICIENT DATA"},
        "replanning_count": {"value": replanned_count, "unit": "replans", "data_quality": "DATABASE_SYNCHRONIZED"},
        "collision_events": {"value": collision_avoided, "unit": "events", "data_quality": "DATABASE_SYNCHRONIZED"},
        "robot_waiting_events": {"value": robot_waiting, "unit": "events", "data_quality": "DATABASE_SYNCHRONIZED"},
        "obstacles_logged": {"value": obstacle_count, "unit": "events", "data_quality": "DATABASE_SYNCHRONIZED"}
    }


def compute_forecasting_analytics(db: Session, warehouse_id: Optional[str]) -> Dict[str, Any]:
    """Retrieves forecast validation metrics (WAPE, MAE) and baseline reliability comparisons."""
    # We poll forecasts calculated in database or fall back to naive averages
    from ml.forecast import forecast_item
    from backend.models import Inventory
    
    # Select sample items to evaluate holdout validation metrics
    inv_sample = db.query(Inventory)
    if warehouse_id:
        inv_sample = inv_sample.filter(Inventory.warehouse_id == warehouse_id)
    samples = inv_sample.limit(10).all()
    
    wape_scores = []
    rmse_scores = []
    items_evaluated = []
    
    for s in samples:
        try:
            fc = forecast_item(s.warehouse_id, s.item_id, horizon=14, db=db)
            if fc and fc.get("status") == "success":
                val_metrics = fc.get("backtest_validation", {})
                wape = val_metrics.get("wape_pct")
                rmse = val_metrics.get("rmse")
                if wape is not None:
                    wape_scores.append(float(wape))
                    rmse_scores.append(float(rmse or 0.0))
                    items_evaluated.append({
                        "item_id": s.item_id,
                        "item_name": s.item.name,
                        "wape": round(float(wape), 1),
                        "reliability": "HIGH" if float(wape) < 15.0 else ("MODERATE" if float(wape) < 30.0 else "LOW")
                    })
        except Exception:
            pass

    median_wape = statistics.median(wape_scores) if wape_scores else None
    avg_rmse = statistics.mean(rmse_scores) if rmse_scores else None

    return {
        "median_wape": {"value": round(median_wape, 1) if median_wape is not None else None, "unit": "percent", "data_quality": "DATABASE_SYNCHRONIZED" if wape_scores else "INSUFFICIENT DATA"},
        "avg_rmse": {"value": round(avg_rmse, 2) if avg_rmse is not None else None, "unit": "rmse", "data_quality": "DATABASE_SYNCHRONIZED" if rmse_scores else "INSUFFICIENT DATA"},
        "items_evaluated": items_evaluated
    }


def compute_anomaly_analytics(db: Session, warehouse_id: Optional[str], start: datetime, end: datetime) -> Dict[str, Any]:
    """Retrieves detected potential inventory discrepancy counts and shrinkage exposure totals."""
    anom_q = db.query(ShrinkageFlag).filter(ShrinkageFlag.date.between(start.date(), end.date()))
    if warehouse_id:
        anom_q = anom_q.filter(ShrinkageFlag.warehouse_id == warehouse_id)
        
    anomalies = anom_q.all()
    exposure = sum(float(a.estimated_exposure or 0.0) for a in anomalies)
    
    # Status levels (mapped by recommendation approval/rejection notes, or default UNDER_REVIEW)
    by_severity = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for a in anomalies:
        sev = a.severity or "MEDIUM"
        by_severity[sev] = by_severity.get(sev, 0) + 1

    return {
        "potential_anomalies_count": {"value": len(anomalies), "unit": "discrepancies", "data_quality": "DATABASE_SYNCHRONIZED"},
        "estimated_exposure": {"value": round(exposure, 2), "unit": "INR", "data_quality": "DATABASE_SYNCHRONIZED"},
        "by_severity": by_severity,
        "raw_anomalies": [
            {
                "id": a.id,
                "date": a.date.isoformat(),
                "item_id": a.item_id,
                "item_name": a.item_name,
                "discrepancy": a.discrepancy_quantity,
                "exposure": a.estimated_exposure,
                "severity": a.severity,
                "cause": a.likely_cause,
                "explanation": a.explanation
            }
            for a in anomalies[:20]
        ]
    }


def compute_ai_analytics(db: Session, warehouse_id: Optional[str], start: datetime, end: datetime) -> Dict[str, Any]:
    """Computes AI recommendation volumes, categorization and manager approval metrics."""
    recs_q = db.query(AIRecommendation).filter(AIRecommendation.timestamp.between(start, end))
    if warehouse_id:
        recs_q = recs_q.filter(AIRecommendation.warehouse_id == warehouse_id)
        
    recs = recs_q.all()
    total = len(recs)
    
    approved = sum(1 for r in recs if r.status == "APPROVED")
    rejected = sum(1 for r in recs if r.status == "REJECTED")
    pending = sum(1 for r in recs if r.status == "NEW")
    
    approval_rate = (approved / (approved + rejected) * 100.0) if (approved + rejected) > 0 else 100.0
    
    # Types distribution
    by_type = {}
    for r in recs:
        rtype = r.recommendation_type or "REPLENISHMENT"
        by_type[rtype] = by_type.get(rtype, 0) + 1

    return {
        "recommendations_generated": {"value": total, "unit": "recommendations", "data_quality": "DATABASE_SYNCHRONIZED"},
        "approved": {"value": approved, "unit": "recommendations", "data_quality": "DATABASE_SYNCHRONIZED"},
        "rejected": {"value": rejected, "unit": "recommendations", "data_quality": "DATABASE_SYNCHRONIZED"},
        "pending": {"value": pending, "unit": "recommendations", "data_quality": "DATABASE_SYNCHRONIZED"},
        "approval_rate": {"value": round(approval_rate, 1), "unit": "percent", "data_quality": "DATABASE_SYNCHRONIZED"},
        "by_type": by_type
    }


def compute_simulation_analytics(db: Session, warehouse_id: Optional[str], start: datetime, end: datetime) -> Dict[str, Any]:
    """Gathers digital twin simulation run durations and scenario throughput parameters."""
    sims_q = db.query(DigitalTwinSimulation).filter(DigitalTwinSimulation.created_at.between(start, end))
    if warehouse_id:
        sims_q = sims_q.filter(DigitalTwinSimulation.warehouse_id == warehouse_id)
        
    sims = sims_q.all()
    total_sims = len(sims)
    
    by_scenario = {}
    durations = []
    ticks = []
    
    for s in sims:
        by_scenario[s.scenario_type] = by_scenario.get(s.scenario_type, 0) + 1
        ticks.append(s.tick_count)
        if s.started_at and s.completed_at:
            durations.append((s.completed_at - s.started_at).total_seconds())

    avg_duration = statistics.mean(durations) if durations else None
    avg_ticks = statistics.mean(ticks) if ticks else None

    return {
        "runs_logged": {"value": total_sims, "unit": "simulations", "data_quality": "DATABASE_SYNCHRONIZED"},
        "avg_run_duration": {"value": round(avg_duration, 1) if avg_duration is not None else None, "unit": "seconds", "data_quality": "DATABASE_SYNCHRONIZED" if durations else "INSUFFICIENT DATA"},
        "avg_ticks": {"value": round(avg_ticks, 1) if avg_ticks is not None else None, "unit": "ticks", "data_quality": "DATABASE_SYNCHRONIZED" if ticks else "INSUFFICIENT DATA"},
        "by_scenario": by_scenario
    }


def compute_system_reliability_analytics(db: Session, start: datetime, end: datetime) -> Dict[str, Any]:
    """Calculates engineering service status, backup checksum failures and notification delivery success."""
    notif_q = db.query(Notification).filter(Notification.created_at.between(start, end))
    notifs = notif_q.all()
    
    total_notifs = len(notifs)
    sent_notifs = sum(1 for n in notifs if n.status in ("SENT", "DELIVERED", "READ"))
    failed_notifs = sum(1 for n in notifs if n.status == "FAILED")
    
    delivery_success = (sent_notifs / total_notifs * 100.0) if total_notifs > 0 else 100.0
    
    # Backups check
    backups = db.query(BackupRecord).filter(BackupRecord.created_at.between(start, end)).all()
    total_backups = len(backups)
    failed_backups = sum(1 for b in backups if b.status == "FAILED" or b.verification_status == "FAILED")
    
    backup_integrity_rate = ((total_backups - failed_backups) / total_backups * 100.0) if total_backups > 0 else 100.0

    return {
        "notification_delivery_success": {"value": round(delivery_success, 1), "unit": "percent", "data_quality": "DATABASE_SYNCHRONIZED"},
        "notification_failures": {"value": failed_notifs, "unit": "failures", "data_quality": "DATABASE_SYNCHRONIZED"},
        "backup_verification_integrity": {"value": round(backup_integrity_rate, 1), "unit": "percent", "data_quality": "DATABASE_SYNCHRONIZED"},
        "backup_failures": {"value": failed_backups, "unit": "failures", "data_quality": "DATABASE_SYNCHRONIZED"}
    }
