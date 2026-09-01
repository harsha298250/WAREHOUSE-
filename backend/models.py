"""
models.py - SQLAlchemy ORM models for PostgreSQL.
This replaces the SQLite layer from v1/v2 with a real PostgreSQL database,
including user accounts, warehouses/items you define yourself (not just
the synthetic demo set), manually-recorded stock movements, and the
tables that back every novelty module (shrinkage flags, audit ledger,
access log).
"""
from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime, Boolean, ForeignKey, Text, UniqueConstraint, JSON
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, UTC

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=True, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="viewer", nullable=False)
    # Roles: admin | manager | operator | auditor | viewer
    full_name = Column(String(120), default="")
    google_subject_id = Column(String(128), nullable=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), onupdate=lambda: datetime.now(UTC).replace(tzinfo=None))

    # Phase 9: Account security fields
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    last_logout_at = Column(DateTime, nullable=True)
    last_login_ip = Column(String(45), nullable=True)
    login_location = Column(String(255), nullable=True)
    login_method = Column(String(30), nullable=True)  # password | google_oauth | recovery
    failed_login_count = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)
    email_verified_at = Column(DateTime, nullable=True)
    password_changed_at = Column(DateTime, nullable=True)



class Warehouse(Base):
    __tablename__ = "warehouses"
    id = Column(String(50), primary_key=True)          # e.g. WH-CHN-01
    name = Column(String(255), nullable=False)
    location = Column(Text, default="")
    city = Column(String(120), nullable=True)
    state = Column(String(120), nullable=True)
    country = Column(String(120), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None))


class Item(Base):
    __tablename__ = "items"
    id = Column(String(20), primary_key=True)          # e.g. ITM001
    name = Column(String(150), nullable=False)
    category = Column(String(80), default="General")
    unit_cost = Column(Float, default=0.0)
    lead_time_days = Column(Integer, default=3)
    safety_stock = Column(Integer, default=10)
    sku = Column(String(64), unique=True, index=True, nullable=True)
    description = Column(Text, nullable=True)
    unit = Column(String(20), default="units")
    weight_kg = Column(Float, default=0.0)
    dimensions = Column(String(50), default="")
    barcode = Column(String(64), nullable=True)
    is_active = Column(Boolean, default=True)
    reorder_threshold = Column(Integer, default=20)
    preferred_storage_type = Column(String(20), default="STORAGE")
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None))


class StockMovement(Base):
    __tablename__ = "stock_movements"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, index=True)
    warehouse_id = Column(String(20), ForeignKey("warehouses.id"), nullable=False, index=True)
    item_id = Column(String(20), ForeignKey("items.id"), nullable=False, index=True)
    stock_in = Column(Integer, default=0)
    stock_out = Column(Integer, default=0)
    closing_stock = Column(Integer, default=0)
    is_anomaly = Column(Boolean, default=False)
    anomaly_type = Column(String(30), default="none")
    entry_source = Column(String(20), default="manual")  # manual | simulated
    entered_by = Column(String(64), default="")
    __table_args__ = (UniqueConstraint("date", "warehouse_id", "item_id", name="uq_movement"),)


class ShrinkageFlag(Base):
    __tablename__ = "shrinkage_flags"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    warehouse_id = Column(String(20), nullable=False)
    item_id = Column(String(20), nullable=False)
    item_name = Column(String(150), default="")
    deviation_score = Column(Float, default=0.0)
    expected_quantity = Column(Float, default=0.0)
    actual_quantity = Column(Float, default=0.0)
    discrepancy_quantity = Column(Float, default=0.0)
    estimated_exposure = Column(Float, default=0.0)
    severity = Column(String(20), default="MEDIUM")
    likely_cause = Column(String(80), default="")
    explanation = Column(Text, default="")


class AuditLedger(Base):
    __tablename__ = "audit_ledger"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None))
    event_type = Column(String(50), nullable=False)
    details = Column(Text, default="{}")
    prev_hash = Column(String(64), nullable=False)
    hash = Column(String(64), nullable=False)


class AccessLog(Base):
    """
    Real access-log table (replaces the simulated version from v2).
    Every authenticated action a user takes gets recorded here, so the
    access-anomaly novelty module analyses genuine login/edit activity
    instead of synthetic data.
    """
    __tablename__ = "access_log"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), index=True)
    username = Column(String(64), nullable=False)
    warehouse_id = Column(String(20), default="")
    action = Column(String(50), nullable=False)   # login | add_stock | add_warehouse | add_item | view
    ip_address = Column(String(45), default="")


class AIRecommendation(Base):
    """
    Human-in-the-loop AI recommendation tracking model.
    Stores explainable recommendations, confidence scores, and manager decisions.
    """
    __tablename__ = "ai_recommendations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), index=True)
    warehouse_id = Column(String(20), nullable=False)
    item_id = Column(String(50), default="")
    title = Column(String(100), nullable=False)
    risk_level = Column(String(20), default="MEDIUM")  # LOW | MEDIUM | HIGH | CRITICAL
    action_recommended = Column(String(100), nullable=False)
    confidence_score = Column(Integer, default=85)  # 0-100
    input_factors = Column(Text, default="{}")
    status = Column(String(20), default="NEW")  # NEW | REVIEWED | APPROVED | REJECTED | EXECUTED | EXPIRED | DISMISSED
    decision_by = Column(String(64), default="")
    decision_time = Column(DateTime, nullable=True)
    notes = Column(Text, default="")

    # Phase 8 extensions
    recommendation_type = Column(String(50), nullable=True, index=True)
    # DEMAND_FORECAST|REPLENISHMENT|STOCKOUT_RISK|OVERSTOCK_RISK|ANOMALY|SHRINKAGE_REVIEW|TASK_PRIORITY|ROBOT_ASSIGNMENT|CONGESTION|CAPACITY|ORDER_RISK|WAREHOUSE_RISK
    description = Column(Text, nullable=True)
    priority = Column(String(20), default="MEDIUM", nullable=True)
    score = Column(Integer, default=0, nullable=True)
    confidence_or_reliability = Column(String(50), default="HIGH", nullable=True)
    source_model = Column(String(50), nullable=True)
    source_entity_type = Column(String(50), nullable=True)
    source_entity_id = Column(String(50), nullable=True)
    recommended_action = Column(String(200), nullable=True)
    estimated_impact = Column(Float, nullable=True)
    explanation = Column(Text, nullable=True)
    supporting_metrics = Column(Text, default="{}", nullable=True)  # JSON string
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False, index=True)
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by = Column(String(64), nullable=True)
    review_notes = Column(Text, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    rec_metadata = Column("metadata", Text, default="{}", nullable=False)


class RecoveryCredential(Base):
    __tablename__ = "recovery_credentials"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), onupdate=lambda: datetime.now(UTC).replace(tzinfo=None))

    user = relationship("User", back_populates="recovery_credential_rel")


