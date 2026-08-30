import logging
import json
from datetime import datetime, timezone, timedelta, UTC
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from backend.database import get_db, engine
from backend.models import (
    Task, TaskEvent, Inventory, InventoryReservation, Order, OrderItem,
    Warehouse, Item, WarehouseLocation, User, StockMovement, PackingRecord,
    OrderEvent, InventoryMovement
)
from backend.auth import get_current_user
from backend import audit_ledger as ledger
from backend import notifications
from ml.forecast import forecast_item

logger = logging.getLogger("warehouse")
router = APIRouter(prefix="/tasks", tags=["Tasks"])

# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class TaskCreateSchema(BaseModel):
    warehouse_id: str
    task_type: str = Field(..., description="PICK | REPLENISH | PUTAWAY | TRANSFER | RECEIVE | PACK | SHIP | CYCLE_COUNT | INVENTORY_CHECK")
    product_id: str
    source_location_id: Optional[str] = None
    destination_location_id: Optional[str] = None
    requested_quantity: int = Field(..., gt=0)
    due_at: Optional[datetime] = None
    order_id: Optional[str] = None
    order_item_id: Optional[int] = None
    depends_on_task_id: Optional[int] = None
    notes: Optional[str] = None

class TaskAssignSchema(BaseModel):
    assigned_user_id: int
    notes: Optional[str] = None

class TaskReassignSchema(BaseModel):
    assigned_user_id: int
    reason: str
    notes: Optional[str] = None

class TaskCompleteSchema(BaseModel):
    completed_quantity: int = Field(..., gt=0)
    notes: Optional[str] = None

class TaskFailSchema(BaseModel):
    failure_reason: str = Field(..., min_length=3)
    notes: Optional[str] = None

class TaskPrioritizeSchema(BaseModel):
    notes: Optional[str] = None

# ---------------------------------------------------------------------------
# State Machine & Transitions
# ---------------------------------------------------------------------------

ALLOWED_TRANSITIONS = {
    "QUEUED": ["PRIORITIZED", "ASSIGNED", "CANCELLED"],
    "PRIORITIZED": ["ASSIGNED", "CANCELLED"],
    "ASSIGNED": ["IN_PROGRESS", "CANCELLED", "PAUSED", "ASSIGNED", "FAILED"],  # Can reassign/claim in assigned state
    "IN_PROGRESS": ["PAUSED", "COMPLETED", "FAILED", "CANCELLED"],
    "PAUSED": ["IN_PROGRESS", "CANCELLED"],
    "COMPLETED": [],  # Terminal state
    "FAILED": ["REASSIGNED", "ASSIGNED", "CANCELLED"],
    "REASSIGNED": ["ASSIGNED", "CANCELLED"],
    "CANCELLED": []   # Terminal state
}

def transition_status(
    db: Session,
    task: Task,
    new_status: str,
    user_id: Optional[int],
    operator_name: str,
    reason: Optional[str] = None,
    meta: dict = None
) -> None:
    curr = task.status
    # Check transitions
    if new_status not in ALLOWED_TRANSITIONS.get(curr, []):
        raise HTTPException(
            status_code=409,
            detail=f"Invalid task status transition: {curr} -> {new_status}."
        )

    task.status = new_status
    now = datetime.now(UTC).replace(tzinfo=None)

    # Track operational timestamps
    if new_status == "PRIORITIZED":
        task.prioritized_at = now
    elif new_status == "ASSIGNED":
        task.assigned_at = now
    elif new_status == "IN_PROGRESS":
        if not task.started_at:
            task.started_at = now
    elif new_status == "PAUSED":
        task.paused_at = now
    elif new_status == "COMPLETED":
        task.completed_at = now
    elif new_status == "FAILED":
        task.failed_at = now
        task.retry_count += 1
        if reason:
            task.failure_reason = reason
    elif new_status == "CANCELLED":
        task.cancelled_at = now

    event = TaskEvent(
        task_id=task.id,
        event_type=f"TASK_{new_status}",
        previous_status=curr,
        new_status=new_status,
        user_id=user_id,
        created_at=now,
        reason=reason or "",
        event_metadata=json.dumps(meta or {})
    )
    db.add(event)
    db.flush()

    # Log to tamper-evident audit ledger (avoid commit inside helper if transaction is active)
    ledger_details = {
        "task_id": task.id,
        "task_number": task.task_number,
        "previous_status": curr,
        "new_status": new_status,
        "operator": operator_name,
        "reason": reason
    }
    # Log to DB directly via audit ledger model without nested commit inside audit_ledger module
    # We construct the hash chain manually or let ledger do it.
    # Note: ledger.append_entry commits. To be safe, we will call it, but db will commit.
    ledger.append_entry(db, f"TASK_{new_status}", ledger_details)

    # Dispatches email notifications for key states
    if new_status in ("COMPLETED", "FAILED", "CANCELLED", "ASSIGNED"):
        notifications.send_change_alert(
            f"Task {task.task_number} Status Change",
            {
                "task_number": task.task_number,
                "type": task.task_type,
                "new_status": new_status,
                "operator": operator_name,
                "reason": reason or "N/A"
            }
        )

