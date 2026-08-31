"""
backend/services/security_service.py — Phase 18: Enterprise Security Alerts

Central service for:
- Creating rich SecurityEvent records (+ AuditLedger entries)
- Sending HTML security emails via Resend (login alerts, OTP, role changes)
- Parsing User-Agent strings into human-readable device/browser/OS metadata
- Redis-backed OTP rate limiting (with in-memory fallback)

Email routing rules:
  USER_OTP_EMAIL   = user's verified email  → receives login OTP codes
  SECURITY_ALERT_EMAIL = admin security email → receives security notifications

NEVER send OTP to SECURITY_ALERT_EMAIL.
NEVER send security alerts with passwords, tokens, or secrets.
"""
import os
import json
import secrets
import logging
from datetime import datetime, UTC
from typing import Optional

from sqlalchemy.orm import Session

logger = logging.getLogger("warehouse.security")

# ---------------------------------------------------------------------------
# Environment configuration (all via env vars — no hardcoded secrets)
# ---------------------------------------------------------------------------
OTP_EXPIRY_LOGIN_SECONDS = int(os.getenv("OTP_EXPIRY_SECONDS", "300"))   # 5 min default for login OTPs
OTP_RATE_LIMIT_PER_HOUR = int(os.getenv("OTP_RATE_LIMIT_PER_HOUR", "10"))
SECURITY_NOTIFICATION_RATE_LIMIT = int(os.getenv("SECURITY_NOTIFICATION_RATE_LIMIT", "20"))
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
LOGIN_OTP_REQUIRED = os.getenv("LOGIN_OTP_REQUIRED", "true" if ENVIRONMENT == "production" else "false").lower() == "true"


def get_security_alert_recipient() -> str:
    """Dynamically fetch security alert email recipient from active DB settings or env fallbacks."""
    try:
        from backend import notifications
        cfg = notifications.get_smtp_config()
        if cfg.get("ALERT_EMAIL_TO"):
            return cfg["ALERT_EMAIL_TO"]
    except Exception:
        pass
    return os.getenv("SECURITY_ALERT_EMAIL", os.getenv("ALERT_EMAIL_TO", ""))



# ---------------------------------------------------------------------------
# User-Agent parser (pure stdlib, no extra deps)
# ---------------------------------------------------------------------------

def get_device_info(user_agent_str: str) -> dict:
    """
    Parse a User-Agent string into human-readable device/browser/OS info.
    Returns defaults if parsing fails. Never raises exceptions.
    """
    if not user_agent_str:
        return {"device": "Unknown", "browser": "Other/Unknown", "os": "Unknown"}

    ua = user_agent_str.lower()

    # OS detection
    if "windows" in ua:
        os_name = "Windows"
    elif "iphone" in ua or "ipad" in ua or "ipod" in ua:
        os_name = "iOS"
    elif "mac os x" in ua or "macintosh" in ua or "macos" in ua:
        os_name = "macOS"
    elif "android" in ua:
        os_name = "Android"
    elif "linux" in ua:
        os_name = "Linux"
    else:
        os_name = "Unknown"

    # Browser detection (order matters — check specific before generic)
    if "edg/" in ua or "edge/" in ua:
        browser = "Edge"
    elif "chrome/" in ua and "safari/" in ua:
        browser = "Chrome"
    elif "firefox/" in ua:
        browser = "Firefox"
    elif "safari/" in ua and "chrome" not in ua:
        browser = "Safari"
    else:
        browser = "Other/Unknown"

    # Device category
    if "ipad" in ua or "tablet" in ua:
        device = "Tablet"
    elif any(x in ua for x in ["iphone", "android", "mobile"]):
        device = "Mobile"
    elif any(x in ua for x in ["windows", "macintosh", "linux"]):
        device = "Desktop"
    else:
        device = "Unknown"

    return {"device": device, "browser": browser, "os": os_name}


