import pytest
import json
from datetime import datetime, UTC
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from backend.models import (
    Warehouse, Item, Task, Robot, WarehouseLocation, WarehouseGridCell,
    WarehouseObstacle, RobotRoute, User
)
from backend.auth import hash_password
from backend.routers.pathfinding import (
    run_a_star,
    run_dijkstra,
    run_a_star_verbose,
    run_dijkstra_verbose,
    validate_path,
    initialize_warehouse_grid_if_empty
)
from backend.services.operational_pathfinding import (
    get_operational_task_route,
    validate_and_reroute_robot_path
)


@pytest.fixture
def phase4_admin_user(db: Session):
    user = db.query(User).filter(User.username == "phase4_admin").first()
    if not user:
        user = User(
            username="phase4_admin",
            password_hash=hash_password("AdminPass123!"),
            role="admin",
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@pytest.fixture
def phase4_staff_user(db: Session):
    user = db.query(User).filter(User.username == "phase4_staff").first()
    if not user:
        user = User(
            username="phase4_staff",
            password_hash=hash_password("StaffPass123!"),
            role="staff",
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@pytest.fixture
def admin_token_p4(client: TestClient, phase4_admin_user):
    res = client.post("/auth/login", json={"username": "phase4_admin", "password": "AdminPass123!"})
    assert res.status_code == 200
    return res.json()["access_token"]


@pytest.fixture
def staff_token_p4(client: TestClient, phase4_staff_user):
    res = client.post("/auth/login", json={"username": "phase4_staff", "password": "StaffPass123!"})
    assert res.status_code == 200
    return res.json()["access_token"]


@pytest.fixture
def setup_phase4_data(db: Session):
    # Setup Warehouse
    wh = db.query(Warehouse).filter(Warehouse.id == "WH-P4-01").first()
    if not wh:
        wh = Warehouse(id="WH-P4-01", name="Phase 4 Pathfinding Warehouse", location="Zone 4")
        db.add(wh)

    # Setup Product Item
    item = db.query(Item).filter(Item.id == "ITM-P4-01").first()
    if not item:
        item = Item(id="ITM-P4-01", name="Phase 4 Test Item", sku="SKU-P4-01", weight_kg=15.0)
        db.add(item)

    # Setup Locations
    loc_src = db.query(WarehouseLocation).filter(WarehouseLocation.id == "LOC-P4-SRC").first()
    if not loc_src:
        loc_src = WarehouseLocation(
            id="LOC-P4-SRC", warehouse_id="WH-P4-01", zone="A", aisle="01", rack="01", shelf="01",
            location_type="STORAGE", x=2.0, y=2.0
        )
        db.add(loc_src)

    loc_dst = db.query(WarehouseLocation).filter(WarehouseLocation.id == "LOC-P4-DST").first()
    if not loc_dst:
        loc_dst = WarehouseLocation(
            id="LOC-P4-DST", warehouse_id="WH-P4-01", zone="A", aisle="02", rack="01", shelf="01",
            location_type="PICKING", x=10.0, y=2.0
        )
        db.add(loc_dst)

    db.commit()

    # Populate 12x5 grid matrix for WH-P4-01
    initialize_warehouse_grid_if_empty(db, "WH-P4-01")

    # Robot
    rob = db.query(Robot).filter(Robot.robot_code == "ROB-P4-01").first()
    if not rob:
        rob = Robot(
            robot_code="ROB-P4-01", name="Phase 4 AGV", warehouse_id="WH-P4-01",
            status="AVAILABLE", battery_level=90.0, current_x=1.0, current_y=1.0, enabled=True, max_speed=1.5
        )
        db.add(rob)
    else:
        rob.current_x = 1.0
        rob.current_y = 1.0
        rob.assigned_task_id = None
        rob.status = "AVAILABLE"

    db.commit()
    return {
        "wh_id": "WH-P4-01",
        "item_id": "ITM-P4-01",
        "loc_src": "LOC-P4-SRC",
        "loc_dst": "LOC-P4-DST",
        "robot_code": "ROB-P4-01"
    }


# ---------------------------------------------------------------------------
# Test Scenario 1: A* Straight Line & Detour Pathfinding
# ---------------------------------------------------------------------------
def test_scenario_1_astar_straight_line_and_detour():
    grid = {
        (x, y): {"traversable": True, "cost": 1.0, "type": "FLOOR"}
        for x in range(1, 6) for y in range(1, 4)
    }

    # Straight line path
    path, cost, elapsed, msg, expanded = run_a_star((1, 1), (5, 1), grid)
    assert msg == "Success"
    assert path == [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1)]
    assert cost == 4.0

    # Introduce obstacle at (3, 1)
    grid[(3, 1)]["traversable"] = False
    path_detour, cost_detour, _, msg_detour, _ = run_a_star((1, 1), (5, 1), grid)
    assert msg_detour == "Success"
    assert (3, 1) not in path_detour
    assert path_detour[0] == (1, 1)
    assert path_detour[-1] == (5, 1)
    assert cost_detour > cost


# ---------------------------------------------------------------------------
# Test Scenario 2: Dijkstra Shortest Path Calculation
# ---------------------------------------------------------------------------
def test_scenario_2_dijkstra_shortest_path():
    grid = {
        (x, y): {"traversable": True, "cost": 1.0, "type": "FLOOR"}
        for x in range(1, 6) for y in range(1, 4)
    }

    path, cost, elapsed, msg, expanded = run_dijkstra((1, 1), (5, 1), grid)
    assert msg == "Success"
    assert path == [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1)]
    assert cost == 4.0


