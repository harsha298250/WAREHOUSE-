"""
routers/security.py — Phase 9: Security Center & Audit Ledger API

Endpoints:
  GET  /security/dashboard      — KPIs and security posture summary
  GET  /security/events         — Recent security events
  GET  /audit/ledger            — Paginated audit log with filtering
  GET  /audit/verify            — Hash chain integrity verification
  GET  /security/permissions    — Role-permission matrix (public)
"""
import logging
from datetime import datetime, timedelta, UTC
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from backend.database import get_db
from backend.models import User, AccessLog, AuditLedger, SecurityEvent, UserSession
from backend.auth import (
    get_current_user,
    require_permission,
    ROLE_PERMISSIONS,
    Permissions,
)
from backend import audit_ledger as ledger

logger = logging.getLogger("warehouse")
router = APIRouter()


# ---------------------------------------------------------------------------
# Security Dashboard
# ---------------------------------------------------------------------------

@router.get("/security/dashboard")
def security_dashboard(
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permissions.VIEW_SECURITY))
):
    """
    Returns a comprehensive security posture summary:
    - User counts (active, inactive, locked, unverified)
    - Recent failed login count
    - Login method breakdown
    - Recent security events
    """
    now = datetime.now(UTC).replace(tzinfo=None)
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)

    all_users = db.query(User).all()
    active_users = [u for u in all_users if getattr(u, "is_active", True)]
    inactive_users = [u for u in all_users if not getattr(u, "is_active", True)]
    locked_users = [u for u in all_users if u.locked_until and u.locked_until > now]
    unverified_users = [u for u in all_users if not getattr(u, "is_verified", True)]

    # Recent access log analysis
    recent_events = db.query(AccessLog).filter(AccessLog.timestamp >= last_24h).all()
    failed_login_events = [e for e in recent_events if "login" in e.action.lower() and e.action not in ["login", "google_oauth_login", "recovery_login"]]
    login_events_24h = [e for e in recent_events if e.action in ["login", "google_oauth_login", "recovery_login"]]

    # Role distribution
    role_counts: dict = {}
    for u in all_users:
        role_counts[u.role] = role_counts.get(u.role, 0) + 1

    # Login method breakdown
    login_method_counts: dict = {}
    for u in all_users:
        method = u.login_method or "unknown"
        login_method_counts[method] = login_method_counts.get(method, 0) + 1

    # Audit ledger stats
    total_audit_entries = db.query(func.count(AuditLedger.id)).scalar() or 0
    recent_audit = db.query(AuditLedger).filter(AuditLedger.timestamp >= last_24h).count()

    # Recent security events from access log
    security_events = (
        db.query(AccessLog)
        .filter(AccessLog.timestamp >= last_7d)
        .order_by(desc(AccessLog.timestamp))
        .limit(20)
        .all()
    )

    # Chain integrity (quick check on last 10 entries)
    chain_status = ledger.verify_chain(db)

    return {
        "summary": {
            "total_users": len(all_users),
            "active_users": len(active_users),
            "inactive_users": len(inactive_users),
            "locked_accounts": len(locked_users),
            "unverified_accounts": len(unverified_users),
            "logins_last_24h": len(login_events_24h),
            "audit_entries_total": total_audit_entries,
            "audit_entries_24h": recent_audit,
        },
        "role_distribution": role_counts,
        "login_method_breakdown": login_method_counts,
        "locked_accounts_detail": [
            {
                "id": u.id,
                "username": u.username,
                "role": u.role,
                "locked_until": u.locked_until.isoformat() if u.locked_until else None,
                "failed_login_count": u.failed_login_count or 0,
            }
            for u in locked_users
        ],
        "recent_security_events": [
            {
                "timestamp": e.timestamp.isoformat() if e.timestamp else "",
                "username": e.username,
                "action": e.action,
                "ip_address": e.ip_address,
            }
            for e in security_events
        ],
        "audit_chain_integrity": chain_status,
        "generated_at": now.isoformat(),
    }


# ---------------------------------------------------------------------------
# Security Events Feed
# ---------------------------------------------------------------------------

@router.get("/security/events")
def security_events(
    limit: int = Query(50, ge=1, le=500),
    action_filter: Optional[str] = Query(None),
    username_filter: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permissions.VIEW_SECURITY))
):
    """Recent security events from the access log."""
    q = db.query(AccessLog).order_by(desc(AccessLog.timestamp))
    if action_filter:
        q = q.filter(AccessLog.action.ilike(f"%{action_filter}%"))
    if username_filter:
        q = q.filter(AccessLog.username.ilike(f"%{username_filter}%"))
    rows = q.limit(limit).all()
    return [
        {
            "id": r.id,
            "timestamp": r.timestamp.isoformat() if r.timestamp else "",
            "username": r.username,
            "action": r.action,
            "warehouse_id": r.warehouse_id,
            "ip_address": r.ip_address,
        }
        for r in rows
    ]


