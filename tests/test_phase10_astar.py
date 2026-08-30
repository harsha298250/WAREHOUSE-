import pytest
from backend.routers.pathfinding import run_a_star, validate_path


def test_astar_expanded_nodes_and_timing():
    """Verifies that run_a_star returns timing, path, status, and expanded nodes count."""
    grid = {
        (x, y): {"traversable": True, "cost": 1.0, "type": "FLOOR"}
        for x in range(1, 6) for y in range(1, 6)
    }
    path, cost, duration, msg, expanded = run_a_star((1, 1), (5, 5), grid)

    assert msg == "Success"
    assert len(path) == 9
    assert cost == 8.0
    assert duration > 0.0
    assert expanded > 0


def test_astar_blocked_goal():
    """Verifies that run_a_star returns appropriate error status on blocked goal."""
    grid = {
        (x, y): {"traversable": True, "cost": 1.0, "type": "FLOOR"}
        for x in range(1, 3) for y in range(1, 3)
    }
    grid[(2, 2)]["traversable"] = False

    path, cost, duration, msg, expanded = run_a_star((1, 1), (2, 2), grid)
    assert path is None
    assert "non-traversable" in msg


def test_astar_unreachable_goal():
    """Verifies that run_a_star returns No traversable route exists on fully blocked goals."""
    grid = {
        (x, y): {"traversable": True, "cost": 1.0, "type": "FLOOR"}
        for x in range(1, 4) for y in range(1, 4)
    }
    # Create wall in middle column
    grid[(2, 1)]["traversable"] = False
    grid[(2, 2)]["traversable"] = False
    grid[(2, 3)]["traversable"] = False

    path, cost, duration, msg, expanded = run_a_star((1, 1), (3, 3), grid)
    assert path is None
    assert "No traversable route" in msg


def test_astar_path_validation():
    """Verifies validate_path enforces adjacency, bounds, and obstacles."""
    grid = {
        (x, y): {"traversable": True, "cost": 1.0, "type": "FLOOR"}
        for x in range(1, 4) for y in range(1, 4)
    }

    # Valid consecutive path
    is_valid, msg = validate_path([(1, 1), (1, 2), (2, 2)], grid)
    assert is_valid
    assert msg == "Path is valid"

    # Non-consecutive jump
    is_valid, msg = validate_path([(1, 1), (3, 3)], grid)
    assert not is_valid
    assert "Non-consecutive" in msg

    # Out of bounds cell
    is_valid, msg = validate_path([(1, 1), (1, 5)], grid)
    assert not is_valid
    assert "out of bounds" in msg
