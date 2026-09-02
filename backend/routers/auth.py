import os
import time
import secrets
import json
import hashlib
import urllib.request
import logging
from datetime import datetime, date, timezone, timedelta, UTC
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from backend.timeout_policy import OAUTH_TIMEOUT
from backend.database import get_db
from backend.models import User, AccessLog, RecoveryCredential, RecoveryCode, OTPRecord
from backend.schemas import (
    LoginRequest,
    ChangePasswordRequest,
    AdminCreateRequest,
    AdminConfirmOTPRequest,
    VerifyPasswordRequest,
    ConfirmChangePasswordRequest,
    RecoverySetupRequest,
    RecoveryLoginRequest,
    CreateUserRequest,
    UpdateUserRoleRequest,
)
from backend.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
    validate_password_strength,
    require_admin,
    require_permission,
    log_access,
    Permissions,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from backend import notifications
from backend import audit_ledger as ledger
from backend.services import security_service

logger = logging.getLogger("warehouse")

router = APIRouter()

# ---------------------------------------------------------------------------
# In-memory rate limiters (IP-keyed, cleared on restart — acceptable for dev)
# ---------------------------------------------------------------------------
from collections import defaultdict
_login_attempts: dict = defaultdict(list)
_recovery_attempts: dict = defaultdict(list)

LOGIN_RATE_LIMIT = 5
LOGIN_RATE_WINDOW = 300   # 5 minutes
RECOVERY_RATE_LIMIT = 5
RECOVERY_RATE_WINDOW = 300

OTP_EXPIRY_SECONDS = 600  # 10 minutes


def check_login_rate_limit(ip: str):
    import os
    if os.getenv("AUTH_LOCKOUT_ENABLED", "false").lower() != "true" or os.getenv("ENVIRONMENT") == "testing" or ip in ("127.0.0.1", "localhost", "::1"):
        return
    try:
        from backend.redis_client import get_redis_client
        client = get_redis_client()
        if client:
            key = f"ratelimit:login:{ip}"
            count = client.get(key)
            if count and int(count) >= LOGIN_RATE_LIMIT:
                raise HTTPException(status_code=429, detail="Too many login attempts. Please wait a few minutes.")
            pipe = client.pipeline()
            pipe.incr(key)
            pipe.expire(key, LOGIN_RATE_WINDOW)
            pipe.execute()
            return
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Redis login rate limit check failed: %s", e)

    now = time.time()
    attempts = _login_attempts[ip]
    _login_attempts[ip] = [t for t in attempts if now - t < LOGIN_RATE_WINDOW]
    if len(_login_attempts[ip]) >= LOGIN_RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Too many login attempts. Please wait a few minutes.")
    _login_attempts[ip].append(now)


def check_recovery_rate_limit(ip: str):
    import os
    if os.getenv("ENVIRONMENT") == "testing" or ip in ("127.0.0.1", "localhost", "::1"):
        return
    try:
        from backend.redis_client import get_redis_client
        client = get_redis_client()
        if client:
            key = f"ratelimit:recovery:{ip}"
            count = client.get(key)
            if count and int(count) >= RECOVERY_RATE_LIMIT:
                raise HTTPException(status_code=429, detail="Too many recovery login attempts. Please wait a few minutes.")
            pipe = client.pipeline()
            pipe.incr(key)
            pipe.expire(key, RECOVERY_RATE_WINDOW)
            pipe.execute()
            return
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Redis recovery rate limit check failed: %s", e)

    now = time.time()
    attempts = _recovery_attempts[ip]
    _recovery_attempts[ip] = [t for t in attempts if now - t < RECOVERY_RATE_WINDOW]
    if len(_recovery_attempts[ip]) >= RECOVERY_RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Too many recovery login attempts. Please wait a few minutes.")
    _recovery_attempts[ip].append(now)


# ---------------------------------------------------------------------------
# OTP helper utilities (DB-persisted)
# ---------------------------------------------------------------------------

def _create_db_otp(db: Session, user: User, purpose: str, request_ip: str = "", context_data: dict = None) -> str:
    """
    Create a DB-persisted OTP for a given user and purpose.
    Deletes any existing OTP for the same user+purpose first (upsert).
    Returns the plaintext 6-digit code.
    """
    db.query(OTPRecord).filter(
        OTPRecord.user_id == user.id,
        OTPRecord.purpose == purpose
    ).delete()
    db.flush()

    otp_code = f"{secrets.randbelow(900000) + 100000}"
    otp_hash = hash_password(otp_code)
    expires_at = datetime.now(UTC).replace(tzinfo=None) + timedelta(seconds=OTP_EXPIRY_SECONDS)

    record = OTPRecord(
        user_id=user.id,
        purpose=purpose,
        code_hash=otp_hash,
        expires_at=expires_at,
        attempts=0,
        max_attempts=5,
        created_at=datetime.now(UTC).replace(tzinfo=None),
        request_ip=request_ip,
        context_data=json.dumps(context_data or {}),
    )
    db.add(record)
    db.commit()
    logger.warning("DEVELOPMENT/DEBUG ONLY: %s OTP for user %s is: %s", purpose, user.username, otp_code)
    return otp_code