class RecoveryCode(Base):
    __tablename__ = "recovery_codes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    code_hash = Column(String(255), nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None))
    used_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="recovery_codes_rel")


class BackupRecord(Base):
    __tablename__ = "backup_records"
    id = Column(Integer, primary_key=True, autoincrement=True)
    backup_id = Column(String(64), nullable=False, unique=True, index=True)
    filename = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), index=True)
    size_bytes = Column(Integer, nullable=True)
    sha256 = Column(String(64), nullable=True)
    status = Column(String(20), default="QUEUED", nullable=False) # QUEUED | RUNNING | UPLOADED | VERIFIED | RESTORE_TESTED | FAILED | EXPIRED | DELETED
    storage_key = Column(String(255), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Extended Phase 11 fields
    backup_type = Column(String(50), default="MANUAL", nullable=True) # MANUAL | SCHEDULED | PRE_MAINTENANCE | EMERGENCY
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    storage_provider = Column(String(50), nullable=True) # e.g. "Backblaze B2", "Local Fallback"
    bucket = Column(String(255), nullable=True)
    checksum_algorithm = Column(String(20), default="SHA-256")
    verification_status = Column(String(50), default="PENDING") # PENDING | VERIFIED | FAILED
    verification_at = Column(DateTime, nullable=True)
    restore_test_status = Column(String(50), default="PENDING") # PENDING | SUCCESS | FAILED
    restore_test_at = Column(DateTime, nullable=True)
    retention_status = Column(String(50), default="ACTIVE") # ACTIVE | EXPIRED | DELETED
    initiated_by = Column(String(100), nullable=True)
    audit_ref = Column(String(255), nullable=True)


class WarehouseLocation(Base):
    __tablename__ = "warehouse_locations"
    id = Column(String(50), primary_key=True)  # e.g. WH-BLR-01-A-01-02
    warehouse_id = Column(String(20), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False, index=True)
    zone = Column(String(20), nullable=False)
    aisle = Column(String(20), nullable=False)
    rack = Column(String(20), nullable=False)
    shelf = Column(String(20), nullable=False)
    x = Column(Float, nullable=True)
    y = Column(Float, nullable=True)
    capacity = Column(Integer, default=500)
    current_utilization = Column(Integer, default=0)
    location_type = Column(String(20), default="STORAGE")  # STORAGE | PICKING | PACKING | RECEIVING | SHIPPING | STAGING | CHARGING | BUFFER
    status = Column(String(20), default="ACTIVE")
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None))

    warehouse = relationship("Warehouse")


class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, autoincrement=True)
    warehouse_id = Column(String(20), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False, index=True)
    item_id = Column(String(20), ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True)
    location_id = Column(String(50), ForeignKey("warehouse_locations.id", ondelete="SET NULL"), nullable=True, index=True)
    on_hand = Column(Integer, default=0, nullable=False)
    reserved = Column(Integer, default=0, nullable=False)
    available = Column(Integer, default=0, nullable=False)
    damaged = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), onupdate=lambda: datetime.now(UTC).replace(tzinfo=None))

    warehouse = relationship("Warehouse")
    item = relationship("Item")
    location = relationship("WarehouseLocation")

    __table_args__ = (
        UniqueConstraint("warehouse_id", "item_id", "location_id", name="uq_warehouse_item_location"),
    )


class Order(Base):
    __tablename__ = "orders"
    id = Column(String(20), primary_key=True)  # e.g. ORD-2026-001
    customer_ref = Column(String(100), nullable=False)
    warehouse_id = Column(String(20), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), onupdate=lambda: datetime.now(UTC).replace(tzinfo=None))
    status = Column(String(30), default="CREATED", nullable=False, index=True)
    priority = Column(String(20), default="MEDIUM", nullable=False)
    total_items = Column(Integer, default=0, nullable=False)
    notes = Column(Text, nullable=True)
    created_by = Column(String(64), default="")

    warehouse = relationship("Warehouse")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(20), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    item_id = Column(String(20), ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True)
    requested_qty = Column(Integer, nullable=False)
    reserved_qty = Column(Integer, default=0, nullable=False)
    picked_qty = Column(Integer, default=0, nullable=False)
    packed_qty = Column(Integer, default=0, nullable=False)
    shipped_qty = Column(Integer, default=0, nullable=False)
    status = Column(String(20), default="PENDING", nullable=False)

    order = relationship("Order", back_populates="items")
    item = relationship("Item")


class InventoryReservation(Base):
    __tablename__ = "inventory_reservations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(20), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    item_id = Column(String(20), ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True)
    location_id = Column(String(50), ForeignKey("warehouse_locations.id", ondelete="SET NULL"), nullable=True, index=True)
    reserved_qty = Column(Integer, nullable=False)
    released_qty = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), index=True)

    order = relationship("Order")
    item = relationship("Item")
    location = relationship("WarehouseLocation")


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_number = Column(String(64), unique=True, nullable=False, index=True)
    warehouse_id = Column(String(20), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False, index=True)
    task_type = Column(String(30), nullable=False, index=True)  # PICK | REPLENISH | PUTAWAY | TRANSFER | RECEIVE | PACK | SHIP | CYCLE_COUNT | INVENTORY_CHECK
    priority = Column(String(20), default="MEDIUM", nullable=False)  # CRITICAL | HIGH | MEDIUM | LOW
    priority_score = Column(Integer, default=0, nullable=False, index=True)
    status = Column(String(30), default="QUEUED", nullable=False, index=True)  # QUEUED | PRIORITIZED | ASSIGNED | IN_PROGRESS | COMPLETED | PAUSED | FAILED | REASSIGNED | CANCELLED
    source_type = Column(String(30), nullable=True)  # ORDER | REPLENISHMENT | manual
    source_id = Column(String(64), nullable=True)
    order_id = Column(String(20), ForeignKey("orders.id", ondelete="CASCADE"), nullable=True, index=True)
    order_item_id = Column(Integer, ForeignKey("order_items.id", ondelete="CASCADE"), nullable=True, index=True)
    product_id = Column(String(20), ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True)
    source_location_id = Column(String(50), ForeignKey("warehouse_locations.id", ondelete="SET NULL"), nullable=True, index=True)
    destination_location_id = Column(String(50), ForeignKey("warehouse_locations.id", ondelete="SET NULL"), nullable=True, index=True)
    requested_quantity = Column(Integer, nullable=False)
    completed_quantity = Column(Integer, default=0, nullable=False)
    assigned_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    assigned_robot_id = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), index=True)
    prioritized_at = Column(DateTime, nullable=True)
    assigned_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    paused_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    due_at = Column(DateTime, nullable=True, index=True)
    retry_count = Column(Integer, default=0, nullable=False)
    failure_reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    task_metadata = Column("metadata", Text, default="{}", nullable=False)
    depends_on_task_id = Column(Integer, ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)

    order = relationship("Order")
    order_item = relationship("OrderItem")
    product = relationship("Item", foreign_keys=[product_id])
    source_location = relationship("WarehouseLocation", foreign_keys=[source_location_id])
    destination_location = relationship("WarehouseLocation", foreign_keys=[destination_location_id])
    assigned_user = relationship("User", foreign_keys=[assigned_user_id])
    depends_on_task = relationship("Task", remote_side=[id])
    events = relationship("TaskEvent", back_populates="task", cascade="all, delete-orphan")
    assigned_robot = relationship("Robot", foreign_keys=[assigned_robot_id], primaryjoin="Task.assigned_robot_id == Robot.robot_code")