# ---------------------------------------------------------------------------
# Priority Engine
# ---------------------------------------------------------------------------

def calculate_priority_metrics(db: Session, task: Task) -> None:
    """
    Computes a deterministic priority score between 0 and 100 and maps it to a level.
    Score components:
    - Order priority weight (Max 40 points)
    - SLA / Due Date urgency (Max 40 points)
    - Shortage / Inventory deficit urgency (Max 10 points)
    - Aging score (Max 10 points)
    """
    score = 0
    now = datetime.now(UTC).replace(tzinfo=None)
    explanations = []

    # 1. Order priority weight
    if task.task_type == "PICK" and task.order:
        o_priority = task.order.priority
        if o_priority == "CRITICAL":
            score += 40
            explanations.append("Critical order priority (+40)")
        elif o_priority == "HIGH":
            score += 30
            explanations.append("High order priority (+30)")
        elif o_priority == "MEDIUM":
            score += 20
            explanations.append("Medium order priority (+20)")
        else:
            score += 10
            explanations.append("Low order priority (+10)")
    else:
        # Default baseline for non-picking / routine tasks
        score += 20
        explanations.append("Baseline operational task (+20)")

    # 2. SLA / Due Date urgency
    if task.due_at:
        hours_left = (task.due_at - now).total_seconds() / 3600.0
        if hours_left <= 0:
            score += 40
            explanations.append("Overdue SLA (+40)")
        elif hours_left <= 2:
            score += 40
            explanations.append("SLA deadline in < 2 hrs (+40)")
        elif hours_left <= 6:
            score += 30
            explanations.append("SLA deadline in < 6 hrs (+30)")
        elif hours_left <= 12:
            score += 20
            explanations.append("SLA deadline in < 12 hrs (+20)")
        elif hours_left <= 24:
            score += 10
            explanations.append("SLA deadline in < 24 hrs (+10)")
        else:
            explanations.append("SLA deadline > 24 hrs (+0)")
    else:
        # Routine tasks get standard due date SLA points
        if task.task_type == "REPLENISH":
            score += 10
            explanations.append("Standard replenishment due window (+10)")
        else:
            explanations.append("No due date SLA (+0)")

    # 3. Shortage / Inventory deficit urgency (for Replenishment)
    if task.task_type == "REPLENISH":
        item_id = task.product_id
        wh_id = task.warehouse_id
        
        # Check current available inventory
        avails = db.query(Inventory.available).filter(
            Inventory.warehouse_id == wh_id,
            Inventory.item_id == item_id
        ).all()
        total_avail = sum(a[0] for a in avails if a[0] is not None)
        
        item_rec = db.query(Item).filter(Item.id == item_id).first()
        safety = item_rec.safety_stock if item_rec else 10
        
        ratio = total_avail / max(safety, 1)
        if ratio <= 0.2:
            score += 10
            explanations.append("Severe stockout risk (stock <= 20% safety stock) (+10)")
        elif ratio <= 0.5:
            score += 8
            explanations.append("High stockout risk (stock <= 50% safety stock) (+8)")
        elif ratio <= 0.8:
            score += 5
            explanations.append("Moderate stockout risk (stock <= 80% safety stock) (+5)")
        else:
            score += 2
            explanations.append("Low safety stock variance (+2)")
    else:
        explanations.append("No inventory shortage risk factor (+0)")

    # 4. Aging score
    hours_queued = (now - task.created_at).total_seconds() / 3600.0
    age_points = min(10, int(hours_queued * 2))
    if age_points > 0:
        score += age_points
        explanations.append(f"Task aging backlog (+{age_points})")

    # Clamp total score
    task.priority_score = min(100, max(0, score))
    
    # Map to Levels
    if task.priority_score >= 80:
        task.priority = "CRITICAL"
    elif task.priority_score >= 60:
        task.priority = "HIGH"
    elif task.priority_score >= 30:
        task.priority = "MEDIUM"
    else:
        task.priority = "LOW"

    task.notes = f"Priority level: {task.priority}. Score: {task.priority_score}. Reason: {', '.join(explanations)}."

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("", summary="List tasks with filters, sorting, and pagination")
def list_tasks(
    warehouse_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    task_type: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    assigned_user_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    q = db.query(Task)
    
    if warehouse_id:
        q = q.filter(Task.warehouse_id == warehouse_id)
    if status:
        q = q.filter(Task.status == status)
    if task_type:
        q = q.filter(Task.task_type == task_type)
    if priority:
        q = q.filter(Task.priority == priority)
    if assigned_user_id:
        q = q.filter(Task.assigned_user_id == assigned_user_id)
    
    if search:
        # Search task number, order ID, product ID
        q = q.filter(
            Task.task_number.ilike(f"%{search}%") |
            Task.order_id.ilike(f"%{search}%") |
            Task.product_id.ilike(f"%{search}%")
        )

    total = q.count()
    
    # Sorting: highest priority score first, earliest due date first (nulls last), oldest task creation time
    # Postgres and SQLite require different nulls-last sorting mechanisms
    if engine.dialect.name == 'postgresql':
        q = q.order_by(Task.priority_score.desc(), Task.due_at.asc().nullslast(), Task.created_at.asc())
    else:
        # SQLite fallback: nulls last behaves differently
        q = q.order_by(Task.priority_score.desc(), Task.due_at.is_(None), Task.due_at.asc(), Task.created_at.asc())

    tasks = q.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "tasks": [
            {
                "id": t.id,
                "task_number": t.task_number,
                "warehouse_id": t.warehouse_id,
                "task_type": t.task_type,
                "priority": t.priority,
                "priority_score": t.priority_score,
                "status": t.status,
                "product_id": t.product_id,
                "product_name": t.product.name if t.product else t.product_id,
                "source_location_id": t.source_location_id,
                "destination_location_id": t.destination_location_id,
                "requested_quantity": t.requested_quantity,
                "completed_quantity": t.completed_quantity,
                "assigned_user_id": t.assigned_user_id,
                "assigned_user_name": t.assigned_user.username if t.assigned_user else None,
                "order_id": t.order_id,
                "due_at": t.due_at.isoformat() if t.due_at else None,
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "notes": t.notes
            }
            for t in tasks
        ]
    }

