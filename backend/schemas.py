"""
schemas.py — Pydantic request/response models for the API.
Phase 9: Added CreateUserRequest, UpdateUserRoleRequest.
"""
from pydantic import BaseModel, Field
from datetime import date as date_type
from typing import Optional


class LoginRequest(BaseModel):
    username: str
    password: str


class WarehouseCreate(BaseModel):
    id: str
    name: str
    location: str = ""
    city: Optional[str] = ""
    state: Optional[str] = ""
    country: Optional[str] = ""
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)


class WarehouseUpdate(BaseModel):
    name: str
    location: str = ""
    city: Optional[str] = ""
    state: Optional[str] = ""
    country: Optional[str] = ""
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)


class ItemCreate(BaseModel):
    id: str
    name: str
    category: str = "General"
    unit_cost: float = 0.0
    lead_time_days: int = 3
    safety_stock: int = 10


class StockMovementCreate(BaseModel):
    date: date_type
    warehouse_id: str
    item_id: str
    stock_in: int = 0
    stock_out: int = 0


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class AdminCreateRequest(BaseModel):
    current_admin_password: str = ""
    username: str
    full_name: str
    email: str
    password: str
    role: Optional[str] = "admin"   # Phase 9: allow specifying role


class AdminConfirmOTPRequest(BaseModel):
    passkey: str


class VerifyPasswordRequest(BaseModel):
    password: str


class ConfirmChangePasswordRequest(BaseModel):
    passkey: str


class RecommendationActionRequest(BaseModel):
    action: str  # APPROVED | REJECTED | MODIFIED
    notes: Optional[str] = ""


class SimulationRequest(BaseModel):
    warehouse_id: str
    demand_surge_pct: float = 0.0  # e.g. 20.0 for +20%
    supplier_delay_days: int = 0
    transport_disruption: bool = False


class RecoverySetupRequest(BaseModel):
    password: Optional[str] = None
    generate_codes: bool = True


class RecoveryLoginRequest(BaseModel):
    username: str
    password_or_code: str


# ---------------------------------------------------------------------------
# Phase 9: User management schemas
# ---------------------------------------------------------------------------

class CreateUserRequest(BaseModel):
    username: str
    full_name: str
    email: str
    role: str = "viewer"
    password: Optional[str] = None   # If None, user must log in via Google OAuth


class UpdateUserRoleRequest(BaseModel):
    role: str
    reason: Optional[str] = ""
    confirm_password: str