class TaskEvent(Base):
    __tablename__ = "task_events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)
    previous_status = Column(String(30), nullable=True)
    new_status = Column(String(30), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False)
    reason = Column(Text, nullable=True)
    event_metadata = Column("metadata", Text, default="{}", nullable=False)

    task = relationship("Task", back_populates="events")
    user = relationship("User")



class PackingRecord(Base):
    __tablename__ = "packing_records"
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(20), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(20), default="PENDING", nullable=False)  # PENDING | IN_PROGRESS | COMPLETED | FAILED
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    operator = Column(String(64), default="")
    package_count = Column(Integer, default=1, nullable=False)
    weight_kg = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)

    order = relationship("Order")


class Shipment(Base):
    __tablename__ = "shipments"
    id = Column(String(20), primary_key=True)  # e.g. SHP-2026-001
    order_id = Column(String(20), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(20), default="READY", nullable=False)  # READY | SHIPPED | IN_TRANSIT | DELIVERED | CANCELLED
    tracking_reference = Column(String(100), nullable=True)
    carrier = Column(String(50), default="Standard Carrier")
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None))
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)

    order = relationship("Order")


class OrderEvent(Base):
    __tablename__ = "order_events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(20), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), index=True)
    status = Column(String(30), nullable=False)
    event_type = Column(String(50), nullable=False)
    operator = Column(String(64), default="")
    notes = Column(Text, nullable=True)

    order = relationship("Order")


class Robot(Base):
    __tablename__ = "robots"
    id = Column(Integer, primary_key=True, autoincrement=True)
    robot_code = Column(String(30), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    warehouse_id = Column(String(20), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(30), default="IDLE", nullable=False, index=True) # IDLE, AVAILABLE, ASSIGNED, MOVING, PICKING, RETURNING, CHARGING, PAUSED, OFFLINE, FAILED, MAINTENANCE
    battery_level = Column(Float, default=100.0, nullable=False)
    current_location_id = Column(String(50), ForeignKey("warehouse_locations.id", ondelete="SET NULL"), nullable=True, index=True)
    current_x = Column(Float, default=0.0, nullable=False)
    current_y = Column(Float, default=0.0, nullable=False)
    target_location_id = Column(String(50), ForeignKey("warehouse_locations.id", ondelete="SET NULL"), nullable=True, index=True)
    target_x = Column(Float, default=0.0, nullable=False)
    target_y = Column(Float, default=0.0, nullable=False)
    assigned_task_id = Column(Integer, ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True, index=True)
    total_tasks_completed = Column(Integer, default=0, nullable=False)
    total_distance = Column(Float, default=0.0, nullable=False)
    total_operating_time = Column(Float, default=0.0, nullable=False)
    utilization_percent = Column(Float, default=0.0, nullable=False)
    failure_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), onupdate=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False)
    last_heartbeat_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False)
    robot_type = Column(String(30), default="AGV", nullable=False)
    max_payload = Column(Float, default=200.0, nullable=False)
    max_speed = Column(Float, default=1.5, nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)
    robot_metadata = Column("metadata", Text, default="{}", nullable=False)

    warehouse = relationship("Warehouse")
    current_location = relationship("WarehouseLocation", foreign_keys=[current_location_id])
    target_location = relationship("WarehouseLocation", foreign_keys=[target_location_id])
    assigned_task = relationship("Task", foreign_keys=[assigned_task_id])

class RobotTelemetryEvent(Base):
    __tablename__ = "robot_telemetry"
    id = Column(Integer, primary_key=True, autoincrement=True)
    robot_id = Column(Integer, ForeignKey("robots.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False) # POSITION_UPDATED, BATTERY_UPDATED, STATUS_CHANGED, TASK_STARTED, TASK_COMPLETED, FAILURE, CHARGING_STARTED, CHARGING_COMPLETED
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False, index=True)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    battery = Column(Float, nullable=False)
    status = Column(String(30), nullable=False)
    task_id = Column(Integer, nullable=True)
    telemetry_metadata = Column("metadata", Text, default="{}", nullable=False)

    robot = relationship("Robot")


class WarehouseGridCell(Base):
    __tablename__ = "warehouse_grid_cells"
    id = Column(Integer, primary_key=True, autoincrement=True)
    warehouse_id = Column(String(20), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False, index=True)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    cell_type = Column(String(30), default="FLOOR", nullable=False) # FLOOR, RACK, WALL, OBSTACLE, CHARGING, PICKING, PACKING, RECEIVING, SHIPPING, STAGING, RESTRICTED
    traversable = Column(Boolean, default=True, nullable=False)
    occupied = Column(Boolean, default=False, nullable=False)
    restricted = Column(Boolean, default=False, nullable=False)
    cost = Column(Float, default=1.0, nullable=False)
    cell_metadata = Column("metadata", Text, default="{}", nullable=False)

    warehouse = relationship("Warehouse")
    __table_args__ = (UniqueConstraint("warehouse_id", "x", "y", name="uq_grid_cell"),)

class WarehouseObstacle(Base):
    __tablename__ = "warehouse_obstacles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    warehouse_id = Column(String(20), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False, index=True)
    obstacle_type = Column(String(30), default="TEMPORARY_BLOCK", nullable=False) # RACK, WALL, EQUIPMENT, TEMPORARY_BLOCK, RESTRICTED_ZONE
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    width = Column(Integer, default=1, nullable=False)
    height = Column(Integer, default=1, nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    severity = Column(String(20), default="MEDIUM", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), onupdate=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False)

    warehouse = relationship("Warehouse")

class RobotRoute(Base):
    __tablename__ = "robot_routes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    robot_id = Column(Integer, ForeignKey("robots.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True, index=True)
    warehouse_id = Column(String(20), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False, index=True)
    start_x = Column(Integer, nullable=False)
    start_y = Column(Integer, nullable=False)
    goal_x = Column(Integer, nullable=False)
    goal_y = Column(Integer, nullable=False)
    algorithm = Column(String(30), default="A_STAR", nullable=False)
    path_data = Column(Text, default="[]", nullable=False) # JSON list of [x, y] coordinates
    distance = Column(Float, default=0.0, nullable=False)
    cost = Column(Float, default=0.0, nullable=False)
    status = Column(String(20), default="PLANNED", nullable=False) # PLANNED, ACTIVE, COMPLETED, INVALIDATED, REPLANNED, FAILED
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False)
    completed_at = Column(DateTime, nullable=True)

    robot = relationship("Robot")
    task = relationship("Task")
    warehouse = relationship("Warehouse")

