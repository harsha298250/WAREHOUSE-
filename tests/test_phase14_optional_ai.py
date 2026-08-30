import pytest
import os
import json
import asyncio
import queue
import threading
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.models import Warehouse, User, Robot
from backend.services.ai_service import (
    GeminiService,
    search_warehouse_documents,
    read_warehouse_document,
    execute_python_calculation,
    TOOL_REGISTRY
)


def run_async(coro_creator):
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


def test_optional_capabilities_registered():
    """Asserts that all optional capability tools are present in the registry."""
    assert "search_warehouse_documents" in TOOL_REGISTRY
    assert "read_warehouse_document" in TOOL_REGISTRY
    assert "execute_python_calculation" in TOOL_REGISTRY
    assert "grounding_web_search" not in TOOL_REGISTRY
    assert "grounding_maps_search" not in TOOL_REGISTRY

def test_agentic_multi_tool_execution_loop(db):
    """Mocks a sequential double-tool agent calling loop."""
    async def run():
        # 1st call requests get_warehouse_status
        resp1 = MagicMock()
        resp1.status_code = 200
        resp1.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "functionCall": {
                            "name": "get_warehouse_status",
                            "args": {"warehouse_id": "WH-BLR-01"}
                        }
                    }]
                }
            }]
        }

        # 2nd call requests get_robot_telemetry
        resp2 = MagicMock()
        resp2.status_code = 200
        resp2.json.return_value = {
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

        # 3rd call finishes and explains the combined results
        resp3 = MagicMock()
        resp3.status_code = 200
        resp3.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": "Warehouse WH-BLR-01 status and robot telemetry have been successfully parsed."
                    }]
                }
            }]
        }

        wh = db.query(Warehouse).filter(Warehouse.id == "WH-BLR-01").first()
        if not wh:
            wh = Warehouse(id="WH-BLR-01", name="Bangalore Hub", location="BLR")
            db.add(wh)
            db.commit()

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.side_effect = [resp1, resp2, resp3]
            
            with patch("backend.services.ai_service.GEMINI_API_KEY", "fake-key"):
                user = User(username="admin_user", role="admin")
                res = await GeminiService.run_ai_chat(db, "Give me warehouse summary and robot fleet status.", "WH-BLR-01", user)
                
                assert res["status"] == "success"
                assert "successfully parsed" in res["response"]
                assert len(res["tool_calls"]) == 2
                assert res["tool_calls"][0]["name"] == "get_warehouse_status"
                assert res["tool_calls"][1]["name"] == "get_robot_telemetry"
    run_async(run)

def test_rag_document_search(db):
    """Verifies document search (RAG) scanning local directories for matching keywords."""
    # Run RAG search over documents
    res = search_warehouse_documents(db, "viewer", "datasets")
    assert "query" in res
    assert "matches" in res
    assert res["source"] == "RAG Document Knowledge"

def test_document_reader_safety(db):
    """Asserts that document reader blocks path traversal injection tricks."""
    # Test safe path reading
    res = read_warehouse_document(db, "viewer", "DATASETS.md")
    assert res["filename"] == "DATASETS.md"
    assert "content_preview" in res

    # Test path traversal injection block
    with pytest.raises(HTTPException) as exc:
        read_warehouse_document(db, "viewer", "../database.py")
    assert exc.value.status_code == 400
    assert "traversal" in exc.value.detail

def test_sandbox_code_execution(db):
    """Asserts secure evaluation of math/stats formulas and rejection of imports/fs access."""
    # Test safe calculations
    res = execute_python_calculation(db, "admin", "100 * 50")
    assert res["status"] == "success"
    assert res["result"] == 5000

    # Test unsafe import keywords block (ast.parse mode="eval" rejects statements naturally)
    res_unsafe = execute_python_calculation(db, "admin", "import os; os.system('echo 1')")
    assert res_unsafe["status"] == "error"
    assert "Security" in res_unsafe["error"] or "error" in res_unsafe["error"].lower()

    # Test unsafe builtins/dunder block
    res_dunder = execute_python_calculation(db, "admin", "__builtins__.__dict__")
    assert res_dunder["status"] == "error"

def test_grounding_search_and_maps(db):
    """Ensures search and maps grounding tools are completely removed and unavailable."""
    assert "grounding_web_search" not in TOOL_REGISTRY
    assert "grounding_maps_search" not in TOOL_REGISTRY

def test_voice_ai_endpoint_transcription(db):
    """Verifies voice AI endpoint converts base64, runs tool calls, and synthesizes audio replies."""
    async def run():
        from backend.routers.ai_assistant import VoiceMessage, ask_voice_ai_assistant
        
        # 1st call requests get_warehouse_status
        resp1 = MagicMock()
        resp1.status_code = 200
        resp1.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": "Voice instruction processed."
                    }]
                }
            }]
        }

        wh = db.query(Warehouse).filter(Warehouse.id == "WH-BLR-01").first()
        if not wh:
            wh = Warehouse(id="WH-BLR-01", name="Bangalore Hub", location="BLR")
            db.add(wh)
            db.commit()

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value = resp1
            
            with patch("backend.services.ai_service.GEMINI_API_KEY", "fake-key"):
                user = User(username="voice_user", role="admin")
                payload = VoiceMessage(audio_base64="base64_robots", warehouse_id="WH-BLR-01")
                
                res = await ask_voice_ai_assistant(payload, db, user)
                
                assert res["status"] == "success"
                assert res["transcription"] == "How many robots are active?"
                assert res["audio_response_base64"] == "mock_speech_synthesized_response_data"
    run_async(run)
