import csv
import io
import logging
from datetime import datetime, UTC
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

import sqlalchemy as sa

from backend.database import get_db
from backend.auth import get_current_user, require_admin
from backend.routers.wms import check_warehouse_access
from backend.models import (
    User, ForecastRun, ForecastResult, ABCClassification,
    AnomalyResult, ReplenishmentRecommendation
)
from backend import analytics_engine as engine

logger = logging.getLogger("warehouse.analytics")

router = APIRouter(prefix="/analytics", tags=["Analytics & KPIs"])


def list_to_csv_response(data_list: list, headers: list, filename: str) -> StreamingResponse:
    """Helper to convert a list of dictionaries into a downloadable CSV response."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    for row in data_list:
        writer.writerow([row.get(h.lower().replace(" ", "_"), "") for h in headers])
    output.seek(0)
    return StreamingResponse(
        io.StringIO(output.getvalue()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/datasets")
def get_datasets_metadata(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves external datasets ingestion status and verification metadata."""
    from backend.models import DatasetSource, DatasetImportRun, DatasetValidationResult
    
    res = {}
    keys = ["m5", "online_retail_ii", "store_sales_forecasting", "retail_sales_forecasting"]
    for key in keys:
        source = db.query(DatasetSource).filter(DatasetSource.id == key).first()
        if not source:
            name_mapping = {
                "m5": "M5 Forecasting / Walmart",
                "online_retail_ii": "UCI Online Retail II",
                "store_sales_forecasting": "Store Sales Time Series Forecasting / NeuroCipher",
                "retail_sales_forecasting": "Retail Sales Forecasting / TEVEC Systems"
            }
            source_mapping = {
                "m5": "Kaggle",
                "online_retail_ii": "UCI Machine Learning Repository",
                "store_sales_forecasting": "Kaggle",
                "retail_sales_forecasting": "Kaggle"
            }
            res[key] = {
                "id": key,
                "name": name_mapping.get(key, key),
                "import_status": "MISSING",
                "validation_status": "FAIL",
                "rows_count": 0,
                "access_download_date": "N/A",
                "official_source": source_mapping.get(key, "N/A"),
                "license": "N/A",
                "doi": "N/A",
                "date_range": "N/A",
                "source_url": "",
                "description": "Dataset missing from the system database.",
                "intended_use": "",
                "known_limitations": ""
            }
            continue
            
        # Get latest run
        run = db.query(DatasetImportRun).filter(DatasetImportRun.dataset_id == key).order_by(DatasetImportRun.id.desc()).first()
        val = None
        if run:
            val = db.query(DatasetValidationResult).filter(DatasetValidationResult.import_run_id == run.id).first()
            
        res[key] = {
            "id": source.id,
            "name": source.name,
            "official_source": source.official_source,
            "source_url": source.source_url,
            "version": source.version,
            "license": source.license,
            "doi": source.doi,
            "publisher": source.publisher,
            "description": source.description,
            "intended_use": source.intended_use,
            "known_limitations": source.known_limitations,
            "import_status": run.status if run else "MISSING",
            "import_timestamp": run.import_timestamp.isoformat() if run else None,
            "rows_count": run.record_count if run else 0,
            "validation_status": val.status if val else "FAIL",
            "duplicate_count": val.duplicate_count if val else 0,
            "missing_values": val.missing_values if val else {},
            "date_range": f"{val.date_range_start} to {val.date_range_end}" if val and val.date_range_start else "N/A"
        }
    return res