class RobotReservation(Base):
    __tablename__ = "robot_reservations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    robot_id = Column(Integer, ForeignKey("robots.id", ondelete="CASCADE"), nullable=False, index=True)
    warehouse_id = Column(String(20), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False, index=True)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    tick = Column(Integer, nullable=False)

    robot = relationship("Robot")
    warehouse = relationship("Warehouse")


# ---------------------------------------------------------------------------
# Phase 7: Digital Twin Simulation Models
# ---------------------------------------------------------------------------

class DigitalTwinSimulation(Base):
    """
    Represents one Digital Twin simulation session lifecycle.
    Simulation state is separate from production operational state.
    """
    __tablename__ = "digital_twin_simulations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    warehouse_id = Column(String(20), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False, index=True)
    simulation_status = Column(String(20), default="IDLE", nullable=False, index=True)
    # Valid: IDLE | READY | RUNNING | PAUSED | COMPLETED | STOPPED | ERROR
    simulation_time_seconds = Column(Float, default=0.0, nullable=False)
    speed_multiplier = Column(Float, default=1.0, nullable=False)  # 0.5, 1, 2, 5, 10
    seed = Column(Integer, default=42, nullable=False)
    mode = Column(String(20), default="OBSERVATION", nullable=False)  # OBSERVATION | SIMULATION
    scenario_type = Column(String(30), default="NORMAL_OPERATIONS", nullable=False)
    # Valid: NORMAL_OPERATIONS | HIGH_DEMAND | ROBOT_FAILURE | CONGESTION | OBSTACLE_EVENT
    tick_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False, index=True)
    started_at = Column(DateTime, nullable=True)
    paused_at = Column(DateTime, nullable=True)
    stopped_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    created_by = Column(String(64), default="system", nullable=False)

    warehouse = relationship("Warehouse")
    snapshots = relationship("SimulationSnapshot", back_populates="simulation", cascade="all, delete-orphan")
    events = relationship("SimulationEvent", back_populates="simulation", cascade="all, delete-orphan")


class SimulationSnapshot(Base):
    """
    Point-in-time snapshot of Digital Twin state.
    Used for RESET restoration and state comparison.
    Production inventory (on_hand) is NEVER modified by simulation.
    sim_inventory_delta tracks simulated pick changes in isolation.
    """
    __tablename__ = "simulation_snapshots"
    id = Column(Integer, primary_key=True, autoincrement=True)
    simulation_id = Column(Integer, ForeignKey("digital_twin_simulations.id", ondelete="CASCADE"), nullable=False, index=True)
    warehouse_id = Column(String(20), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False, index=True)
    snapshot_version = Column(Integer, default=1, nullable=False)
    taken_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False)
    sim_time_seconds = Column(Float, default=0.0, nullable=False)
    robot_states = Column(Text, default="[]", nullable=False)        # JSON list of robot state dicts
    task_states = Column(Text, default="[]", nullable=False)         # JSON list of task state dicts
    obstacle_states = Column(Text, default="[]", nullable=False)     # JSON list of obstacle state dicts
    sim_inventory_delta = Column(Text, default="{}", nullable=False) # JSON: {item_id: qty_simulated_picked}
    snapshot_metadata = Column("metadata", Text, default="{}", nullable=False)

    simulation = relationship("DigitalTwinSimulation", back_populates="snapshots")
    warehouse = relationship("Warehouse")


class SimulationEvent(Base):
    """
    Digital Twin event stream entry.
    Captures significant simulation state changes for event replay and timeline.
    """
    __tablename__ = "simulation_events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    simulation_id = Column(Integer, ForeignKey("digital_twin_simulations.id", ondelete="CASCADE"), nullable=False, index=True)
    warehouse_id = Column(String(20), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    # ROBOT_MOVED|ROBOT_ASSIGNED|TASK_STARTED|TASK_COMPLETED|ROUTE_PLANNED|ROUTE_REPLANNED
    # |COLLISION_AVOIDED|ROBOT_WAITING|BATTERY_LOW|BATTERY_CRITICAL|OBSTACLE_CREATED
    # |OBSTACLE_REMOVED|TASK_FAILED|ROBOT_FAILED|SIMULATION_STARTED|SIMULATION_PAUSED
    # |SIMULATION_RESUMED|SIMULATION_STOPPED|SIMULATION_COMPLETED|SIMULATION_RESET|SIMULATION_ERROR
    severity = Column(String(10), default="INFO", nullable=False)    # INFO | SUCCESS | WARNING | CRITICAL
    sim_time_seconds = Column(Float, default=0.0, nullable=False)
    real_timestamp = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False, index=True)
    robot_id = Column(Integer, nullable=True, index=True)
    task_id = Column(Integer, nullable=True, index=True)
    location_id = Column(String(50), nullable=True)
    route_id = Column(Integer, nullable=True)
    message = Column(Text, nullable=False)
    event_metadata = Column("metadata", Text, default="{}", nullable=False)

    simulation = relationship("DigitalTwinSimulation", back_populates="events")
    warehouse = relationship("Warehouse")