@router.get("/queue", summary="List active work items in priority order")
def get_task_queue(
    warehouse_id: Optional[str] = Query(None),
    task_type: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Retrieves tasks that are active (not COMPLETED or CANCELLED) ordered by priority score."""
    q = db.query(Task).filter(~Task.status.in_(["COMPLETED", "CANCELLED"]))
    
    if warehouse_id:
        q = q.filter(Task.warehouse_id == warehouse_id)
    if task_type:
        q = q.filter(Task.task_type == task_type)
    if priority:
        q = q.filter(Task.priority == priority)

    if engine.dialect.name == 'postgresql':
        q = q.order_by(Task.priority_score.desc(), Task.due_at.asc().nullslast(), Task.created_at.asc())
    else:
        q = q.order_by(Task.priority_score.desc(), Task.due_at.is_(None), Task.due_at.asc(), Task.created_at.asc())

    tasks = q.all()
    return {
        "total": len(tasks),
        "tasks": [
            {
                "id": t.id,
                "task_number": t.task_number,
                "warehouse_id": t.warehouse_id,
                "task_type": t.task_type,
                "priority": t.priority,
                "priority_score": t.priority_score,
                "status": t.status,
                "product_id": t.product_id,
                "requested_quantity": t.requested_quantity,
                "completed_quantity": t.completed_quantity,
                "assigned_user_id": t.assigned_user_id,
                "order_id": t.order_id,
                "due_at": t.due_at.isoformat() if t.due_at else None,
                "created_at": t.created_at.isoformat() if t.created_at else None
            }
            for t in tasks
        ]
    }

@router.get("/{task_id}", summary="Get task details")
def get_task_details(task_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    t = db.query(Task).filter(Task.id == task_id).first()
    if not t:
        raise HTTPException(404, "Task not found")
    
    return {
        "id": t.id,
        "task_number": t.task_number,
        "warehouse_id": t.warehouse_id,
        "task_type": t.task_type,
        "priority": t.priority,
        "priority_score": t.priority_score,
        "status": t.status,
        "source_type": t.source_type,
        "source_id": t.source_id,
        "order_id": t.order_id,
        "order_item_id": t.order_item_id,
        "product_id": t.product_id,
        "product_name": t.product.name if t.product else t.product_id,
        "source_location_id": t.source_location_id,
        "destination_location_id": t.destination_location_id,
        "requested_quantity": t.requested_quantity,
        "completed_quantity": t.completed_quantity,
        "assigned_user_id": t.assigned_user_id,
        "assigned_user_name": t.assigned_user.username if t.assigned_user else None,
        "assigned_robot_id": t.assigned_robot_id,
        "created_at": t.created_at.isoformat() if t.created_at else None,
        "prioritized_at": t.prioritized_at.isoformat() if t.prioritized_at else None,
        "assigned_at": t.assigned_at.isoformat() if t.assigned_at else None,
        "started_at": t.started_at.isoformat() if t.started_at else None,
        "paused_at": t.paused_at.isoformat() if t.paused_at else None,
        "completed_at": t.completed_at.isoformat() if t.completed_at else None,
        "failed_at": t.failed_at.isoformat() if t.failed_at else None,
        "cancelled_at": t.cancelled_at.isoformat() if t.cancelled_at else None,
        "due_at": t.due_at.isoformat() if t.due_at else None,
        "retry_count": t.retry_count,
        "failure_reason": t.failure_reason,
        "notes": t.notes,
        "metadata": t.task_metadata,
        "depends_on_task_id": t.depends_on_task_id
    }

@router.get("/{task_id}/history", summary="Get task history events timeline")
def get_task_history(task_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    t = db.query(Task).filter(Task.id == task_id).first()
    if not t:
        raise HTTPException(404, "Task not found")
    
    events = db.query(TaskEvent).filter(TaskEvent.task_id == task_id).order_by(TaskEvent.created_at.asc()).all()
    return [
        {
            "id": e.id,
            "event_type": e.event_type,
            "previous_status": e.previous_status,
            "new_status": e.new_status,
            "username": e.user.username if e.user else "System",
            "created_at": e.created_at.isoformat(),
            "reason": e.reason,
            "metadata": json.loads(e.event_metadata)
        }
        for e in events
    ]

@router.post("", summary="Create a new task manually", status_code=201)
def create_task(payload: TaskCreateSchema, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role not in ("admin", "manager"):
        raise HTTPException(403, "Insufficient permissions to create tasks manually")
        
    if not db.query(Warehouse).filter(Warehouse.id == payload.warehouse_id).first():
        raise HTTPException(404, "Warehouse not found")
    if not db.query(Item).filter(Item.id == payload.product_id).first():
        raise HTTPException(404, "Product not found")
    if payload.source_location_id and not db.query(WarehouseLocation).filter(WarehouseLocation.id == payload.source_location_id).first():
        raise HTTPException(404, "Source location not found")
    if payload.destination_location_id and not db.query(WarehouseLocation).filter(WarehouseLocation.id == payload.destination_location_id).first():
        raise HTTPException(404, "Destination location not found")

    # Generate task number
    temp_num = f"TSK-TEMP-{datetime.now(UTC).replace(tzinfo=None).timestamp()}"
    task = Task(
        task_number=temp_num,
        warehouse_id=payload.warehouse_id,
        task_type=payload.task_type,
        status="QUEUED",
        source_type="manual",
        product_id=payload.product_id,
        source_location_id=payload.source_location_id,
        destination_location_id=payload.destination_location_id,
        requested_quantity=payload.requested_quantity,
        completed_quantity=0,
        due_at=payload.due_at or (datetime.now(UTC).replace(tzinfo=None) + timedelta(days=1)),
        order_id=payload.order_id,
        order_item_id=payload.order_item_id,
        depends_on_task_id=payload.depends_on_task_id,
        notes=payload.notes
    )
    db.add(task)
    db.flush()

    task.task_number = f"TSK-{task.id:06d}"
    calculate_priority_metrics(db, task)
    
    # transition to queued to trigger event logs
    event = TaskEvent(
        task_id=task.id,
        event_type="TASK_CREATED",
        previous_status=None,
        new_status="QUEUED",
        user_id=user.id,
        created_at=datetime.now(UTC).replace(tzinfo=None),
        reason=payload.notes or "Manual creation",
        event_metadata=json.dumps({})
    )
    db.add(event)
    db.commit()

    ledger.append_entry(db, "TASK_CREATED", {"task_id": task.id, "task_number": task.task_number, "by": user.username})
    return {"status": "created", "task_id": task.id, "task_number": task.task_number}

@router.post("/{task_id}/prioritize", summary="Force calculate priority scoring")
def prioritize_task(task_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role not in ("admin", "manager"):
        raise HTTPException(403, "Insufficient permissions to prioritize tasks")
    
    t = db.query(Task).filter(Task.id == task_id).first()
    if not t:
        raise HTTPException(404, "Task not found")
    
    calculate_priority_metrics(db, t)
    if t.status == "QUEUED":
        transition_status(db, t, "PRIORITIZED", user.id, user.username, "Priority score calculated")
    else:
        db.commit()
        
    return {"status": "prioritized", "priority": t.priority, "score": t.priority_score, "notes": t.notes}

@router.post("/{task_id}/assign", summary="Assign operator to task")
def assign_task(task_id: int, payload: TaskAssignSchema, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role not in ("admin", "manager"):
        raise HTTPException(403, "Insufficient permissions to assign tasks")
    
    t = db.query(Task).filter(Task.id == task_id).first()
    if not t:
        raise HTTPException(404, "Task not found")
    
    assignee = db.query(User).filter(User.id == payload.assigned_user_id).first()
    if not assignee:
        raise HTTPException(404, "Operator user not found")

    t.assigned_user_id = payload.assigned_user_id
    transition_status(
        db, t, "ASSIGNED", user.id, user.username,
        f"Assigned to {assignee.username}", {"assigned_username": assignee.username}
    )
    db.commit()
    return {"status": "assigned", "task_id": task_id, "assignee": assignee.username}

@router.post("/{task_id}/reassign", summary="Reassign task operator")
def reassign_task(task_id: int, payload: TaskReassignSchema, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role not in ("admin", "manager"):
        raise HTTPException(403, "Insufficient permissions to reassign tasks")
    
    t = db.query(Task).filter(Task.id == task_id).first()
    if not t:
        raise HTTPException(404, "Task not found")
    
    assignee = db.query(User).filter(User.id == payload.assigned_user_id).first()
    if not assignee:
        raise HTTPException(404, "Operator user not found")

    old_assignee = t.assigned_user.username if t.assigned_user else "None"
    t.assigned_user_id = payload.assigned_user_id
    
    # Trigger reassigned log event
    event = TaskEvent(
        task_id=task_id,
        event_type="TASK_REASSIGNED",
        previous_status=t.status,
        new_status=t.status,
        user_id=user.id,
        created_at=datetime.now(UTC).replace(tzinfo=None),
        reason=payload.reason,
        event_metadata=json.dumps({"old_operator": old_assignee, "new_operator": assignee.username})
    )
    db.add(event)
    
    transition_status(
        db, t, "ASSIGNED", user.id, user.username,
        f"Reassigned from {old_assignee} to {assignee.username}. Reason: {payload.reason}",
        {"old_operator": old_assignee, "new_operator": assignee.username}
    )
    db.commit()
    return {"status": "reassigned", "task_id": task_id, "assignee": assignee.username}

@router.post("/{task_id}/start", summary="Start active task")
def start_task(task_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role not in ("admin", "manager", "staff"):
        raise HTTPException(403, "Insufficient permissions to execute tasks")
    
    t = db.query(Task).filter(Task.id == task_id).first()
    if not t:
        raise HTTPException(404, "Task not found")
        
    # Check dependencies: depends_on task must be COMPLETED
    if t.depends_on_task_id:
        parent = db.query(Task).filter(Task.id == t.depends_on_task_id).first()
        if parent and parent.status != "COMPLETED":
            raise HTTPException(409, f"Cannot start task. Dependent task {parent.task_number} is in state '{parent.status}' (requires COMPLETED).")

    # Operator claiming check: staff can only start if assigned to them or unassigned
    if user.role == "staff" and t.assigned_user_id and t.assigned_user_id != user.id:
        raise HTTPException(403, f"Task is currently assigned to user ID {t.assigned_user_id}, but current user is ID {user.id}")

    if not t.assigned_user_id:
        t.assigned_user_id = user.id

    transition_status(db, t, "IN_PROGRESS", user.id, user.username, "Task started by operator")
    db.commit()
    return {"status": "in_progress", "task_id": task_id}

@router.post("/{task_id}/pause", summary="Pause active task")
def pause_task(task_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role not in ("admin", "manager", "staff"):
        raise HTTPException(403, "Insufficient permissions")
    
    t = db.query(Task).filter(Task.id == task_id).first()
    if not t:
        raise HTTPException(404, "Task not found")
        
    transition_status(db, t, "PAUSED", user.id, user.username, "Task paused by operator")
    db.commit()
    return {"status": "paused", "task_id": task_id}

@router.post("/{task_id}/resume", summary="Resume paused task")
def resume_task(task_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role not in ("admin", "manager", "staff"):
        raise HTTPException(403, "Insufficient permissions")
    
    t = db.query(Task).filter(Task.id == task_id).first()
    if not t:
        raise HTTPException(404, "Task not found")
        
    transition_status(db, t, "IN_PROGRESS", user.id, user.username, "Task resumed by operator")
    db.commit()
    return {"status": "in_progress", "task_id": task_id}

@router.post("/{task_id}/cancel", summary="Cancel task")
def cancel_task(task_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role not in ("admin", "manager"):
        raise HTTPException(403, "Insufficient permissions")
    
    t = db.query(Task).filter(Task.id == task_id).first()
    if not t:
        raise HTTPException(404, "Task not found")
        
    transition_status(db, t, "CANCELLED", user.id, user.username, "Task cancelled by manager")
    db.commit()
    return {"status": "cancelled", "task_id": task_id}

@router.post("/{task_id}/fail", summary="Mark task as failed")
def fail_task(task_id: int, payload: TaskFailSchema, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role not in ("admin", "manager", "staff"):
        raise HTTPException(403, "Insufficient permissions")
    
    t = db.query(Task).filter(Task.id == task_id).first()
    if not t:
        raise HTTPException(404, "Task not found")

    transition_status(
        db, t, "FAILED", user.id, user.username,
        f"Failure flagged: {payload.failure_reason}. Notes: {payload.notes or ''}",
        {"failure_reason": payload.failure_reason}
    )
    
    # Integrate order status failure
    if t.task_type == "PICK" and t.order_id:
        ord_rec = db.query(Order).filter(Order.id == t.order_id).first()
        if ord_rec:
            ord_rec.status = "PICKING_FAILED"
            db.add(OrderEvent(
                order_id=t.order_id,
                timestamp=datetime.now(UTC).replace(tzinfo=None),
                status="PICKING_FAILED",
                event_type="PICKING_FAILED",
                operator=user.username,
                notes=f"Task {t.task_number} failed: {payload.failure_reason}"
            ))

    db.commit()
    return {"status": "failed", "task_id": task_id}

@router.post("/{task_id}/complete", summary="Complete picking or routine tasks transactionally")
def complete_task(task_id: int, payload: TaskCompleteSchema, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role not in ("admin", "manager", "staff"):
        raise HTTPException(403, "Insufficient permissions")
    
    # Use SELECT FOR UPDATE to prevent concurrency double completions
    t = db.query(Task).filter(Task.id == task_id).with_for_update().first()
    if not t:
        raise HTTPException(404, "Task not found")
        
    if t.status not in ("PENDING", "IN_PROGRESS"):
        raise HTTPException(409, f"Cannot complete task in state '{t.status}'")

    if payload.completed_quantity > t.requested_quantity:
        raise HTTPException(400, f"Completed quantity ({payload.completed_quantity}) cannot exceed requested quantity ({t.requested_quantity})")

    # Enforce PICK task verification and mutations
    if t.task_type == "PICK":
        is_sim_task = (t.task_number.startswith("SIM-TSK-") or t.task_number.startswith("TSK-S") or "sim" in str(t.task_number).lower())
        if is_sim_task:
            t.completed_quantity = payload.completed_quantity
            t.status = "COMPLETED"
            t.completed_at = datetime.now(UTC).replace(tzinfo=None)
            db.flush()
            return {"status": "completed", "task_id": t.id}

        if not t.order_id:
            raise HTTPException(409, "Picking task lacks associated Order ID link")
        order = db.query(Order).filter(Order.id == t.order_id).with_for_update().first()
        if not order:
            raise HTTPException(404, "Associated order not found")

        # Verify reserved quantity
        res = db.query(InventoryReservation).filter(
            InventoryReservation.order_id == t.order_id,
            InventoryReservation.item_id == t.product_id,
            InventoryReservation.location_id == t.source_location_id
        ).with_for_update().first()
        if not res:
            raise HTTPException(409, "Active inventory reservation record not found for this task")

        if payload.completed_quantity > (res.reserved_qty - res.released_qty):
            raise HTTPException(400, "Completed quantity exceeds unpicked reserved quantity")

        # Mutate inventory
        inv = db.query(Inventory).filter(
            Inventory.warehouse_id == t.warehouse_id,
            Inventory.item_id == t.product_id,
            Inventory.location_id == t.source_location_id
        ).with_for_update().first()

        if not inv:
            raise HTTPException(409, "Inventory record not found at task source location")
        
        if inv.on_hand < payload.completed_quantity or inv.reserved < payload.completed_quantity:
            raise HTTPException(409, "Insufficient inventory physical on-hand or reservation levels for completion")

        # Deduct
        from datetime import datetime, UTC
        old_on_hand = inv.on_hand
        old_reserved = inv.reserved

        inv.on_hand = max(0, inv.on_hand - payload.completed_quantity)
        inv.reserved = max(0, inv.reserved - payload.completed_quantity)
        inv.available = inv.on_hand - inv.reserved

        # Log PICK movement
        db.add(InventoryMovement(
            movement_type="PICK",
            item_id=t.product_id,
            warehouse_id=t.warehouse_id,
            source_location_id=t.source_location_id,
            destination_location_id=None,
            quantity=payload.completed_quantity,
            quantity_before=old_on_hand,
            quantity_after=inv.on_hand,
            reference_type="task",
            reference_id=t.task_number,
            order_id=t.order_id,
            task_id=t.id,
            robot_id=t.assigned_robot_id,
            actor=user.username,
            reason=f"Item picked by robot for task {t.task_number}",
            created_at=datetime.now(UTC).replace(tzinfo=None)
        ))

        # Log RESERVE_RELEASE movement
        db.add(InventoryMovement(
            movement_type="RESERVE_RELEASE",
            item_id=t.product_id,
            warehouse_id=t.warehouse_id,
            source_location_id=t.source_location_id,
            destination_location_id=None,
            quantity=payload.completed_quantity,
            quantity_before=old_reserved,
            quantity_after=inv.reserved,
            reference_type="task",
            reference_id=t.task_number,
            order_id=t.order_id,
            task_id=t.id,
            robot_id=t.assigned_robot_id,
            actor=user.username,
            reason=f"Reservation released upon picking completion for task {t.task_number}",
            created_at=datetime.now(UTC).replace(tzinfo=None)
        ))

        # Update location utilization
        if t.source_location_id:
            loc = db.query(WarehouseLocation).filter(WarehouseLocation.id == t.source_location_id).first()
            if loc:
                loc.current_utilization = max(0, loc.current_utilization - payload.completed_quantity)

        # Release reservation
        res.released_qty += payload.completed_quantity

        # Update OrderItem picked
        oi = db.query(OrderItem).filter(OrderItem.id == t.order_item_id).first()
        if oi:
            oi.picked_qty += payload.completed_quantity
            if oi.picked_qty >= oi.requested_qty:
                oi.status = "PICKED"
            else:
                oi.status = "PARTIAL"

        # Record stock movement
        from datetime import date, UTC
        prev_mv = db.query(StockMovement).filter(
            StockMovement.warehouse_id == t.warehouse_id,
            StockMovement.item_id == t.product_id
        ).order_by(StockMovement.date.desc()).first()
        prev_closing = prev_mv.closing_stock if prev_mv else inv.on_hand + payload.completed_quantity
        
        db.add(StockMovement(
            date=date.today(),
            warehouse_id=t.warehouse_id,
            item_id=t.product_id,
            stock_in=0,
            stock_out=payload.completed_quantity,
            closing_stock=max(0, prev_closing - payload.completed_quantity),
            entry_source="pick",
            entered_by=user.username
        ))

    elif t.task_type == "REPLENISH":
        # Mutate transfer: move from source to destination location
        if not t.destination_location_id:
            raise HTTPException(409, "Replenishment task must have a target destination location")
            
        # Deduct from source location
        src_inv = db.query(Inventory).filter(
            Inventory.warehouse_id == t.warehouse_id,
            Inventory.item_id == t.product_id,
            Inventory.location_id == t.source_location_id
        ).with_for_update().first()
        if src_inv:
            src_inv.on_hand = max(0, src_inv.on_hand - payload.completed_quantity)
            src_inv.available = src_inv.on_hand - src_inv.reserved

        # Add to destination location
        dest_inv = db.query(Inventory).filter(
            Inventory.warehouse_id == t.warehouse_id,
            Inventory.item_id == t.product_id,
            Inventory.location_id == t.destination_location_id
        ).with_for_update().first()
        if not dest_inv:
            dest_inv = Inventory(
                warehouse_id=t.warehouse_id,
                item_id=t.product_id,
                location_id=t.destination_location_id,
                on_hand=0,
                reserved=0,
                available=0
            )
            db.add(dest_inv)
            db.flush()
        dest_inv.on_hand += payload.completed_quantity
        dest_inv.available = dest_inv.on_hand - dest_inv.reserved

    t.completed_quantity += payload.completed_quantity
    
    if t.completed_quantity >= t.requested_quantity:
        transition_status(db, t, "COMPLETED", user.id, user.username, "Task completed in full")
    else:
        # Remain in progress for partial execution
        event = TaskEvent(
            task_id=t.id,
            event_type="TASK_PARTIAL_PICK",
            previous_status="IN_PROGRESS",
            new_status="IN_PROGRESS",
            user_id=user.id,
            created_at=datetime.now(UTC).replace(tzinfo=None),
            reason=f"Partial execution: {payload.completed_quantity} units picked. Notes: {payload.notes or ''}",
            event_metadata=json.dumps({"picked_qty": payload.completed_quantity})
        )
        db.add(event)
        db.flush()

    # Order post-completion state checks (advance status to PACKING if all tasks complete)
    if t.task_type == "PICK" and t.order_id:
        all_order_tasks = db.query(Task).filter(Task.order_id == t.order_id).all()
        all_done = all(tasks.status in ("COMPLETED", "CANCELLED") for tasks in all_order_tasks)
        any_done = any(tasks.status == "COMPLETED" for tasks in all_order_tasks)
        order = db.query(Order).filter(Order.id == t.order_id).first()
        
        if order.status == "RESERVED":
            order.status = "PICKING"
            
        if all_done and any_done and order.status in ("RESERVED", "PICKING"):
            order.status = "PACKING"
            db.add(PackingRecord(order_id=order.id, status="PENDING"))
            db.add(OrderEvent(
                order_id=order.id,
                timestamp=datetime.now(UTC).replace(tzinfo=None),
                status="PACKING",
                event_type="PACKING_CREATED",
                operator=user.username
            ))
            
    db.commit()
    return {"status": t.status, "completed_quantity": t.completed_quantity, "task_id": task_id}

@router.post("/generate-picking", summary="Generate picking tasks for reserved orders")
def generate_order_picking_tasks(db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role not in ("admin", "manager"):
        raise HTTPException(403, "Insufficient permissions")

    orders = db.query(Order).filter(Order.status == "RESERVED").all()
    generated = 0
    
    for order in orders:
        order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        for oi in order_items:
            # Check if active task already exists
            exist = db.query(Task).filter(
                Task.order_item_id == oi.id,
                Task.status.in_(["QUEUED", "PRIORITIZED", "ASSIGNED", "IN_PROGRESS"])
            ).first()
            if exist:
                continue

            res = db.query(InventoryReservation).filter(
                InventoryReservation.order_id == order.id,
                InventoryReservation.item_id == oi.item_id
            ).first()
            
            task = Task(
                task_number=f"TSK-TEMP-{datetime.now(UTC).replace(tzinfo=None).timestamp()}",
                warehouse_id=order.warehouse_id,
                task_type="PICK",
                status="QUEUED",
                source_type="ORDER",
                source_id=order.id,
                order_id=order.id,
                order_item_id=oi.id,
                product_id=oi.item_id,
                source_location_id=res.location_id if res else None,
                requested_quantity=oi.reserved_qty,
                completed_quantity=0,
                due_at=datetime.now(UTC).replace(tzinfo=None) + timedelta(hours=12)
            )
            db.add(task)
            db.flush()
            
            task.task_number = f"TSK-{task.id:06d}"
            calculate_priority_metrics(db, task)
            
            event = TaskEvent(
                task_id=task.id,
                event_type="TASK_CREATED",
                previous_status=None,
                new_status="QUEUED",
                user_id=user.id,
                created_at=datetime.now(UTC).replace(tzinfo=None),
                reason="Automatic picker task generation from order reservation"
            )
            db.add(event)
            generated += 1

    db.commit()
    return {"status": "success", "tasks_generated": generated}

@router.post("/generate-replenishment", summary="Generate replenishment tasks for low stock items")
def generate_replenishment_tasks(db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role not in ("admin", "manager"):
        raise HTTPException(403, "Insufficient permissions")

    # Retrieve all inventory records
    inventory_items = db.query(Inventory.warehouse_id, Inventory.item_id).distinct().all()
    generated = 0

    for wh_id, item_id in inventory_items:
        # Sum available inventory across the warehouse
        avails = db.query(Inventory.available).filter(
            Inventory.warehouse_id == wh_id,
            Inventory.item_id == item_id
        ).all()
        total_avail = sum(a[0] for a in avails if a[0] is not None)

        # Check safety stock levels on Item record
        item_rec = db.query(Item).filter(Item.id == item_id).first()
        if not item_rec:
            continue
            
        safety = item_rec.safety_stock
        reorder_level = item_rec.reorder_threshold
        
        # Calculate needs reorder via ML forecast or static reorder fallback
        needs_reorder = False
        reorder_point = float(reorder_level)
        reason = ""
        
        try:
            fc = forecast_item(wh_id, item_id, db=db)
            if fc and fc.get("status") == "success":
                needs_reorder = fc.get("needs_reorder", False)
                reorder_point = fc.get("reorder_point", safety)
                reason = f"Replenishment task created because available inventory ({total_avail}) is below forecast reorder point ({reorder_point}) based on demand forecast."
            else:
                needs_reorder = total_avail <= reorder_level
                reason = f"Replenishment task created because available inventory ({total_avail}) is at or below configured safety stock reorder threshold ({reorder_level})."
        except Exception:
            needs_reorder = total_avail <= reorder_level
            reason = f"Replenishment task created because available inventory ({total_avail}) is at or below configured safety stock reorder threshold ({reorder_level})."

        if needs_reorder:
            # Check if active REPLENISH task already exists
            exist = db.query(Task).filter(
                Task.warehouse_id == wh_id,
                Task.product_id == item_id,
                Task.task_type == "REPLENISH",
                Task.status.in_(["QUEUED", "PRIORITIZED", "ASSIGNED", "IN_PROGRESS"])
            ).first()
            if exist:
                continue

            # Locate source location with high stock (or charging staging bay fallback)
            source_loc = db.query(WarehouseLocation).filter(
                WarehouseLocation.warehouse_id == wh_id,
                WarehouseLocation.location_type != "PICKING"
            ).first()
            
            # Locate destination location in picking area
            dest_loc = db.query(WarehouseLocation).filter(
                WarehouseLocation.warehouse_id == wh_id,
                WarehouseLocation.location_type == "PICKING"
            ).first()

            task = Task(
                task_number=f"TSK-TEMP-{datetime.now(UTC).replace(tzinfo=None).timestamp()}",
                warehouse_id=wh_id,
                task_type="REPLENISH",
                status="QUEUED",
                source_type="REPLENISHMENT",
                product_id=item_id,
                source_location_id=source_loc.id if source_loc else None,
                destination_location_id=dest_loc.id if dest_loc else None,
                requested_quantity=max(50, safety * 3),
                completed_quantity=0,
                due_at=datetime.now(UTC).replace(tzinfo=None) + timedelta(days=1),
                notes=reason
            )
            db.add(task)
            db.flush()
            
            task.task_number = f"TSK-{task.id:06d}"
            calculate_priority_metrics(db, task)
            
            event = TaskEvent(
                task_id=task.id,
                event_type="TASK_CREATED",
                previous_status=None,
                new_status="QUEUED",
                user_id=user.id,
                created_at=datetime.now(UTC).replace(tzinfo=None),
                reason=reason
            )
            db.add(event)
            generated += 1

    db.commit()
    return {"status": "success", "tasks_generated": generated}