# ---------------------------------------------------------------------------
# Test Scenario 3: Preservation of Both Algorithms
# ---------------------------------------------------------------------------
def test_scenario_3_dual_algorithm_preservation(client: TestClient, admin_token_p4, setup_phase4_data):
    wh_id = setup_phase4_data["wh_id"]

    # Test A* API request
    res_a = client.post(
        "/pathfinding/plan",
        headers={"Authorization": f"Bearer {admin_token_p4}"},
        json={"warehouse_id": wh_id, "start_x": 1, "start_y": 1, "goal_x": 4, "goal_y": 1, "algorithm": "A_STAR"}
    )
    assert res_a.status_code == 200
    assert res_a.json()["algorithm"] == "A_STAR"
    assert res_a.json()["success"] is True

    # Test Dijkstra API request
    res_d = client.post(
        "/pathfinding/plan",
        headers={"Authorization": f"Bearer {admin_token_p4}"},
        json={"warehouse_id": wh_id, "start_x": 1, "start_y": 1, "goal_x": 4, "goal_y": 1, "algorithm": "DIJKSTRA"}
    )
    assert res_d.status_code == 200
    assert res_d.json()["algorithm"] == "DIJKSTRA"
    assert res_d.json()["success"] is True


# ---------------------------------------------------------------------------
# Test Scenario 4: Empirical Algorithm Comparison (COMPARE Mode)
# ---------------------------------------------------------------------------
def test_scenario_4_empirical_comparison(client: TestClient, admin_token_p4, setup_phase4_data):
    wh_id = setup_phase4_data["wh_id"]

    res = client.post(
        "/pathfinding/plan",
        headers={"Authorization": f"Bearer {admin_token_p4}"},
        json={"warehouse_id": wh_id, "start_x": 1, "start_y": 1, "goal_x": 10, "goal_y": 2, "algorithm": "COMPARE"}
    )
    assert res.status_code == 200
    body = res.json()
    assert body["algorithm"] == "COMPARE"
    assert body["success"] is True
    assert "a_star" in body and "dijkstra" in body

    a_star = body["a_star"]
    dijkstra = body["dijkstra"]

    assert a_star["success"] is True
    assert dijkstra["success"] is True
    assert a_star["cost"] == dijkstra["cost"]
    assert "planning_time" in a_star and "expanded_nodes" in a_star
    assert "planning_time" in dijkstra and "expanded_nodes" in dijkstra


# ---------------------------------------------------------------------------
# Test Scenario 5: Heuristic Admissibility & Optimal Path Agreement
# ---------------------------------------------------------------------------
def test_scenario_5_heuristic_admissibility_and_optimality():
    grid = {
        (x, y): {"traversable": True, "cost": 1.0, "type": "FLOOR"}
        for x in range(1, 8) for y in range(1, 5)
    }
    grid[(4, 1)]["cost"] = 5.0
    grid[(4, 2)]["cost"] = 5.0

    path_a, cost_a, _, _, _ = run_a_star((1, 1), (7, 1), grid)
    path_d, cost_d, _, _, _ = run_dijkstra((1, 1), (7, 1), grid)

    assert cost_a == cost_d
    assert len(path_a) == len(path_d)


