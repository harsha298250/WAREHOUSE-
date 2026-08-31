"""
backend/routers/decision_support.py — Safe Read-Only Decision Support & Optimization Router.

Provides endpoints for priority recommendations, explainable insights,
operational health scores, and read-only what-if scenario simulations.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.auth import get_current_user
from backend.models import User
from backend import decision_support_engine as engine

router = APIRouter(prefix="/decision-support", tags=["Decision Support & Optimization"])


class WhatIfRequest(BaseModel):
    scenario_type: str # ROBOT_UNAVAILABLE | DEMAND_INCREASE | AISLE_BLOCKAGE | REPLENISHMENT_DELAY | TASK_LOAD_INCREASE
    warehouse_id: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


@router.get("/overview", summary="Get consolidated Decision Support Dashboard data")
def get_decision_support_overview(
    warehouse_id: Optional[str] = Query(None, description="Optional warehouse ID filter"),
    date_range: str = Query("30d", description="Date range: 7d, 30d, 90d, 1y"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve consolidated operational health, priority recommendations, and domain insights."""
    return engine.get_decision_support_overview(db, warehouse_id=warehouse_id, date_range=date_range)


@router.get("/recommendations", summary="Get prioritized, explainable recommendations")
def get_recommendations(
    warehouse_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve categorized recommendations with explicit 'why' reasoning and suggested action URLs."""
    recs = engine.evaluate_priority_recommendations(db, warehouse_id=warehouse_id)
    return {
        "count": len(recs),
        "warehouse_id": warehouse_id or "ALL",
        "recommendations": recs
    }


@router.get("/robot-insights", summary="Get AGV fleet optimization insights")
def get_robot_insights(
    warehouse_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Analyze AGV workload balance, battery status, and fleet efficiency."""
    return engine.evaluate_robot_insights(db, warehouse_id=warehouse_id)


@router.get("/route-insights", summary="Get pathfinding optimization insights")
def get_route_insights(
    warehouse_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Analyze A* vs Dijkstra execution metrics and map traversability."""
    return engine.evaluate_route_insights(db, warehouse_id=warehouse_id)


@router.get("/inventory-risks", summary="Get inventory stockout and risk intelligence")
def get_inventory_risks(
    warehouse_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Analyze stockout risks, safety stock breaches, and reorder points."""
    return engine.evaluate_inventory_risk(db, warehouse_id=warehouse_id)


@router.get("/health-score", summary="Get transparent operational health score")
def get_health_score(
    warehouse_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Compute 0-100 warehouse operational health score with itemized contributing factors."""
    return engine.calculate_operational_health_score(db, warehouse_id=warehouse_id)


@router.post("/what-if", summary="Run a read-only What-If scenario simulation")
def run_what_if_scenario(
    payload: WhatIfRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Run read-only What-If analysis (ROBOT_UNAVAILABLE, DEMAND_INCREASE, AISLE_BLOCKAGE, REPLENISHMENT_DELAY, TASK_LOAD_INCREASE).
    Produces estimated impact metrics without mutating production database tables.
    """
    params = payload.parameters or {}
    if payload.warehouse_id:
        params["warehouse_id"] = payload.warehouse_id

    res = engine.run_what_if_analysis(db, scenario_type=payload.scenario_type, parameters=params)
    if "status" in res and res["status"] == 400:
        raise HTTPException(status_code=400, detail=res.get("error", "Invalid simulation parameter."))
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return res


# ---------------------------------------------------------------------------
# PHASE 8: DECISION INTELLIGENCE ENDPOINTS
# ---------------------------------------------------------------------------
@router.get("/decisions", summary="Get prioritized, explainable decision intelligence feed")
def get_decision_intelligence_feed(
    warehouse_id: Optional[str] = Query(None, description="Optional warehouse ID filter"),
    category: Optional[str] = Query(None, description="Filter by decision category"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve Decision Intelligence feed synthesized across Orders, Tasks, Robots, Routes, Inventory, Replenishment, Digital Twin & Simulation."""
    res = engine.evaluate_decision_intelligence(db, warehouse_id=warehouse_id)
    if category:
        cat_upper = category.upper()
        res["decisions"] = [d for d in res["decisions"] if d["category"].upper() == cat_upper]
        res["total_decisions"] = len(res["decisions"])
    return res


@router.get("/top-actions", summary="Get top actionable warehouse recommendations")
def get_top_actions(
    warehouse_id: Optional[str] = Query(None),
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve top actionable recommendations for the Decision Center dashboard."""
    res = engine.evaluate_decision_intelligence(db, warehouse_id=warehouse_id)
    return {
        "warehouse_id": warehouse_id or "ALL",
        "count": min(limit, len(res["top_actions"])),
        "top_actions": res["top_actions"][:limit]
    }


@router.post("/decisions/{decision_id}/acknowledge", summary="Acknowledge a decision record")
def acknowledge_decision(
    decision_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a decision record as acknowledged by an authorized user."""
    from backend.models import AIRecommendation
    rec = db.query(AIRecommendation).filter(AIRecommendation.id == decision_id).first()
    if not rec:
        # Search by recommendation_type or title match
        rec = db.query(AIRecommendation).filter(AIRecommendation.source_entity_id == decision_id).first()
    if rec:
        rec.status = "ACKNOWLEDGED"
        rec.decision_by = current_user.username
        rec.decision_time = engine.datetime.now(engine.UTC).replace(tzinfo=None)
        db.commit()
        return {"status": "ACKNOWLEDGED", "decision_id": decision_id, "user": current_user.username}
    return {"status": "ACKNOWLEDGED", "decision_id": decision_id, "note": "Acknowledged in session"}


@router.post("/decisions/{decision_id}/dismiss", summary="Dismiss a decision record")
def dismiss_decision(
    decision_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Dismiss a decision record."""
    from backend.models import AIRecommendation
    rec = db.query(AIRecommendation).filter(AIRecommendation.id == decision_id).first()
    if not rec:
        rec = db.query(AIRecommendation).filter(AIRecommendation.source_entity_id == decision_id).first()
    if rec:
        rec.status = "DISMISSED"
        rec.decision_by = current_user.username
        rec.decision_time = engine.datetime.now(engine.UTC).replace(tzinfo=None)
        db.commit()
        return {"status": "DISMISSED", "decision_id": decision_id, "user": current_user.username}
    return {"status": "DISMISSED", "decision_id": decision_id, "note": "Dismissed in session"}


@router.post("/decisions/{decision_id}/resolve", summary="Resolve a decision record")
def resolve_decision(
    decision_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a decision record as resolved."""
    from backend.models import AIRecommendation
    rec = db.query(AIRecommendation).filter(AIRecommendation.id == decision_id).first()
    if not rec:
        rec = db.query(AIRecommendation).filter(AIRecommendation.source_entity_id == decision_id).first()
    if rec:
        rec.status = "RESOLVED"
        rec.decision_by = current_user.username
        rec.decision_time = engine.datetime.now(engine.UTC).replace(tzinfo=None)
        db.commit()
        return {"status": "RESOLVED", "decision_id": decision_id, "user": current_user.username}
    return {"status": "RESOLVED", "decision_id": decision_id, "note": "Resolved in session"}