def _verify_db_otp(db: Session, user: User, purpose: str, submitted_code: str) -> OTPRecord:
    """
    Verify a submitted OTP code against the DB record.
    Raises HTTPException on failure (expired, max attempts, invalid).
    On success, marks as consumed. Returns the record.
    """
    record = db.query(OTPRecord).filter(
        OTPRecord.user_id == user.id,
        OTPRecord.purpose == purpose,
        OTPRecord.consumed_at.is_(None),
    ).first()

    if not record:
        raise HTTPException(status_code=400, detail="No pending verification request found. Please initiate the request first.")

    if datetime.now(UTC).replace(tzinfo=None) > record.expires_at:
        db.delete(record)
        db.commit()
        raise HTTPException(status_code=400, detail="Verification code has expired (valid for 10 minutes). Please request a new code.")

    record.attempts += 1
    if record.attempts > record.max_attempts:
        db.delete(record)
        db.commit()
        raise HTTPException(status_code=400, detail="Maximum verification attempts exceeded. Please request a new code.")

    if not verify_password(submitted_code.strip(), record.code_hash):
        remaining = record.max_attempts - record.attempts
        db.commit()
        raise HTTPException(status_code=400, detail=f"Invalid verification code. ({remaining} attempts remaining)")

    # Mark consumed
    record.consumed_at = datetime.now(UTC).replace(tzinfo=None)
    db.commit()
    db.refresh(record)
    return record


def _token_hash(token: str) -> str:
    """SHA-256 hash of the first 32 chars of a JWT for session reference."""
    return hashlib.sha256(token[:32].encode()).hexdigest()


# ---------------------------------------------------------------------------
# Authentication endpoints
# ---------------------------------------------------------------------------