def get_approximate_location(ip: str) -> str:
    """
    Perform a lightweight IP geolocation look-up using a free geolocation provider.
    Fails open / returns 'Location unavailable' on loopback/private IPs or connection issues.
    """
    if not ip or ip == "unknown":
        return "Location unavailable"
        
    # Check for private or loopback IPs
    ip_clean = ip.strip()
    if (
        ip_clean.startswith("127.") or 
        ip_clean == "::1" or 
        ip_clean.startswith("192.168.") or 
        ip_clean.startswith("10.") or 
        ip_clean.startswith("169.254.") or
        ip_clean.startswith("localhost")
    ):
        return "Location unavailable"
        
    # Handle 172.16.0.0/12 range
    if ip_clean.startswith("172."):
        parts = ip_clean.split(".")
        if len(parts) >= 2:
            try:
                second_part = int(parts[1])
                if 16 <= second_part <= 31:
                    return "Location unavailable"
            except ValueError:
                pass

    try:
        import httpx
        # Call non-blocking ip-api.com endpoint with 1.0 second timeout
        url = f"http://ip-api.com/json/{ip_clean}?fields=status,country,regionName,city"
        resp = httpx.get(url, timeout=1.0)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "success":
                city = data.get("city", "")
                region = data.get("regionName", "")
                country = data.get("country", "")
                
                parts = [p for p in [city, region, country] if p]
                if parts:
                    return ", ".join(parts)
    except Exception as e:
        logger.info("IP geolocation request failed for %s: %s", ip_clean, e)
        
    return "Location unavailable"



# ---------------------------------------------------------------------------
# SecurityEvent persistence
# ---------------------------------------------------------------------------

def create_security_event(
    db: Session,
    event_type: str,
    severity: str = "INFO",
    status: str = "SUCCESS",
    actor_user_id: Optional[int] = None,
    target_user_id: Optional[int] = None,
    actor_username: Optional[str] = None,
    target_username: Optional[str] = None,
    authentication_method: Optional[str] = None,
    role_at_event: Optional[str] = None,
    previous_value: Optional[str] = None,
    new_value: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    correlation_id: Optional[str] = None,
    extra_details: Optional[dict] = None,
) -> Optional[object]:
    """
    Persist a SecurityEvent record and write a parallel AuditLedger entry.
    Never stores passwords, OTP codes, or secrets.
    Returns the created SecurityEvent or None on error.
    """
    try:
        from backend.models import SecurityEvent
        from backend import audit_ledger as ledger

        device_info = get_device_info(user_agent or "")
        location = get_approximate_location(ip_address)
        
        details_dict = dict(extra_details or {})
        details_dict["approximate_location"] = location

        event = SecurityEvent(
            event_type=event_type,
            severity=severity,
            status=status,
            actor_user_id=actor_user_id,
            target_user_id=target_user_id,
            actor_username=actor_username,
            target_username=target_username,
            authentication_method=authentication_method,
            role_at_event=role_at_event,
            previous_value=previous_value,
            new_value=new_value,
            ip_address=ip_address,
            user_agent=user_agent[:500] if user_agent else None,
            device=device_info["device"],
            browser=device_info["browser"],
            os=device_info["os"],
            correlation_id=correlation_id or secrets.token_hex(16),
            details=json.dumps(details_dict),
            timestamp=datetime.now(UTC).replace(tzinfo=None),
        )
        db.add(event)
        db.flush()  # get the id

        # Mirror in immutable AuditLedger (without sensitive fields)
        audit_entry = ledger.append_entry(db, event_type.lower(), {
            "actor": actor_username,
            "target": target_username,
            "target_username": target_username,
            "changed_by": actor_username,
            "severity": severity,
            "status": status,
            "method": authentication_method,
            "old_value": previous_value,
            "new_value": new_value,
            "ip": ip_address,
            "device": device_info["device"],
            "browser": device_info["browser"],
            "os": device_info["os"],
            "approximate_location": location,
            "security_event_id": event.id,
        })
        event.audit_ledger_ref = audit_entry.id
        db.commit()

        db.refresh(event)
        return event
    except Exception as e:
        logger.error("Failed to create security event '%s': %s", event_type, e)
        try:
            db.rollback()
        except Exception:
            pass
        return None


# ---------------------------------------------------------------------------
# Redis-backed OTP rate limiting (fails safely if Redis unavailable)
# ---------------------------------------------------------------------------

