import pytest
from backend.routers.pathfinding import run_a_star, initialize_warehouse_grid_if_empty
from backend.models import Warehouse, WarehouseGridCell, WarehouseObstacle
from backend.routers.robots import execute_simulation_tick

def test_a_star_basic_straight_line():
    # 3x3 simple walkable floor grid
    grid = {
        (x, y): {"traversable": True, "cost": 1.0, "type": "FLOOR"}
        for x in range(1, 4) for y in range(1, 4)
    }
    
    path, cost, elapsed, msg, expanded = run_a_star((1, 1), (3, 1), grid)
    assert msg == "Success"
    assert path == [(1, 1), (2, 1), (3, 1)]
    assert cost == 2.0

def test_a_star_simple_turn_around_obstacle():
    # 3x3 grid with center blocked
    grid = {
        (x, y): {"traversable": True, "cost": 1.0, "type": "FLOOR"}
        for x in range(1, 4) for y in range(1, 4)
    }
    grid[(2, 2)]["traversable"] = False # Block center
    
    # Path from (1, 2) to (3, 2) around (2, 2)
    path, cost, elapsed, msg, expanded = run_a_star((1, 2), (3, 2), grid)
    assert msg == "Success"
    # Should take detour: (1,2) -> (1,1) -> (2,1) -> (3,1) -> (3,2) or via row 3
    assert len(path) == 5
    assert cost == 4.0

def test_a_star_dynamic_obstacle_avoidance():
    # Grid where direct route has high cost (congested)
    grid = {
        (x, y): {"traversable": True, "cost": 1.0, "type": "FLOOR"}
        for x in range(1, 4) for y in range(1, 3)
    }
    
    # Congest cell (2, 1) to cost 5.0
    grid[(2, 1)]["cost"] = 5.0
    
    # Path from (1, 1) to (3, 1)
    # Detour path via row 2: (1,1) -> (1,2) -> (2,2) -> (3,2) -> (3,1) (cost = 1 + 1 + 1 + 1 = 4.0)
    # Direct path: (1,1) -> (2,1) -> (3,1) (cost = 5.0 + 1.0 = 6.0)
    path, cost, elapsed, msg, expanded = run_a_star((1, 1), (3, 1), grid)
    assert msg == "Success"
    assert path == [(1, 1), (1, 2), (2, 2), (3, 2), (3, 1)]
    assert cost == 4.0

def test_a_star_no_path_scenarios():
    grid = {
        (x, y): {"traversable": True, "cost": 1.0, "type": "FLOOR"}
        for x in range(1, 4) for y in range(1, 4)
    }
    # Fully block center column
    grid[(2, 1)]["traversable"] = False
    grid[(2, 2)]["traversable"] = False
    grid[(2, 3)]["traversable"] = False

    path, cost, elapsed, msg, expanded = run_a_star((1, 2), (3, 2), grid)
    assert path is None
    assert "No traversable route" in msg

def test_a_star_blocked_start_or_goal():
    grid = {
        (x, y): {"traversable": True, "cost": 1.0, "type": "FLOOR"}
        for x in range(1, 3) for y in range(1, 3)
    }
    grid[(1, 1)]["traversable"] = False

    path, cost, elapsed, msg, expanded = run_a_star((1, 1), (2, 2), grid)
    assert path is None
    assert "non-traversable" in msg
