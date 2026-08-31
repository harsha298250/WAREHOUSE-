from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.auth import get_current_user
from backend.models import User
from backend.settings import get_settings, save_settings, reset_to_defaults, DEFAULT_SETTINGS

router = APIRouter(prefix="/api/settings", tags=["settings"])


def _require_admin(user: User = Depends(get_current_user)) -> User:
    if not user or getattr(user, "role", "").lower() != "admin":
        raise HTTPException(status_code=403, detail="Settings are restricted exclusively to Admin users.")
    return user


@router.get("", summary="Get global WMS settings")
def read_settings(
    db: Session = Depends(get_db),
    user: User = Depends(_require_admin)
):
    """Retrieve the consolidated WMS platform settings from PostgreSQL. Restricted to Admin users."""
    return get_settings(db)


@router.get("/defaults", summary="Get built-in default settings")
def read_default_settings(user: User = Depends(_require_admin)):
    """Return the hard-coded DEFAULT_SETTINGS. Restricted to Admin users."""
    return dict(DEFAULT_SETTINGS)


@router.post("", summary="Save global WMS settings")
def write_settings(
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(_require_admin)
):
    """Save/update WMS platform settings in the PostgreSQL database. Restricted to Admin users."""
    return save_settings(db, payload)


@router.delete("", summary="Reset settings to factory defaults")
def reset_settings(
    db: Session = Depends(get_db),
    user: User = Depends(_require_admin)
):
    """Wipe persisted settings and restore built-in defaults. Restricted to Admin users."""
    return reset_to_defaults(db)