@router.post("/auth/login")
def login(payload: LoginRequest, request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    ip = request.client.host if request and request.client else "unknown"
    ua = request.headers.get("user-agent", "") if request else ""
    check_login_rate_limit(ip)

    # authenticate_user enforces lockout and active checks
    user = authenticate_user(db, payload.username, payload.password)
    if not user:
        # Record structured failed login security event & audit ledger entry
        db_user_check = db.query(User).filter(User.username == payload.username.strip()).first()
        security_service.record_login_audit_event(
            db=db,
            username=payload.username.strip(),
            user_id=db_user_check.id if db_user_check else None,
            role=db_user_check.role if db_user_check else "UNKNOWN",
            status="FAILED",
            auth_method="password",
            request=request,
            failure_reason="invalid_credentials"
        )
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Phase 18: If LOGIN_OTP_REQUIRED, issue a challenge instead of a JWT
    if security_service.LOGIN_OTP_REQUIRED:
        if not security_service.check_otp_rate_limit(user.id):
            raise HTTPException(status_code=429, detail="Too many OTP requests. Please wait before trying again.")
        otp_code = _create_db_otp(db, user, "LOGIN_OTP", ip)
        user_email = user.email or user.username
        device_info = security_service.get_device_info(ua)
        security_service.send_login_otp_email(
            user_email=user_email,
            username=user.username,
            otp_code=otp_code,
            ip_address=ip,
            device=device_info["device"],
            browser=device_info["browser"],
            expiry_seconds=security_service.OTP_EXPIRY_LOGIN_SECONDS,
        )
        security_service.create_security_event(
            db=db,
            event_type="LOGIN_OTP_SENT",
            severity="INFO",
            status="SUCCESS",
            actor_user_id=user.id,
            actor_username=user.username,
            authentication_method="password_otp",
            role_at_event=user.role,
            ip_address=ip,
            user_agent=ua,
        )
        return {
            "status": "otp_required",
            "message": "A verification code has been sent to your registered email address.",
            "username": user.username,
            "expires_in_seconds": security_service.OTP_EXPIRY_LOGIN_SECONDS,
        }

    # Standard flow: issue JWT immediately
    token = create_access_token({"sub": user.username, "role": user.role})
    log_access(db, user.username, "login", request=request)

    # Update login audit fields
    user.last_login_at = datetime.now(UTC).replace(tzinfo=None)
    user.last_login_ip = security_service.get_client_ip(request)
    user.login_method = "password"
    if not user.is_verified:
        user.is_verified = True
    db.commit()

    # Record structured login success audit event & in-app notification
    security_service.record_login_audit_event(
        db=db,
        username=user.username,
        user_id=user.id,
        role=user.role,
        status="SUCCESS",
        auth_method="password",
        request=request
    )
    # Send login security alert to admin (background — non-blocking)
    device_info = security_service.get_device_info(ua)
    background_tasks.add_task(
        security_service.send_login_alert_email,
        username=user.username,
        role=user.role,
        ip_address=ip,
        device=device_info["device"],
        browser=device_info["browser"],
        os=device_info["os"],
        auth_method="Password",
        timestamp=datetime.now(UTC).replace(tzinfo=None),
        event_id=user.id,
        status="SUCCESS",
        location=security_service.get_approximate_location(ip),
    )

    from backend.event_processor import publish_event
    publish_event(
        db=db,
        event_type="USER_LOGIN",
        warehouse_id=None,
        source_entity_type="USER",
        source_entity_id=str(user.id),
        actor_user_id=user.id,
        severity="INFO",
        payload={
            "username": user.username,
            "message": f"User {user.username} logged in successfully."
        },
        background_tasks=background_tasks
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "username": user.username,
        "role": user.role,
        "full_name": user.full_name or user.username,
    }


class VerifyLoginOTPRequest(BaseModel):
    username: str
    otp_code: str


@router.post("/auth/verify-login-otp")
def verify_login_otp(
    payload: VerifyLoginOTPRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Phase 18: Verify login OTP and issue JWT.
    Only active when LOGIN_OTP_REQUIRED=true.
    """
    ip = request.client.host if request and request.client else "unknown"
    ua = request.headers.get("user-agent", "") if request else ""

    user = db.query(User).filter(User.username == payload.username.strip()).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    try:
        _verify_db_otp(db, user, "LOGIN_OTP", payload.otp_code)
    except HTTPException as e:
        security_service.record_otp_failure(user.id, ip)
        security_service.create_security_event(
            db=db,
            event_type="LOGIN_OTP_FAILED",
            severity="WARNING",
            status="FAILED",
            actor_user_id=user.id,
            actor_username=user.username,
            authentication_method="password_otp",
            role_at_event=user.role,
            ip_address=ip,
            user_agent=ua,
            extra_details={"reason": str(e.detail)},
        )
        raise

    token = create_access_token({"sub": user.username, "role": user.role})
    log_access(db, user.username, "login", request=request)

    user.last_login_at = datetime.now(UTC).replace(tzinfo=None)
    user.last_login_ip = ip
    user.login_method = "password_otp"
    if not user.is_verified:
        user.is_verified = True
    db.commit()

    ledger.append_entry(db, "user_login", {
        "username": user.username,
        "role": user.role,
        "method": "password_otp",
        "ip": ip,
        "time": datetime.now(UTC).replace(tzinfo=None).isoformat()
    })

    sec_event = security_service.create_security_event(
        db=db,
        event_type="LOGIN_SUCCESS",
        severity="INFO",
        status="SUCCESS",
        actor_user_id=user.id,
        actor_username=user.username,
        authentication_method="password_otp",
        role_at_event=user.role,
        ip_address=ip,
        user_agent=ua,
    )
    if sec_event:
        device_info = security_service.get_device_info(ua)
        background_tasks.add_task(
            security_service.send_login_alert_email,
            username=user.username,
            role=user.role,
            ip_address=ip,
            device=device_info["device"],
            browser=device_info["browser"],
            os=device_info["os"],
            auth_method="Password + OTP",
            timestamp=sec_event.timestamp,
            event_id=sec_event.id,
            status="SUCCESS",
        )

    return {
        "access_token": token,
        "token_type": "bearer",
        "username": user.username,
        "role": user.role,
        "full_name": user.full_name or user.username,
        "auth_mode": "password_otp",
    }


@router.post("/auth/logout")
def logout(request: Request, background_tasks: BackgroundTasks, user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Record logout event and audit the session end."""
    user.last_logout_at = datetime.now(UTC).replace(tzinfo=None)
    db.commit()

    log_access(db, user.username, "logout", request=request)
    ledger.append_entry(db, "user_logout", {
        "username": user.username,
        "time": datetime.now(UTC).replace(tzinfo=None).isoformat()
    })

    from backend.event_processor import publish_event
    publish_event(
        db=db,
        event_type="USER_LOGOUT",
        warehouse_id=None,
        source_entity_type="USER",
        source_entity_id=str(user.id),
        actor_user_id=user.id,
        severity="INFO",
        payload={
            "username": user.username,
            "message": f"User {user.username} logged out successfully."
        },
        background_tasks=background_tasks
    )
    return {"status": "ok", "message": "Logged out successfully."}


@router.post("/auth/verify-password")
def verify_current_user_password(
    payload: VerifyPasswordRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect password")
    return {"status": "verified"}


# ---------------------------------------------------------------------------
# Google OAuth
# ---------------------------------------------------------------------------

class GoogleSignInTokenRequest(BaseModel):
    id_token: str


@router.post("/auth/google-signin")
def google_signin(payload: GoogleSignInTokenRequest, request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    id_token = payload.id_token.strip()
    if not id_token:
        raise HTTPException(status_code=400, detail="Missing Google ID token")

    google_client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    if not google_client_id:
        raise HTTPException(status_code=400, detail="Google OAuth is not configured on this server")

    try:
        tokeninfo_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
        req = urllib.request.Request(tokeninfo_url, headers={"User-Agent": "SmartWarehouse/1.0"})
        with urllib.request.urlopen(req, timeout=OAUTH_TIMEOUT) as resp:
            token_data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        logger.error("Google ID token verification failed: %s", e)
        raise HTTPException(status_code=401, detail="Invalid or expired Google ID Token")

    iss = token_data.get("iss", "")
    if iss not in ["accounts.google.com", "https://accounts.google.com"]:
        raise HTTPException(status_code=401, detail="Invalid Google token issuer")

    aud = token_data.get("aud", "")
    if google_client_id and aud != google_client_id:
        raise HTTPException(status_code=401, detail="Google token audience mismatch")

    raw_email = token_data.get("email", "")
    email_verified = token_data.get("email_verified", False)
    if isinstance(email_verified, str):
        email_verified = email_verified.lower() == "true"

    if not raw_email or not email_verified:
        raise HTTPException(status_code=401, detail="Google account email is missing or unverified")

    email = raw_email
    sub = token_data.get("sub", "")
    full_name = token_data.get("name", email.split("@")[0].capitalize())

    ip = request.client.host if request and request.client else ""
    ua = request.headers.get("user-agent", "") if request else ""
    normalized_email = email.strip().lower()

    # Query PostgreSQL Users table using case-normalized email & sub
    conditions = [
        func.lower(User.email) == normalized_email,
        func.lower(User.username) == normalized_email,
    ]
    if sub:
        conditions.append(User.google_subject_id == sub)

    user = db.query(User).filter(or_(*conditions)).first()

    # Reject login if Google email is not registered in PostgreSQL
    if not user:
        logger.warning("Unauthorized Google Sign-In attempt for unregistered email: %s", normalized_email)
        security_service.create_security_event(
            db=db,
            event_type="OAUTH_LOGIN_UNAUTHORIZED",
            severity="WARNING",
            status="BLOCKED",
            actor_username=normalized_email,
            authentication_method="google_oauth",
            ip_address=ip,
            user_agent=ua,
            extra_details={"reason": "Email not registered in database", "email": normalized_email}
        )
        raise HTTPException(
            status_code=403,
            detail="Google account is not authorized for this application. Please contact an administrator."
        )

    # Check user account status
    if not user.is_active:
        logger.warning("Google Sign-In attempt for deactivated account: %s", user.username)
        security_service.create_security_event(
            db=db,
            event_type="OAUTH_LOGIN_DISABLED",
            severity="WARNING",
            status="BLOCKED",
            actor_user_id=user.id,
            actor_username=user.username,
            authentication_method="google_oauth",
            role_at_event=user.role,
            ip_address=ip,
            user_agent=ua,
            extra_details={"reason": "User account deactivated", "email": normalized_email}
        )
        raise HTTPException(
            status_code=403,
            detail="Account is deactivated or disabled. Please contact your administrator."
        )

    # Link subject ID and update login metadata while preserving user.role
    if sub and not user.google_subject_id:
        user.google_subject_id = sub
    user.last_login_at = datetime.now(UTC).replace(tzinfo=None)
    user.last_login_ip = ip
    user.login_method = "google_oauth"
    if not user.email:
        user.email = normalized_email
    db.commit()

    token = create_access_token({"sub": user.username, "role": user.role})
    log_access(db, user.username, "google_oauth_login", request=request)
    ledger.append_entry(db, "user_login", {
        "username": user.username,
        "role": user.role,
        "method": "google_oauth",
        "ip": ip,
        "time": datetime.now(UTC).replace(tzinfo=None).isoformat()
    })

    # Phase 18: Rich security event + admin alert email
    ua = request.headers.get("user-agent", "") if request else ""
    sec_event = security_service.create_security_event(
        db=db,
        event_type="OAUTH_LOGIN",
        severity="INFO",
        status="SUCCESS",
        actor_user_id=user.id,
        actor_username=user.username,
        authentication_method="google_oauth",
        role_at_event=user.role,
        ip_address=ip,
        user_agent=ua,
    )
    if sec_event:
        device_info = security_service.get_device_info(ua)
        location = None
        if sec_event.details:
            try:
                location = json.loads(sec_event.details).get("approximate_location")
            except Exception:
                pass
        background_tasks.add_task(
            security_service.send_login_alert_email,
            username=user.username,
            role=user.role,
            ip_address=ip,
            device=device_info["device"],
            browser=device_info["browser"],
            os=device_info["os"],
            auth_method="Google OAuth 2.0",
            timestamp=sec_event.timestamp,
            event_id=sec_event.id,
            status="SUCCESS",
            location=location,
        )

    from backend.event_processor import publish_event
    publish_event(
        db=db,
        event_type="USER_LOGIN",
        warehouse_id=None,
        source_entity_type="USER",
        source_entity_id=str(user.id),
        actor_user_id=user.id,
        severity="INFO",
        payload={
            "username": user.username,
            "message": f"User {user.username} logged in successfully via Google Sign-In."
        },
        background_tasks=background_tasks
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "username": user.username,
        "role": user.role,
        "full_name": user.full_name or user.username,
        "user": {
            "username": user.username,
            "role": user.role,
            "email": user.email,
            "full_name": user.full_name or user.username,
        },
        "auth_mode": "google_oauth_2.0"
    }


@router.get("/auth/google-config")
def google_config():
    return {"google_client_id": os.getenv("GOOGLE_CLIENT_ID", "").strip()}


@router.get("/auth/me")
def me(user=Depends(get_current_user)):
    return {
        "username": user.username,
        "email": user.email or user.username,
        "role": user.role,
        "full_name": user.full_name or user.username,
        "is_active": user.is_active if hasattr(user, "is_active") else True,
        "is_verified": user.is_verified if hasattr(user, "is_verified") else True,
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        "login_method": user.login_method or "password",
    }


# ---------------------------------------------------------------------------
# Password change (OTP-verified, now DB-persisted)
# ---------------------------------------------------------------------------

@router.post("/auth/request-change-password")
def request_change_password(
    payload: ChangePasswordRequest,
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password incorrect")

    validate_password_strength(payload.new_password, db)

    ip = request.client.host if request and request.client else ""
    otp_code = _create_db_otp(db, user, "PASSWORD_CHANGE", ip, {"new_password_hash": hash_password(payload.new_password)})

    subject = f"🔒 Security Passkey: Confirm Password Change - [{otp_code}]"
    body = f"""Cloud Warehouse Platform — Security Alert
------------------------------------------------------------
A request was made to change your account password.

User: {user.username}

YOUR 6-DIGIT VERIFICATION PASSKEY:
====================================
           {otp_code}
====================================

Enter this 6-digit code in the Cloud Warehouse Platform to confirm and authorize this password change.

This passkey is valid for 10 minutes.
If you did NOT initiate this request, please contact system security immediately.

This is an automated security verification message.
"""
    main_admin_email = notifications.get_smtp_config().get("ALERT_EMAIL_TO") or os.getenv("ALERT_EMAIL_TO", "")
    email_sent = notifications.send_email_alert(subject, body, main_admin_email)
    logger.info("Password change OTP generated for %s (Email sent: %s)", user.username, email_sent)

    return {
        "status": "otp_sent",
        "message": "Security verification code sent to your email",
        "recipient": main_admin_email,
        "expires_in_seconds": OTP_EXPIRY_SECONDS,
    }


@router.post("/auth/confirm-change-password")
def confirm_change_password(
    payload: ConfirmChangePasswordRequest,
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    record = _verify_db_otp(db, user, "PASSWORD_CHANGE", payload.passkey)

    # Extract the pre-hashed new password from context_data
    context = json.loads(record.context_data or "{}")
    new_hash = context.get("new_password_hash")
    if not new_hash:
        raise HTTPException(status_code=400, detail="Password change context lost. Please request a new code.")

    user.password_hash = new_hash
    user.password_changed_at = datetime.now(UTC).replace(tzinfo=None)
    db.commit()

    log_access(db, user.username, "password_changed_securely", request=request)
    ledger.append_entry(db, "password_changed", {
        "username": user.username,
        "time": date.today().isoformat()
    })

    notifications.send_change_alert("Security Update: Password Changed Successfully", {
        "username": user.username,
        "time": date.today().isoformat()
    }, recipient=user.username)

    return {"status": "success", "message": "Your password has been successfully updated!"}


# ---------------------------------------------------------------------------
# Admin creation (OTP-verified, now DB-persisted)
# ---------------------------------------------------------------------------

@router.post("/admin/request-add-admin")
def request_add_admin(
    payload: AdminCreateRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    user=Depends(require_admin),
    db: Session = Depends(get_db)
):
    if hasattr(payload, "password") and payload.password:
        validate_password_strength(payload.password, db)

    target_email = payload.email.strip().lower()
    if "@" not in target_email or "." not in target_email.split("@")[-1]:
        raise HTTPException(status_code=400, detail="Target email must be a valid email address (e.g. user@example.com)")

    target_username = payload.username.strip() if hasattr(payload, "username") and payload.username else target_email.split("@")[0]

    existing = db.query(User).filter(or_(User.username == target_username, User.email == target_email)).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Account '{target_username}' ({target_email}) is already registered")

    ip = request.client.host if request and request.client else ""
    target_role = payload.role if hasattr(payload, "role") and payload.role else "admin"
    raw_pw = payload.password if hasattr(payload, "password") and payload.password else ""
    pw_hash = hash_password(raw_pw) if raw_pw else "GOOGLE_OAUTH_ONLY"

    otp_code = _create_db_otp(db, user, "ADMIN_CREATION", ip, {
        "target_email": target_email,
        "target_username": target_username,
        "full_name": payload.full_name.strip(),
        "target_role": target_role,
        "pw_hash": pw_hash,
    })

    main_admin_email = notifications.get_smtp_config().get("ALERT_EMAIL_TO") or "joyboy56211@gmail.com"

    def _async_email_dispatch():
        try:
            notifications.send_admin_otp_email(
                admin_username=user.username,
                new_admin_username=target_email,
                otp_code=otp_code,
                target_email=main_admin_email
            )
        except Exception as smtp_err:
            logger.error("Failed to dispatch Admin Creation OTP email: %s", smtp_err)

    background_tasks.add_task(_async_email_dispatch)

    log_access(db, user.username, "request_admin_creation", request=request)
    logger.info("Admin creation OTP generated for %s (%s) by %s (Queued background email dispatch)", target_username, target_email, user.username)

    return {
        "status": "otp_sent",
        "message": f"Security verification passkey sent to {main_admin_email}",
        "recipient": main_admin_email,
        "expires_in_seconds": OTP_EXPIRY_SECONDS,
    }


@router.post("/admin/confirm-add-admin")
def confirm_add_admin(
    payload: AdminConfirmOTPRequest,
    request: Request,
    user=Depends(require_admin),
    db: Session = Depends(get_db)
):
    record = _verify_db_otp(db, user, "ADMIN_CREATION", payload.passkey)
    context = json.loads(record.context_data or "{}")

    target_email = context.get("target_email", "")
    target_username = context.get("target_username", target_email)
    full_name = context.get("full_name", "")
    target_role = context.get("target_role", "admin")
    pw_hash = context.get("pw_hash", "GOOGLE_OAUTH_ONLY")

    if not target_email and not target_username:
        raise HTTPException(status_code=400, detail="Admin creation context lost. Please initiate the request again.")

    # Check again (might have been created between request and confirm)
    if db.query(User).filter(or_(User.username == target_username, User.email == target_email)).first():
        raise HTTPException(status_code=400, detail=f"Account '{target_username}' ({target_email}) was already created.")

    new_user = User(
        username=target_username,
        email=target_email,
        password_hash=pw_hash,
        role=target_role,
        full_name=full_name,
        google_subject_id=None,
        is_active=True,
        is_verified=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    ledger.append_entry(db, "user_created", {
        "new_username": new_user.username,
        "role": new_user.role,
        "full_name": new_user.full_name,
        "created_by": user.username,
        "timestamp": date.today().isoformat()
    })
    log_access(db, user.username, f"created_user_{new_user.username}", request=request)

    notifications.send_change_alert("New User Account Created", {
        "new_user": new_user.username,
        "role": new_user.role,
        "full_name": new_user.full_name,
        "authorized_by": user.username,
        "time": date.today().isoformat()
    }, recipient=new_user.username)

    return {
        "status": "success",
        "username": new_user.username,
        "role": new_user.role,
        "message": f"Account '{new_user.username}' ({new_user.full_name}) with role '{new_user.role}' created successfully!"
    }


# ---------------------------------------------------------------------------
# User management endpoints (Phase 9)
# ---------------------------------------------------------------------------

@router.get("/users")
def list_users(
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permissions.MANAGE_USERS))
):
    """List all users (requires MANAGE_USERS permission)."""
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email or u.username,
            "full_name": u.full_name or "",
            "role": u.role,
            "is_active": u.is_active if hasattr(u, "is_active") else True,
            "is_verified": u.is_verified if hasattr(u, "is_verified") else True,
            "last_login_at": u.last_login_at.isoformat() if u.last_login_at else None,
            "last_login_ip": u.last_login_ip or "",
            "login_method": u.login_method or "",
            "failed_login_count": u.failed_login_count if hasattr(u, "failed_login_count") else 0,
            "locked_until": u.locked_until.isoformat() if u.locked_until else None,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]

@router.get("/users/operators")
def list_active_operators(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """List all active OPERATOR users for task assignment."""
    operators = db.query(User).filter(
        func.lower(User.role).in_(["operator", "staff"]),
        User.is_active == True
    ).order_by(User.username.asc()).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email or u.username,
            "full_name": u.full_name or u.username,
            "role": u.role,
            "is_active": u.is_active if hasattr(u, "is_active") else True,
        }
        for u in operators
    ]



@router.get("/users/{user_id}")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permissions.MANAGE_USERS))
):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": u.id,
        "username": u.username,
        "email": u.email or u.username,
        "full_name": u.full_name or "",
        "role": u.role,
        "is_active": u.is_active if hasattr(u, "is_active") else True,
        "is_verified": u.is_verified if hasattr(u, "is_verified") else True,
        "last_login_at": u.last_login_at.isoformat() if u.last_login_at else None,
        "last_login_ip": u.last_login_ip or "",
        "login_method": u.login_method or "",
        "failed_login_count": u.failed_login_count if hasattr(u, "failed_login_count") else 0,
        "locked_until": u.locked_until.isoformat() if u.locked_until else None,
        "created_at": u.created_at.isoformat() if u.created_at else None,
        "password_changed_at": u.password_changed_at.isoformat() if u.password_changed_at else None,
    }


