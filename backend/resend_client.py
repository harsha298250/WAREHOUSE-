import os
import logging
import re
from typing import Optional
import resend

logger = logging.getLogger("warehouse.resend")

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")

# Initialize Resend SDK if key exists
if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY
    logger.info("Resend Email client initialized with API key.")
else:
    logger.info("Resend API key not configured; emails will be logged locally in mock mode.")


def sanitize_message_for_logs(text: str) -> str:
    """Masks OTP codes, passkeys, and passwords from console log outputs."""
    # Mask 6-digit numeric codes
    text = re.sub(r'\b\d{6}\b', '[SCRUBBED-OTP]', text)
    # Mask password parameters
    text = re.sub(r'password["\']?\s*:\s*["\']?[^"\',\s]+', 'password: [SCRUBBED]', text)
    return text


def send_html_email(subject: str, body: str, recipient: str, sender: Optional[str] = None) -> bool:
    """
    Adapter function that redirects all email requests to the authoritative 
    SMTP sender in notifications.py (ensuring Resend API is never invoked).
    """
    from backend import notifications
    # Directly dispatch via notifications SMTP sender
    return notifications.send_email_alert(subject, body, recipient)


def check_resend_health() -> dict:
    """Bypasses Resend API. Checks SMTP client availability."""
    from backend import notifications
    configured = notifications.email_configured()
    return {
        "status": "healthy" if configured else "unconfigured",
        "connected": configured,
        "provider": "Gmail SMTP (Resend Disabled)"
    }
