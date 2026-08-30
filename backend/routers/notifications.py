import json
import logging
from datetime import datetime, UTC
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from backend.database import get_db
from backend.models import User, Notification, NotificationPreference, UserWarehouseAccess
from backend.auth import get_current_user, require_permission, Permissions
from backend.event_processor import EVENT_CATEGORIES, SEVERITY_LEVELS, DEFAULT_PREFERENCES, get_user_preference
from backend import notifications as email_service
from backend import audit_ledger as ledger

logger = logging.getLogger("warehouse.notifications_router")
router = APIRouter()


# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------
class PreferenceItem(BaseModel):
    category: str
    in_app_enabled: bool
    email_enabled: bool
    min_severity: str = "INFO"


class PreferenceUpdateList(BaseModel):
    preferences: List[PreferenceItem]


class WarehouseAccessPayload(BaseModel):
    user_id: int
    warehouse_id: str


# ---------------------------------------------------------------------------
# Notifications View Endpoints
# ---------------------------------------------------------------------------
@router.get("/notifications", summary="Fetch current user notifications")
def list_notifications(
    read_filter: Optional[bool] = Query(None, description="True=Read, False=Unread, None=All"),
    category: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    warehouse_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Returns paginated notifications for the logged-in user.
    Adheres strictly to owner-only scoping and filters by category/severity/read status.
    """
    q = db.query(Notification).filter(Notification.user_id == user.id, Notification.channel == "IN_APP")
    
    if read_filter is not None:
        if read_filter:
            q = q.filter(Notification.status == "READ")
        else:
            q = q.filter(Notification.status != "READ")
            
    if category:
        # Resolve event types belonging to category
        event_types = [et for et, cat in EVENT_CATEGORIES.items() if cat.lower() == category.lower()]
        q = q.filter(Notification.event_type.in_(event_types))
        
    if severity:
        q = q.filter(Notification.severity == severity.upper())
        
    if warehouse_id:
        q = q.filter(Notification.warehouse_id == warehouse_id)
        
    q = q.order_by(desc(Notification.created_at))
    total = q.count()
    rows = q.offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "notifications": [
            {
                "id": r.id,
                "warehouse_id": r.warehouse_id,
                "event_type": r.event_type,
                "category": EVENT_CATEGORIES.get(r.event_type, "system"),
                "notification_type": r.notification_type,
                "title": r.title,
                "message": r.message,
                "severity": r.severity,
                "status": r.status,
                "source_entity_type": r.source_entity_type,
                "source_entity_id": r.source_entity_id,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "read_at": r.read_at.isoformat() if r.read_at else None,
                "payload": json.loads(r.notif_metadata) if r.notif_metadata else {}
            }
            for r in rows
        ]
    }


@router.get("/notifications/unread-count", summary="Fetch unread count")
def get_unread_count(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Returns the unread notification count for the topbar badge."""
    count = db.query(func.count(Notification.id)).filter(
        Notification.user_id == user.id,
        Notification.channel == "IN_APP",
        Notification.status != "READ"
    ).scalar() or 0
    return {"unread_count": count}


@router.get("/notifications/{id}", summary="Fetch single notification details")
def get_notification_detail(
    id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Returns details for a single notification.
    Enforces strict ownership check to block IDOR attacks (Step 36).
    """
    notif = db.query(Notification).filter(Notification.id == id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found.")
        
    # Owner-only IDOR gate
    if notif.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied. You do not own this notification.")
        
    return {
        "id": notif.id,
        "warehouse_id": notif.warehouse_id,
        "event_type": notif.event_type,
        "category": EVENT_CATEGORIES.get(notif.event_type, "system"),
        "title": notif.title,
        "message": notif.message,
        "severity": notif.severity,
        "status": notif.status,
        "source_entity_type": notif.source_entity_type,
        "source_entity_id": notif.source_entity_id,
        "created_at": notif.created_at.isoformat() if notif.created_at else None,
        "read_at": notif.read_at.isoformat() if notif.read_at else None,
        "payload": json.loads(notif.notif_metadata) if notif.notif_metadata else {}
    }


@router.post("/notifications/{id}/read", summary="Mark notification as read")
def mark_read(
    id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Marks a single notification as read."""
    notif = db.query(Notification).filter(Notification.id == id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found.")
        
    if notif.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied.")
        
    notif.status = "READ"
    notif.read_at = datetime.now(UTC).replace(tzinfo=None)
    db.commit()
    
    # Audit trail
    ledger.append_entry(db, "NOTIFICATION_READ", {"notification_id": id, "user": user.username})
    return {"status": "success", "message": "Notification marked as read."}


@router.post("/notifications/{id}/unread", summary="Mark notification as unread")
def mark_unread(
    id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Marks a single notification back as unread."""
    notif = db.query(Notification).filter(Notification.id == id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found.")
        
    if notif.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied.")
        
    notif.status = "DELIVERED"
    notif.read_at = None
    db.commit()
    return {"status": "success", "message": "Notification marked as unread."}


@router.post("/notifications/{id}/dismiss", summary="Dismiss notification")
def dismiss_notification(
    id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Dismisses a notification by marking its status as CANCELLED."""
    notif = db.query(Notification).filter(Notification.id == id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found.")
        
    if notif.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied.")
        
    notif.status = "CANCELLED"
    db.commit()
    
    ledger.append_entry(db, "NOTIFICATION_DISMISSED", {"notification_id": id, "user": user.username})
    return {"status": "success", "message": "Notification dismissed."}


@router.post("/notifications/mark-all-read", summary="Mark all user notifications as read")
def mark_all_read(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Marks all unread In-App notifications for the current user as read."""
    unread = db.query(Notification).filter(
        Notification.user_id == user.id,
        Notification.channel == "IN_APP",
        Notification.status != "READ"
    ).all()
    
    now = datetime.now(UTC).replace(tzinfo=None)
    for n in unread:
        n.status = "READ"
        n.read_at = now
        
    db.commit()
    ledger.append_entry(db, "NOTIFICATION_ALL_READ", {"user": user.username, "count": len(unread)})
    return {"status": "success", "message": f"Marked {len(unread)} notifications as read."}


# ---------------------------------------------------------------------------
# Preferences API (Step 10)
# ---------------------------------------------------------------------------
@router.get("/notification-preferences", summary="Get user preferences")
def get_preferences(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Returns a list of notification preferences for all categories for the current user."""
    categories = ["orders", "inventory", "tasks", "robots", "ai", "security", "simulation", "system"]
    result = []
    
    for cat in categories:
        pref = get_user_preference(db, user.id, cat)
        result.append({
            "category": cat,
            "in_app_enabled": pref["in_app_enabled"],
            "email_enabled": pref["email_enabled"],
            "min_severity": pref["min_severity"]
        })
        
    return {"preferences": result}


@router.put("/notification-preferences", summary="Update user preferences")
def update_preferences(
    payload: PreferenceUpdateList,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Saves/Updates user-specific notification preferences.
    Validates categories and severity tags.
    """
    valid_categories = ["orders", "inventory", "tasks", "robots", "ai", "security", "simulation", "system"]
    valid_severities = ["INFO", "SUCCESS", "WARNING", "HIGH", "CRITICAL"]

    for item in payload.preferences:
        cat = item.category.lower()
        if cat not in valid_categories:
            raise HTTPException(status_code=400, detail=f"Invalid category: {item.category}")
            
        sev = item.min_severity.upper()
        if sev not in valid_severities:
            raise HTTPException(status_code=400, detail=f"Invalid severity level: {item.min_severity}")
            
        # Update or Insert
        pref = db.query(NotificationPreference).filter(
            NotificationPreference.user_id == user.id,
            NotificationPreference.category == cat
        ).first()
        
        if pref:
            pref.in_app_enabled = item.in_app_enabled
            pref.email_enabled = item.email_enabled
            pref.min_severity = sev
        else:
            new_pref = NotificationPreference(
                user_id=user.id,
                category=cat,
                in_app_enabled=item.in_app_enabled,
                email_enabled=item.email_enabled,
                min_severity=sev
            )
            db.add(new_pref)
            
    db.commit()
    ledger.append_entry(db, "NOTIFICATION_PREFERENCE_CHANGED", {"user": user.username})
    
    from backend.event_processor import publish_event
    publish_event(
        db=db,
        event_type="SENSITIVE_ACTION_COMPLETED",
        warehouse_id=None,
        source_entity_type="USER",
        source_entity_id=str(user.id),
        actor_user_id=user.id,
        severity="WARNING",
        payload={
            "message": f"User '{user.username}' updated their notification preferences.",
            "user": user.username
        }
    )
    return {"status": "success", "message": "Notification preferences updated successfully."}


# ---------------------------------------------------------------------------
# Notification History (Step 31)
# ---------------------------------------------------------------------------
@router.get("/notification-history", summary="Fetch administrative history log")
def get_notification_history(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    category: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    channel: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permissions.VIEW_AUDIT))
):
    """
    Audit ledger history for administrative and security auditing.
    Requires admin or auditor privileges.
    """
    q = db.query(Notification).order_by(desc(Notification.created_at))
    
    if category:
        event_types = [et for et, cat in EVENT_CATEGORIES.items() if cat.lower() == category.lower()]
        q = q.filter(Notification.event_type.in_(event_types))
    if severity:
        q = q.filter(Notification.severity == severity.upper())
    if channel:
        q = q.filter(Notification.channel == channel.upper())
    if status:
        q = q.filter(Notification.status == status.upper())
        
    total = q.count()
    rows = q.offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "history": [
            {
                "id": r.id,
                "recipient_username": r.user.username if r.user else "Unknown",
                "warehouse_id": r.warehouse_id,
                "event_type": r.event_type,
                "category": EVENT_CATEGORIES.get(r.event_type, "system"),
                "channel": r.channel,
                "status": r.status,
                "severity": r.severity,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "retry_count": r.retry_count
            }
            for r in rows
        ]
    }


# ---------------------------------------------------------------------------
# Warehouse Access / Scoping Management Helper
# ---------------------------------------------------------------------------
@router.post("/admin/user-warehouse-access", summary="Grant user warehouse access scope")
def grant_warehouse_access(
    payload: WarehouseAccessPayload,
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permissions.MANAGE_USERS))
):
    """Grants a user access scope for notifications and operations at a warehouse."""
    # Check if user exists
    target = db.query(User).filter(User.id == payload.user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target user not found.")
        
    # Check if access already exists
    existing = db.query(UserWarehouseAccess).filter(
        UserWarehouseAccess.user_id == payload.user_id,
        UserWarehouseAccess.warehouse_id == payload.warehouse_id
    ).first()
    
    if existing:
        return {"status": "success", "message": "Access already granted."}
        
    access = UserWarehouseAccess(
        user_id=payload.user_id,
        warehouse_id=payload.warehouse_id
    )
    db.add(access)
    db.commit()
    
    ledger.append_entry(db, "WAREHOUSE_ACCESS_GRANTED", {"user_id": payload.user_id, "warehouse_id": payload.warehouse_id, "by": user.username})
    return {"status": "success", "message": f"Granted access for user to {payload.warehouse_id}."}


# ---------------------------------------------------------------------------
# Test Email Delivery Connection Validation (Step 38)
# ---------------------------------------------------------------------------
@router.post("/notifications/test-email", summary="Validate SMTP email delivery configuration")
def test_email_notification(
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permissions.VIEW_SYSTEM_HEALTH))
):
    """Sends a safe validation message to check SMTP configuration settings."""
    if not email_service.email_configured():
        return {"success": False, "message": "Email SMTP service is currently unconfigured in .env."}
        
    res = email_service.test_email_connection()
    if not res.get("success"):
        return {"success": False, "message": f"SMTP Authentication failed: {res.get('message')}"}
        
    subject = "🔬 SMTP Configuration Validation Check — Warehouse OS"
    body = f"""Warehouse OS — Email Configuration Check
------------------------------------------------------------
This message confirms that the Warehouse OS system SMTP 
credentials are valid, operational, and connected.

Timestamp: {datetime.now(UTC).replace(tzinfo=None).strftime('%d %b %Y, %H:%M UTC')}
Validated By: {user.username} (Role: {user.role})

No further action is required.
"""
    cfg = email_service.get_smtp_config()
    recipient = cfg.get("ALERT_EMAIL_TO")
    success = email_service.send_email_alert(subject, body, recipient)
    if success:
        return {"success": True, "message": f"Test email successfully dispatched to {recipient}."}
    else:
        return {"success": False, "message": "Connection was successful, but email dispatch failed."}