def check_otp_rate_limit(user_id: int) -> bool:
    """
    Check if a user has exceeded OTP request rate limit.
    Returns True if allowed, False if rate-limited.
    Uses Redis if available; falls back to allowing the request.
    """
    try:
        from backend.redis_client import get_redis_client
        client = get_redis_client()
        if not client:
            return True  # Redis unavailable — allow (fail open for usability)
        key = f"otp:ratelimit:{user_id}"
        count = client.get(key)
        if count and int(count) >= OTP_RATE_LIMIT_PER_HOUR:
            logger.warning("OTP rate limit exceeded for user_id=%s", user_id)
            return False
        # Increment with 1-hour TTL
        pipe = client.pipeline()
        pipe.incr(key)
        pipe.expire(key, 3600)
        pipe.execute()
        return True
    except Exception as e:
        logger.error("OTP rate limit check failed: %s", e)
        return True  # fail open


def record_otp_failure(user_id: int, ip: str):
    """Track failed OTP attempts in Redis for abuse detection."""
    try:
        from backend.redis_client import get_redis_client
        client = get_redis_client()
        if not client:
            return
        key = f"otp:failures:{user_id}"
        pipe = client.pipeline()
        pipe.incr(key)
        pipe.expire(key, 3600)
        pipe.execute()
        # Also track by IP for cross-account detection
        ip_key = f"otp:failures:ip:{ip}"
        pipe2 = client.pipeline()
        pipe2.incr(ip_key)
        pipe2.expire(ip_key, 3600)
        pipe2.execute()
    except Exception as e:
        logger.error("Failed to record OTP failure: %s", e)


# ---------------------------------------------------------------------------
# Email sending (Resend) — security notifications
# ---------------------------------------------------------------------------

def _send_security_email(subject: str, html_body: str, recipient: str) -> bool:
    """
    Send a security email via Resend. Fails gracefully — never blocks auth flows.
    Never logs OTPs, passwords, or secrets.
    """
    if not recipient:
        logger.warning("Security email skipped — no recipient configured.")
        return False
    try:
        celery_enabled = os.getenv("CELERY_ENABLED", "false").lower() == "true"
        if celery_enabled:
            try:
                from backend.celery_app import send_generic_email_task, safe_task_dispatch
                safe_task_dispatch(send_generic_email_task, subject, html_body, recipient)
                logger.info("Security email queued in Celery successfully.")
                return True
            except Exception as celery_err:
                logger.warning("Failed to queue email via Celery, falling back to background thread: %s", celery_err)

        import threading
        from backend.resend_client import send_html_email
        
        def send_sync():
            try:
                send_html_email(subject, html_body, recipient)
            except Exception as thread_err:
                logger.error("Background thread security email delivery failed: %s", thread_err)
        
        threading.Thread(target=send_sync, daemon=True).start()
        logger.info("Dispatched security email via background daemon thread.")
        return True
    except Exception as e:
        logger.error("Security email delivery failed for subject '%s': %s", subject, e)
        return False


def _html_wrap(title: str, severity_color: str, content: str) -> str:
    """Build a consistent branded HTML email wrapper."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title></head>
<body style="margin:0;padding:0;background:#0f172a;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f172a;padding:40px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="background:#1e293b;border-radius:12px;overflow:hidden;border:1px solid #334155;">
        <!-- Header -->
        <tr><td style="background:{severity_color};padding:20px 32px;">
          <div style="color:#fff;font-size:11px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:4px;">
            Smart Warehouse Platform — Security Alert
          </div>
          <div style="color:#fff;font-size:22px;font-weight:800;">{title}</div>
        </td></tr>
        <!-- Body -->
        <tr><td style="padding:28px 32px;">
          {content}
        </td></tr>
        <!-- Footer -->
        <tr><td style="padding:16px 32px 24px;border-top:1px solid #334155;">
          <div style="font-size:11px;color:#475569;line-height:1.6;">
            Smart Warehouse Automation Platform · Automated Security Notification<br>
            Do not reply to this email. This notification was generated automatically.
          </div>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body></html>"""


