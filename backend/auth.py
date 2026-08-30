"""
auth.py — Admin login security layer.

- Passwords are never stored in plain text: bcrypt hash only.
- Login issues a JWT access token; every protected API route requires it
  in the Authorization header (Bearer token).
- SECRET_KEY MUST be changed and kept out of source control in a real
  deployment — it's read from an environment variable with a dev-only
  fallback so the project still runs out of the box for coursework.
- Phase 9: Added PERMISSIONS system, require_permission() dependency,
  account lockout enforcement, and active-user checks.
"""
import os
import bcrypt
from datetime import datetime, timedelta, UTC
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User, AccessLog

import logging

logger = logging.getLogger("warehouse")

RAW_SECRET = os.getenv("JWT_SECRET_KEY", "").strip()
IS_PROD = os.getenv("ENVIRONMENT", "development").lower() == "production"

if not RAW_SECRET or RAW_SECRET in ["dev-only-secret-change-me-in-production", "change-this-to-a-long-random-string"]:
    if IS_PROD:
        raise RuntimeError("JWT_SECRET_KEY is not configured for production environment!")
    else:
        logger.warning("SECURITY WARNING: JWT_SECRET_KEY is using a dev fallback string. Configure JWT_SECRET_KEY in production.")
        SECRET_KEY = "dev-only-secret-change-me-in-production"
else:
    SECRET_KEY = RAW_SECRET

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440 if os.getenv("ENVIRONMENT") == "testing" else 60

# Account lockout configuration
MAX_FAILED_LOGINS = 5          # lock after 5 consecutive failures
LOCKOUT_DURATION_MINUTES = 15  # lock for 15 minutes

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ---------------------------------------------------------------------------
# Phase 9: Permission System
# ---------------------------------------------------------------------------

# Permission constants
class Permissions:
    VIEW_DASHBOARD = "VIEW_DASHBOARD"
    VIEW_WAREHOUSE = "VIEW_WAREHOUSE"
    MANAGE_WAREHOUSE = "MANAGE_WAREHOUSE"
    VIEW_INVENTORY = "VIEW_INVENTORY"
    ADJUST_INVENTORY = "ADJUST_INVENTORY"
    CREATE_ORDER = "CREATE_ORDER"
    CANCEL_ORDER = "CANCEL_ORDER"
    PICK_ORDER = "PICK_ORDER"
    PACK_ORDER = "PACK_ORDER"
    SHIP_ORDER = "SHIP_ORDER"
    VIEW_TASKS = "VIEW_TASKS"
    MANAGE_TASKS = "MANAGE_TASKS"
    VIEW_ROBOTS = "VIEW_ROBOTS"
    CONTROL_SIMULATION = "CONTROL_SIMULATION"
    VIEW_AI = "VIEW_AI"
    REVIEW_AI_RECOMMENDATION = "REVIEW_AI_RECOMMENDATION"
    APPROVE_AI_RECOMMENDATION = "APPROVE_AI_RECOMMENDATION"
    VIEW_REPORTS = "VIEW_REPORTS"
    VIEW_AUDIT = "VIEW_AUDIT"
    VIEW_SECURITY = "VIEW_SECURITY"
    MANAGE_USERS = "MANAGE_USERS"
    MANAGE_ROLES = "MANAGE_ROLES"
    MANAGE_BACKUPS = "MANAGE_BACKUPS"
    VIEW_SYSTEM_HEALTH = "VIEW_SYSTEM_HEALTH"


# Role → Permission mapping
ROLE_PERMISSIONS: dict[str, set[str]] = {
    "admin": {
        # Admin has all permissions
        Permissions.VIEW_DASHBOARD, Permissions.VIEW_WAREHOUSE, Permissions.MANAGE_WAREHOUSE,
        Permissions.VIEW_INVENTORY, Permissions.ADJUST_INVENTORY,
        Permissions.CREATE_ORDER, Permissions.CANCEL_ORDER,
        Permissions.PICK_ORDER, Permissions.PACK_ORDER, Permissions.SHIP_ORDER,
        Permissions.VIEW_TASKS, Permissions.MANAGE_TASKS,
        Permissions.VIEW_ROBOTS, Permissions.CONTROL_SIMULATION,
        Permissions.VIEW_AI, Permissions.REVIEW_AI_RECOMMENDATION, Permissions.APPROVE_AI_RECOMMENDATION,
        Permissions.VIEW_REPORTS, Permissions.VIEW_AUDIT, Permissions.VIEW_SECURITY,
        Permissions.MANAGE_USERS, Permissions.MANAGE_ROLES,
        Permissions.MANAGE_BACKUPS, Permissions.VIEW_SYSTEM_HEALTH,
    },
    "manager": {
        Permissions.VIEW_DASHBOARD, Permissions.VIEW_WAREHOUSE, Permissions.MANAGE_WAREHOUSE,
        Permissions.VIEW_INVENTORY, Permissions.ADJUST_INVENTORY,
        Permissions.CREATE_ORDER, Permissions.CANCEL_ORDER,
        Permissions.PICK_ORDER, Permissions.PACK_ORDER, Permissions.SHIP_ORDER,
        Permissions.VIEW_TASKS, Permissions.MANAGE_TASKS,
        Permissions.VIEW_ROBOTS, Permissions.CONTROL_SIMULATION,
        Permissions.VIEW_AI, Permissions.REVIEW_AI_RECOMMENDATION, Permissions.APPROVE_AI_RECOMMENDATION,
        Permissions.VIEW_REPORTS, Permissions.VIEW_SECURITY,
        Permissions.VIEW_SYSTEM_HEALTH,
    },
    "operator": {
        Permissions.VIEW_DASHBOARD, Permissions.VIEW_WAREHOUSE,
        Permissions.VIEW_INVENTORY, Permissions.ADJUST_INVENTORY,
        Permissions.CREATE_ORDER, Permissions.PICK_ORDER, Permissions.PACK_ORDER, Permissions.SHIP_ORDER,
        Permissions.VIEW_TASKS,
        Permissions.VIEW_ROBOTS,
        Permissions.VIEW_AI,
    },
    "auditor": {
        Permissions.VIEW_DASHBOARD, Permissions.VIEW_WAREHOUSE,
        Permissions.VIEW_INVENTORY,
        Permissions.VIEW_TASKS,
        Permissions.VIEW_ROBOTS,
        Permissions.VIEW_AI,
        Permissions.VIEW_REPORTS, Permissions.VIEW_AUDIT, Permissions.VIEW_SECURITY,
        Permissions.VIEW_SYSTEM_HEALTH,
    },
    "viewer": {
        Permissions.VIEW_DASHBOARD, Permissions.VIEW_WAREHOUSE,
        Permissions.VIEW_INVENTORY,
        Permissions.VIEW_SYSTEM_HEALTH,
    },
    # Legacy alias for backward compatibility
    "staff": {
        Permissions.VIEW_DASHBOARD, Permissions.VIEW_WAREHOUSE,
        Permissions.VIEW_INVENTORY, Permissions.ADJUST_INVENTORY,
        Permissions.CREATE_ORDER, Permissions.PICK_ORDER, Permissions.PACK_ORDER, Permissions.SHIP_ORDER,
        Permissions.VIEW_TASKS,
    },
}


