import os
import json
import logging
from datetime import datetime, timedelta, UTC
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.models import User, Warehouse, Notification, NotificationPreference, UserWarehouseAccess, AuditLedger
from backend import notifications as email_service
from backend import audit_ledger as ledger

logger = logging.getLogger("warehouse.event_processor")

# ---------------------------------------------------------------------------
# Categories & Severities (Step 5 & 6)
# ---------------------------------------------------------------------------
EVENT_CATEGORIES = {
    # Orders
    "ORDER_CREATED": "orders",
    "ORDER_RESERVED": "orders",
    "ORDER_PICKING_STARTED": "orders",
    "ORDER_PICKED": "orders",
    "ORDER_PACKED": "orders",
    "ORDER_SHIPPED": "orders",
    "ORDER_COMPLETED": "orders",
    "ORDER_CANCELLED": "orders",
    "ORDER_EXCEPTION": "orders",
    # Inventory
    "INVENTORY_CHANGED": "inventory",
    "LOW_STOCK": "inventory",
    "STOCKOUT_RISK": "inventory",
    "OVERSTOCK_RISK": "inventory",
    "INVENTORY_ADJUSTED": "inventory",
    "RECEIPT_COMPLETED": "inventory",
    "INVENTORY_ANOMALY": "inventory",
    # Tasks
    "TASK_CREATED": "tasks",
    "TASK_ASSIGNED": "tasks",
    "TASK_STARTED": "tasks",
    "TASK_COMPLETED": "tasks",
    "TASK_FAILED": "tasks",
    "TASK_OVERDUE": "tasks",
    "TASK_REASSIGNED": "tasks",
    "TASK_CANCELLED": "tasks",
    # Robots
    "ROBOT_ASSIGNED": "robots",
    "ROBOT_BATTERY_LOW": "robots",
    "ROBOT_BATTERY_CRITICAL": "robots",
    "ROBOT_FAILED": "robots",
    "ROBOT_RECOVERED": "robots",
    "ROBOT_MAINTENANCE": "robots",
    "ROBOT_OFFLINE": "robots",
    # Simulation
    "CONGESTION_WARNING": "simulation",
    "ROUTE_REPLANNED": "simulation",
    "COLLISION_AVOIDANCE_SPIKE": "simulation",
    "SIMULATION_STARTED": "simulation",
    "SIMULATION_COMPLETED": "simulation",
    "SIMULATION_FAILED": "simulation",
    "ROBOT_SIMULATION_FAILURE": "simulation",
    "CONGESTION_THRESHOLD_REACHED": "simulation",
    "CRITICAL_SIMULATION_EVENT": "simulation",
    # AI
    "AI_RECOMMENDATION_CREATED": "ai",
    "AI_RECOMMENDATION_APPROVED": "ai",
    "AI_RECOMMENDATION_REJECTED": "ai",
    "ANOMALY_DETECTED": "ai",
    "WAREHOUSE_RISK_HIGH": "ai",
    # Security
    "NEW_USER_CREATED": "security",
    "ACCOUNT_ACTIVATED": "security",
    "PASSWORD_CHANGED": "security",
    "ROLE_CHANGED": "security",
    "ACCOUNT_LOCKED": "security",
    "MULTIPLE_FAILED_LOGINS": "security",
    "SENSITIVE_ACTION_COMPLETED": "security",
    "AUDIT_INTEGRITY_FAILURE": "security",
    "USER_LOGIN": "security",
    "USER_LOGOUT": "security",
    # System
    "SYSTEM_WARNING": "system",
    "SYSTEM_ERROR": "system",
    "SERVICE_DEGRADED": "system",
    "DATABASE_WARNING": "system",
}

SEVERITY_LEVELS = {
    "INFO": 1,
    "SUCCESS": 2,
    "WARNING": 3,
    "HIGH": 4,
    "CRITICAL": 5
}

DEFAULT_PREFERENCES = {
    "orders": {"in_app_enabled": True, "email_enabled": True, "min_severity": "INFO"},
    "inventory": {"in_app_enabled": True, "email_enabled": True, "min_severity": "INFO"},
    "tasks": {"in_app_enabled": True, "email_enabled": True, "min_severity": "INFO"},
    "robots": {"in_app_enabled": True, "email_enabled": True, "min_severity": "INFO"},
    "ai": {"in_app_enabled": True, "email_enabled": True, "min_severity": "INFO"},
    "security": {"in_app_enabled": True, "email_enabled": True, "min_severity": "INFO"},
    "simulation": {"in_app_enabled": True, "email_enabled": True, "min_severity": "INFO"},
    "system": {"in_app_enabled": True, "email_enabled": True, "min_severity": "INFO"}
}


