"""
backend/settings.py — Settings retrieval, persistence and fallback defaults.
"""
from typing import Any
from sqlalchemy.orm import Session
from backend.models import AppSetting
from datetime import datetime, UTC

DEFAULT_SETTINGS = {
  # 1. GENERAL
  "system_name": "Warehouse OS",
  "system_desc": "Intelligent Warehouse Management System",
  "default_warehouse": "WH-BLR-01",
  "timezone": "Asia/Kolkata (UTC+05:30)",
  "date_format": "DD/MM/YYYY",
  "time_format": "24 Hour",
  "language": "English",
  "week_starts": "Monday",
  "system_logo": "default",

  # 2. WAREHOUSE
  "warehouse_name": "Main Warehouse",
  "warehouse_code": "WH-BLR-01",
  "warehouse_loc": "Bangalore, India",
  "warehouse_address": "Electronic City, Phase 1, Bangalore, Karnataka, 560100",
  "warehouse_hours": "08:00 – 20:00",
  "warehouse_days": "Mon-Sat",
  "warehouse_area": 15000,
  "warehouse_capacity": 100000,

  # 3. ZONES
  "zones": [
    { "name": "Receiving", "type": "RECEIVING", "desc": "Inbound dock and staging area", "enabled": True },
    { "name": "Storage", "type": "STORAGE", "desc": "Main high-density storage racks", "enabled": True },
    { "name": "Picking", "type": "PICKING", "desc": "Zone optimized for picker pathing", "enabled": True },
    { "name": "Packing", "type": "PACKING", "desc": "Packing tables and sorting lanes", "enabled": True },
    { "name": "Shipping", "type": "SHIPPING", "desc": "Outbound staging and shipping dock", "enabled": True },
    { "name": "Charging", "type": "CHARGING", "desc": "Robot battery charging stations", "enabled": True },
    { "name": "Returns", "type": "RETURNS", "desc": "Returns processing and QA inspection", "enabled": True }
  ],

  # 4. INVENTORY
  "low_stock_thresh": 10,
  "reorder_point": 20,
  "safety_stock": 5,
  "obsolete_stock_thresh": 180,
  "inventory_update_method": "REAL_TIME",
  "enable_batch_tracking": True,
  "enable_expiry_tracking": False,
  "default_unit": "PCS",

  # 5. ORDERS
  "default_order_priority": 50,
  "allow_partial_shipment": False,
  "auto_assign_orders": True,
  "max_order_proc_time": 120,
  "order_num_prefix": "ORD-",
  "priority_levels": "Low,Medium,High,Critical",

  # 6. TASKS
  "default_task_priority": 50,
  "task_timeout": 30,
  "auto_reassign_failed": True,
  "max_retry_count": 3,
  "task_expiry_time": 1440,
  "show_task_confirmation": True,
  "allow_manual_task_creation": True,

  # 7. ROBOTS
  "default_robot_count": 5,
  "max_robot_count": 10,
  "robot_speed": 1.2,
  "battery_capacity": 100,
  "low_battery_thresh": 20,
  "charging_speed": 5.0,
  "collision_distance": 1.0,
  "default_robot_unit": "AGV",

  # 8. PATHFINDING
  "pathfinding_alg": "A_STAR",
  "allow_diagonal": False,
  "dynamic_replanning": True,
  "obstacle_avoidance": True,
  "route_optimization": True,
  "grid_resolution": 1.0,
  "replan_on_blocked": True,

  # 9. SIMULATION
  "sim_speed": "1x",
  "sim_mode": "Normal Operations",
  "auto_start_sim": False,
  "show_robot_trails": True,
  "show_routes": True,
  "show_obstacles": True,
  "show_heatmap": False,
  "sim_tick_interval": 2.0,

  # 10. SCENARIOS
  "default_order_surge": 1.2,
  "default_robot_failure_rate": 0.05,
  "default_obstacle_frequency": 0.1,
  "default_congestion_level": 1.0,
  "sim_duration": 60,
  "random_seed": 42,
  "auto_generate_scenarios": False,

  # 11. NOTIFICATIONS
  "notif_task": True,
  "notif_robot": True,
  "notif_low_battery": True,
  "notif_system": True,
  "notif_order": True,
  "notif_inventory": True,
  "notif_maintenance": True,

  # 12. EMAIL
  "sender_email": "joyboy56211@gmail.com",
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_username": "joyboy56211@gmail.com",
  "smtp_password": "xgmmumehdjguzhsz",
  "enable_email_notifs": True,

  # 13. CURRENCY
  "primary_currency": "INR",
  "secondary_currency": "USD",
  "show_currency_symbol": True,
  "exchange_rate_source": "RBI API",
  "refresh_rate": "Daily",

  # 14. DATE & TIME
  "datetime_timezone": "Asia/Kolkata (UTC+05:30)",
  "datetime_date_format": "DD/MM/YYYY",
  "datetime_time_format": "24 Hour",
  "first_day_of_week": "Monday",
  "show_seconds": False,
  "sync_server_time": False,

  # 15. USER PREFERENCES
  "pref_landing_page": "Dashboard",
  "pref_items_per_page": 25,
  "pref_compact_mode": False,
  "pref_show_tutorials": True,
  "pref_default_view": "Grid",
  "pref_language": "English",
  "pref_auto_save": False,

  # 16. SECURITY
  "session_timeout": 30,
  "password_requirements": "Min 8 chars, 1 digit, 1 special char",
  "require_strong_pass": True,
  "enable_2fa": False,
  "login_attempt_limit": 5,
  "lockout_duration": 15,

  # 17. AUDIT
  "enable_audit_logging": True,
  "log_user_actions": True,
  "log_data_changes": True,
  "log_login_events": True,
  "audit_retention_period": 90,
  "audit_export_format": "JSON",

  # 18. SYSTEM HEALTH
  "enable_health_monitoring": True,
  "health_check_interval": 10,
  "alert_service_down": True,
  "alert_high_response_time": True,
  "response_time_thresh": 500,
  "enable_beta_features": False,

  # 19. DATA MANAGEMENT
  "backup_schedule": "daily",
  "backup_retention_days": 30,
  "auto_backup_enabled": True,

  # 20. APPEARANCE
  "theme": "dark",
  "compact_mode": False,
  "reduce_animations": False,
  "primary_accent": "#818cf8",
  "app_logo": "default",
  "app_name": "Warehouse OS",

  # 21. ADVANCED / DEVELOPER
  "debug_mode": False,
  "api_request_logging": True,
  "dev_tools_enabled": False,
  "show_perf_metrics": True,
  "cache_duration": 300,
  "max_log_size": 10,

  # 22. ABOUT (read-only metadata)
  "version": "1.0.0",
  "environment": "Production",
  "license": "Enterprise Student Capstone"
}