# ---------------------------------------------------------------------------
# Audit Ledger Endpoints
# ---------------------------------------------------------------------------

@router.get("/audit/ledger")
def get_audit_ledger(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    event_type_filter: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permissions.VIEW_AUDIT))
):
    """Paginated, filterable audit ledger — ordered newest first."""
    q = db.query(AuditLedger).order_by(desc(AuditLedger.id))
    if event_type_filter:
        q = q.filter(AuditLedger.event_type.ilike(f"%{event_type_filter}%"))

    total = q.count()
    rows = q.offset(offset).limit(limit).all()

    import json
    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "entries": [
            {
                "id": r.id,
                "timestamp": r.timestamp.isoformat() if r.timestamp else "",
                "event_type": r.event_type,
                "details": json.loads(r.details) if r.details else {},
                "hash": r.hash,
                "prev_hash": r.prev_hash,
            }
            for r in rows
        ]
    }


@router.get("/audit/verify")
def verify_audit_chain(
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permissions.VIEW_AUDIT))
):
    """
    Verify the SHA-256 hash chain integrity of the tamper-evident audit ledger.
    Returns: {valid: bool, checked: int, broken_at: int|null}
    """
    result = ledger.verify_chain(db)
    if not result["valid"]:
        from backend.event_processor import publish_event
        publish_event(
            db=db,
            event_type="AUDIT_INTEGRITY_FAILURE",
            warehouse_id=None,
            source_entity_type="AUDIT_LEDGER",
            source_entity_id=str(result.get("broken_at", "unknown")),
            severity="CRITICAL",
            payload={"message": f"Tamper Alert: Cryptographic chain mismatch detected at entry #{result.get('broken_at')}."}
        )
    total = db.query(func.count(AuditLedger.id)).scalar() or 0
    return {
        "valid": result["valid"],
        "checked_entries": result["checked"],
        "records_checked": result["checked"],
        "broken_at_entry": result["broken_at"],
        "broken_at_record": result["broken_at"],
        "total_entries": total,
        "total_records": total,
        "verified_at": datetime.now(UTC).replace(tzinfo=None).isoformat(),
        "integrity_status": "INTACT" if result["valid"] else "COMPROMISED",
        "message": f"Audit ledger integrity verified across {result['checked']} records." if result["valid"] else f"Audit ledger integrity failure detected at record #{result['broken_at']}!"
    }


# ---------------------------------------------------------------------------
# Permissions Reference
# ---------------------------------------------------------------------------

@router.get("/security/permissions")
def get_permissions_matrix(user=Depends(get_current_user)):
    """Return the role-permission matrix (useful for frontend navigation gating)."""
    return {
        "current_user_role": user.role,
        "current_user_permissions": sorted(list(ROLE_PERMISSIONS.get(user.role, set()))),
        "role_matrix": {
            role: sorted(list(perms))
            for role, perms in ROLE_PERMISSIONS.items()
        }
    }


# ---------------------------------------------------------------------------
# Phase 18: Security Events endpoints (SecurityEvent table)
# ---------------------------------------------------------------------------

SEVERITY_FILTER_MAP = {
    "logins": ["LOGIN_SUCCESS", "LOGIN_FAILED", "LOGIN_OTP_SENT", "LOGIN_OTP_SUCCESS", "LOGIN_OTP_FAILED", "OAUTH_LOGIN", "RECOVERY_LOGIN"],
    "failed": ["LOGIN_FAILED", "LOGIN_OTP_FAILED", "OTP_FAILED"],
    "role_changes": ["ROLE_CHANGED"],
    "password_changes": ["PASSWORD_CHANGED"],
    "oauth": ["OAUTH_LOGIN"],
    "critical": None,  # handled by severity filter
}


def _format_security_event(e: SecurityEvent) -> dict:
    import json as _json
    details_dict = _json.loads(e.details) if e.details else {}
    return {
        "id": e.id,
        "event_type": e.event_type,
        "severity": e.severity,
        "status": e.status,
        "actor_username": e.actor_username,
        "target_username": e.target_username,
        "actor_user_id": e.actor_user_id,
        "target_user_id": e.target_user_id,
        "authentication_method": e.authentication_method,
        "role_at_event": e.role_at_event,
        "previous_value": e.previous_value,
        "new_value": e.new_value,
        "ip_address": e.ip_address,
        "device": e.device,
        "browser": e.browser,
        "os": e.os,
        "location": details_dict.get("approximate_location", "Location unavailable"),
        "correlation_id": e.correlation_id,
        "audit_ledger_ref": e.audit_ledger_ref,
        "timestamp": e.timestamp.isoformat() if e.timestamp else "",
        "details": details_dict,
    }


