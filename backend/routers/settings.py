from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.auth import get_current_user, require_permission, Permissions
from backend.models import User
from backend.settings import get_settings, save_settings, reset_to_defaults, DEFAULT_SETTINGS

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("", summary="Get global WMS settings")
def read_settings(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Retrieve the consolidated WMS platform settings from PostgreSQL.
    Always returns the full settings dict with defaults for any missing keys.
    """
    return get_settings(db)


@router.get("/defaults", summary="Get built-in default settings")
def read_default_settings(user: User = Depends(get_current_user)):
    """Return the hard-coded DEFAULT_SETTINGS so the frontend can show them on Reset."""
    return dict(DEFAULT_SETTINGS)


@router.post("", summary="Save global WMS settings")
def write_settings(
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permissions.VIEW_SYSTEM_HEALTH))
):
    """Save/update WMS platform settings in the PostgreSQL database."""
    if user.role not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail="Only administrators or managers can modify settings.")
    return save_settings(db, payload)


@router.delete("", summary="Reset settings to factory defaults")
def reset_settings(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Wipe persisted settings and restore built-in defaults."""
    if user.role not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail="Only administrators or managers can reset settings.")
    return reset_to_defaults(db)
