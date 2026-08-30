import os
import threading
import time
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.main import app

def test_schedulers_do_not_start_in_testing():
    """
    Verify that background schedulers/workers are not started
    when the environment is set to 'testing'.
    """
    # Verify that ENVIRONMENT is indeed 'testing' (forced by conftest.py)
    assert os.getenv("ENVIRONMENT") == "testing"
    
    # Store initial thread count or thread names
    initial_threads = {t.name for t in threading.enumerate()}
    
    # Launch TestClient (which triggers lifespan startup)
    with TestClient(app) as client:
        # Get active threads during TestClient lifespan
        active_threads = {t.name for t in threading.enumerate()}
        
        # Verify that none of the background workers are active
        assert "BackupWorker" not in active_threads
        assert "HealthWorker" not in active_threads
        assert "SimulationWorker" not in active_threads


def test_schedulers_lifecycle_in_production():
    """
    Verify that background schedulers/workers start when ENVIRONMENT != 'testing',
    and cleanly stop and join on lifespan shutdown.
    """
    # Patch ENVIRONMENT to 'production' during TestClient lifespan
    with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
        # Create a test lock/event that keeps the thread running
        running_event = threading.Event()
        def mock_worker():
            # Wait until running_event is set, simulating a running loop
            running_event.wait()

        with patch("backend.main.schedule_backups_worker", side_effect=mock_worker) as mock_backups, \
             patch("backend.main.schedule_health_telemetry_worker", side_effect=mock_worker) as mock_health, \
             patch("backend.main.schedule_simulation_worker", side_effect=mock_worker) as mock_sim:
            
            # Reset worker thread references to simulate fresh startup
            import backend.main as main
            main.BACKUP_WORKER_THREAD = None
            main.HEALTH_WORKER_THREAD = None
            main.SIMULATION_WORKER_THREAD = None
            
            # Start TestClient
            with TestClient(app) as client:
                # Give threads a tiny bit to start
                time.sleep(0.5)
                
                # Check that thread objects were created and are running
                assert main.BACKUP_WORKER_THREAD is not None
                assert main.BACKUP_WORKER_THREAD.is_alive()
                assert main.HEALTH_WORKER_THREAD is not None
                assert main.HEALTH_WORKER_THREAD.is_alive()
                assert main.SIMULATION_WORKER_THREAD is not None
                assert main.SIMULATION_WORKER_THREAD.is_alive()
                
                # Retrieve active thread names
                active_threads = {t.name for t in threading.enumerate()}
                assert "BackupWorker" in active_threads
                assert "HealthWorker" in active_threads
                assert "SimulationWorker" in active_threads
                
                # Release the mock worker threads so they can stop when lifespan shutdown sets events
                running_event.set()
            
            # TestClient exited (lifespan shutdown complete).
            # Verify that threads are no longer alive
            assert not main.BACKUP_WORKER_THREAD.is_alive()
            assert not main.HEALTH_WORKER_THREAD.is_alive()
            assert not main.SIMULATION_WORKER_THREAD.is_alive()