# ---------------------------------------------------------------------------
# Phase 9: Security — OTP Records and User Sessions
# ---------------------------------------------------------------------------

class OTPRecord(Base):
    """
    DB-persisted OTP record replacing the in-memory pending dicts.
    Supports purposes: ACCOUNT_ACTIVATION | EMAIL_VERIFICATION |
    PASSWORD_CHANGE | PASSWORD_RESET | SENSITIVE_ACTION | ADMIN_CREATION
    """
    __tablename__ = "otp_records"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    purpose = Column(String(50), nullable=False)
    code_hash = Column(String(255), nullable=False)  # bcrypt hash — never store plaintext
    expires_at = Column(DateTime, nullable=False, index=True)
    attempts = Column(Integer, default=0, nullable=False)
    max_attempts = Column(Integer, default=5, nullable=False)
    consumed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False)
    request_ip = Column(String(45), nullable=True)
    context_data = Column(Text, default="{}", nullable=True)  # JSON — stores target email for ADMIN_CREATION, etc.

    user = relationship("User", back_populates="otp_records_rel")

    __table_args__ = (
        # Composite index for fast lookup of active OTPs per user+purpose
        UniqueConstraint("user_id", "purpose", name="uq_otp_user_purpose"),
    )


class UserSession(Base):
    """
    Session tracking table for login/logout lifecycle audit.
    Does not store the actual JWT (stateless), only a reference hash.
    """
    __tablename__ = "user_sessions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_token_hash = Column(String(64), nullable=False, unique=True)  # SHA-256 of token prefix
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False)
    last_seen_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    revoked_at = Column(DateTime, nullable=True)
    revoke_reason = Column(String(100), nullable=True)  # logout | password_change | admin_revoke
    login_method = Column(String(30), nullable=True)
    ip_address = Column(String(45), nullable=True)
    login_location = Column(String(255), nullable=True)
    user_agent = Column(String(500), nullable=True)

    user = relationship("User", back_populates="sessions_rel")


# Add relationships to User model
User.recovery_credential_rel = relationship("RecoveryCredential", uselist=False, back_populates="user", cascade="all, delete-orphan")
User.recovery_codes_rel = relationship("RecoveryCode", back_populates="user", cascade="all, delete-orphan")
User.otp_records_rel = relationship("OTPRecord", back_populates="user", cascade="all, delete-orphan")
User.sessions_rel = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")

# Mappings optimized directly in model declarations above


# ---------------------------------------------------------------------------
# Phase 10: Event & Notification Automation Models
# ---------------------------------------------------------------------------

class UserWarehouseAccess(Base):
    __tablename__ = "user_warehouse_access"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    warehouse_id = Column(String(20), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False)

    user = relationship("User", back_populates="warehouse_access_rel")
    warehouse = relationship("Warehouse")

    __table_args__ = (
        UniqueConstraint("user_id", "warehouse_id", name="uq_user_warehouse"),
    )


class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    warehouse_id = Column(String(20), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=True, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    notification_type = Column(String(50), nullable=False)
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(20), default="INFO", nullable=False)  # INFO | SUCCESS | WARNING | HIGH | CRITICAL
    status = Column(String(20), default="PENDING", nullable=False, index=True)  # PENDING | QUEUED | SENT | DELIVERED | READ | FAILED | EXPIRED | CANCELLED
    channel = Column(String(20), nullable=False)  # IN_APP | EMAIL
    source_entity_type = Column(String(50), nullable=True)
    source_entity_id = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False, index=True)
    read_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    notif_metadata = Column("metadata", Text, default="{}", nullable=False)  # JSON string
    idempotency_key = Column(String(255), unique=True, nullable=True)

    user = relationship("User", back_populates="notifications_rel")
    warehouse = relationship("Warehouse")


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)  # orders | inventory | tasks | robots | ai | security | simulation | system
    in_app_enabled = Column(Boolean, default=True, nullable=False)
    email_enabled = Column(Boolean, default=True, nullable=False)
    min_severity = Column(String(20), default="INFO", nullable=False)  # INFO | SUCCESS | WARNING | HIGH | CRITICAL
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), onupdate=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False)

    user = relationship("User", back_populates="notification_preferences_rel")

    __table_args__ = (
        UniqueConstraint("user_id", "category", name="uq_user_category_preference"),
    )


# User relations for Phase 10
User.warehouse_access_rel = relationship("UserWarehouseAccess", back_populates="user", cascade="all, delete-orphan")
User.notifications_rel = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
User.notification_preferences_rel = relationship("NotificationPreference", back_populates="user", cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# Phase 13: Scenario Lab & Algorithm Experiments Models
# ---------------------------------------------------------------------------

class Scenario(Base):
    __tablename__ = "scenarios"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    warehouse_id = Column(String(20), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False, index=True)
    scenario_type = Column(String(30), default="BASELINE", nullable=False)
    configuration = Column(JSON, default={}, nullable=False)
    random_seed = Column(Integer, default=42, nullable=False)
    status = Column(String(20), default="ACTIVE", nullable=False)
    tags = Column(Text, default="[]", nullable=False)
    notes = Column(Text, nullable=True)
    created_by = Column(String(64), default="system", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), onupdate=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False)

    warehouse = relationship("Warehouse")


class Experiment(Base):
    __tablename__ = "experiments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id", ondelete="CASCADE"), nullable=False, index=True)
    experiment_name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="QUEUED", nullable=False)
    algorithm_name = Column(String(50), nullable=False)
    algorithm_version = Column(String(20), default="1.0", nullable=False)
    configuration = Column(JSON, default={}, nullable=False)
    random_seed = Column(Integer, default=42, nullable=False)
    repetitions = Column(Integer, default=1, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    created_by = Column(String(64), default="system", nullable=False)
    error_message = Column(Text, nullable=True)
    metrics_summary = Column(JSON, nullable=True)  # Aggregated metrics across repetitions
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False)

    scenario = relationship("Scenario")
    runs = relationship("ExperimentRun", back_populates="experiment", cascade="all, delete-orphan")


class ExperimentRun(Base):
    __tablename__ = "experiment_runs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False, index=True)
    repetition_number = Column(Integer, nullable=False)
    random_seed = Column(Integer, nullable=False)
    status = Column(String(20), default="QUEUED", nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
    metrics = Column(JSON, nullable=True)  # KPIs for this specific run
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False)

    experiment = relationship("Experiment", back_populates="runs")