# ---------------------------------------------------------------------------
# Default Preference Getter & Initialization
# ---------------------------------------------------------------------------
def get_user_preference(db: Session, user_id: int, category: str) -> Dict[str, Any]:
    """Retrieve user's preferences, falling back to sensible system defaults."""
    pref = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == user_id,
        NotificationPreference.category == category
    ).first()
    
    if pref:
        return {
            "in_app_enabled": pref.in_app_enabled,
            "email_enabled": pref.email_enabled,
            "min_severity": pref.min_severity
        }
    
    return DEFAULT_PREFERENCES.get(category, {"in_app_enabled": True, "email_enabled": True, "min_severity": "INFO"})


def init_default_preferences(db: Session, user_id: int):
    """Seed default notification preferences for a new user account."""
    for category, val in DEFAULT_PREFERENCES.items():
        pref = NotificationPreference(
            user_id=user_id,
            category=category,
            in_app_enabled=val["in_app_enabled"],
            email_enabled=val["email_enabled"],
            min_severity=val["min_severity"]
        )
        db.add(pref)
    db.commit()


# ---------------------------------------------------------------------------
# Deduplication Check (Step 16)
# ---------------------------------------------------------------------------
def is_duplicate_event(db: Session, user_id: int, event_type: str, source_entity_type: Optional[str], source_entity_id: Optional[str], severity: str, window_minutes: int = 5) -> bool:
    """
    Checks if a matching notification was sent in the last window_minutes.
    High/Critical security alerts override deduplication check and are always sent.
    """
    if event_type in ["ACCOUNT_LOCKED", "AUDIT_INTEGRITY_FAILURE"] or severity in ["HIGH", "CRITICAL"]:
        return False
        
    cutoff = datetime.now(UTC).replace(tzinfo=None) - timedelta(minutes=window_minutes)
    dup = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.event_type == event_type,
        Notification.source_entity_type == source_entity_type,
        Notification.source_entity_id == source_entity_id,
        Notification.severity == severity,
        Notification.created_at >= cutoff
    ).first()
    
    return dup is not None


# ---------------------------------------------------------------------------
# Throttling Check (Step 17)
# ---------------------------------------------------------------------------
def is_email_throttled(db: Session, user_id: int, window_minutes: int = 10, max_emails: int = 5) -> bool:
    """Disables artificial email throttling to guarantee real-time delivery of operational and security alerts."""
    return False


# ---------------------------------------------------------------------------
# Recipient Resolution (Step 8 & 9)
# ---------------------------------------------------------------------------
def resolve_recipients(db: Session, event_type: str, warehouse_id: Optional[str], severity: str, source_details: Dict[str, Any]) -> List[User]:
    """
    Resolves eligible users based on roles, warehouse assignment access,
    preferences, and specific event filters.
    """
    category = EVENT_CATEGORIES.get(event_type, "system")
    users = db.query(User).filter(User.is_active == True).all()
    recipients = []

    for u in users:
        # 1. Warehouse Scope checks
        if warehouse_id and u.role != "admin":
            access = db.query(UserWarehouseAccess).filter(
                UserWarehouseAccess.user_id == u.id,
                UserWarehouseAccess.warehouse_id == warehouse_id
            ).first()
            if not access:
                continue

        # 2. Role suitability filtering
        role = u.role
        if category == "security":
            if role not in ["admin", "auditor"]:
                continue
        elif category == "ai":
            if role not in ["admin", "manager"]:
                continue
        elif category == "system":
            if role != "admin":
                continue
        elif category == "robots" or category == "simulation":
            if role not in ["admin", "manager", "operator"]:
                continue
        elif category == "tasks":
            assigned_user_id = source_details.get("assigned_user_id")
            if assigned_user_id and u.id != assigned_user_id and role != "manager" and role != "admin":
                continue
            if role not in ["admin", "manager", "operator"]:
                continue
        elif category == "inventory":
            if role not in ["admin", "manager", "operator"]:
                continue
        elif category == "orders":
            if role not in ["admin", "manager", "operator", "viewer"]:
                continue

        # 3. Preference matching
        pref = get_user_preference(db, u.id, category)
        is_security_override = (category == "security")
        event_sev_val = SEVERITY_LEVELS.get(severity, 1)
        pref_sev_val = SEVERITY_LEVELS.get(pref["min_severity"], 1)
        
        if is_security_override or (event_sev_val >= pref_sev_val):
            recipients.append(u)

    return recipients