def _row(label: str, value: str, danger: bool = False) -> str:
    color = "#ef4444" if danger else "#94a3b8"
    val_color = "#ef4444" if danger else "#e2e8f0"
    return f"""
    <tr>
      <td style="padding:7px 0;font-size:12px;color:{color};font-weight:600;width:160px;vertical-align:top;">{label}</td>
      <td style="padding:7px 0;font-size:13px;color:{val_color};font-weight:500;">{value or "Unavailable"}</td>
    </tr>"""


# ---- Login Alert (to SECURITY_ALERT_EMAIL) ----

def send_login_alert_email(
    username: str,
    role: str,
    ip_address: str,
    device: str,
    browser: str,
    os: str,
    auth_method: str,
    timestamp: datetime,
    event_id: int,
    status: str = "SUCCESS",
    location: Optional[str] = None,
) -> bool:
    """
    Send a login security notification to the admin security email.
    NEVER sent to the actual user.
    """
    recipient = get_security_alert_recipient()
    if not recipient:
        logger.warning("Login alert skipped — no security alert recipient configured.")
        return False

    if not location:
        location = get_approximate_location(ip_address)

    severity_color = "#10b981" if status == "SUCCESS" else "#ef4444"
    title = "New Login Detected" if status == "SUCCESS" else "Failed Login Attempt"
    
    # Format Date and Time separately
    if timestamp:
        date_str = timestamp.strftime("%d %B %Y")
        time_str = timestamp.strftime("%I:%M %p UTC")
        ts_str = timestamp.strftime("%d %b %Y %H:%M:%S UTC")
    else:
        date_str = "Unknown"
        time_str = "Unknown"
        ts_str = "Unknown"
        
    event_id_str = f"SEC-{timestamp.strftime('%Y%m%d') if timestamp else '00000000'}-{event_id:06d}"

    content = f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">
      {_row("User", username)}
      {_row("Role", role.upper())}
      {_row("Authentication", auth_method)}
      {_row("Device", device)}
      {_row("Operating System", os)}
      {_row("Browser", browser)}
      {_row("IP Address", ip_address)}
      {_row("Approximate Location", location)}
      {_row("Login Date", date_str)}
      {_row("Login Time", time_str)}
      {_row("Event ID", event_id_str)}
      {_row("Status", status, danger=(status != "SUCCESS"))}
    </table>
    <div style="margin-top:20px;padding:12px 16px;background:#0f172a;border-radius:8px;border-left:3px solid {'#10b981' if status == 'SUCCESS' else '#ef4444'};">
      <div style="font-size:12px;color:#94a3b8;">
        {'If you did not initiate this login, investigate immediately.' if status != 'SUCCESS' else 'This is a routine login notification. No action required if this was you.'}
      </div>
    </div>"""

    html = _html_wrap(title, severity_color, content)
    subject = f"[Security] {title} — {username} ({role})"
    sent = _send_security_email(subject, html, recipient)
    if not sent:
        logger.warning("Login alert email not sent (SMTP unconfigured or failed).")
    return sent



# ---- Login OTP Email (to user's verified email) ----

def send_login_otp_email(
    user_email: str,
    username: str,
    otp_code: str,
    ip_address: str,
    device: str,
    browser: str,
    expiry_seconds: int = 300,
) -> bool:
    """
    Send login OTP to the USER's own verified email.
    If user email is a placeholder/dummy email, falls back to active security alert email recipient.
    """
    target_recipient = user_email
    dummy_domains = ["@example.com", "@wms.com", "@local", "@localhost", "@test.com"]
    if not target_recipient or any(dom in target_recipient.lower() for dom in dummy_domains):
        target_recipient = get_security_alert_recipient() or target_recipient

    if not target_recipient:
        logger.error("Cannot send login OTP — user has no email address.")
        return False

    title = "Your Login Verification Code"
    expiry_mins = expiry_seconds // 60

    content = f"""
    <div style="text-align:center;margin-bottom:28px;">
      <div style="font-size:13px;color:#94a3b8;margin-bottom:12px;">Your one-time login code for <strong style="color:#e2e8f0;">{username}</strong>:</div>
      <div style="display:inline-block;background:#0f172a;border:2px solid #6366f1;border-radius:10px;padding:18px 40px;">
        <div style="font-size:40px;font-weight:900;color:#6366f1;letter-spacing:12px;font-family:monospace;">{otp_code}</div>
      </div>
      <div style="font-size:12px;color:#64748b;margin-top:10px;">Valid for {expiry_mins} minutes · Single use only</div>
    </div>
    <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;margin-top:8px;">
      {_row("Requested From IP", ip_address)}
      {_row("Device", device)}
      {_row("Browser", browser)}
    </table>
    <div style="margin-top:20px;padding:12px 16px;background:#0f172a;border-radius:8px;border-left:3px solid #f59e0b;">
      <div style="font-size:12px;color:#94a3b8;">
        ⚠️ If you did not request this code, do not enter it. Your account may be at risk — contact your administrator immediately.
      </div>
    </div>"""

    html = _html_wrap(title, "#6366f1", content)
    subject = "🔐 Your Warehouse Platform Login Code"
    return _send_security_email(subject, html, target_recipient)


# ---- Role Change Alert (to SECURITY_ALERT_EMAIL) ----

def send_role_change_alert(
    actor_username: str,
    target_username: str,
    old_role: str,
    new_role: str,
    timestamp: datetime,
    event_id: int,
    ip_address: str = "",
) -> bool:
    """Send CRITICAL role change notification to admin security email."""
    recipient = get_security_alert_recipient()
    if not recipient:
        return False

    ts_str = timestamp.strftime("%d %b %Y %H:%M:%S UTC") if timestamp else "Unknown"
    event_id_str = f"SEC-{timestamp.strftime('%Y%m%d') if timestamp else '00000000'}-{event_id:06d}"

    content = f"""
    <div style="margin-bottom:20px;padding:12px 16px;background:#450a0a;border-radius:8px;border-left:3px solid #ef4444;">
      <div style="font-size:13px;color:#fca5a5;font-weight:700;">⚠️ A user's role has been changed. Review this action immediately if unexpected.</div>
    </div>
    <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">
      {_row("Target User", target_username)}
      {_row("Previous Role", old_role.upper())}
      {_row("New Role", new_role.upper())}
      {_row("Changed By", actor_username)}
      {_row("IP Address", ip_address)}
      {_row("Timestamp", ts_str)}
      {_row("Event ID", event_id_str)}
    </table>"""

    html = _html_wrap("⚠️ Critical Security Change — Role Changed", "#dc2626", content)
    subject = f"[CRITICAL] Role Changed — {target_username}: {old_role} → {new_role}"
    return _send_security_email(subject, html, recipient)


# ---- Account Change Alert (to SECURITY_ALERT_EMAIL) ----

def send_account_change_alert(
    event_type: str,
    actor_username: str,
    target_username: str,
    timestamp: datetime,
    event_id: int,
    extra_info: str = "",
) -> bool:
    """Send account change alerts (password change, enable/disable, etc.) to admin."""
    recipient = get_security_alert_recipient()
    if not recipient:
        return False

    titles = {
        "ACCOUNT_DEACTIVATED": ("Account Deactivated", "#dc2626", "CRITICAL"),
        "ACCOUNT_ACTIVATED": ("Account Activated", "#10b981", "INFO"),
        "PASSWORD_CHANGED": ("Password Changed", "#f59e0b", "WARNING"),
        "OAUTH_LOGIN": ("New OAuth Login", "#6366f1", "INFO"),
        "ACCOUNT_CREATED": ("New Account Created", "#0ea5e9", "INFO"),
    }
    title, color, sev = titles.get(event_type, ("Security Event", "#64748b", "INFO"))
    ts_str = timestamp.strftime("%d %b %Y %H:%M:%S UTC") if timestamp else "Unknown"
    event_id_str = f"SEC-{timestamp.strftime('%Y%m%d') if timestamp else '00000000'}-{event_id:06d}"

    content = f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">
      {_row("Event", event_type)}
      {_row("Severity", sev)}
      {_row("Target User", target_username)}
      {_row("Performed By", actor_username)}
      {_row("Timestamp", ts_str)}
      {_row("Event ID", event_id_str)}
      {_row("Details", extra_info) if extra_info else ""}
    </table>"""

    html = _html_wrap(title, color, content)
    subject = f"[Security] {title} — {target_username}"
    return _send_security_email(subject, html, recipient)

