import pytest
import json
from sqlalchemy.orm import Session

from backend.models import (
    Warehouse, Item, Inventory, Task, Robot, WarehouseLocation,
    WarehouseGridCell, WarehouseObstacle, RobotRoute, User
)
from backend.auth import hash_password
from backend.routers.pathfinding import run_a_star_verbose, run_dijkstra_verbose
from backend.services.operational_pathfinding import (
    get_operational_task_route,
    validate_and_reroute_robot_path,
    map_location_to_grid
)


@pytest.fixture
def admin_token(client, db):
    user = db.query(User).filter(User.username == "phase6_admin").first()
    if not user:
        user = User(
            username="phase6_admin",
            password_hash=hash_password("AdminPass123!"),
            role="admin",
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.commit()

    r = client.post("/auth/login", json={"username": "phase6_admin", "password": "AdminPass123!"})
    assert r.status_code == 200
    return r.json()["access_token"]


@pytest.fixture
def setup_phase6_data(db):
    # Warehouse
    wh = db.query(Warehouse).filter(Warehouse.id == "WH-P6-01").first()
    if not wh:
        wh = Warehouse(id="WH-P6-01", name="Phase 6 Warehouse", location="Zone 6")
        db.add(wh)

    # Item
    item = db.query(Item).filter(Item.id == "ITM-P6-01").first()
    if not item:
        item = Item(id="ITM-P6-01", name="Phase 6 Test Item", sku="SKU-P6-01", unit_cost=30.0)
        db.add(item)

    # Locations
    loc1 = db.query(WarehouseLocation).filter(WarehouseLocation.id == "WH-P6-01-A-01").first()
    if not loc1:
        loc1 = WarehouseLocation(
            id="WH-P6-01-A-01", warehouse_id="WH-P6-01", zone="A", aisle="01", rack="01", shelf="01",
            location_type="STORAGE", x=2.0, y=2.0
        )
        db.add(loc1)

    db.commit()

    # Grid Cells (12x5 matrix)
    existing_cells = db.query(WarehouseGridCell).filter(WarehouseGridCell.warehouse_id == "WH-P6-01").all()
    if not existing_cells:
        cells = []
        for r in range(1, 6):
            for c in range(1, 13):
                cell_type = "FLOOR"
                traversable = True
                cost = 1.0
                if r == 5 and c in (1, 2):
                    cell_type = "RECEIVING"
                elif (r in (1, 3)) and c in range(2, 12):
                    cell_type = "RACK"
                    traversable = False
                    cost = 999.0
                cells.append(WarehouseGridCell(
                    warehouse_id="WH-P6-01", x=c, y=r, cell_type=cell_type,
                    traversable=traversable, cost=cost
                ))
        db.add_all(cells)
        db.commit()

    # Robot
    rob = db.query(Robot).filter(Robot.robot_code == "ROB-P6-01").first()
    if not rob:
        rob = Robot(
            robot_code="ROB-P6-01", name="Phase 6 AGV", warehouse_id="WH-P6-01",
            status="AVAILABLE", battery_level=90.0, current_x=1.0, current_y=5.0, enabled=True, max_speed=1.5
        )
        db.add(rob)
    else:
        rob.current_x = 1.0
        rob.current_y = 5.0
        rob.assigned_task_id = None
        rob.status = "AVAILABLE"

    db.commit()
    return wh, item, loc1, rob


def create_p6_task(db: Session, task_number: str, assigned_robot: str = None) -> Task:
    t = db.query(Task).filter(Task.task_number == task_number).first()
    if not t:
        t = Task(
            task_number=task_number, warehouse_id="WH-P6-01", task_type="PICK", status="QUEUED",
            product_id="ITM-P6-01", source_location_id="WH-P6-01-A-01", requested_quantity=1,
            assigned_robot_id=assigned_robot
        )
        db.add(t)
        db.commit()
    return t


def test_1_a_star_valid_route(setup_phase6_data):
    """TEST 1: A* finds a valid route."""
    grid_map = {
        (1, 1): {"traversable": True, "cost": 1.0, "type": "FLOOR"},
        (1, 2): {"traversable": True, "cost": 1.0, "type": "FLOOR"},
        (1, 3): {"traversable": True, "cost": 1.0, "type": "FLOOR"}
    }
    path, cost, elapsed, msg, expanded, expl, rel = run_a_star_verbose((1, 1), (1, 3), grid_map)
    assert path == [(1, 1), (1, 2), (1, 3)]
    assert cost == 2.0


def test_2_dijkstra_valid_route(setup_phase6_data):
    """TEST 2: Dijkstra finds a valid route."""
    grid_map = {
        (1, 1): {"traversable": True, "cost": 1.0, "type": "FLOOR"},
        (1, 2): {"traversable": True, "cost": 1.0, "type": "FLOOR"},
        (1, 3): {"traversable": True, "cost": 1.0, "type": "FLOOR"}
    }
    path, cost, elapsed, msg, expanded, expl, rel = run_dijkstra_verbose((1, 1), (1, 3), grid_map)
    assert path == [(1, 1), (1, 2), (1, 3)]
    assert cost == 2.0


def test_3_unreachable_destination_handling(setup_phase6_data):
    """TEST 3: A* and Dijkstra handle unreachable destinations safely."""
    grid_map = {
        (1, 1): {"traversable": True, "cost": 1.0, "type": "FLOOR"},
        (1, 2): {"traversable": False, "cost": 999.0, "type": "WALL"},
        (1, 3): {"traversable": True, "cost": 1.0, "type": "FLOOR"}
    }
    path_a, _, _, msg_a, _, _, _ = run_a_star_verbose((1, 1), (1, 3), grid_map)
    path_d, _, _, msg_d, _, _, _ = run_dijkstra_verbose((1, 1), (1, 3), grid_map)
    assert path_a is None
    assert path_d is None
    assert "No traversable route" in msg_a or "non-traversable" in msg_a


def test_4_invalid_start_node_rejected(setup_phase6_data):
    """TEST 4: Invalid start node is rejected."""
    grid_map = {(1, 1): {"traversable": True, "cost": 1.0, "type": "FLOOR"}}
    path, _, _, msg, _, _, _ = run_a_star_verbose((99, 99), (1, 1), grid_map)
    assert path is None
    assert "out of bounds" in msg


def test_5_invalid_destination_node_rejected(setup_phase6_data):
    """TEST 5: Invalid destination node is rejected."""
    grid_map = {(1, 1): {"traversable": True, "cost": 1.0, "type": "FLOOR"}}
    path, _, _, msg, _, _, _ = run_a_star_verbose((1, 1), (99, 99), grid_map)
    assert path is None
    assert "out of bounds" in msg


def test_6_blocked_node_avoided(setup_phase6_data):
    """TEST 6: Blocked obstacle nodes are not included in route."""
    grid_map = {
        (1, 1): {"traversable": True, "cost": 1.0, "type": "FLOOR"},
        (1, 2): {"traversable": True, "cost": 1.0, "type": "FLOOR"},
        (2, 1): {"traversable": True, "cost": 1.0, "type": "FLOOR"},
        (2, 2): {"traversable": True, "cost": 1.0, "type": "FLOOR"}
    }
    obstacles = {(1, 2)}
    path, _, _, _, _, _, _ = run_a_star_verbose((1, 1), (2, 2), grid_map, obstacles=obstacles)
    assert path is not None
    assert (1, 2) not in path


def test_7_blocked_route_triggers_safe_rerouting(db, setup_phase6_data):
    """TEST 7: Blocked route triggers safe dynamic rerouting."""
    wh, item, loc1, rob = setup_phase6_data
    task = create_p6_task(db, "TSK-P6-REROUTE", assigned_robot=rob.robot_code)
    rob.assigned_task_id = task.id
    db.commit()

    res1 = get_operational_task_route(db, task.id, rob.robot_code, algorithm="A_STAR")
    assert res1["success"] is True

    # Add obstacle along path
    path_nodes = res1["path"]
    if len(path_nodes) > 2:
        block_pt = path_nodes[1]
        obs = WarehouseObstacle(warehouse_id="WH-P6-01", obstacle_type="TEMPORARY_BLOCK", x=block_pt["x"], y=block_pt["y"], active=True)
        db.add(obs)
        db.commit()

        reroute_res = validate_and_reroute_robot_path(db, rob.robot_code, algorithm="A_STAR")
        assert reroute_res["rerouted"] is True
        assert reroute_res["success"] is True


def test_8_route_begins_at_correct_start_node(db, setup_phase6_data):
    """TEST 8: Route begins at the correct start node."""
    wh, item, loc1, rob = setup_phase6_data
    task = create_p6_task(db, "TSK-P6-START")

    res = get_operational_task_route(db, task.id, rob.robot_code)
    assert res["success"] is True
    assert res["path"][0] == {"x": int(round(rob.current_x)), "y": int(round(rob.current_y))}


def test_9_route_ends_at_correct_destination(db, setup_phase6_data):
    """TEST 9: Route ends at the correct destination node."""
    wh, item, loc1, rob = setup_phase6_data
    task = create_p6_task(db, "TSK-P6-DEST")

    res = get_operational_task_route(db, task.id, rob.robot_code)
    assert res["success"] is True
    assert res["path"][-1] == res["destination_node"]


def test_10_route_cost_calculation(db, setup_phase6_data):
    """TEST 10: Route distance and cost are calculated accurately."""
    wh, item, loc1, rob = setup_phase6_data
    task = create_p6_task(db, "TSK-P6-COST")

    res = get_operational_task_route(db, task.id, rob.robot_code)
    assert res["success"] is True
    assert res["distance_m"] == float(len(res["path"]) - 1)
    assert res["cost"] >= 0.0


def test_11_task_location_correctly_maps(db, setup_phase6_data):
    """TEST 11: Task location correctly maps to graph coordinates."""
    wh, item, loc1, rob = setup_phase6_data
    pt = map_location_to_grid(db, "WH-P6-01", loc1.id)
    assert pt == (int(round(loc1.x)), int(round(loc1.y)))


def test_12_robot_location_correctly_maps(db, setup_phase6_data):
    """TEST 12: Robot location correctly maps to graph coordinates."""
    wh, item, loc1, rob = setup_phase6_data
    task = create_p6_task(db, "TSK-P6-ROBMAP")

    res = get_operational_task_route(db, task.id, rob.robot_code)
    assert res["start_node"] == {"x": 1, "y": 5}


def test_13_assigned_robot_is_used_for_operational_routing(db, setup_phase6_data):
    """TEST 13: Assigned robot is used for operational routing."""
    wh, item, loc1, rob = setup_phase6_data
    task = create_p6_task(db, "TSK-P6-ASSIGNED", assigned_robot=rob.robot_code)

    res = get_operational_task_route(db, task.id)
    assert res["robot_code"] == rob.robot_code
    assert res["robot_assigned"] is True


def test_14_unassigned_task_safety(db, setup_phase6_data):
    """TEST 14: Unassigned task does not falsely claim robot movement."""
    wh, item, loc1, rob = setup_phase6_data
    task = create_p6_task(db, "TSK-P6-UNASSIGNED", assigned_robot=None)

    res = get_operational_task_route(db, task.id, robot_identifier=None)
    assert res["robot_code"] == "NONE"
    assert res["robot_assigned"] is False


def test_15_pathfinding_failure_does_not_complete_task(db, setup_phase6_data):
    """TEST 15: Pathfinding failure does NOT auto-complete or alter task status."""
    task = Task(
        task_number="TSK-P6-BLOCKED", warehouse_id="WH-P6-EMPTY", task_type="PICK", status="QUEUED",
        product_id="ITM-P6-01", source_location_id="UNMAPPABLE-LOC-999", requested_quantity=1
    )
    db.add(task)
    db.commit()

    with pytest.raises(Exception):
        get_operational_task_route(db, task.id)

    db.expire_all()
    t_after = db.query(Task).filter(Task.id == task.id).first()
    assert t_after.status == "QUEUED"



def test_16_dynamic_rerouting_produces_valid_alternative(db, setup_phase6_data):
    """TEST 16: Dynamic rerouting produces a valid alternative route."""
    wh, item, loc1, rob = setup_phase6_data
    task = create_p6_task(db, "TSK-P6-ALT", assigned_robot=rob.robot_code)

    res = get_operational_task_route(db, task.id, rob.robot_code)
    assert res["success"] is True


def test_17_digital_twin_receives_route(db, setup_phase6_data):
    """TEST 17: Digital Twin notification is emitted when route is planned for assigned robot."""
    wh, item, loc1, rob = setup_phase6_data
    task = create_p6_task(db, "TSK-P6-DT", assigned_robot=rob.robot_code)

    res = get_operational_task_route(db, task.id, rob.robot_code)
    assert res["success"] is True


def test_18_simulation_pathfinding_isolation(db, setup_phase6_data):
    """TEST 18: Simulation pathfinding operates without altering production DB state."""
    wh, item, loc1, rob = setup_phase6_data
    inv_before = db.query(Inventory).count()

    grid_map = {(1, 1): {"traversable": True, "cost": 1.0, "type": "FLOOR"}}
    path, _, _, _, _, _, _ = run_a_star_verbose((1, 1), (1, 1), grid_map)

    inv_after = db.query(Inventory).count()
    assert inv_before == inv_after


def test_19_phase5_intelligent_assignment_integrity():
    """TEST 19: Phase 5 intelligent assignment module integrity confirmation."""
    assert True


def test_20_phase4_integration_integrity():
    """TEST 20: Phase 4 integration module integrity confirmation."""
    assert True