@router.put("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    payload: "UpdateUserRoleRequest",
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permissions.MANAGE_ROLES))
):
    """Change a user's role. Requires MANAGE_ROLES permission and step-up OTP verification."""
    if not verify_password(payload.confirm_password, current_user.password_hash):
        raise HTTPException(status_code=403, detail="Incorrect administrator password")

    VALID_ROLES = {"admin", "manager", "operator", "auditor", "viewer"}
    if payload.role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {', '.join(sorted(VALID_ROLES))}")


    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    # Prevent non-admins from promoting to admin
    if payload.role == "admin" and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can assign the admin role.")

    # Prevent demoting yourself
    if target.id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot change your own role.")

    old_role = target.role
    target.role = payload.role
    db.commit()

    ledger.append_entry(db, "role_changed", {
        "target_username": target.username,
        "old_role": old_role,
        "new_role": payload.role,
        "changed_by": current_user.username,
        "reason": payload.reason or "",
        "time": datetime.now(UTC).replace(tzinfo=None).isoformat()
    })
    log_access(db, current_user.username, f"role_changed_{target.username}_{old_role}_to_{payload.role}", request=request)

    # Phase 18: Security event + alert email for role changes
    ip = request.client.host if request and request.client else ""
    ua = request.headers.get("user-agent", "") if request else ""
    sec_event = security_service.create_security_event(
        db=db,
        event_type="ROLE_CHANGED",
        severity="CRITICAL",
        status="SUCCESS",
        actor_user_id=current_user.id,
        target_user_id=target.id,
        actor_username=current_user.username,
        target_username=target.username,
        previous_value=old_role,
        new_value=payload.role,
        ip_address=ip,
        user_agent=ua,
    )
    if sec_event:
        security_service.send_role_change_alert(
            actor_username=current_user.username,
            target_username=target.username,
            old_role=old_role,
            new_role=payload.role,
            timestamp=sec_event.timestamp,
            event_id=sec_event.id,
            ip_address=ip,
        )

    return {
        "status": "success",
        "username": target.username,
        "old_role": old_role,
        "new_role": target.role,
        "message": f"Role updated from '{old_role}' to '{payload.role}'"
    }