def get_user_permissions(role: str) -> set[str]:
    """Return the set of permissions granted to a role."""
    return ROLE_PERMISSIONS.get(role, set())


def has_permission(user: User, permission: str) -> bool:
    """Check if a user has a specific permission."""
    perms = get_user_permissions(user.role)
    return permission in perms


# ---------------------------------------------------------------------------
# Core auth utilities
# ---------------------------------------------------------------------------

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))


def create_access_token(data: dict, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC).replace(tzinfo=None) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def log_access(db: Session, username: str, action: str, warehouse_id: str = "", request=None):
    ip = request.client.host if request and request.client else ""
    db.add(AccessLog(username=username, action=action, warehouse_id=warehouse_id, ip_address=ip))
    db.commit()
    logger.info("ACCESS: user=%s action=%s warehouse=%s ip=%s", username, action, warehouse_id, ip)


def authenticate_user(db: Session, username: str, password: str):
    """
    Authenticate a user with password.
    Phase 9: Also checks is_active, enforces lockout, and tracks failed attempts.
    """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None

    # Check account lockout
    if user.locked_until and datetime.now(UTC).replace(tzinfo=None) < user.locked_until:
        minutes_remaining = int((user.locked_until - datetime.now(UTC).replace(tzinfo=None)).total_seconds() / 60) + 1
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account temporarily locked due to too many failed login attempts. "
                   f"Please try again in {minutes_remaining} minute(s)."
        )

    # Check account active status
    if hasattr(user, 'is_active') and not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Please contact your administrator."
        )

    if not verify_password(password, user.password_hash):
        # Increment failed login count
        if hasattr(user, 'failed_login_count'):
            user.failed_login_count = (user.failed_login_count or 0) + 1
            if user.failed_login_count >= MAX_FAILED_LOGINS:
                user.locked_until = datetime.now(UTC).replace(tzinfo=None) + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
                logger.warning("SECURITY: Account '%s' locked due to %d failed login attempts", username, user.failed_login_count)
                try:
                    from backend.event_processor import publish_event
                    publish_event(
                        db=db,
                        event_type="ACCOUNT_LOCKED",
                        warehouse_id=None,
                        source_entity_type="USER",
                        source_entity_id=str(user.id),
                        severity="HIGH",
                        payload={"username": username, "message": f"Account '{username}' has been locked due to repeated login failures."}
                    )
                except Exception as err:
                    logger.error("Failed to publish ACCOUNT_LOCKED event: %s", err)
            db.commit()
        return None

    # Successful login: reset failed counter and clear lockout
    if hasattr(user, 'failed_login_count'):
        user.failed_login_count = 0
        user.locked_until = None
        db.commit()

    return user


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception

    # Phase 9: Check active status on every authenticated request
    if hasattr(user, 'is_active') and not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Please contact your administrator."
        )

    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


def require_role(allowed_roles: list):
    """FastAPI dependency factory enforcing role-based access control."""
    def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles and user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires one of roles: {allowed_roles}"
            )
        return user
    return role_checker


def require_permission(permission: str):
    """
    Phase 9: FastAPI dependency factory for permission-level access control.
    More granular than require_role — checks specific permission within role matrix.
    
    Usage:
        @router.post("/inventory/adjust")
        def adjust(user=Depends(require_permission(Permissions.ADJUST_INVENTORY))):
            ...
    """
    def permission_checker(user: User = Depends(get_current_user)) -> User:
        if not has_permission(user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You do not have permission to perform this action. Required: {permission}"
            )
        return user
    return permission_checker
