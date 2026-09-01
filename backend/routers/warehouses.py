import logging
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.database import get_db, engine
from backend.models import Warehouse, Item, StockMovement, Inventory, OrderItem, Task, Order
from backend.schemas import WarehouseCreate, ItemCreate, StockMovementCreate, WarehouseUpdate, ItemUpdate
from backend.auth import get_current_user, require_admin, log_access
from backend import notifications
from backend import audit_ledger as ledger
from backend.geocoding_service import geocode_address, reverse_geocode

logger = logging.getLogger("warehouse")

router = APIRouter()


class CoordinatesUpdate(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)


@router.get("/warehouses")
def list_warehouses(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return [{"id": w.id, "name": w.name, "location": w.location,
             "city": w.city, "state": w.state, "country": w.country,
             "latitude": w.latitude, "longitude": w.longitude} for w in db.query(Warehouse).all()]


@router.post("/warehouses")
def create_warehouse(payload: WarehouseCreate, request: Request, db: Session = Depends(get_db), user=Depends(require_admin)):
    wh_id = (payload.id or "").strip()
    wh_name = (payload.name or "").strip()

    if not wh_id:
        raise HTTPException(400, "Warehouse ID is required")
    if len(wh_id) > 20:
        raise HTTPException(400, "Warehouse ID cannot exceed 20 characters")
    if not wh_name:
        raise HTTPException(400, "Warehouse Name is required")
    if len(wh_name) > 120:
        raise HTTPException(400, "Warehouse Name cannot exceed 120 characters")

    if payload.latitude is not None and (payload.latitude < -90.0 or payload.latitude > 90.0):
        raise HTTPException(400, "Latitude must be between -90.0 and 90.0")
    if payload.longitude is not None and (payload.longitude < -180.0 or payload.longitude > 180.0):
        raise HTTPException(400, "Longitude must be between -180.0 and 180.0")

    if db.query(Warehouse).filter(Warehouse.id == wh_id).first():
        raise HTTPException(409, f"Warehouse ID '{wh_id}' already exists")
    
    lat = payload.latitude
    lon = payload.longitude
    resolved_addr = None
    warning_msg = None
    
    # Geocoding fallback sequence if coordinates are not manually entered
    if lat is None or lon is None:
        try:
            lat, lon, resolved_addr = geocode_address(
                wh_name, payload.city, payload.state, payload.country, payload.location
            )
        except Exception as ge_err:
            logger.warning("Geocoding failed for warehouse %s: %s", wh_id, ge_err)
            lat, lon, resolved_addr = None, None, None

        if lat is None or lon is None:
            warning_msg = "Location could not be automatically resolved. Please enter coordinates or select the location on the map."
            
    w = Warehouse(
        id=wh_id, name=wh_name, location=resolved_addr or payload.location or "",
        city=payload.city or "", state=payload.state or "", country=payload.country or "",
        latitude=lat, longitude=lon
    )
    
    try:
        db.add(w)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error("Failed to insert warehouse into database: %s", e)
        raise HTTPException(500, f"Database error creating warehouse: {str(e)}")

    try:
        log_access(db, user.username, "add_warehouse", warehouse_id=w.id, request=request)
    except Exception as log_err:
        logger.warning("Failed to log access for warehouse creation: %s", log_err)

    logger.info("Warehouse created: id=%s name=%s by=%s", w.id, w.name, user.username)
    
    try:
        notifications.send_change_alert("New Warehouse Added", {
            "warehouse_id": w.id,
            "name": w.name,
            "location": f"{w.city}, {w.country}" if w.city else w.location,
            "coordinates": f"{w.latitude}, {w.longitude}" if w.latitude else "Pending",
            "created_by": user.username
        })
    except Exception as notif_err:
        logger.warning("Failed to send warehouse creation notification alert: %s", notif_err)
    
    res = {"status": "created", "id": w.id, "latitude": lat, "longitude": lon, "warning": warning_msg}
    return res


@router.get("/warehouses/{id}")
def get_warehouse(id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    w = db.query(Warehouse).filter(Warehouse.id == id).first()
    if not w:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return {
        "id": w.id,
        "name": w.name,
        "location": w.location,
        "city": w.city,
        "state": w.state,
        "country": w.country,
        "latitude": w.latitude,
        "longitude": w.longitude
    }


@router.put("/warehouses/{id}")
def update_warehouse(id: str, payload: WarehouseUpdate, request: Request, db: Session = Depends(get_db), user=Depends(require_admin)):
    w = db.query(Warehouse).filter(Warehouse.id == id).first()
    if not w:
        raise HTTPException(404, f"Warehouse '{id}' not found")

    wh_name = (payload.name or "").strip()
    if not wh_name:
        raise HTTPException(400, "Warehouse Name cannot be empty")
    if len(wh_name) > 120:
        raise HTTPException(400, "Warehouse Name cannot exceed 120 characters")

    if payload.latitude is not None and (payload.latitude < -90.0 or payload.latitude > 90.0):
        raise HTTPException(400, "Latitude must be between -90.0 and 90.0")
    if payload.longitude is not None and (payload.longitude < -180.0 or payload.longitude > 180.0):
        raise HTTPException(400, "Longitude must be between -180.0 and 180.0")

    w.name = wh_name
    w.location = payload.location or ""
    w.city = payload.city or ""
    w.state = payload.state or ""
    w.country = payload.country or ""

    lat = payload.latitude
    lon = payload.longitude
    resolved_addr = None
    if lat is None or lon is None:
        try:
            lat, lon, resolved_addr = geocode_address(
                wh_name, payload.city or "", payload.state or "", payload.country or "", payload.location
            )
        except Exception as ge_err:
            logger.warning("Geocoding failed during warehouse update for %s: %s", id, ge_err)
            lat, lon, resolved_addr = None, None, None

    w.latitude = lat if lat is not None else w.latitude
    w.longitude = lon if lon is not None else w.longitude
    if resolved_addr:
        w.location = resolved_addr

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error("Failed to update warehouse %s in database: %s", id, e)
        raise HTTPException(500, f"Database error updating warehouse: {str(e)}")

    try:
        log_access(db, user.username, "update_warehouse", warehouse_id=w.id, request=request)
    except Exception as log_err:
        logger.warning("Failed to log access for warehouse update: %s", log_err)

    return {"status": "updated", "id": w.id}


@router.delete("/warehouses/{id}")
def delete_warehouse(id: str, request: Request, db: Session = Depends(get_db), user=Depends(require_admin)):
    w = db.query(Warehouse).filter(Warehouse.id == id).first()
    if not w:
        raise HTTPException(404, f"Warehouse '{id}' not found")
    try:
        db.delete(w)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error("Failed to delete warehouse %s: %s", id, e)
        raise HTTPException(500, f"Database error deleting warehouse: {str(e)}")

    try:
        log_access(db, user.username, "delete_warehouse", warehouse_id=id, request=request)
    except Exception:
        pass
    return {"status": "deleted", "id": id}


@router.patch("/warehouses/{id}/location")
@router.put("/warehouses/{id}/location")
def update_warehouse_location_coords(id: str, payload: CoordinatesUpdate, request: Request, db: Session = Depends(get_db), user=Depends(require_admin)):
    w = db.query(Warehouse).filter(Warehouse.id == id).first()
    if not w:
        raise HTTPException(status_code=404, detail=f"Warehouse '{id}' not found")

    if payload.latitude < -90.0 or payload.latitude > 90.0:
        raise HTTPException(400, "Latitude must be between -90.0 and 90.0")
    if payload.longitude < -180.0 or payload.longitude > 180.0:
        raise HTTPException(400, "Longitude must be between -180.0 and 180.0")

    w.latitude = payload.latitude
    w.longitude = payload.longitude
    
    # Optional reverse geocoding to update address safely
    try:
        resolved_addr = reverse_geocode(payload.latitude, payload.longitude)
        if resolved_addr:
            w.location = resolved_addr
    except Exception as e:
        logger.warning("Reverse geocoding failed during coordinate patch: %s", e)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error("Failed to patch warehouse location coords for %s: %s", id, e)
        raise HTTPException(500, f"Database error updating coordinates: {str(e)}")
    log_access(db, user.username, "update_warehouse_location", warehouse_id=id, request=request)
    logger.info("Warehouse coordinates updated via map: id=%s lat=%s lng=%s by=%s", id, payload.latitude, payload.longitude, user.username)
    
    # Audit logging
    ledger.append_entry(db, "warehouse_location_updated", {
        "actor": user.username,
        "warehouse_id": id,
        "old_latitude": old_lat,
        "old_longitude": old_lng,
        "new_latitude": payload.latitude,
        "new_longitude": payload.longitude
    })
    
    return {"status": "updated", "id": id, "latitude": w.latitude, "longitude": w.longitude, "location": w.location}


@router.put("/warehouses/{id}/coordinates")
def update_warehouse_coordinates(id: str, payload: CoordinatesUpdate, request: Request, db: Session = Depends(get_db), user=Depends(require_admin)):
    w = db.query(Warehouse).filter(Warehouse.id == id).first()
    if not w:
        raise HTTPException(404, "Warehouse not found")
    
    old_lat = w.latitude
    old_lon = w.longitude
    w.latitude = payload.latitude
    w.longitude = payload.longitude
    
    # Trigger reverse geocoding to enrich location metadata
    reverse_res = reverse_geocode(payload.latitude, payload.longitude)
    if reverse_res:
        if isinstance(reverse_res, dict):
            if reverse_res.get("city"):
                w.city = reverse_res["city"]
            if reverse_res.get("state"):
                w.state = reverse_res["state"]
            if reverse_res.get("country"):
                w.country = reverse_res["country"]
        elif isinstance(reverse_res, str):
            w.location = reverse_res
            
    db.commit()
    log_access(db, user.username, "update_coordinates", warehouse_id=w.id, request=request)
    
    ledger.append_entry(db, "warehouse_location_changed", {
        "actor": user.username,
        "warehouse_id": w.id,
        "old_latitude": old_lat,
        "old_longitude": old_lon,
        "new_latitude": w.latitude,
        "new_longitude": w.longitude
    })

    notifications.send_change_alert("Warehouse Coordinates Updated", {
        "warehouse_id": w.id,
        "name": w.name,
        "old_coords": f"{old_lat}, {old_lon}",
        "new_coords": f"{w.latitude}, {w.longitude}",
        "updated_by": user.username
    })
    
    return {
        "status": "updated",
        "id": w.id,
        "latitude": w.latitude,
        "longitude": w.longitude,
        "city": w.city,
        "state": w.state,
        "country": w.country
    }


@router.get("/warehouses/{id}/weather")
def get_warehouse_weather_endpoint(id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    from backend.weather_service import get_warehouse_weather
    w = db.query(Warehouse).filter(Warehouse.id == id).first()
    if not w:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    if w.latitude is None or w.longitude is None:
        raise HTTPException(status_code=400, detail="Location coordinates not configured for this warehouse")
    try:
        return get_warehouse_weather(w.id, w.latitude, w.longitude)
    except Exception as e:
        logger.error("Failed to fetch weather for warehouse %s: %s", id, e, exc_info=True)
        raise HTTPException(status_code=503, detail="Weather service temporarily unavailable")


@router.get("/items")
def list_items(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return [{"id": i.id, "name": i.name, "category": i.category, "unit_cost": i.unit_cost,
             "lead_time_days": i.lead_time_days, "safety_stock": i.safety_stock,
             "reorder_threshold": i.reorder_threshold, "sku": i.sku, "unit": i.unit, "is_active": i.is_active}
            for i in db.query(Item).filter(Item.is_active == True).all()]


@router.get("/items/{item_id}")
def get_item(item_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    i = db.query(Item).filter(Item.id == item_id).first()
    if not i:
        raise HTTPException(404, f"Item '{item_id}' not found")
    inv_records = db.query(Inventory).filter(Inventory.item_id == item_id).all()
    return {
        "id": i.id, "name": i.name, "category": i.category, "unit_cost": i.unit_cost,
        "lead_time_days": i.lead_time_days, "safety_stock": i.safety_stock,
        "reorder_threshold": i.reorder_threshold, "sku": i.sku, "unit": i.unit,
        "is_active": i.is_active,
        "inventory": [{"warehouse_id": inv.warehouse_id, "on_hand": inv.on_hand, "reserved": inv.reserved, "available": inv.available} for inv in inv_records]
    }


@router.post("/items")
def create_item(payload: ItemCreate, request: Request, db: Session = Depends(get_db), user=Depends(require_admin)):
    if db.query(Item).filter(Item.id == payload.id).first():
        raise HTTPException(400, "Item ID already exists")
    if payload.sku and db.query(Item).filter(Item.sku == payload.sku).first():
        raise HTTPException(400, "Item SKU already exists")

    sku_val = payload.sku if payload.sku else f"SKU-{payload.id}"
    i = Item(
        id=payload.id,
        name=payload.name,
        category=payload.category or "General",
        unit_cost=payload.unit_cost or 0.0,
        lead_time_days=payload.lead_time_days or 3,
        safety_stock=payload.safety_stock or 10,
        reorder_threshold=payload.reorder_threshold or 20,
        sku=sku_val,
        unit=payload.unit or "units",
        is_active=True
    )
    db.add(i)
    db.flush()

    target_wh = payload.warehouse_id
    if not target_wh:
        wh_row = db.query(Warehouse).first()
        target_wh = wh_row.id if wh_row else "WH-BLR-01"

    init_qty = payload.initial_stock or 0
    inv = db.query(Inventory).filter(
        Inventory.warehouse_id == target_wh,
        Inventory.item_id == i.id
    ).first()
    if not inv:
        inv = Inventory(
            warehouse_id=target_wh,
            item_id=i.id,
            on_hand=init_qty,
            reserved=0,
            available=init_qty
        )
        db.add(inv)

    if init_qty > 0:
        from datetime import date
        today = date.today()
        db.add(StockMovement(
            date=today,
            warehouse_id=target_wh,
            item_id=i.id,
            stock_in=init_qty,
            stock_out=0,
            closing_stock=init_qty,
            entry_source="initial_creation",
            entered_by=user.username
        ))

    db.commit()
    log_access(db, user.username, "add_item", warehouse_id=target_wh, request=request)
    ledger.append_entry(db, "INVENTORY_ITEM_CREATED", {
        "item_id": i.id, "name": i.name, "warehouse_id": target_wh,
        "initial_stock": init_qty, "created_by": user.username
    })

    notifications.send_change_alert("New Item/SKU Added", {
        "item_id": i.id,
        "name": i.name,
        "category": i.category,
        "unit_cost": f"INR {i.unit_cost}",
        "safety_stock": i.safety_stock,
        "created_by": user.username
    })

    return {"status": "created", "id": i.id, "warehouse_id": target_wh, "initial_stock": init_qty}


@router.patch("/items/{item_id}")
def update_item(item_id: str, payload: ItemUpdate, request: Request, db: Session = Depends(get_db), user=Depends(require_admin)):
    i = db.query(Item).filter(Item.id == item_id).first()
    if not i:
        raise HTTPException(404, f"Item '{item_id}' not found")

    upd_dict = payload.model_dump(exclude_unset=True)
    curr_stock = upd_dict.pop("current_stock", None)
    target_wh = upd_dict.pop("warehouse_id", None)

    for k, v in upd_dict.items():
        if hasattr(i, k) and v is not None:
            setattr(i, k, v)

    if curr_stock is not None:
        wh_id = target_wh or "WH-BLR-01"
        inv = db.query(Inventory).filter(Inventory.warehouse_id == wh_id, Inventory.item_id == item_id).first()
        if not inv:
            inv = Inventory(warehouse_id=wh_id, item_id=item_id, on_hand=curr_stock, reserved=0, available=curr_stock)
            db.add(inv)
        else:
            inv.on_hand = curr_stock
            inv.available = max(0, curr_stock - inv.reserved)

        from datetime import date
        today = date.today()
        sm = db.query(StockMovement).filter(StockMovement.warehouse_id == wh_id, StockMovement.item_id == item_id, StockMovement.date == today).first()
        if sm:
            sm.closing_stock = curr_stock
        else:
            db.add(StockMovement(
                date=today, warehouse_id=wh_id, item_id=item_id,
                stock_in=0, stock_out=0, closing_stock=curr_stock,
                entry_source="manual_update", entered_by=user.username
            ))

    db.commit()
    log_access(db, user.username, "update_item", warehouse_id=target_wh or "", request=request)
    ledger.append_entry(db, "INVENTORY_ITEM_UPDATED", {
        "item_id": i.id, "updated_by": user.username, "changes": [k for k in upd_dict.keys()]
    })
    return {"status": "updated", "id": i.id}


@router.delete("/items/{item_id}")
def delete_item(item_id: str, request: Request, db: Session = Depends(get_db), user=Depends(require_admin)):
    i = db.query(Item).filter(Item.id == item_id).first()
    if not i:
        raise HTTPException(404, f"Item '{item_id}' not found")

    has_orders = db.query(OrderItem).filter(OrderItem.item_id == item_id).first() is not None
    has_tasks = db.query(Task).filter(Task.product_id == item_id).first() is not None
    has_movements = db.query(StockMovement).filter(StockMovement.item_id == item_id).first() is not None

    if has_orders or has_tasks or has_movements:
        i.is_active = False
        db.commit()
        ledger.append_entry(db, "INVENTORY_ITEM_ARCHIVED", {"item_id": i.id, "archived_by": user.username, "reason": "Operational history exists"})
        return {"status": "archived", "id": i.id, "message": f"Item '{item_id}' has historical operations and was safely soft-archived."}
    else:
        db.query(Inventory).filter(Inventory.item_id == item_id).delete(synchronize_session=False)
        db.delete(i)
        db.commit()
        ledger.append_entry(db, "INVENTORY_ITEM_DELETED", {"item_id": item_id, "deleted_by": user.username})
        return {"status": "deleted", "id": item_id, "message": f"Item '{item_id}' deleted successfully."}


@router.post("/stock-movements")
def record_stock_movement(payload: StockMovementCreate, request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role == "viewer":
        raise HTTPException(status_code=403, detail="Access denied. Role 'viewer' is read-only.")
    if not db.query(Warehouse).filter(Warehouse.id == payload.warehouse_id).first():
        raise HTTPException(404, "Warehouse not found")
    if not db.query(Item).filter(Item.id == payload.item_id).first():
        raise HTTPException(404, "Item not found")

    inv = db.query(Inventory).filter(Inventory.warehouse_id == payload.warehouse_id, Inventory.item_id == payload.item_id).first()
    prev_closing = inv.on_hand if inv else 0
    closing = max(0, prev_closing - payload.stock_out + payload.stock_in)

    existing = (db.query(StockMovement)
                .filter(StockMovement.warehouse_id == payload.warehouse_id, StockMovement.item_id == payload.item_id,
                        StockMovement.date == payload.date).first())
    if existing:
        existing.stock_in = payload.stock_in
        existing.stock_out = payload.stock_out
        existing.closing_stock = closing
        existing.entered_by = user.username
    else:
        db.add(StockMovement(
            date=payload.date, warehouse_id=payload.warehouse_id, item_id=payload.item_id,
            stock_in=payload.stock_in, stock_out=payload.stock_out, closing_stock=closing,
            entry_source="manual", entered_by=user.username,
        ))

    # Keep inventory table in sync
    inv = db.query(Inventory).filter(Inventory.warehouse_id == payload.warehouse_id, Inventory.item_id == payload.item_id).first()
    if not inv:
        inv = Inventory(
            warehouse_id=payload.warehouse_id, item_id=payload.item_id,
            on_hand=closing, reserved=0, available=closing
        )
        db.add(inv)
    else:
        inv.on_hand = closing
        inv.available = max(0, closing - inv.reserved)

    db.commit()
    log_access(db, user.username, "add_stock", warehouse_id=payload.warehouse_id, request=request)
    ledger.append_entry(db, "stock_entry", {
        "warehouse_id": payload.warehouse_id, "item_id": payload.item_id,
        "date": str(payload.date), "stock_in": payload.stock_in, "stock_out": payload.stock_out,
        "entered_by": user.username,
    })
    
    notifications.send_change_alert("Stock Movement Recorded", {
        "date": str(payload.date),
        "warehouse_id": payload.warehouse_id,
        "item_id": payload.item_id,
        "stock_in": payload.stock_in,
        "stock_out": payload.stock_out,
        "new_closing_stock": closing,
        "recorded_by": user.username
    })
    
    return {"status": "recorded", "closing_stock": closing}


@router.get("/stock-movements/{warehouse_id}")
def list_stock_movements(warehouse_id: str, limit: int = 100, db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = (db.query(StockMovement).filter(StockMovement.warehouse_id == warehouse_id)
            .order_by(StockMovement.date.desc()).limit(limit).all())
    return [{"date": str(r.date), "item_id": r.item_id, "stock_in": r.stock_in,
             "stock_out": r.stock_out, "closing_stock": r.closing_stock, "entered_by": r.entered_by} for r in rows]


@router.get("/inventory/{warehouse_id}")
def get_inventory(warehouse_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    df = pd.read_sql(text("""
        SELECT 
            i.id AS item_id,
            i.name AS item_name,
            i.category,
            COALESCE(inv.on_hand, sm.closing_stock, 0) AS current_stock,
            COALESCE(i.safety_stock, 10) AS safety_stock,
            COALESCE(i.unit_cost, 0.0) AS unit_cost,
            COALESCE(i.reorder_threshold, 20) AS reorder_threshold,
            COALESCE(inv.available, inv.on_hand, sm.closing_stock, 0) AS available_stock,
            COALESCE(inv.reserved, 0) AS reserved_stock
        FROM items i
        LEFT JOIN inventory inv ON i.id = inv.item_id AND inv.warehouse_id = :wh
        LEFT JOIN (
            SELECT sm_inner.warehouse_id, sm_inner.item_id, sm_inner.closing_stock
            FROM stock_movements sm_inner
            JOIN (
                SELECT warehouse_id, item_id, MAX(date) md 
                FROM stock_movements 
                WHERE warehouse_id = :wh 
                GROUP BY warehouse_id, item_id
            ) latest ON sm_inner.warehouse_id = latest.warehouse_id 
                   AND sm_inner.item_id = latest.item_id 
                   AND sm_inner.date = latest.md
        ) sm ON i.id = sm.item_id
        WHERE i.is_active = TRUE OR i.is_active IS NULL
    """), engine, params={"wh": warehouse_id})
    return df.to_dict(orient="records")


@router.get("/trend/{warehouse_id}")
def get_trend(warehouse_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    df = pd.read_sql(text("""
        SELECT date, SUM(stock_out) AS total_stock_out, SUM(stock_in) AS total_stock_in
        FROM stock_movements WHERE warehouse_id = :wh GROUP BY date ORDER BY date
    """), engine, params={"wh": warehouse_id})
    df["date"] = df["date"].astype(str)
    return df.to_dict(orient="records")