# ---------------------------------------------------------------------------
# Email Templates Rendering (Step 14 & 15)
# ---------------------------------------------------------------------------
def build_email_body(event_type: str, severity: str, title: str, message: str, warehouse_id: Optional[str], details: Dict[str, Any]) -> str:
    """Builds a structured, professional, clean corporate-SaaS email template."""
    timestamp_str = datetime.now(UTC).replace(tzinfo=None).strftime("%d %b %Y, %H:%M UTC")
    
    body = f"""WAREHOUSE OS — ENTERPRISE SERVICE ALERT
------------------------------------------------------------
Priority: [{severity.upper()}]
Category: {EVENT_CATEGORIES.get(event_type, 'system').upper()}
Event Type: {event_type}

Title: {title}
Message: {message}

Operational Scope Details:
-------------------------
Warehouse: {warehouse_id or 'System-Wide'}
Generated At: {timestamp_str}
"""
    if details:
        body += "\nAssociated Metadata:\n"
        for k, v in details.items():
            if k not in ["assigned_user_id", "password", "otp"]: # sanitization (Step 14)
                body += f"- {k.replace('_', ' ').capitalize()}: {v}\n"
                
    body += """
------------------------------------------------------------
To take action or adjust your notification preferences,
please open your local Warehouse OS Dashboard.

This is an automated system notification. Please do not reply.
"""
    return body