@router.get("/overview")
def get_overview(
    warehouse_id: Optional[str] = None,
    period: str = "30d",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Provides high-level consolidated executive KPIs summary."""
    start, end = engine.get_date_range(period, start_date, end_date)
    
    orders = engine.compute_order_analytics(db, warehouse_id, start, end)
    inventory = engine.compute_inventory_analytics(db, warehouse_id, start, end)
    tasks = engine.compute_task_analytics(db, warehouse_id, start, end)
    robots = engine.compute_robot_analytics(db, warehouse_id, start, end)
    routing = engine.compute_routing_analytics(db, warehouse_id, start, end)
    forecasting = engine.compute_forecasting_analytics(db, warehouse_id)
    anomalies = engine.compute_anomaly_analytics(db, warehouse_id, start, end)
    ai = engine.compute_ai_analytics(db, warehouse_id, start, end)
    system = engine.compute_system_reliability_analytics(db, start, end)

    return {
        "generated_at": datetime.now(UTC).replace(tzinfo=None).isoformat(),
        "period": period,
        "warehouse_id": warehouse_id,
        "kpis": {
            "orders_completed": orders["throughput"],
            "order_cycle_time": orders["avg_cycle_time_hours"],
            "inventory_availability": inventory["available"],
            "stockout_risk": inventory["stockout_rate"],
            "task_completion_rate": tasks["completion_rate"],
            "robot_utilization": robots["avg_utilization"],
            "congestion_events": routing["collision_events"],
            "forecast_reliability": forecasting["median_wape"],
            "potential_anomalies": anomalies["potential_anomalies_count"],
            "ai_approval_rate": ai["approval_rate"],
            "notification_success": system["notification_delivery_success"]
        }
    }


@router.get("/orders")
def get_orders(
    warehouse_id: Optional[str] = None,
    period: str = "30d",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    format: str = "json",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves order performance throughput and SLAs."""
    start, end = engine.get_date_range(period, start_date, end_date)
    data = engine.compute_order_analytics(db, warehouse_id, start, end)
    
    if format == "csv":
        csv_data = [
            {"metric": k, "value": v.get("value"), "unit": v.get("unit"), "quality": v.get("data_quality")}
            for k, v in data.items()
        ]
        return list_to_csv_response(csv_data, ["Metric", "Value", "Unit", "Quality"], f"order_analytics_{period}.csv")
        
    return data


@router.get("/inventory")
def get_inventory(
    warehouse_id: Optional[str] = None,
    period: str = "30d",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    format: str = "json",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves detailed stock levels, values, ABC tiers and turnover rates."""
    start, end = engine.get_date_range(period, start_date, end_date)
    data = engine.compute_inventory_analytics(db, warehouse_id, start, end)
    
    if format == "csv":
        csv_data = [
            {"metric": k, "value": v.get("value") if isinstance(v, dict) else str(v), "unit": v.get("unit") if isinstance(v, dict) else "", "quality": v.get("data_quality") if isinstance(v, dict) else ""}
            for k, v in data.items() if k != "abc_distribution"
        ]
        return list_to_csv_response(csv_data, ["Metric", "Value", "Unit", "Quality"], f"inventory_analytics_{period}.csv")
        
    return data


@router.get("/tasks")
def get_tasks(
    warehouse_id: Optional[str] = None,
    period: str = "30d",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    format: str = "json",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves task execution timing logs, priority weighting and completion speeds."""
    start, end = engine.get_date_range(period, start_date, end_date)
    data = engine.compute_task_analytics(db, warehouse_id, start, end)
    
    if format == "csv":
        csv_data = [
            {"metric": k, "value": v.get("value") if isinstance(v, dict) else str(v), "unit": v.get("unit") if isinstance(v, dict) else "", "quality": v.get("data_quality") if isinstance(v, dict) else ""}
            for k, v in data.items() if k not in ("by_type", "by_priority", "avg_duration_by_priority")
        ]
        return list_to_csv_response(csv_data, ["Metric", "Value", "Unit", "Quality"], f"task_analytics_{period}.csv")
        
    return data


@router.get("/robots")
def get_robots(
    warehouse_id: Optional[str] = None,
    period: str = "30d",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    format: str = "json",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves utilization rates, travel distance metrics and charging cycles of the robot fleet."""
    start, end = engine.get_date_range(period, start_date, end_date)
    data = engine.compute_robot_analytics(db, warehouse_id, start, end)
    
    if format == "csv":
        return list_to_csv_response(
            data["comparison"],
            ["Robot Code", "Name", "Status", "Utilization Percent", "Tasks Completed", "Distance Travelled", "Failures", "Avg Battery"],
            f"robot_performance_{period}.csv"
        )
        
    return data


@router.get("/routing")
def get_routing(
    warehouse_id: Optional[str] = None,
    period: str = "30d",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    format: str = "json",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves routing efficiency parameters and cell congestion durations."""
    start, end = engine.get_date_range(period, start_date, end_date)
    data = engine.compute_routing_analytics(db, warehouse_id, start, end)
    
    if format == "csv":
        csv_data = [
            {"metric": k, "value": v.get("value"), "unit": v.get("unit"), "quality": v.get("data_quality")}
            for k, v in data.items()
        ]
        return list_to_csv_response(csv_data, ["Metric", "Value", "Unit", "Quality"], f"routing_analytics_{period}.csv")
        
    return data


@router.get("/forecasting")
def get_forecasting(
    warehouse_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves forecasting accuracy parameters (WAPE, RMSE) and prediction outcomes."""
    return engine.compute_forecasting_analytics(db, warehouse_id)


@router.get("/anomalies")
def get_anomalies(
    warehouse_id: Optional[str] = None,
    period: str = "30d",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    format: str = "json",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves active shrinkage discrepancies and severity distributions."""
    start, end = engine.get_date_range(period, start_date, end_date)
    data = engine.compute_anomaly_analytics(db, warehouse_id, start, end)
    
    if format == "csv":
        return list_to_csv_response(
            data["raw_anomalies"],
            ["Date", "Item ID", "Item Name", "Discrepancy", "Exposure", "Severity", "Cause", "Explanation"],
            f"inventory_anomalies_{period}.csv"
        )
        
    return data


@router.get("/ai")
def get_ai(
    warehouse_id: Optional[str] = None,
    period: str = "30d",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves replenishment approvals, recommendation volumes and AI outcomes."""
    # Restricted to Admin/Manager/Auditor
    if current_user.role not in ("admin", "manager", "auditor"):
        raise HTTPException(status_code=403, detail="Unauthorized access to decision center analytics.")
        
    start, end = engine.get_date_range(period, start_date, end_date)
    return engine.compute_ai_analytics(db, warehouse_id, start, end)


@router.get("/simulation")
def get_simulation(
    warehouse_id: Optional[str] = None,
    period: str = "30d",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves digital twin scenario completions and tick count executions."""
    start, end = engine.get_date_range(period, start_date, end_date)
    return engine.compute_simulation_analytics(db, warehouse_id, start, end)


@router.get("/system")
def get_system(
    period: str = "30d",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves service health ratios, backups and Sentry error counts."""
    # Restricted to Admin/Auditor
    if current_user.role not in ("admin", "auditor"):
        raise HTTPException(status_code=403, detail="Unauthorized access to system engineering logs.")
        
    start, end = engine.get_date_range(period, start_date, end_date)
    return engine.compute_system_reliability_analytics(db, start, end)


# ============================================================
# Phase 9 — ML Demand, ABC, Anomalies & Replenishment Endpoints
# ============================================================

@router.post("/forecasting/run", summary="Trigger dataset-level forecasting pipeline")
def run_dataset_forecasting(
    family: Optional[str] = Query(None, description="Optional specific family to forecast"),
    horizon: int = Query(28, ge=7, le=90),
    train_pct: float = Query(0.80, ge=0.5, le=0.95),
    warehouse_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Triggers the time-series forecasting model fitting and pipeline. Admin/manager only."""
    if current_user.role not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail="Insufficient privileges to trigger ML training.")
        
    if warehouse_id:
        check_warehouse_access(db, current_user, warehouse_id)

    from ml.demand.pipeline import run_forecast_pipeline
    res = run_forecast_pipeline(db, family=family, horizon=horizon, train_pct=train_pct, warehouse_id=warehouse_id)
    if res.get("status") == "error":
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res


@router.get("/forecasting/runs", summary="List historical forecast training runs")
def get_forecast_runs(
    warehouse_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns ForecastRun logs."""
    query = db.query(ForecastRun)
    if warehouse_id:
        check_warehouse_access(db, current_user, warehouse_id)
        query = query.filter(ForecastRun.warehouse_id == warehouse_id)
    elif current_user.role != "admin":
        # Filter by allowed warehouses
        from backend.models import UserWarehouseAccess
        allowed_whs = [a.warehouse_id for a in db.query(UserWarehouseAccess).filter(UserWarehouseAccess.user_id == current_user.id).all()]
        query = query.filter(sa.or_(ForecastRun.warehouse_id.in_(allowed_whs), ForecastRun.warehouse_id.is_(None)))

    runs = query.order_by(ForecastRun.created_at.desc()).offset(offset).limit(limit).all()
    return runs


@router.get("/forecasting/results", summary="Get paginated forecast results")
def get_forecast_results(
    family: Optional[str] = Query(None),
    run_id: Optional[str] = Query(None),
    warehouse_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns detailed daily predicted demand from the latest run or a specific run_id."""
    if warehouse_id:
        check_warehouse_access(db, current_user, warehouse_id)

    query = db.query(ForecastResult).join(ForecastRun)
    if run_id:
        query = query.filter(ForecastResult.run_id == run_id)
    else:
        # Get latest run
        run_q = db.query(ForecastRun)
        if warehouse_id:
            run_q = run_q.filter(ForecastRun.warehouse_id == warehouse_id)
        elif current_user.role != "admin":
            from backend.models import UserWarehouseAccess
            allowed_whs = [a.warehouse_id for a in db.query(UserWarehouseAccess).filter(UserWarehouseAccess.user_id == current_user.id).all()]
            run_q = run_q.filter(sa.or_(ForecastRun.warehouse_id.in_(allowed_whs), ForecastRun.warehouse_id.is_(None)))
            
        latest_run = run_q.order_by(ForecastRun.created_at.desc()).first()
        if latest_run:
            query = query.filter(ForecastResult.run_id == latest_run.run_id)
        else:
            return []

    if family:
        query = query.filter(ForecastResult.entity == family)

    results = query.order_by(ForecastResult.forecast_date.asc()).offset(offset).limit(limit).all()
    return results


@router.post("/abc/run", summary="Trigger ABC classification on a source dataset")
def run_abc_classification(
    source: str = Query("wms", description="wms | store_sales | online_retail | mlzc"),
    threshold_a: float = Query(80.0, ge=10.0, le=95.0),
    threshold_b: float = Query(95.0, ge=15.0, le=99.0),
    warehouse_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Triggers ABC calculation and saves to db. Admin/manager only."""
    if current_user.role not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail="Insufficient privileges to run ABC classification.")
    
    if threshold_a >= threshold_b:
        raise HTTPException(status_code=400, detail="threshold_a must be less than threshold_b.")

    if warehouse_id:
        check_warehouse_access(db, current_user, warehouse_id)

    from ml.abc.classifier import ABCClassifier
    import pandas as pd

    if source == "wms":
        # Load from WMS Items + StockMovements
        from backend.models import Item, StockMovement
        from sqlalchemy import func
        items = db.query(Item).all()
        data_list = []
        for it in items:
            q_sum = db.query(func.sum(StockMovement.stock_out)).filter(StockMovement.item_id == it.id)
            if warehouse_id:
                q_sum = q_sum.filter(StockMovement.warehouse_id == warehouse_id)
            qty = float(q_sum.scalar() or 0.0)
            data_list.append({
                "item_id": it.id,
                "item_name": it.name,
                "qty": qty,
                "unit_cost": float(it.unit_cost or 0.0)
            })
        df = pd.DataFrame(data_list)
        clf = ABCClassifier(threshold_a, threshold_b)
        if not df.empty and df["qty"].sum() > 0:
            clf.fit(df, item_col="item_id", qty_col="qty", value_col="unit_cost", item_name_col="item_name")
        else:
            clf.fit(pd.DataFrame(), "item_id", "qty", "unit_cost")
            
    elif source == "store_sales":
        # Load from raw/processed Store Sales CSV Family-level sales
        from ml.demand.feature_engineering import build_family_series
        try:
            fseries = build_family_series()
            data_list = []
            for fam_name, fdf in fseries.items():
                qty = float(fdf["daily_sales"].sum())
                data_list.append({"family": fam_name, "qty": qty, "price": 1.0})
            df = pd.DataFrame(data_list)
            clf = ABCClassifier(threshold_a, threshold_b)
            if not df.empty:
                clf.fit(df, item_col="family", qty_col="qty", value_col="price")
            else:
                clf.fit(pd.DataFrame(), "family", "qty", "price")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load store sales data: {e}")
            
    elif source == "online_retail":
        # UCI Online Retail II raw/processed dataset
        meta = engine.models.DatasetSource.get_id_or_none(db, "online_retail_ii")
        # Just compute it on the processed CSV if present
        import os
        csv_path = os.path.join("data", "processed", "online_retail_ii", "online_retail_II_processed.csv")
        if not os.path.isfile(csv_path):
            raise HTTPException(status_code=400, detail="UCI Online Retail II processed file not found.")
        try:
            chunks = []
            for chunk in pd.read_csv(csv_path, chunksize=100000):
                chunks.append(chunk[["StockCode", "Quantity", "Price", "Description"]].copy())
            df_full = pd.concat(chunks, ignore_index=True)
            clf = ABCClassifier(threshold_a, threshold_b)
            clf.fit(df_full, item_col="StockCode", qty_col="Quantity", value_col="Price", item_name_col="Description")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process UCI dataset: {e}")
            
    elif source == "mlzc":
        import os
        csv_path = os.path.join("data", "processed", "retail_sales_forecasting", "sales_processed.csv")
        catalog_path = os.path.join("data", "processed", "retail_sales_forecasting", "catalog_processed.csv")
        if not os.path.isfile(csv_path):
            raise HTTPException(status_code=400, detail="MLZC processed sales.csv file not found.")
        try:
            chunks = []
            for chunk in pd.read_csv(csv_path, chunksize=100000):
                chunks.append(chunk[["item_id", "quantity", "price_base"]].copy())
            df_sales = pd.concat(chunks, ignore_index=True)
            # Try to map names if catalog exists
            item_names = {}
            if os.path.isfile(catalog_path):
                cat = pd.read_csv(catalog_path)
                item_names = dict(zip(cat["item_id"].astype(str), cat["dept_name"].astype(str)))
            df_sales["item_name"] = df_sales["item_id"].astype(str).map(item_names)
            clf = ABCClassifier(threshold_a, threshold_b)
            clf.fit(df_sales, item_col="item_id", qty_col="quantity", value_col="price_base", item_name_col="item_name")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process MLZC dataset: {e}")
            
    else:
        raise HTTPException(status_code=400, detail=f"Invalid source: {source}")

    saved_count = clf.save_to_db(db, source, warehouse_id=warehouse_id)
    return {
        "status": "success",
        "source": source,
        "records_classified": saved_count,
        "summary": clf.get_summary()
    }


@router.get("/abc", summary="Get latest ABC classification results")
def get_abc_classifications(
    source: str = Query("wms", description="wms | store_sales | online_retail | mlzc"),
    abc_class: Optional[str] = Query(None, description="A | B | C"),
    warehouse_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves computed ABC inventory classifications for a source dataset."""
    query = db.query(ABCClassification).filter(ABCClassification.source == source)
    
    if warehouse_id:
        check_warehouse_access(db, current_user, warehouse_id)
        query = query.filter(ABCClassification.warehouse_id == warehouse_id)
    elif source == "wms" and current_user.role != "admin":
        # Filter by allowed warehouses
        from backend.models import UserWarehouseAccess
        allowed_whs = [a.warehouse_id for a in db.query(UserWarehouseAccess).filter(UserWarehouseAccess.user_id == current_user.id).all()]
        query = query.filter(sa.or_(ABCClassification.warehouse_id.in_(allowed_whs), ABCClassification.warehouse_id.is_(None)))

    if abc_class:
        query = query.filter(ABCClassification.abc_class == abc_class.upper())
    
    total_count = query.count()
    results = query.order_by(ABCClassification.total_value.desc()).offset(offset).limit(limit).all()
    
    # Generate summary stats
    summary = {}
    for cls in ("A", "B", "C"):
        sub_q = db.query(ABCClassification).filter(ABCClassification.source == source, ABCClassification.abc_class == cls)
        if warehouse_id:
            sub_q = sub_q.filter(ABCClassification.warehouse_id == warehouse_id)
        elif source == "wms" and current_user.role != "admin":
            from backend.models import UserWarehouseAccess
            allowed_whs = [a.warehouse_id for a in db.query(UserWarehouseAccess).filter(UserWarehouseAccess.user_id == current_user.id).all()]
            sub_q = sub_q.filter(sa.or_(ABCClassification.warehouse_id.in_(allowed_whs), ABCClassification.warehouse_id.is_(None)))
            
        summary[cls] = {
            "count": sub_q.count(),
            "total_value": round(float(db.query(sa.func.sum(ABCClassification.total_value)).filter(
                ABCClassification.source == source,
                ABCClassification.abc_class == cls
            ).filter(
                ABCClassification.warehouse_id == warehouse_id if warehouse_id else sa.true()
            ).scalar() or 0.0), 2)
        }

    return {
        "total": total_count,
        "summary": summary,
        "results": results
    }


@router.post("/anomalies/run", summary="Trigger dataset demand anomaly detection")
def run_demand_anomalies(
    contamination: float = Query(0.05, ge=0.01, le=0.2),
    warehouse_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Runs IsolationForest on NeuroCipher daily family demand series. Admin/manager only."""
    if current_user.role not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail="Insufficient privileges to trigger anomaly runs.")

    if warehouse_id:
        check_warehouse_access(db, current_user, warehouse_id)

    from ml.anomaly.demand_anomaly import detect_demand_anomalies, save_anomalies_to_db
    res = detect_demand_anomalies(contamination=contamination)
    if res.get("status") == "insufficient_data":
        raise HTTPException(status_code=400, detail=res.get("error", "Insufficient data"))
        
    save_anomalies_to_db(db, res, warehouse_id=warehouse_id)
    return res


@router.get("/anomalies/demand", summary="Get paginated demand anomalies")
def get_demand_anomalies(
    severity: Optional[str] = Query(None, description="LOW | MEDIUM | HIGH | CRITICAL"),
    warehouse_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves detected demand anomalies from NeuroCipher dataset."""
    query = db.query(AnomalyResult).filter(AnomalyResult.dataset_id == "store_sales_forecasting")
    
    if warehouse_id:
        check_warehouse_access(db, current_user, warehouse_id)
        query = query.filter(AnomalyResult.warehouse_id == warehouse_id)
    elif current_user.role != "admin":
        from backend.models import UserWarehouseAccess
        allowed_whs = [a.warehouse_id for a in db.query(UserWarehouseAccess).filter(UserWarehouseAccess.user_id == current_user.id).all()]
        query = query.filter(sa.or_(AnomalyResult.warehouse_id.in_(allowed_whs), AnomalyResult.warehouse_id.is_(None)))

    if severity:
        query = query.filter(AnomalyResult.severity == severity.upper())
        
    total = query.count()
    results = query.order_by(AnomalyResult.anomaly_score.desc(), AnomalyResult.date.desc()).offset(offset).limit(limit).all()
    return {
        "total": total,
        "results": results
    }


@router.post("/replenishment/run", summary="Trigger replenishment recommendations engine")
def run_replenishment_recommendations(
    warehouse_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Triggers replenishment calculations across all warehouses. Admin/manager only."""
    if current_user.role not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail="Insufficient privileges to trigger replenishment.")

    if warehouse_id:
        check_warehouse_access(db, current_user, warehouse_id)
    elif current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Non-admin users must specify a warehouse_id to run replenishment.")

    from ml.replenishment.engine import run_replenishment_engine
    res = run_replenishment_engine(db, warehouse_id=warehouse_id)
    return res


@router.get("/replenishment", summary="Get latest replenishment recommendations")
def get_replenishment_recommendations(
    warehouse_id: Optional[str] = Query(None),
    urgency: Optional[str] = Query(None, description="NO_ACTION | MONITOR | REORDER_RECOMMENDED | URGENT_REORDER | INSUFFICIENT_DATA"),
    abc_class: Optional[str] = Query(None, description="A | B | C"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves computed replenishment recommendations. Sourced from latest run."""
    query = db.query(ReplenishmentRecommendation)
    
    if warehouse_id:
        check_warehouse_access(db, current_user, warehouse_id)
        query = query.filter(ReplenishmentRecommendation.warehouse_id == warehouse_id)
    elif current_user.role != "admin":
        from backend.models import UserWarehouseAccess
        allowed_whs = [a.warehouse_id for a in db.query(UserWarehouseAccess).filter(UserWarehouseAccess.user_id == current_user.id).all()]
        query = query.filter(ReplenishmentRecommendation.warehouse_id.in_(allowed_whs))

    if urgency:
        query = query.filter(ReplenishmentRecommendation.urgency == urgency.upper())
    if abc_class:
        query = query.filter(ReplenishmentRecommendation.abc_class == abc_class.upper())
        
    total = query.count()
    results = query.order_by(sa.case(
        (ReplenishmentRecommendation.urgency == 'URGENT_REORDER', 1),
        (ReplenishmentRecommendation.urgency == 'REORDER_RECOMMENDED', 2),
        (ReplenishmentRecommendation.urgency == 'MONITOR', 3),
        (ReplenishmentRecommendation.urgency == 'INSUFFICIENT_DATA', 4),
        else_=5
    ), ReplenishmentRecommendation.item_id.asc()).offset(offset).limit(limit).all()

    # Provenance labels
    data_provenance = {
        "current_stock": "ACTUAL — PostgreSQL WMS (inventories table)",
        "lead_time_days": "ACTUAL — PostgreSQL WMS (items table)",
        "safety_stock": "ACTUAL — PostgreSQL WMS (items table)",
        "forecast_demand": "FORECAST — TrendSeasonalityModel on NeuroCipher dataset",
        "abc_class": "CALCULATED — ABCClassifier",
        "reorder_point": "CALCULATED — lead_time_demand + safety_stock",
        "inventory_not_modified": "TRUE — recommendations only"
    }

    return {
        "total": total,
        "data_provenance": data_provenance,
        "results": results
    }

