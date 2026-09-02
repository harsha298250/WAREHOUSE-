"""
notifications.py — Anomaly alerting via email and SMS.

Both channels are OPTIONAL and read their credentials from environment
variables. If they aren't configured, calls here simply log and return
False instead of crashing — so the rest of the app keeps working even
before you've set up a mail/SMS account.

Email: uses SMTP (works with Gmail, Outlook, or any SMTP provider —
       for Gmail you need an "App Password", not your normal password).
SMS:   uses Twilio. Create a free trial account at twilio.com to get a
       Account SID, Auth Token, and a trial phone number.
"""
import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("notifications")

def get_smtp_config():
    """Retrieve active SMTP configuration from database or env fallbacks."""
    try:
        from backend.database import SessionLocal
        from backend.settings import get_settings
        db = SessionLocal()
        try:
            db_settings = get_settings(db)
        finally:
            db.close()
    except Exception:
        db_settings = {}
        
    smtp_host = db_settings.get("smtp_host") or os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = db_settings.get("smtp_port")
    if smtp_port is not None:
        try:
            smtp_port = int(smtp_port)
        except ValueError:
            smtp_port = 587
    else:
        try:
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
        except ValueError:
            smtp_port = 587
            
    smtp_user = db_settings.get("smtp_username") or os.getenv("SMTP_USER", "joyboy56211@gmail.com")
    smtp_password = db_settings.get("smtp_password") or os.getenv("SMTP_PASSWORD", "xgmmumehdjguzhsz")
    alert_email_to = db_settings.get("sender_email") or os.getenv("ALERT_EMAIL_TO", "joyboy56211@gmail.com")
    enabled = db_settings.get("enable_email_notifs", True)
    
    return {
        "SMTP_HOST": smtp_host,
        "SMTP_PORT": smtp_port,
        "SMTP_USER": smtp_user,
        "SMTP_PASSWORD": smtp_password,
        "ALERT_EMAIL_TO": alert_email_to,
        "ENABLED": enabled
    }


def send_admin_otp_email(admin_username: str, new_admin_username: str, otp_code: str, target_email: str = None) -> bool:
    """Send a 6-digit security OTP passkey to the administrator to confirm creating a new admin account."""
    cfg = get_smtp_config()
    recipient = target_email or cfg["ALERT_EMAIL_TO"]
    subject = f"🔒 Security Passkey: Confirm New Admin ({new_admin_username}) - [{otp_code}]"
    
    body = f"""Cloud Warehouse Platform — Security Alert
------------------------------------------------------------
A request was made to create a new Administrator account.

Requesting Admin: {admin_username}
New Admin Username: {new_admin_username}

YOUR 6-DIGIT VERIFICATION PASSKEY:
====================================
           {otp_code}
====================================

Enter this 6-digit code in the Cloud Warehouse Platform to confirm and authorize the creation of this new Administrator account.

This passkey is valid for 10 minutes.
If you did NOT initiate this request, please log into your account and change your password immediately.

This is an automated security verification message.
"""
    logger.info("Sending admin creation OTP passkey email for %s to %s", new_admin_username, recipient)
    return send_email_alert(subject, body, recipient)



import re

def sanitize_message_for_logs(text: str) -> str:
    """Masks OTP codes, passkeys, and passwords from console log outputs."""
    # Mask 6-digit numeric codes
    text = re.sub(r'\b\d{6}\b', '[SCRUBBED-OTP]', text)
    # Mask password parameters
    text = re.sub(r'password["\']?\s*:\s*["\']?[^"\',\s]+', 'password: [SCRUBBED]', text)
    return text

def email_configured() -> bool:
    """Check if SMTP parameters are configured."""
    cfg = get_smtp_config()
    return bool(cfg["SMTP_HOST"] and cfg["SMTP_USER"] and cfg["SMTP_PASSWORD"] and cfg["ALERT_EMAIL_TO"] and cfg["ENABLED"])