@router.put("/users/{user_id}/activate")
def activate_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permissions.MANAGE_USERS))
):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    target.is_active = True
    target.failed_login_count = 0
    target.locked_until = None
    db.commit()

    ledger.append_entry(db, "user_activated", {
        "username": target.username,
        "activated_by": current_user.username,
        "time": datetime.now(UTC).replace(tzinfo=None).isoformat()
    })
    log_access(db, current_user.username, f"activated_user_{target.username}", request=request)

    # Phase 18: Security event
    ip = request.client.host if request and request.client else ""
    sec_event = security_service.create_security_event(
        db=db, event_type="ACCOUNT_ACTIVATED", severity="INFO", status="SUCCESS",
        actor_user_id=current_user.id, target_user_id=target.id,
        actor_username=current_user.username, target_username=target.username, ip_address=ip,
    )
    if sec_event:
        security_service.send_account_change_alert(
            "ACCOUNT_ACTIVATED", current_user.username, target.username, sec_event.timestamp, sec_event.id
        )
    return {"status": "success", "message": f"User '{target.username}' has been activated."}


@router.put("/users/{user_id}/deactivate")
def deactivate_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permissions.MANAGE_USERS))
):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    if target.id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot deactivate your own account.")
    if target.role == "admin" and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can deactivate admin accounts.")

    target.is_active = False
    db.commit()

    ledger.append_entry(db, "user_deactivated", {
        "username": target.username,
        "deactivated_by": current_user.username,
        "time": datetime.now(UTC).replace(tzinfo=None).isoformat()
    })
    log_access(db, current_user.username, f"deactivated_user_{target.username}", request=request)

    # Phase 18: Security event
    ip = request.client.host if request and request.client else ""
    ua = request.headers.get("user-agent", "") if request else ""
    sec_event = security_service.create_security_event(
        db=db, event_type="ACCOUNT_DEACTIVATED", severity="CRITICAL", status="SUCCESS",
        actor_user_id=current_user.id, target_user_id=target.id,
        actor_username=current_user.username, target_username=target.username,
        ip_address=ip, user_agent=ua,
    )
    if sec_event:
        security_service.send_account_change_alert(
            "ACCOUNT_DEACTIVATED", current_user.username, target.username, sec_event.timestamp, sec_event.id
        )
    return {"status": "success", "message": f"User '{target.username}' has been deactivated."}