class SimulationRun(Base):
    __tablename__ = "simulation_runs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    warehouse_id = Column(String(20), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False, index=True)
    mode = Column(String(30), nullable=False)  # OFFLINE_SNAPSHOT | HISTORICAL_REPLAY | EXPERIMENT
    status = Column(String(20), default="QUEUED", nullable=False)  # QUEUED | RUNNING | COMPLETED | FAILED
    created_by = Column(String(64), default="system", nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    simulation_duration = Column(Float, nullable=False, default=480.0)  # in minutes
    random_seed = Column(Integer, default=42, nullable=False)
    configuration = Column(JSON, default={}, nullable=False)
    data_source = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False)

    warehouse = relationship("Warehouse")
    results = relationship("SimulationResult", back_populates="run", cascade="all, delete-orphan")


class SimulationResult(Base):
    __tablename__ = "simulation_results"
    id = Column(Integer, primary_key=True, autoincrement=True)
    simulation_run_id = Column(Integer, ForeignKey("simulation_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    metric = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=True)
    category = Column(String(50), nullable=False)

    run = relationship("SimulationRun", back_populates="results")


class SystemIncident(Base):
    __tablename__ = "system_incidents"
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), default="INFO", nullable=False)  # INFO | WARNING | HIGH | CRITICAL
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    source = Column(String(50), default="system", nullable=False)
    status = Column(String(20), default="OPEN", nullable=False)  # OPEN | ACKNOWLEDGED | RESOLVED
    fingerprint = Column(String(128), unique=True, nullable=True, index=True)
    started_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False)


class HealthThresholdConfiguration(Base):
    __tablename__ = "health_thresholds"
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(64), unique=True, nullable=False, index=True)
    value = Column(Float, nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), onupdate=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False)


class SystemHealthSnapshot(Base):
    __tablename__ = "system_health_snapshots"
    id = Column(Integer, primary_key=True, autoincrement=True)
    service = Column(String(50), nullable=False, index=True)
    status = Column(String(20), nullable=False)  # HEALTHY | DEGRADED | UNAVAILABLE | UNKNOWN | NOT_CONFIGURED
    latency_ms = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False, index=True)


class IncomingShipment(Base):
    __tablename__ = "incoming_shipments"
    id = Column(String(20), primary_key=True)  # e.g. ISHP-2026-001
    warehouse_id = Column(String(20), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False, index=True)
    supplier = Column(String(100), default="Apex Technologies Ltd")
    item_id = Column(String(20), ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True)
    expected_qty = Column(Integer, nullable=False)
    received_qty = Column(Integer, default=0, nullable=False)
    verified = Column(Boolean, default=False, nullable=False)
    qc_result = Column(String(30), default="PENDING", nullable=False)  # PENDING | QC_PASSED | QC_FAILED
    status = Column(String(30), default="INCOMING", nullable=False, index=True)  # INCOMING | RECEIVED | VERIFIED | QC_PASSED | QC_FAILED | PUTAWAY_PENDING | PUTAWAY_COMPLETED
    received_at = Column(DateTime, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    qc_at = Column(DateTime, nullable=True)
    putaway_at = Column(DateTime, nullable=True)
    responsible_user = Column(String(64), nullable=True)

    warehouse = relationship("Warehouse")
    item = relationship("Item")


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"
    id = Column(Integer, primary_key=True, autoincrement=True)
    movement_type = Column(String(30), nullable=False)  # RECEIVING | PUTAWAY | PICK | RESERVE | RESERVE_RELEASE | ADJUSTMENT
    item_id = Column(String(20), ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True)
    warehouse_id = Column(String(20), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False, index=True)
    source_location_id = Column(String(50), ForeignKey("warehouse_locations.id", ondelete="SET NULL"), nullable=True, index=True)
    destination_location_id = Column(String(50), ForeignKey("warehouse_locations.id", ondelete="SET NULL"), nullable=True, index=True)
    quantity = Column(Integer, nullable=False)
    quantity_before = Column(Integer, nullable=False)
    quantity_after = Column(Integer, nullable=False)
    reference_type = Column(String(50), nullable=True)  # e.g. order | task | shipment | receiving | adjustment
    reference_id = Column(String(100), nullable=True)
    order_id = Column(String(20), ForeignKey("orders.id", ondelete="SET NULL"), nullable=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True, index=True)
    robot_id = Column(String(30), ForeignKey("robots.robot_code", ondelete="SET NULL"), nullable=True, index=True)
    shipment_id = Column(String(20), nullable=True, index=True)
    actor = Column(String(64), nullable=True)
    reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False, index=True)

    item = relationship("Item")
    warehouse = relationship("Warehouse")
    source_location = relationship("WarehouseLocation", foreign_keys=[source_location_id])
    destination_location = relationship("WarehouseLocation", foreign_keys=[destination_location_id])
    order = relationship("Order")
    task = relationship("Task")
    robot = relationship("Robot", foreign_keys=[robot_id], primaryjoin="InventoryMovement.robot_id == Robot.robot_code")


class FinancialTransaction(Base):
    __tablename__ = "financial_transactions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String(30), unique=True, index=True, nullable=False)
    order_id = Column(String(20), ForeignKey("orders.id", ondelete="CASCADE"), nullable=True, index=True)
    transaction_type = Column(String(30), nullable=False)  # SALE | REFUND | REVENUE
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False, default="INR")
    status = Column(String(20), default="COMPLETED", nullable=False)
    reference_id = Column(String(100), nullable=True)
    description = Column(String(255), nullable=True)
    warehouse_id = Column(String(20), ForeignKey("warehouses.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False)

    order = relationship("Order")
    warehouse = relationship("Warehouse")


# ---------------------------------------------------------------------------
# Phase 8: Legitimate External Datasets & Data Pipeline Models
# ---------------------------------------------------------------------------

class DatasetSource(Base):
    __tablename__ = "dataset_sources"
    id = Column(String(50), primary_key=True)  # e.g., "m5", "online_retail_ii"
    name = Column(String(100), nullable=False)
    official_source = Column(String(150), nullable=False)
    source_url = Column(String(255), nullable=True)
    version = Column(String(30), nullable=True)
    license = Column(String(100), nullable=True)
    doi = Column(String(50), nullable=True)
    publisher = Column(String(150), nullable=True)
    description = Column(Text, nullable=True)
    intended_use = Column(Text, nullable=True)
    known_limitations = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False)


class DatasetImportRun(Base):
    __tablename__ = "dataset_import_runs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(String(50), ForeignKey("dataset_sources.id", ondelete="CASCADE"), nullable=False, index=True)
    import_timestamp = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False)
    record_count = Column(Integer, nullable=False, default=0)
    status = Column(String(20), default="PENDING", nullable=False)  # PENDING | SUCCESS | FAILED
    raw_checksum = Column(String(255), nullable=True)
    processing_version = Column(String(20), default="1.0", nullable=False)
    error_message = Column(Text, nullable=True)

    dataset = relationship("DatasetSource")


