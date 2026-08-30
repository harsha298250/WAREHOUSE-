import logging
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.database import get_db, engine
from backend.models import Warehouse, Item, StockMovement
from backend.schemas import WarehouseCreate, ItemCreate, StockMovementCreate, WarehouseUpdate
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
    if db.query(Warehouse).filter(Warehouse.id == payload.id).first():
        raise HTTPException(400, "Warehouse ID already exists")
    
    lat = payload.latitude
    lon = payload.longitude
    resolved_addr = None
    warning_msg = None
    
    # Geocoding fallback sequence if coordinates are not manually entered
    if lat is None or lon is None:
        lat, lon, resolved_addr = geocode_address(
            payload.name, payload.city, payload.state, payload.country, payload.location
        )
        if lat is None or lon is None:
            warning_msg = "Location could not be automatically resolved. Please enter coordinates or select the location on the map."
            
    w = Warehouse(
        id=payload.id,
        name=payload.name,
        location=resolved_addr if resolved_addr else payload.location,
        city=payload.city,
        state=payload.state,
        country=payload.country,
        latitude=lat,
        longitude=lon
    )
    db.add(w)
    db.commit()
    log_access(db, user.username, "add_warehouse", warehouse_id=payload.id, request=request)
    logger.info("Warehouse created: id=%s name=%s by=%s", payload.id, payload.name, user.username)
    
    # Audit logging
    ledger.append_entry(db, "warehouse_created", {
        "actor": user.username,
        "warehouse_id": w.id,
        "latitude": w.latitude,
        "longitude": w.longitude
    })
    
    notifications.send_change_alert("New Warehouse Registered", {
        "warehouse_id": w.id,
        "name": w.name,
        "location": w.location,
        "coordinates": f"{w.latitude}, {w.longitude}",
        "created_by": user.username
    })
    
    return {"status": "created", "id": w.id, "warning": warning_msg}


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
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    old_lat = w.latitude
    old_lng = w.longitude
    
    lat = payload.latitude
    lon = payload.longitude
    resolved_addr = None
    warning_msg = None
    
    # Geocoding fallback sequence if coordinates are not manually entered
    if lat is None or lon is None:
        lat, lon, resolved_addr = geocode_address(
            payload.name, payload.city, payload.state, payload.country, payload.location
        )
        if lat is None or lon is None:
            warning_msg = "Location could not be automatically resolved. Please enter coordinates or select the location on the map."
            
    w.name = payload.name
    w.location = resolved_addr if resolved_addr else payload.location
    w.city = payload.city
    w.state = payload.state
    w.country = payload.country
    w.latitude = lat
    w.longitude = lon
    
    db.commit()
    log_access(db, user.username, "update_warehouse", warehouse_id=id, request=request)
    logger.info("Warehouse updated: id=%s name=%s by=%s", id, payload.name, user.username)
    
    # Audit logging
    ledger.append_entry(db, "warehouse_updated", {
        "actor": user.username,
        "warehouse_id": id,
        "old_latitude": old_lat,
        "old_longitude": old_lng,
        "new_latitude": lat,
        "new_longitude": lon
    })
    
    return {"status": "updated", "id": id, "warning": warning_msg}


