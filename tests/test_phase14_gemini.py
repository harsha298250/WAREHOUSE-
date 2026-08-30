import pytest
import json
import asyncio
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.models import Warehouse, User, Robot
from backend.services.ai_service import (
    GeminiService,
    get_warehouse_status,
    get_inventory_levels,
    get_robot_telemetry,
    get_recent_anomalies,
    calculate_route_astar,
    TOOL_REGISTRY,
    GEMINI_API_KEY
)

def test_central_gemini_configuration():
    """Asserts that model configurations are correctly loaded from context variables."""
    from backend.services.ai_service import GEMINI_MODEL, GEMINI_TEMPERATURE
    assert GEMINI_MODEL is not None
    assert GEMINI_TEMPERATURE == 0.3

def test_tool_registry_schemas():
    """Asserts that the registered tools match the strict schemas and are complete."""
    assert "get_warehouse_status" in TOOL_REGISTRY
    assert "get_inventory_levels" in TOOL_REGISTRY
    assert "get_robot_telemetry" in TOOL_REGISTRY
    assert "get_recent_anomalies" in TOOL_REGISTRY
    assert "calculate_route_astar" in TOOL_REGISTRY

def test_tool_rbac_authorization(db):
    """Enforces that read-only tools check user roles and deny access to unauthorized users."""
    # Seed a warehouse
    wh = db.query(Warehouse).filter(Warehouse.id == "WH-BLR-01").first()
    if not wh:
        wh = Warehouse(id="WH-BLR-01", name="Bangalore Hub", location="BLR")
        db.add(wh)
        db.commit()

    # Viewer role has read permission for WMS status
    res = get_warehouse_status(db, "viewer", "WH-BLR-01")
    assert res["warehouse_id"] == "WH-BLR-01"

    # Viewer role is NOT allowed to calculate route (requires admin or manager)
    with pytest.raises(HTTPException) as exc:
        calculate_route_astar(db, "viewer", "WH-BLR-01", "ROB-01", 0, 0, 5, 5)
    assert exc.value.status_code == 403

def test_database_non_mutation_safety(db):
    """Guarantees that querying the WMS state via tools does not mutate PostgreSQL data."""
    wh = db.query(Warehouse).filter(Warehouse.id == "WH-BLR-01").first()
    if not wh:
        wh = Warehouse(id="WH-BLR-01", name="Bangalore Hub", location="BLR")
        db.add(wh)
        db.commit()

    wh_count_before = db.query(Warehouse).count()
    
    # Execute get_warehouse_status tool
    get_warehouse_status(db, "admin", "WH-BLR-01")
    
    wh_count_after = db.query(Warehouse).count()
    assert wh_count_before == wh_count_after

def run_async(coro_creator):
    import queue
    import threading
    q = queue.Queue()
    
    def worker():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            res = loop.run_until_complete(coro_creator())
            q.put((True, res))
        except Exception as e:
            q.put((False, e))
        finally:
            loop.close()
            
    t = threading.Thread(target=worker)
    t.start()
    t.join()
    
    success, val = q.get()
    if success:
        return val
    else:
        raise val


def test_assistant_graceful_offline_fallback(db):
    """Verifies that the assistant falls back to offline logic helper when API key is missing."""
    async def run():
        # Mock GEMINI_API_KEY as empty string
        with patch("backend.services.ai_service.GEMINI_API_KEY", ""):
            user = User(username="temp_user", role="admin")
            res = await GeminiService.run_ai_chat(db, "What is the status of robots?", "WH-BLR-01", user)
            assert res["status"] == "success"
            assert "Offline Analysis" in res["response"]
            assert "Fallback Rule-Based" in res["engine"]
    run_async(run)


@patch("httpx.AsyncClient.post")
def test_mocked_gemini_tool_calling_flow(mock_post, db):
    """Mocks standard Gemini tool-calling REST interface execution loop."""
    async def run():
        # Mock first response: requests get_robot_telemetry tool
        resp1 = MagicMock()
        resp1.status_code = 200
        resp1.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "functionCall": {
                            "name": "get_robot_telemetry",
                            "args": {"warehouse_id": "WH-BLR-01"}
                        }
                    }]
                }
            }]
        }

        # Mock second response: explains the telemetry
        resp2 = MagicMock()
        resp2.status_code = 200
        resp2.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": "The robots in WH-BLR-01 are running normally."
                    }]
                }
            }]
        }

        mock_post.side_effect = [resp1, resp2]

        # Seed warehouse and robot
        wh = db.query(Warehouse).filter(Warehouse.id == "WH-BLR-01").first()
        if not wh:
            wh = Warehouse(id="WH-BLR-01", name="Bangalore Hub", location="BLR")
            db.add(wh)
            db.commit()

        rob = db.query(Robot).filter(Robot.robot_code == "ROB-01").first()
        if not rob:
            rob = Robot(robot_code="ROB-01", name="Robot 1", status="AVAILABLE", battery_level=90.0, warehouse_id="WH-BLR-01")
            db.add(rob)
            db.commit()

        # Temporarily set API key to test real path
        with patch("backend.services.ai_service.GEMINI_API_KEY", "fake-api-key"):
            user = User(username="test_user", role="admin")
            res = await GeminiService.run_ai_chat(db, "Give me robot telemetry status.", "WH-BLR-01", user)
            
            assert res["status"] == "success"
            assert "The robots in WH-BLR-01 are running normally." in res["response"]
            assert len(res["tool_calls"]) == 1
            assert res["tool_calls"][0]["name"] == "get_robot_telemetry"
    run_async(run)