class DatasetValidationResult(Base):
    __tablename__ = "dataset_validation_results"
    id = Column(Integer, primary_key=True, autoincrement=True)
    import_run_id = Column(Integer, ForeignKey("dataset_import_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(20), default="PASS", nullable=False)  # PASS | WARNING | FAIL
    rows_count = Column(Integer, nullable=False, default=0)
    missing_values = Column(JSON, default={}, nullable=False)
    duplicate_count = Column(Integer, nullable=False, default=0)
    invalid_records_count = Column(Integer, nullable=False, default=0)
    date_range_start = Column(String(50), nullable=True)
    date_range_end = Column(String(50), nullable=True)
    validation_report = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False)

    import_run = relationship("DatasetImportRun")


# ============================================================
# Phase 9 — ML Analytics Models
# ============================================================

class ForecastRun(Base):
    """Records each dataset-level model training + evaluation run."""
    __tablename__ = "forecast_runs"
    run_id = Column(String(36), primary_key=True)  # UUID
    warehouse_id = Column(String(20), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=True, index=True)
    dataset_id = Column(String(50), nullable=False, index=True)
    model_name = Column(String(100), nullable=False)
    grain = Column(String(100), nullable=False)  # e.g. "family-level"
    train_start = Column(String(20), nullable=True)
    train_end = Column(String(20), nullable=True)
    val_start = Column(String(20), nullable=True)
    val_end = Column(String(20), nullable=True)
    horizon_days = Column(Integer, nullable=False, default=28)
    feature_set = Column(JSON, nullable=True)       # list of feature names used
    params = Column(JSON, nullable=True)             # model parameter dict (serializable)
    mae = Column(Float, nullable=True)
    rmse = Column(Float, nullable=True)
    wape_pct = Column(Float, nullable=True)
    smape_pct = Column(Float, nullable=True)
    naive_wape_pct = Column(Float, nullable=True)
    ma_wape_pct = Column(Float, nullable=True)
    wape_improvement_pct = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False)

    results = relationship("ForecastResult", back_populates="run", cascade="all, delete-orphan")


class ForecastResult(Base):
    """Per-entity per-date forecast outputs for a given ForecastRun."""
    __tablename__ = "forecast_results"
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(36), ForeignKey("forecast_runs.run_id", ondelete="CASCADE"), nullable=False, index=True)
    entity = Column(String(100), nullable=False, index=True)  # family name
    forecast_date = Column(String(20), nullable=False, index=True)
    predicted_demand = Column(Float, nullable=False)
    lower_bound = Column(Float, nullable=True)
    upper_bound = Column(Float, nullable=True)

    run = relationship("ForecastRun", back_populates="results")


class ABCClassification(Base):
    """Per-item ABC classification results with configurable thresholds."""
    __tablename__ = "abc_classifications"
    id = Column(Integer, primary_key=True, autoincrement=True)
    warehouse_id = Column(String(20), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=True, index=True)
    source = Column(String(50), nullable=False, index=True)  # wms | store_sales | online_retail | mlzc
    run_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False, index=True)
    item_id = Column(String(100), nullable=False)
    item_name = Column(String(255), nullable=True)
    total_qty = Column(Float, nullable=False, default=0.0)
    total_value = Column(Float, nullable=False, default=0.0)
    pct_contribution = Column(Float, nullable=False, default=0.0)
    cumulative_pct = Column(Float, nullable=False, default=0.0)
    abc_class = Column(String(1), nullable=False)  # A | B | C
    threshold_a = Column(Float, nullable=False, default=80.0)
    threshold_b = Column(Float, nullable=False, default=95.0)


class AnomalyResult(Base):
    """Dataset-level demand anomaly detection results."""
    __tablename__ = "anomaly_results"
    id = Column(Integer, primary_key=True, autoincrement=True)
    warehouse_id = Column(String(20), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=True, index=True)
    dataset_id = Column(String(50), nullable=False, index=True)
    entity = Column(String(100), nullable=False)   # family name or item_id
    date = Column(String(20), nullable=False, index=True)
    anomaly_score = Column(Integer, nullable=False)  # 0-100
    is_anomaly = Column(Boolean, nullable=False, default=True)
    severity = Column(String(10), nullable=False)   # LOW | MEDIUM | HIGH | CRITICAL
    reason = Column(String(255), nullable=True)
    features_json = Column(JSON, nullable=True)
    model_name = Column(String(50), nullable=False, default="IsolationForest")
    model_version = Column(String(20), nullable=False, default="1.0")
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False, index=True)


class ReplenishmentRecommendation(Base):
    """Data-driven replenishment recommendations. Does NOT modify inventory."""
    __tablename__ = "replenishment_recommendations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(String(100), nullable=False, index=True)
    item_name = Column(String(255), nullable=True)
    warehouse_id = Column(String(100), nullable=True, index=True)
    current_stock = Column(Float, nullable=True)
    forecast_demand = Column(Float, nullable=True)   # total forecast over horizon
    lead_time_days = Column(Integer, nullable=True)
    safety_stock = Column(Float, nullable=True)
    reorder_point = Column(Float, nullable=True)
    recommended_qty = Column(Float, nullable=True)
    abc_class = Column(String(1), nullable=True)
    urgency = Column(String(20), nullable=False, default="NO_ACTION")  # NO_ACTION | MONITOR | REORDER_RECOMMENDED | URGENT_REORDER | INSUFFICIENT_DATA
    status = Column(String(30), nullable=False, default="NO_ACTION")
    reason = Column(Text, nullable=True)
    data_quality = Column(String(50), nullable=False, default="COMPLETE")  # COMPLETE | PARTIAL | INSUFFICIENT_DATA
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False, index=True)





# ---------------------------------------------------------------------------
# Phase 18: Enterprise Security Event Model
# ---------------------------------------------------------------------------