@router.get("/security/events/rich")
def security_events_rich(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    category: Optional[str] = Query(None, description="logins|failed|role_changes|password_changes|oauth|critical"),
    severity: Optional[str] = Query(None, description="INFO|WARNING|CRITICAL"),
    username: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None, description="ISO date YYYY-MM-DD"),
    date_to: Optional[str] = Query(None, description="ISO date YYYY-MM-DD"),
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permissions.VIEW_SECURITY)),
):
    """Phase 18: Rich security events from SecurityEvent table with full metadata."""
    q = db.query(SecurityEvent).order_by(desc(SecurityEvent.timestamp))

    if category == "critical":
        q = q.filter(SecurityEvent.severity == "CRITICAL")
    elif category and category in SEVERITY_FILTER_MAP:
        event_types = SEVERITY_FILTER_MAP[category]
        if event_types:
            q = q.filter(SecurityEvent.event_type.in_(event_types))

    if severity:
        q = q.filter(SecurityEvent.severity == severity.upper())

    if username:
        q = q.filter(
            (SecurityEvent.actor_username.ilike(f"%{username}%")) |
            (SecurityEvent.target_username.ilike(f"%{username}%"))
        )

    if date_from:
        try:
            q = q.filter(SecurityEvent.timestamp >= datetime.fromisoformat(date_from))
        except ValueError:
            pass
    if date_to:
        try:
            q = q.filter(SecurityEvent.timestamp <= datetime.fromisoformat(date_to + "T23:59:59"))
        except ValueError:
            pass

    total = q.count()
    rows = q.offset(offset).limit(limit).all()
    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "events": [_format_security_event(e) for e in rows],
    }


@router.get("/security/events/rich/{event_id}")
def security_event_detail(
    event_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permissions.VIEW_SECURITY)),
):
    """Phase 18: Full detail for a specific security event."""
    event = db.query(SecurityEvent).filter(SecurityEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Security event not found")
    return _format_security_event(event)


@router.get("/security/my-activity")
def my_security_activity(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Phase 18: View the current user's own security activity (no privilege escalation)."""
    events = (
        db.query(SecurityEvent)
        .filter(
            (SecurityEvent.actor_user_id == user.id) |
            (SecurityEvent.target_user_id == user.id)
        )
        .order_by(desc(SecurityEvent.timestamp))
        .limit(limit)
        .all()
    )
    return {
        "username": user.username,
        "total": len(events),
        "events": [_format_security_event(e) for e in events],
    }


@router.get("/security/summary")
def security_summary(
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permissions.VIEW_SECURITY)),
):
    """Phase 18: Lightweight KPI summary for the main dashboard security widget."""
    now = datetime.now(UTC).replace(tzinfo=None)
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)

    total_events = db.query(func.count(SecurityEvent.id)).scalar() or 0
    if total_events == 0:
        return {
            "available": False,
            "message": "NO SECURITY EVENTS AVAILABLE",
        }

    successful_logins_24h = db.query(func.count(SecurityEvent.id)).filter(
        SecurityEvent.event_type == "LOGIN_SUCCESS",
        SecurityEvent.timestamp >= last_24h,
    ).scalar() or 0

    failed_attempts_24h = db.query(func.count(SecurityEvent.id)).filter(
        SecurityEvent.event_type.in_(["LOGIN_FAILED", "LOGIN_OTP_FAILED"]),
        SecurityEvent.timestamp >= last_24h,
    ).scalar() or 0

    critical_events_7d = db.query(func.count(SecurityEvent.id)).filter(
        SecurityEvent.severity == "CRITICAL",
        SecurityEvent.timestamp >= last_7d,
    ).scalar() or 0

    recent_events = (
        db.query(SecurityEvent)
        .order_by(desc(SecurityEvent.timestamp))
        .limit(5)
        .all()
    )

    return {
        "available": True,
        "logins_24h": successful_logins_24h,
        "failed_attempts_24h": failed_attempts_24h,
        "critical_events_7d": critical_events_7d,
        "total_events": total_events,
        "recent_events": [_format_security_event(e) for e in recent_events],
        "generated_at": now.isoformat(),
    }


@router.post("/security/sessions/{session_id}/revoke")
def revoke_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permissions.MANAGE_USERS)),
):
    """Phase 18: Revoke an active user session (admin/manager only). Audited."""
    session = db.query(UserSession).filter(UserSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.revoked_at:
        raise HTTPException(status_code=400, detail="Session is already revoked")

    session.revoked_at = datetime.now(UTC).replace(tzinfo=None)
    session.revoke_reason = "admin_revoke"
    db.commit()

    ledger.append_entry(db, "session_revoked", {
        "session_id": session_id,
        "user_id": session.user_id,
        "revoked_by": current_user.username,
        "time": datetime.now(UTC).replace(tzinfo=None).isoformat(),
    })

    from backend.services import security_service
    security_service.create_security_event(
        db=db,
        event_type="SESSION_REVOKED",
        severity="WARNING",
        status="SUCCESS",
        actor_user_id=current_user.id,
        target_user_id=session.user_id,
        actor_username=current_user.username,
        extra_details={"session_id": session_id, "reason": "admin_revoke"},
    )
    return {"status": "success", "message": f"Session {session_id} has been revoked."}