# ---------------------------------------------------------------------------
# Event Processor Entrypoint (Step 2)
# ---------------------------------------------------------------------------
def publish_event(
    db: Session,
    event_type: str,
    warehouse_id: Optional[str],
    source_entity_type: Optional[str],
    source_entity_id: Optional[str],
    actor_user_id: Optional[int] = None,
    occurred_at: Optional[datetime] = None,
    severity: str = "INFO",
    payload: Optional[Dict[str, Any]] = None,
    background_tasks: Any = None
):
    """
    Main orchestrator of the Event-driven notification system:
    1. Categorizes the event and determines default rules.
    2. Resolves recipients.
    3. Handles event deduplication & throttling.
    4. Persists In-App notifications.
    5. Dispatches email alerts directly via SMTP on background thread.
    6. Appends verification entry to the cryptographically chain-linked Audit Ledger.
    """
    try:
        if occurred_at is None:
            occurred_at = datetime.now(UTC).replace(tzinfo=None)
        if payload is None:
            payload = {}

        category = EVENT_CATEGORIES.get(event_type, "system")
        title = f"{event_type.replace('_', ' ').title()} Alert"
        message = payload.get("message") or f"A {event_type} event occurred."
        
        # Step 8: Resolve recipients
        recipients = resolve_recipients(db, event_type, warehouse_id, severity, payload)
        smtp_cfg = email_service.get_smtp_config()
        configured_alert_email = smtp_cfg.get("ALERT_EMAIL_TO") or "harsha200797@gmail.com"

        for u in recipients:
            try:
                u_id = u.id
                u_username = u.username
                u_email = u.email
            except Exception as e:
                logger.warning("Skipping notification recipient due to expired/deleted user state: %s", e)
                continue

            # Target email resolution: use user email or fallback to Settings configured alert email
            dummy_domains = ["@example.com", "@wms.com", "@local", "@localhost", "@test.com", "@domain.com"]
            is_dummy = not u_email or any(dom in u_email.lower() for dom in dummy_domains)
            target_email = configured_alert_email if is_dummy else u_email

            # Check preferences for channels
            pref = get_user_preference(db, u_id, category)
            is_security_override = (category == "security")
            
            in_app_ok = is_security_override or pref.get("in_app_enabled", True)
            email_ok = is_security_override or pref.get("email_enabled", True)
            
            # Idempotency key (Step 20)
            idempotency_key = f"{event_type}_{source_entity_id or 'sys'}_{u_id}_{occurred_at.timestamp()}"
            
            # Step 16: Deduplication Check
            if is_duplicate_event(db, u_id, event_type, source_entity_type, source_entity_id, severity):
                logger.debug("Event %s duplicate detected for user %s; skipping notification.", event_type, u_username)
                continue
                
            # Create In-App Notification (Step 12)
            if in_app_ok:
                notif = Notification(
                    user_id=u_id,
                    warehouse_id=warehouse_id,
                    event_type=event_type,
                    notification_type=f"{category.upper()}_ALERT",
                    title=title,
                    message=message,
                    severity=severity,
                    status="DELIVERED",  # delivered instantly for in-app
                    channel="IN_APP",
                    source_entity_type=source_entity_type,
                    source_entity_id=source_entity_id,
                    created_at=occurred_at,
                    delivered_at=datetime.now(UTC).replace(tzinfo=None),
                    idempotency_key=idempotency_key,
                    notif_metadata=json.dumps(payload)
                )
                db.add(notif)
                db.commit()
 
            # Create Email Notification (Step 14)
            if email_ok and target_email:
                # Create PENDING/QUEUED email record
                email_notif = Notification(
                    user_id=u_id,
                    warehouse_id=warehouse_id,
                    event_type=event_type,
                    notification_type=f"{category.upper()}_ALERT",
                    title=title,
                    message=message,
                    severity=severity,
                    status="QUEUED",
                    channel="EMAIL",
                    source_entity_type=source_entity_type,
                    source_entity_id=source_entity_id,
                    created_at=occurred_at,
                    idempotency_key=f"email_{idempotency_key}",
                    notif_metadata=json.dumps(payload)
                )
                db.add(email_notif)
                db.commit()
                
                # Render email templates
                subject = f"[{severity.upper()}] {title} — Warehouse OS"
                body_content = build_email_body(event_type, severity, title, message, warehouse_id, payload)
                
                # Directly dispatch via thread-safe daemon background worker
                if os.getenv("ENVIRONMENT") == "testing":
                    _send_email_async_thread(email_notif.id, subject, body_content, target_email)
                else:
                    import threading
                    threading.Thread(
                        target=_send_email_async_thread,
                        args=(email_notif.id, subject, body_content, target_email),
                        daemon=True
                    ).start()


                    
        # Publish event message to RabbitMQ topic exchange
        try:
            from backend import mq_client
            payload_data = {
                "warehouse_id": warehouse_id,
                "source_entity_type": source_entity_type,
                "source_entity_id": source_entity_id,
                "severity": severity,
                "occurred_at": occurred_at.isoformat() if hasattr(occurred_at, "isoformat") else str(occurred_at),
                "message": message
            }
            if background_tasks:
                background_tasks.add_task(
                    mq_client.publish_event,
                    event_type=event_type,
                    category=category,
                    payload=payload_data
                )
            else:
                import threading
                threading.Thread(
                    target=mq_client.publish_event,
                    kwargs={
                        "event_type": event_type,
                        "category": category,
                        "payload": payload_data
                    },
                    daemon=True
                ).start()
        except Exception as mq_err:
            logger.warning("RabbitMQ event publish failed: %s", mq_err)

        # Step 33: Auditing integration with the tamper-evident ledger
        audit_details = {
            "event_type": event_type,
            "warehouse_id": warehouse_id,
            "severity": severity,
            "source_entity_id": source_entity_id,
            "source_entity_type": source_entity_type,
            "recipients_count": len(recipients)
        }
        ledger.append_entry(db, f"NOTIF_PUBLISHED_{event_type}", audit_details)
        
    except Exception as e:
        logger.error("Failed to publish event %s: %s", event_type, e, exc_info=True)


def _send_email_async(db: Session, notification_id: int, subject: str, body: str, recipient: str):
    """Executes the asynchronous email dispatch with retry logic."""
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        return
        
    max_retries = 3
    success = False
    
    while notif.retry_count < max_retries:
        try:
            success = email_service.send_email_alert(subject, body, recipient)
            if success:
                break
        except Exception as err:
            logger.error("SMTP delivery failed for notification ID %s: %s", notification_id, err)
            
        notif.retry_count += 1
        db.commit()
        
    if success:
        notif.status = "SENT"
        notif.delivered_at = datetime.now(UTC).replace(tzinfo=None)
    else:
        notif.status = "FAILED"
        notif.failed_at = datetime.now(UTC).replace(tzinfo=None)
        
    db.commit()


def _send_email_async_thread(notification_id: int, subject: str, body: str, recipient: str):
    """Worker function for threading to safely manage database session lifetime."""
    from backend.database import SessionLocal
    db = SessionLocal()
    try:
        _send_email_async(db, notification_id, subject, body, recipient)
    except Exception as err:
        logger.error("Async thread email worker failed: %s", err)
    finally:
        db.close()