class SecurityEvent(Base):
    """
    Rich security event log for Phase 18 — Enterprise Security Alerts.
    Complements the hash-chained AuditLedger (immutable) with a queryable,
    filterable security event store with device/browser/severity metadata.

    Severity levels: INFO | WARNING | CRITICAL
    Event types: LOGIN_SUCCESS | LOGIN_FAILED | LOGIN_OTP_SENT | LOGIN_OTP_SUCCESS |
                 LOGIN_OTP_FAILED | LOGOUT | PASSWORD_CHANGED | ROLE_CHANGED |
                 ACCOUNT_ACTIVATED | ACCOUNT_DEACTIVATED | ACCOUNT_CREATED |
                 OAUTH_LOGIN | RECOVERY_LOGIN | OTP_REQUESTED | OTP_VERIFIED |
                 OTP_FAILED | STEP_UP_VERIFIED | SUSPICIOUS_LOGIN | SESSION_REVOKED
    """
    __tablename__ = "security_events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String(60), nullable=False, index=True)
    severity = Column(String(20), default="INFO", nullable=False, index=True)  # INFO | WARNING | CRITICAL
    status = Column(String(20), default="SUCCESS", nullable=False)  # SUCCESS | FAILED | BLOCKED

    # Actor & target
    actor_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    target_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    actor_username = Column(String(64), nullable=True)   # denormalized for queries after user deletion
    target_username = Column(String(64), nullable=True)

    # Auth context
    authentication_method = Column(String(30), nullable=True)  # password | password_otp | google_oauth | recovery
    role_at_event = Column(String(20), nullable=True)
    previous_value = Column(String(200), nullable=True)   # old role, old email, etc.
    new_value = Column(String(200), nullable=True)        # new role, new email, etc.

    # Request metadata
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    device = Column(String(60), nullable=True)            # Desktop | Mobile | Tablet | Unknown
    browser = Column(String(80), nullable=True)           # Chrome 126 | Firefox 127 | etc.
    os = Column(String(80), nullable=True)                # Windows 11 | macOS 14 | etc.

    # Traceability
    correlation_id = Column(String(64), nullable=True, index=True)  # ties events in a flow
    audit_ledger_ref = Column(Integer, nullable=True)    # AuditLedger.id FK (soft ref, no FK constraint)
    details = Column(Text, default="{}", nullable=True)  # JSON blob for extra context

    timestamp = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False, index=True)


class QualityControlRecord(Base):
    __tablename__ = "quality_control_records"
    id = Column(Integer, primary_key=True, autoincrement=True)
    shipment_id = Column(String(20), ForeignKey("incoming_shipments.id", ondelete="CASCADE"), nullable=False, index=True)
    item_id = Column(String(20), ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True)
    quantity_passed = Column(Integer, nullable=False, default=0)
    quantity_failed = Column(Integer, nullable=False, default=0)
    inspector = Column(String(64), nullable=False)
    reason = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False)

    shipment = relationship("IncomingShipment")
    item = relationship("Item")


class TransferRequest(Base):
    __tablename__ = "transfer_requests"
    id = Column(String(20), primary_key=True)  # e.g. TR-2026-001
    source_warehouse_id = Column(String(20), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False, index=True)
    destination_warehouse_id = Column(String(20), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(30), default="REQUESTED", nullable=False, index=True)  # REQUESTED | APPROVED | IN_TRANSIT | RECEIVED | CANCELLED
    requester = Column(String(64), nullable=False)
    approver = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), onupdate=lambda: datetime.now(UTC).replace(tzinfo=None))

    source_warehouse = relationship("Warehouse", foreign_keys=[source_warehouse_id])
    destination_warehouse = relationship("Warehouse", foreign_keys=[destination_warehouse_id])
    items = relationship("TransferItem", back_populates="transfer", cascade="all, delete-orphan")


class TransferItem(Base):
    __tablename__ = "transfer_items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    transfer_id = Column(String(20), ForeignKey("transfer_requests.id", ondelete="CASCADE"), nullable=False, index=True)
    item_id = Column(String(20), ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    source_location_id = Column(String(50), ForeignKey("warehouse_locations.id", ondelete="SET NULL"), nullable=True)
    destination_location_id = Column(String(50), ForeignKey("warehouse_locations.id", ondelete="SET NULL"), nullable=True)
    quantity_received = Column(Integer, default=0, nullable=False)

    transfer = relationship("TransferRequest", back_populates="items")
    item = relationship("Item")
    source_location = relationship("WarehouseLocation", foreign_keys=[source_location_id])
    destination_location = relationship("WarehouseLocation", foreign_keys=[destination_location_id])


class DamageRecord(Base):
    __tablename__ = "damage_records"
    id = Column(Integer, primary_key=True, autoincrement=True)
    warehouse_id = Column(String(20), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False, index=True)
    item_id = Column(String(20), ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True)
    location_id = Column(String(50), ForeignKey("warehouse_locations.id", ondelete="SET NULL"), nullable=True, index=True)
    quantity = Column(Integer, nullable=False)
    reported_by = Column(String(64), nullable=False)
    reason = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False, index=True)

    warehouse = relationship("Warehouse")
    item = relationship("Item")
    location = relationship("WarehouseLocation")


class ReturnRequest(Base):
    __tablename__ = "return_requests"
    id = Column(String(20), primary_key=True)  # e.g. RET-2026-001
    order_id = Column(String(20), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    warehouse_id = Column(String(20), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(30), default="REQUESTED", nullable=False, index=True)  # REQUESTED | APPROVED | RECEIVED | INSPECTED | RESTOCKED | QUARANTINED | DAMAGED | REJECTED | CLOSED
    received_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False)

    order = relationship("Order")
    warehouse = relationship("Warehouse")
    items = relationship("ReturnItem", back_populates="return_request", cascade="all, delete-orphan")


class ReturnItem(Base):
    __tablename__ = "return_items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    return_id = Column(String(20), ForeignKey("return_requests.id", ondelete="CASCADE"), nullable=False, index=True)
    item_id = Column(String(20), ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    action = Column(String(30), default="QUARANTINE", nullable=False)  # RESTOCK | QUARANTINE | DAMAGE | REJECT
    reason = Column(String(255), nullable=True)

    return_request = relationship("ReturnRequest", back_populates="items")
    item = relationship("Item")


class AppSetting(Base):
    __tablename__ = "app_settings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), onupdate=lambda: datetime.now(UTC).replace(tzinfo=None))




