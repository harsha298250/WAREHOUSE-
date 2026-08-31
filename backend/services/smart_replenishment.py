"""
smart_replenishment.py — Operational service connecting Demand Forecasting,
Replenishment Recommendations, Approval Workflows, Tasks, Phase 5 Robot Assignment,
Phase 6 Pathfinding, and WMS Inventory Updates.
"""

import logging
import json
from datetime import datetime, UTC
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from backend.models import (
    ReplenishmentRecommendation, Inventory, Item, Task, TaskEvent,
    Robot, WarehouseLocation, InventoryMovement, AuditLedger, Warehouse
)
from backend import audit_ledger, notifications
from ml.replenishment.engine import run_replenishment_engine
from backend.services.intelligent_assignment import recommend_robot_for_task, assign_robot_intelligently
from backend.services.operational_pathfinding import get_operational_task_route

logger = logging.getLogger("smart_replenishment")


def evaluate_smart_replenishment(db: Session, warehouse_id: Optional[str] = None) -> Dict[str, Any]:
    """Runs the replenishment recommendation engine across inventory records."""
    return run_replenishment_engine(db, warehouse_id=warehouse_id)


def approve_replenishment_recommendation(
    db: Session,
    recommendation_id: int,
    user_id: int,
    username: str
) -> Dict[str, Any]:
    """
    Approves a replenishment recommendation, creates a REPLENISH task,
    connects to Phase 5 Robot Assignment and Phase 6 Pathfinding.
    Does NOT modify inventory directly at approval stage.
    """
    rec = db.query(ReplenishmentRecommendation).filter(
        ReplenishmentRecommendation.id == recommendation_id
    ).with_for_update().first()
    if not rec:
        raise HTTPException(404, f"Replenishment recommendation {recommendation_id} not found.")

    if rec.status in ("APPROVED", "COMPLETED"):
        raise HTTPException(409, f"Recommendation {recommendation_id} has already been approved or completed.")

    # 1. Verify SKU and Warehouse
    wh = db.query(Warehouse).filter(Warehouse.id == rec.warehouse_id).first()
    if not wh:
        raise HTTPException(404, f"Warehouse {rec.warehouse_id} not found.")

    item = db.query(Item).filter(Item.id == rec.item_id).first()
    if not item:
        raise HTTPException(404, f"Item {rec.item_id} not found.")

    # 2. Freshness & Stale Check
    inv_records = db.query(Inventory).filter(
        Inventory.warehouse_id == rec.warehouse_id,
        Inventory.item_id == rec.item_id
    ).all()
    current_avail = sum(i.available for i in inv_records if i.available is not None)

    # If inventory increased significantly above reorder point, flag as stale
    if rec.reorder_point and current_avail > rec.reorder_point * 1.2 and current_avail != rec.current_stock:
        raise HTTPException(
            409,
            f"Inventory changed since this recommendation was generated (Current available: {current_avail:.0f}, Previous: {rec.current_stock:.0f}). Please recalculate."
        )

    # 3. Idempotency & Duplicate Task Check
    existing_task = db.query(Task).filter(
        Task.warehouse_id == rec.warehouse_id,
        Task.product_id == rec.item_id,
        Task.task_type == "REPLENISH",
        Task.status.in_(["QUEUED", "PRIORITIZED", "ASSIGNED", "IN_PROGRESS"])
    ).first()

    if existing_task:
        raise HTTPException(409, f"An active replenishment task ({existing_task.task_number}) already exists for this item.")

    # 4. Map Locations
    source_loc = db.query(WarehouseLocation).filter(
        WarehouseLocation.warehouse_id == rec.warehouse_id,
        WarehouseLocation.location_type != "PICKING"
    ).first()

    dest_loc = db.query(WarehouseLocation).filter(
        WarehouseLocation.warehouse_id == rec.warehouse_id,
        WarehouseLocation.location_type == "PICKING"
    ).first()

    # 5. Determine Priority from Urgency
    priority_map = {
        "URGENT_REORDER": "CRITICAL",
        "REORDER_RECOMMENDED": "HIGH",
        "MONITOR": "MEDIUM",
        "NO_ACTION": "NORMAL",
        "INSUFFICIENT_DATA": "NORMAL"
    }
    task_priority = priority_map.get(rec.urgency, "HIGH")
    req_qty = rec.recommended_qty if (rec.recommended_qty and rec.recommended_qty > 0) else 50.0

    # 6. Create Replenishment Task
    now = datetime.now(UTC).replace(tzinfo=None)
    task = Task(
        task_number=f"TSK-TEMP-{now.timestamp()}",
        warehouse_id=rec.warehouse_id,
        task_type="REPLENISH",
        priority=task_priority,
        status="QUEUED",
        source_type="REPLENISHMENT",
        source_id=str(rec.id),
        product_id=rec.item_id,
        source_location_id=source_loc.id if source_loc else None,
        destination_location_id=dest_loc.id if dest_loc else None,
        requested_quantity=int(round(req_qty)),
        completed_quantity=0,
        notes=rec.reason or "Replenishment approved by user"
    )
    db.add(task)
    db.flush()

    task.task_number = f"TSK-REP-{task.id:06d}"

    # Log Task Event
    event = TaskEvent(
        task_id=task.id,
        event_type="TASK_CREATED",
        previous_status=None,
        new_status="QUEUED",
        user_id=user_id,
        created_at=now,
        reason=f"Smart replenishment approved by {username}"
    )
    db.add(event)

    # Update Recommendation Status
    rec.status = "APPROVED"
    rec.notes = f"Approved by {username} on {now.isoformat()}"

    # Audit Ledger entry
    audit_ledger.append_entry(db, "REPLENISHMENT_APPROVED", {
        "recommendation_id": rec.id,
        "item_id": rec.item_id,
        "warehouse_id": rec.warehouse_id,
        "task_id": task.id,
        "approved_by": username
    })

    db.commit()

    # 7. Phase 5 Robot Assignment Attempt
    assigned_robot_code = None
    try:
        rec_robot = recommend_robot_for_task(db, task.id)
        if rec_robot.get("status") == "recommendation_available" and rec_robot.get("recommended_robot"):
            best_bot = rec_robot["recommended_robot"]["robot_code"]
            assign_res = assign_robot_intelligently(
                db=db,
                task_id=task.id,
                robot_identifier=best_bot,
                user_id=user_id,
                username=username,
                assignment_method="INTELLIGENT"
            )
            if assign_res.get("status") == "assigned":
                assigned_robot_code = best_bot
    except Exception as e:
        logger.debug("Phase 5 automatic robot assignment note for task %s: %s", task.id, e)

    # 8. Phase 6 Pathfinding Route Attempt
    route_planned = False
    try:
        route_res = get_operational_task_route(db, task.id, assigned_robot_code, algorithm="A_STAR")
        if route_res.get("success"):
            route_planned = True
    except Exception as e:
        logger.debug("Phase 6 pathfinding route planning note for task %s: %s", task.id, e)

    return {
        "status": "approved",
        "recommendation_id": rec.id,
        "task_id": task.id,
        "task_number": task.task_number,
        "assigned_robot": assigned_robot_code,
        "route_planned": route_planned
    }


def reject_replenishment_recommendation(
    db: Session,
    recommendation_id: int,
    user_id: int,
    username: str,
    reason: Optional[str] = None
) -> Dict[str, Any]:
    """Rejects a replenishment recommendation without modifying inventory or creating tasks."""
    rec = db.query(ReplenishmentRecommendation).filter(ReplenishmentRecommendation.id == recommendation_id).first()
    if not rec:
        raise HTTPException(404, f"Replenishment recommendation {recommendation_id} not found.")

    if rec.status in ("APPROVED", "COMPLETED"):
        raise HTTPException(409, f"Recommendation {recommendation_id} has already been approved or completed.")

    rec.status = "REJECTED"
    rec.notes = f"Rejected by {username}: {reason or 'No reason specified'}"

    audit_ledger.append_entry(db, "REPLENISHMENT_REJECTED", {
        "recommendation_id": rec.id,
        "item_id": rec.item_id,
        "warehouse_id": rec.warehouse_id,
        "rejected_by": username,
        "reason": reason
    })

    db.commit()
    return {"status": "rejected", "recommendation_id": rec.id}