# Keys that are computed/read-only and must never be overwritten by the user
READ_ONLY_KEYS = {"version", "environment", "license"}


def get_settings(db: Session) -> dict:
    """Retrieve full app settings merged with defaults.
    Always returns every key in DEFAULT_SETTINGS; DB overrides defaults.
    """
    if not db:
        return dict(DEFAULT_SETTINGS)
    try:
        row = db.query(AppSetting).filter(AppSetting.key == "wms_platform_settings").first()
        if row and isinstance(row.value, dict):
            return {**DEFAULT_SETTINGS, **row.value}
    except Exception as e:
        pass
    return dict(DEFAULT_SETTINGS)


def get_setting_value(db: Session, key: str, default: Any = None) -> Any:
    """Helper to retrieve a specific setting value by key with DB override and fallback."""
    settings = get_settings(db)
    if key in settings and settings[key] is not None:
        return settings[key]
    if default is not None:
        return default
    return DEFAULT_SETTINGS.get(key)


def save_settings(db: Session, settings_dict: dict) -> dict:
    """Persist app settings. Strips read-only keys before storing."""
    clean = {k: v for k, v in settings_dict.items() if k not in READ_ONLY_KEYS}
    row = db.query(AppSetting).filter(AppSetting.key == "wms_platform_settings").first()
    if not row:
        row = AppSetting(key="wms_platform_settings", value=clean)
        db.add(row)
    else:
        row.value = clean
        row.updated_at = datetime.now(UTC).replace(tzinfo=None)
    db.commit()
    return get_settings(db)


def reset_to_defaults(db: Session) -> dict:
    """Delete the persisted settings row so defaults take effect immediately."""
    row = db.query(AppSetting).filter(AppSetting.key == "wms_platform_settings").first()
    if row:
        db.delete(row)
        db.commit()
    return dict(DEFAULT_SETTINGS)