@router.patch("/warehouses/{id}/location")
def update_warehouse_location_coords(id: str, payload: CoordinatesUpdate, request: Request, db: Session = Depends(get_db), user=Depends(require_admin)):
    w = db.query(Warehouse).filter(Warehouse.id == id).first()
    if not w:
        raise HTTPException(status_code=404, detail="Warehouse not found")
        
    old_lat = w.latitude
    old_lng = w.longitude
    
    w.latitude = payload.latitude
    w.longitude = payload.longitude
    
    # Optional reverse geocoding to update address safely
    try:
        resolved_addr = reverse_geocode(payload.latitude, payload.longitude)
        if resolved_addr:
            w.location = resolved_addr
    except Exception as e:
        logger.warning("Reverse geocoding failed during coordinate patch: %s", e)
        
    db.commit()
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
def update_coordinates(id: str, payload: CoordinatesUpdate, request: Request, db: Session = Depends(get_db), user=Depends(require_admin)):
    w = db.query(Warehouse).filter(Warehouse.id == id).first()
    if not w:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    old_lat = w.latitude
    old_lng = w.longitude
    w.latitude = payload.latitude
    w.longitude = payload.longitude
    db.commit()
    
    log_access(db, user.username, "update_coordinates", warehouse_id=id, request=request)
    logger.info("Warehouse coordinates updated: id=%s lat=%s lng=%s by=%s", id, payload.latitude, payload.longitude, user.username)
    
    # Audit logging
    ledger.append_entry(db, "warehouse_location_changed", {
        "actor": user.username,
        "warehouse_id": id,
        "old_latitude": old_lat,
        "old_longitude": old_lng,
        "new_latitude": payload.latitude,
        "new_longitude": payload.longitude
    })
    
    notifications.send_change_alert("Warehouse Location Coordinates Locked", {
        "warehouse_id": id,
        "name": w.name,
        "location": w.location,
        "previous_coordinates": f"{old_lat}, {old_lng}",
        "new_coordinates": f"{payload.latitude}, {payload.longitude}",
        "updated_by": user.username
    })
    
    return {"status": "updated", "id": id, "latitude": w.latitude, "longitude": w.longitude}


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
             "lead_time_days": i.lead_time_days, "safety_stock": i.safety_stock} for i in db.query(Item).all()]


@router.post("/items")
def create_item(payload: ItemCreate, request: Request, db: Session = Depends(get_db), user=Depends(require_admin)):
    if db.query(Item).filter(Item.id == payload.id).first():
        raise HTTPException(400, "Item ID already exists")
    i = Item(id=payload.id, name=payload.name, category=payload.category, unit_cost=payload.unit_cost,
              lead_time_days=payload.lead_time_days, safety_stock=payload.safety_stock)
    db.add(i)
    db.commit()
    log_access(db, user.username, "add_item", request=request)
    logger.info("Item created: id=%s name=%s by=%s", payload.id, payload.name, user.username)
    
    notifications.send_change_alert("New Item/SKU Added", {
        "item_id": i.id,
        "name": i.name,
        "category": i.category,
        "unit_cost": f"INR {i.unit_cost}",
        "safety_stock": i.safety_stock,
        "created_by": user.username
    })
    
    return {"status": "created", "id": i.id}


@router.post("/stock-movements")
def record_stock_movement(payload: StockMovementCreate, request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role == "viewer":
        raise HTTPException(status_code=403, detail="Access denied. Role 'viewer' is read-only.")
    if not db.query(Warehouse).filter(Warehouse.id == payload.warehouse_id).first():
        raise HTTPException(404, "Warehouse not found")
    if not db.query(Item).filter(Item.id == payload.item_id).first():
        raise HTTPException(404, "Item not found")

    prev = (db.query(StockMovement)
            .filter(StockMovement.warehouse_id == payload.warehouse_id, StockMovement.item_id == payload.item_id,
                    StockMovement.date < payload.date)
            .order_by(StockMovement.date.desc()).first())
    prev_closing = prev.closing_stock if prev else 0
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
        SELECT sm.item_id, i.name AS item_name, i.category, sm.closing_stock AS current_stock,
               i.safety_stock, i.unit_cost
        FROM stock_movements sm
        JOIN items i ON sm.item_id = i.id
        JOIN (SELECT warehouse_id, item_id, MAX(date) md FROM stock_movements
              WHERE warehouse_id = :wh GROUP BY warehouse_id, item_id) latest
        ON sm.warehouse_id = latest.warehouse_id AND sm.item_id = latest.item_id AND sm.date = latest.md
        WHERE sm.warehouse_id = :wh
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