# ---------------------------------------------------------------------------
# Test Scenario 6: Real Operational Context (Robot -> Pickup -> Destination)
# ---------------------------------------------------------------------------
def test_scenario_6_real_operational_context(db: Session, setup_phase4_data, phase4_admin_user):
    wh_id = setup_phase4_data["wh_id"]

    task = Task(
        task_number=f"TSK-P4-S6-{datetime.now(UTC).timestamp()}",
        warehouse_id=wh_id, task_type="PICK", status="ASSIGNED", requested_quantity=1,
        product_id=setup_phase4_data["item_id"], source_location_id=setup_phase4_data["loc_src"],
        destination_location_id=setup_phase4_data["loc_dst"], assigned_robot_id=setup_phase4_data["robot_code"]
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    route_res = get_operational_task_route(db, task.id, setup_phase4_data["robot_code"], "A_STAR")
    assert route_res["success"] is True
    assert route_res["task_id"] == task.id
    assert route_res["robot_code"] == setup_phase4_data["robot_code"]
    assert len(route_res["pickup_segment"]) > 0
    assert len(route_res["delivery_segment"]) > 0
    assert len(route_res["path"]) == len(route_res["pickup_segment"]) + len(route_res["delivery_segment"]) - 1


# ---------------------------------------------------------------------------
# Test Scenario 7: Obstacle Collision Prevention
# ---------------------------------------------------------------------------
def test_scenario_7_obstacle_collision_prevention():
    grid = {
        (x, y): {"traversable": True, "cost": 1.0, "type": "FLOOR"}
        for x in range(1, 5) for y in range(1, 5)
    }
    obstacles = {(2, 1), (2, 2)}

    path, cost, _, msg, _ = run_a_star((1, 1), (3, 1), grid, obstacles=obstacles)
    assert msg == "Success"
    for pt in path:
        assert pt not in obstacles


# ---------------------------------------------------------------------------
# Test Scenario 8: Unreachable Destination Handling
# ---------------------------------------------------------------------------
def test_scenario_8_unreachable_destination():
    grid = {
        (x, y): {"traversable": True, "cost": 1.0, "type": "FLOOR"}
        for x in range(1, 4) for y in range(1, 4)
    }
    # Completely encircle goal (3, 3)
    grid[(2, 3)]["traversable"] = False
    grid[(3, 2)]["traversable"] = False

    path, cost, elapsed, msg, expanded = run_a_star((1, 1), (3, 3), grid)
    assert path is None
    assert "No traversable route" in msg or "non-traversable" in msg


# ---------------------------------------------------------------------------
# Test Scenario 9: Start Equals Destination
# ---------------------------------------------------------------------------
def test_scenario_9_start_equals_destination():
    grid = {(1, 1): {"traversable": True, "cost": 1.0, "type": "FLOOR"}}

    path, cost, elapsed, msg, expanded = run_a_star((1, 1), (1, 1), grid)
    assert msg == "Success"
    assert path == [(1, 1)]
    assert cost == 0.0


# ---------------------------------------------------------------------------
# Test Scenario 10: Dynamic Obstacle Detection & Rerouting
# ---------------------------------------------------------------------------
def test_scenario_10_dynamic_rerouting(db: Session, setup_phase4_data):
    wh_id = setup_phase4_data["wh_id"]

    task = Task(
        task_number=f"TSK-P4-S10-{datetime.now(UTC).timestamp()}",
        warehouse_id=wh_id, task_type="PICK", status="ASSIGNED", requested_quantity=1,
        product_id=setup_phase4_data["item_id"], source_location_id=setup_phase4_data["loc_src"],
        destination_location_id=setup_phase4_data["loc_dst"], assigned_robot_id=setup_phase4_data["robot_code"]
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    rob = db.query(Robot).filter(Robot.robot_code == setup_phase4_data["robot_code"]).first()
    if rob:
        rob.assigned_task_id = task.id
        db.commit()

    # Compute initial route
    initial_res = get_operational_task_route(db, task.id, setup_phase4_data["robot_code"], "A_STAR")
    assert initial_res["success"] is True

    # Place an active obstacle at (5, 2) in middle aisle between pickup (2,2) and dest (10,2)
    obs = WarehouseObstacle(
        warehouse_id=wh_id, obstacle_type="TEMPORARY_BLOCK",
        x=5, y=2, width=1, height=1, active=True, severity="HIGH"
    )
    db.add(obs)
    db.commit()

    reroute_res = validate_and_reroute_robot_path(db, setup_phase4_data["robot_code"], "A_STAR")
    assert reroute_res["rerouted"] is True
    assert reroute_res["success"] is True


# ---------------------------------------------------------------------------
# Test Scenario 11: Path Continuity & Validation
# ---------------------------------------------------------------------------
def test_scenario_11_path_validation():
    grid = {
        (x, y): {"traversable": True, "cost": 1.0, "type": "FLOOR"}
        for x in range(1, 5) for y in range(1, 5)
    }

    # Continuous 1-step path
    valid_path = [(1, 1), (1, 2), (2, 2), (3, 2)]
    is_valid, msg = validate_path(valid_path, grid)
    assert is_valid is True

    # Discontinuous path jump (1,1) -> (3,3)
    invalid_path = [(1, 1), (3, 3)]
    is_invalid, msg_inv = validate_path(invalid_path, grid)
    assert is_invalid is False
    assert "jump" in msg_inv.lower() or "non-consecutive" in msg_inv.lower()


# ---------------------------------------------------------------------------
# Test Scenario 12: RBAC & Security Enforcement
# ---------------------------------------------------------------------------
def test_scenario_12_rbac_security(client: TestClient, setup_phase4_data, admin_token_p4, staff_token_p4):
    wh_id = setup_phase4_data["wh_id"]

    # Staff user attempting to create obstacle should receive 403 Forbidden
    res_staff = client.post(
        "/pathfinding/obstacles",
        headers={"Authorization": f"Bearer {staff_token_p4}"},
        json={"warehouse_id": wh_id, "obstacle_type": "WALL", "x": 2, "y": 2, "width": 1, "height": 1}
    )
    assert res_staff.status_code == 403

    # Admin user attempting to create obstacle should succeed (200 OK)
    res_admin = client.post(
        "/pathfinding/obstacles",
        headers={"Authorization": f"Bearer {admin_token_p4}"},
        json={"warehouse_id": wh_id, "obstacle_type": "WALL", "x": 2, "y": 2, "width": 1, "height": 1}
    )
    assert res_admin.status_code == 200
    assert res_admin.json()["status"] == "created"