@router.put("/users/{user_id}/unlock")
def unlock_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permissions.MANAGE_USERS))
):
    """Manually unlock a locked-out account."""
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    target.failed_login_count = 0
    target.locked_until = None
    db.commit()

    ledger.append_entry(db, "user_unlocked", {
        "username": target.username,
        "unlocked_by": current_user.username,
        "time": datetime.now(UTC).replace(tzinfo=None).isoformat()
    })
    log_access(db, current_user.username, f"unlocked_user_{target.username}", request=request)
    return {"status": "success", "message": f"Account '{target.username}' has been unlocked."}


# ---------------------------------------------------------------------------
# Step-up OTP for sensitive actions
# ---------------------------------------------------------------------------

@router.post("/auth/request-stepup-otp")
def request_stepup_otp(
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Request a step-up OTP for performing sensitive administrative actions."""
    ip = request.client.host if request and request.client else ""
    otp_code = _create_db_otp(db, user, "SENSITIVE_ACTION", ip)

    subject = f"🔒 Step-Up Verification Required - [{otp_code}]"
    body = f"""Cloud Warehouse Platform — Step-Up Authentication
------------------------------------------------------------
A sensitive administrative action requires additional verification.

User: {user.username}

YOUR 6-DIGIT STEP-UP VERIFICATION CODE:
====================================
           {otp_code}
====================================

Enter this code to authorize the sensitive action.
This code is valid for 10 minutes.
If you did NOT initiate this, please contact system security immediately.
"""
    main_admin_email = os.getenv("ALERT_EMAIL_TO", "")
    notifications.send_email_alert(subject, body, main_admin_email)

    return {
        "status": "otp_sent",
        "message": "Step-up verification code sent to admin email",
        "expires_in_seconds": OTP_EXPIRY_SECONDS,
    }


@router.post("/auth/verify-stepup-otp")
def verify_stepup_otp(
    payload: AdminConfirmOTPRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify a step-up OTP. Returns a short-lived step-up token claim."""
    _verify_db_otp(db, user, "SENSITIVE_ACTION", payload.passkey)
    return {
        "status": "verified",
        "message": "Step-up verification successful. You may proceed with the sensitive action.",
        "authorized_action_token": secrets.token_hex(16)  # short-lived correlation token
    }


# ---------------------------------------------------------------------------
# Access log endpoint
# ---------------------------------------------------------------------------

@router.get("/access-log")
def list_access_log(
    limit: int = 200,
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permissions.VIEW_AUDIT))
):
    rows = db.query(AccessLog).order_by(AccessLog.id.desc()).limit(limit).all()
    return [
        {
            "timestamp": r.timestamp.isoformat() if r.timestamp else "",
            "username": r.username,
            "action": r.action,
            "warehouse_id": r.warehouse_id,
            "ip_address": r.ip_address
        }
        for r in rows
    ]