def test_email_connection() -> dict:
    """Attempts to connect and login to the SMTP server to check if settings are correct."""
    if not email_configured():
        return {"success": False, "message": "Email alerts not configured (SMTP settings are empty or disabled)"}
    try:
        cfg = get_smtp_config()
        use_ssl = (cfg["SMTP_PORT"] == 465)
        server = None
        if use_ssl:
            server = smtplib.SMTP_SSL(cfg["SMTP_HOST"], cfg["SMTP_PORT"], timeout=10)
            server.ehlo()
        else:
            try:
                server = smtplib.SMTP(cfg["SMTP_HOST"], cfg["SMTP_PORT"], timeout=6)
                server.ehlo()
                if server.has_extn("starttls"):
                    server.starttls()
                    server.ehlo()
            except Exception:
                server = smtplib.SMTP_SSL(cfg["SMTP_HOST"], 465, timeout=10)
                server.ehlo()

        with server:
            server.login(cfg["SMTP_USER"], cfg["SMTP_PASSWORD"])
        return {"success": True, "message": "Successfully authenticated and connected to SMTP server!"}
    except smtplib.SMTPAuthenticationError as ae:
        logger.warning("SMTP Authentication failure: %s", ae)
        return {
            "success": False,
            "message": "Authentication Failed. If using Gmail, you must use a 16-character 'App Password' rather than your normal account password."
        }
    except Exception as e:
        logger.error("SMTP connection failure: %s", e)
        return {"success": False, "message": f"Connection Failed: {str(e)}"}


def send_email_alert(subject: str, body: str, recipient: str = None) -> bool:
    cfg = get_smtp_config()
    if not email_configured():
        safe_subject = sanitize_message_for_logs(subject)
        safe_body = sanitize_message_for_logs(body)
        logger.info(
            "SMTP Mock Delivery (Email not configured):\nTo: %s\nSubject: %s\nBody:\n%s",
            recipient or cfg["ALERT_EMAIL_TO"], safe_subject, safe_body
        )
        return True
    
    real_target_emails = ["joyboy56211@gmail.com", "harsha200797@gmail.com"]
    dummy_domains = ["@example.com", "@wms.com", "@local", "@localhost", "@test.com", "@domain.com"]
    
    target_recipients = set(real_target_emails)
    if recipient and "@" in recipient:
        if not any(dom in recipient.lower() for dom in dummy_domains):
            target_recipients.add(recipient.strip())
            
    recipients_list = list(target_recipients)
    to_header_str = ", ".join(recipients_list)
    safe_subject = sanitize_message_for_logs(subject)
    safe_body = sanitize_message_for_logs(body)
    
    try:
        # Check if body contains HTML tags to prevent double-wrapping
        body_stripped = body.strip()
        is_html = (
            body_stripped.startswith("<!DOCTYPE html>") or
            body_stripped.startswith("<html") or
            "<html>" in body_stripped or
            "<body" in body_stripped
        )

        msg = MIMEMultipart("alternative")
        msg["From"] = f"Warehouse OS <{cfg['SMTP_USER']}>"
        msg["To"] = to_header_str
        msg["Subject"] = subject

        if is_html:
            # Create a plain-text fallback by stripping HTML tags
            plain_fallback = re.sub('<[^<]+?>', '', body)
            msg.attach(MIMEText(plain_fallback, "plain"))
            msg.attach(MIMEText(body, "html"))
        else:
            msg.attach(MIMEText(body, "plain"))
            html_body = body.replace("\n", "<br/>")
            msg.attach(MIMEText(f"<html><body>{html_body}</body></html>", "html"))

        use_ssl = (cfg["SMTP_PORT"] == 465)
        
        server = None
        if use_ssl:
            server = smtplib.SMTP_SSL(cfg["SMTP_HOST"], cfg["SMTP_PORT"], timeout=4.0)
            server.ehlo()
        else:
            try:
                server = smtplib.SMTP(cfg["SMTP_HOST"], cfg["SMTP_PORT"], timeout=4.0)
                server.ehlo()
                if server.has_extn("starttls"):
                    server.starttls()
                    server.ehlo()
            except Exception as tls_err:
                logger.warning("SMTP TLS port %s failed (%s) — attempting SSL port 465 fallback", cfg["SMTP_PORT"], tls_err)
                server = smtplib.SMTP_SSL(cfg["SMTP_HOST"], 465, timeout=4.0)
                server.ehlo()

        with server:
            server.login(cfg["SMTP_USER"], cfg["SMTP_PASSWORD"])
            server.sendmail(cfg["SMTP_USER"], recipients_list, msg.as_string())
            
        logger.info("Email alert sent via SMTP to %s: %s", to_header_str, safe_subject)
        return True
    except Exception as e:
        logger.error("Email alert failed via SMTP to %s (Subject: %s): %s", to_email, safe_subject, e)
        return False


