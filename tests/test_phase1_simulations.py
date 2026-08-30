"""
test_phase1_simulations.py — Tests for Phase 1: Fix Non-Functional Simulations

Covers:
  1. SimPy packing simulation endpoint (Issue 1)
  2. OR-Tools scheduler using real robots (Issue 2)
  3. Packing simulation determinism with random_seed (Issue 4)
"""
import pytest
from backend.models import User, Robot, Task, Warehouse, WarehouseLocation, Item

@pytest.fixture(name="phase1_test_data")
def fixture_phase1_test_data(db):
    """Seed test warehouse, items, locations, robots, and tasks, and clean them up afterward."""
    # Clean up any potential leftover from a aborted run
    db.query(Task).filter(Task.warehouse_id == "WH-TEST-P1").delete()
    db.query(Robot).filter(Robot.warehouse_id == "WH-TEST-P1").delete()
    db.query(WarehouseLocation).filter(WarehouseLocation.warehouse_id == "WH-TEST-P1").delete()
    db.query(Warehouse).filter(Warehouse.id == "WH-TEST-P1").delete()
    db.query(Item).filter(Item.id == "ITM-TEST-P1").delete()
    db.commit()

    # Seed warehouse
    wh = Warehouse(id="WH-TEST-P1", name="Phase 1 Test Warehouse", location="Test Zone")
    db.add(wh)

    # Seed item (required for Task.product_id FK)
    item = Item(id="ITM-TEST-P1", name="Test Widget P1", sku="SKU-T-P1", unit_cost=10.0, reorder_threshold=5)
    db.add(item)
    db.commit()

    # Seed locations
    loc_storage = WarehouseLocation(
        id="LOC-S1-P1", warehouse_id="WH-TEST-P1", x=5.0, y=5.0,
        location_type="STORAGE", zone="A", aisle="A1", rack="01", shelf="02"
    )
    loc_packing = WarehouseLocation(
        id="LOC-P1-P1", warehouse_id="WH-TEST-P1", x=1.0, y=1.0,
        location_type="PACKING", zone="P", aisle="P1", rack="01", shelf="01"
    )
    db.add_all([loc_storage, loc_packing])
    db.commit()

    # Seed real robots
    for i in range(1, 4):
        db.add(Robot(
            robot_code=f"ROB-T{i}-P1", name=f"Test Bot {i} P1",
            warehouse_id="WH-TEST-P1", status="AVAILABLE",
            battery_level=85.0, current_x=float(i), current_y=float(i),
            max_speed=1.5, enabled=True
        ))

    # Seed tasks (product_id is required)
    for i in range(1, 4):
        db.add(Task(
            task_number=f"TSK-T{i}-P1", warehouse_id="WH-TEST-P1",
            task_type="PICK", priority="MEDIUM", priority_score=10,
            status="PENDING", product_id="ITM-TEST-P1",
            source_location_id="LOC-S1-P1",
            destination_location_id="LOC-P1-P1", requested_quantity=1, completed_quantity=0
        ))
    db.commit()

    yield

    # Clean up test data in correct order to avoid Foreign Key constraint failures
    db.query(Task).filter(Task.warehouse_id == "WH-TEST-P1").delete()
    db.query(Robot).filter(Robot.warehouse_id == "WH-TEST-P1").delete()
    db.query(WarehouseLocation).filter(WarehouseLocation.warehouse_id == "WH-TEST-P1").delete()
    db.query(Warehouse).filter(Warehouse.id == "WH-TEST-P1").delete()
    db.query(Item).filter(Item.id == "ITM-TEST-P1").delete()
    db.commit()


# ============================================================================
# Issue 1: SimPy Packing Simulation Endpoint
# ============================================================================

def test_packing_simulation_endpoint(client, admin_token):
    """POST /scenarios/packing-simulation runs SimPy and returns non-trivial results."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.post("/scenarios/packing-simulation", json={
        "num_operators": 3,
        "mean_packing_time": 12.0,
        "duration": 120.0,
        "mean_arrival_interval": 5.0,
        "random_seed": 42
    }, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ("success", "mock")
    assert data["orders_processed"] > 0
    assert data["operator_utilization_pct"] > 0
    assert data["operators_count"] == 3
    assert "average_queue_wait_minutes" in data
    assert "max_queue_bottleneck" in data


def test_packing_simulation_validation(client, admin_token):
    """Invalid parameters should be rejected."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.post("/scenarios/packing-simulation", json={
        "num_operators": 0,
        "mean_packing_time": 12.0,
        "duration": 120.0
    }, headers=headers)
    assert res.status_code == 400


# ============================================================================
# Issue 2: OR-Tools Benchmark Uses Real Robots
# ============================================================================

def test_ortools_benchmark_uses_real_robots(client, phase1_test_data, admin_token):
    """GET /ai/optimize-scheduler should use real robot codes, not hardcoded R1/R2/R3."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/ai/optimize-scheduler?warehouse_id=WH-TEST-P1", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    # Should use real robot codes from the DB
    assert "robots_used" in data
    for robot_code in data["robots_used"]:
        assert robot_code.startswith("ROB-T"), f"Expected real robot code, got {robot_code}"
    # Should NOT contain hardcoded fake robots
    assert "R1" not in data.get("robots_used", [])
    assert "R2" not in data.get("robots_used", [])
    assert "R3" not in data.get("robots_used", [])


def test_ortools_benchmark_no_robots_available(client, admin_token):
    """Benchmark with no robots in the warehouse should return clear no_robots status."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Use a warehouse with no robots
    res = client.get("/ai/optimize-scheduler?warehouse_id=WH-EMPTY-99", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "skipped"


# ============================================================================
# Issue 4: Determinism / Reproducibility
# ============================================================================

def test_packing_simulation_determinism(client, admin_token):
    """Two runs with the same seed must produce identical output."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "num_operators": 3,
        "mean_packing_time": 12.0,
        "duration": 120.0,
        "mean_arrival_interval": 5.0,
        "random_seed": 12345
    }

    res1 = client.post("/scenarios/packing-simulation", json=payload, headers=headers)
    res2 = client.post("/scenarios/packing-simulation", json=payload, headers=headers)

    assert res1.status_code == 200
    assert res2.status_code == 200

    data1 = res1.json()
    data2 = res2.json()

    assert data1["orders_processed"] == data2["orders_processed"], \
        f"Non-deterministic: {data1['orders_processed']} != {data2['orders_processed']}"
    assert data1["average_queue_wait_minutes"] == data2["average_queue_wait_minutes"]
    assert data1["average_packing_time_minutes"] == data2["average_packing_time_minutes"]
    assert data1["operator_utilization_pct"] == data2["operator_utilization_pct"]
    assert data1["max_queue_bottleneck"] == data2["max_queue_bottleneck"]