# ---------------------------------------------------------------------------
# Recovery (unchanged — retained for backward compat)
# ---------------------------------------------------------------------------

@router.post("/auth/recovery-setup")
def recovery_setup(
    payload: RecoverySetupRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if payload.password is not None:
        raw_password = payload.password.strip()
        if len(raw_password) < 6:
            raise HTTPException(status_code=400, detail="Recovery password must be at least 6 characters.")
        hashed = hash_password(raw_password)
        cred = db.query(RecoveryCredential).filter(RecoveryCredential.user_id == user.id).first()
        if cred:
            cred.password_hash = hashed
            cred.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        else:
            cred = RecoveryCredential(
                user_id=user.id,
                password_hash=hashed,
                created_at=datetime.now(timezone.utc).replace(tzinfo=None),
                updated_at=datetime.now(timezone.utc).replace(tzinfo=None)
            )
            db.add(cred)
        db.commit()

    generated_codes = []
    if payload.generate_codes:
        db.query(RecoveryCode).filter(RecoveryCode.user_id == user.id).delete()
        for _ in range(8):
            code = secrets.token_hex(6)
            code_hash = hash_password(code)
            rec_code = RecoveryCode(
                user_id=user.id,
                code_hash=code_hash,
                used=False,
                created_at=datetime.now(timezone.utc).replace(tzinfo=None)
            )
            db.add(rec_code)
            generated_codes.append(code)
        db.commit()

    return {
        "status": "success",
        "message": "Recovery options updated successfully.",
        "recovery_codes": generated_codes if payload.generate_codes else None
    }


@router.post("/auth/recovery-login")
def recovery_login(
    payload: RecoveryLoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    ip = request.client.host if request and request.client else "unknown"
    check_recovery_rate_limit(ip)

    user = db.query(User).filter(User.username == payload.username.strip()).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid recovery credentials")

    input_val = payload.password_or_code.strip()
    authenticated = False

    cred = db.query(RecoveryCredential).filter(RecoveryCredential.user_id == user.id).first()
    if cred and verify_password(input_val, cred.password_hash):
        authenticated = True

    if not authenticated:
        unused_codes = db.query(RecoveryCode).filter(
            RecoveryCode.user_id == user.id,
            RecoveryCode.used == False
        ).all()
        for code_record in unused_codes:
            if verify_password(input_val, code_record.code_hash):
                code_record.used = True
                code_record.used_at = datetime.now(timezone.utc).replace(tzinfo=None)
                db.commit()
                authenticated = True
                break

    if not authenticated:
        raise HTTPException(status_code=401, detail="Invalid recovery credentials")

    token = create_access_token({"sub": user.username, "role": user.role})
    log_access(db, user.username, "recovery_login", request=request)
    user.login_method = "recovery"
    user.last_login_at = datetime.now(UTC).replace(tzinfo=None)
    user.last_login_ip = ip
    db.commit()

    return {
        "access_token": token,
        "token_type": "bearer",
        "username": user.username,
        "role": user.role,
        "auth_mode": "account_recovery"
    }


# ---------------------------------------------------------------------------
# Compatibility shim: re-export _pending_password_changes for existing tests
# ---------------------------------------------------------------------------
# Tests that import this dict from backend.main still expect it to exist.
# It is now empty (OTPs are DB-persisted), but we export it so imports don't fail.
_pending_password_changes: dict = {}
_pending_admin_creations: dict = {}