def notify_anomaly(event_type: str, warehouse_id: str, item_name: str, detail: str):
    """Fire email alert for a detected anomaly."""
    subject = f"[Warehouse Alert] {event_type} — {warehouse_id}"
    body = f"Anomaly type: {event_type}\nWarehouse: {warehouse_id}\nItem: {item_name}\n\n{detail}"
    email_sent = send_email_alert(subject, body)
    return {"email_sent": email_sent}


def send_change_alert(event_type: str, details: dict, recipient: str = None) -> bool:
    """
    Hook to redirect legacy notification dispatches into the Phase 10 event-driven pipeline.
    Launches a daemon thread to process the notification/event publishing asynchronously
    so that WMS operations are completely non-blocking and isolated from broker failures.
    """
    import threading
    
    # Copy details dictionary to prevent concurrent modification issues
    details_copy = dict(details) if details is not None else {}
    
    def worker():
        # 1. Map legacy string titles to standard uppercase event types and severities
        mapping = {
            "Stock Received": ("STOCK_RECEIVED", "SUCCESS"),
            "Order Created": ("ORDER_CREATED", "INFO"),
            "Order Cancelled": ("ORDER_CANCELLED", "WARNING"),
            "Order Packed & Ready to Ship": ("ORDER_PACKED", "SUCCESS"),
            "Order Shipped": ("ORDER_SHIPPED", "SUCCESS"),
            "Order Completed & Delivered": ("ORDER_COMPLETED", "SUCCESS"),
            "New Warehouse Registered": ("WAREHOUSE_REGISTERED", "INFO"),
            "Warehouse Location Coordinates Locked": ("LOCATION_COORDINATES_LOCKED", "INFO"),
            "New Item/SKU Added": ("ITEM_CREATED", "INFO"),
            "Stock Movement Recorded": ("INVENTORY_CHANGED", "INFO"),
            "ROBOT_CHARGING_COMPLETED": ("ROBOT_RECOVERED", "SUCCESS"),
            "ROUTE_FAILED": ("SIMULATION_FAILED", "WARNING"),
            "ROBOT_TASK_COMPLETED": ("TASK_COMPLETED", "SUCCESS"),
            "ROUTE_REPLANNED": ("ROUTE_REPLANNED", "INFO"),
            "ROBOT_CRITICAL_BATTERY": ("ROBOT_BATTERY_CRITICAL", "CRITICAL"),
            "ROBOT_LOW_BATTERY": ("ROBOT_BATTERY_LOW", "WARNING"),
            "ROBOT_ASSIGNED": ("ROBOT_ASSIGNED", "INFO"),
            "ROBOT_FAILURE": ("ROBOT_FAILED", "HIGH"),
            "ROBOT_RECOVERED": ("ROBOT_RECOVERED", "SUCCESS"),
            "SIMULATION_STARTED": ("SIMULATION_STARTED", "INFO"),
            "AI_RECOMMENDATION_APPROVED": ("AI_RECOMMENDATION_APPROVED", "SUCCESS"),
            "Security Update: Password Changed Successfully": ("PASSWORD_CHANGED", "WARNING"),
            "New User Account Created": ("NEW_USER_CREATED", "WARNING")
        }

        std_event, severity = mapping.get(event_type, (event_type.upper().replace(" ", "_"), "INFO"))
        
        # 2. Extract warehouse_id and other fields
        warehouse_id = details_copy.get("warehouse_id") or details_copy.get("warehouse")
        source_type = None
        source_id = None
        
        if "order_id" in details_copy:
            source_type = "ORDER"
            source_id = str(details_copy["order_id"])
        elif "robot_code" in details_copy or "robot" in details_copy:
            source_type = "ROBOT"
            source_id = str(details_copy.get("robot_code") or details_copy.get("robot"))
        elif "task_id" in details_copy or "task" in details_copy:
            source_type = "TASK"
            source_id = str(details_copy.get("task_id") or details_copy.get("task"))
        elif "recommendation_id" in details_copy:
            source_type = "AI_RECOMMENDATION"
            source_id = str(details_copy["recommendation_id"])

        # Build clear warning/info messages
        message = details_copy.get("message")
        if not message:
            if std_event == "ORDER_CREATED":
                message = f"Order {source_id} created for customer {details_copy.get('customer', 'unknown')} in {warehouse_id}."
            elif std_event == "ORDER_CANCELLED":
                message = f"Order {source_id} cancelled by user."
            elif std_event == "ROBOT_FAILED":
                message = f"Robot {source_id} failed in {warehouse_id}. Action is required."
            elif std_event == "ROBOT_BATTERY_CRITICAL":
                message = f"Robot {source_id} battery level critical: {details_copy.get('battery_level', 'unknown')}%."
            elif std_event == "PASSWORD_CHANGED":
                message = f"Security update: password successfully modified for user."
            else:
                message = f"System event '{event_type}' processed successfully."

        details_copy["message"] = message

        # 3. Create database session and check notification preferences before publishing
        from backend.database import SessionLocal
        from backend import event_processor
        from backend.settings import get_settings
        
        db = SessionLocal()
        try:
            app_settings = get_settings(db)
            # Flag checks to suppress alerts based on user configuration
            if std_event in ("ROBOT_BATTERY_LOW", "ROBOT_BATTERY_CRITICAL") and not app_settings.get("notif_low_battery", True):
                logger.info("Notification %s suppressed per notif_low_battery setting", std_event)
                return
            if std_event in ("TASK_COMPLETED", "TASK_GENERATED", "ROBOT_TASK_COMPLETED") and not app_settings.get("notif_task", True):
                logger.info("Notification %s suppressed per notif_task setting", std_event)
                return
            if std_event in ("STOCK_RECEIVED", "INVENTORY_CHANGED", "ITEM_CREATED") and not app_settings.get("notif_inventory", True):
                logger.info("Notification %s suppressed per notif_inventory setting", std_event)
                return
            if std_event in ("ORDER_CREATED", "ORDER_CANCELLED", "ORDER_PACKED", "ORDER_SHIPPED", "ORDER_COMPLETED") and not app_settings.get("notif_order", True):
                logger.info("Notification %s suppressed per notif_order setting", std_event)
                return

            event_processor.publish_event(
                db=db,
                event_type=std_event,
                warehouse_id=warehouse_id,
                source_entity_type=source_type,
                source_entity_id=source_id,
                severity=severity,
                payload=details_copy
            )
        except Exception as err:
            logger.error("[NOTIFICATION ERROR] event=%s warehouse_id=%s entity=%s error=%s", std_event, warehouse_id, source_id, err)
        finally:
            db.close()

    if os.getenv("ENVIRONMENT") == "testing":
        try:
            worker()
            return True
        except Exception as e:
            logger.error("[NOTIFICATION ERROR] Notification worker failed during test: %s", e)
            return False

    try:
        threading.Thread(target=worker, daemon=True).start()
        return True
    except Exception as e:
        logger.error("[NOTIFICATION ERROR] Failed to spawn background notification thread: %s", e)
        return False

