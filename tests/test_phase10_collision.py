import pytest
from sqlalchemy.orm import Session
from backend.models import Robot, Task, RobotRoute, Warehouse, WarehouseLocation, Item
from backend.routers.robots import execute_simulation_tick, WAIT_TICKS


def test_collision_waiting_and_deadlock_pausing(db: Session):
    """Verifies that conflicts lead to WAITING status, replanning at 3 ticks, and PAUSED status at 5 ticks."""
    # Reset waiting tracker
    WAIT_TICKS.clear()

    # Seed warehouse
    wh = Warehouse(id="WH-TEST-COL", name="Test Collision WH")
    db.add(wh)
    db.commit()

    # Seed items
    item = Item(id="ITM-COL", name="Collision Item", weight_kg=1.0)
    db.add(item)
    db.commit()

    # Seed location coordinates
    loc1 = WarehouseLocation(id="LOC-COL-1", warehouse_id="WH-TEST-COL", location_type="STORAGE", x=1.0, y=2.0, zone="A", aisle="01", rack="01", shelf="01")
    loc2 = WarehouseLocation(id="LOC-COL-2", warehouse_id="WH-TEST-COL", location_type="STORAGE", x=3.0, y=2.0, zone="A", aisle="01", rack="01", shelf="01")
    db.add_all([loc1, loc2])
    db.commit()

    # Two robots: ROB-A at (1, 2), ROB-B at (3, 2)
    r_a = Robot(robot_code="ROB-A", name="Rob A", warehouse_id="WH-TEST-COL", current_x=1.0, current_y=2.0, status="MOVING", enabled=True, battery_level=100.0)
    r_b = Robot(robot_code="ROB-B", name="Rob B", warehouse_id="WH-TEST-COL", current_x=3.0, current_y=2.0, status="MOVING", enabled=True, battery_level=100.0)
    db.add_all([r_a, r_b])
    db.commit()

    # Tasks
    t_a = Task(task_number="TSK-COL-A", warehouse_id="WH-TEST-COL", task_type="PICK", product_id="ITM-COL", source_location_id="LOC-COL-2", destination_location_id="LOC-COL-2", requested_quantity=1, status="IN_PROGRESS", priority_score=1000)
    t_b = Task(task_number="TSK-COL-B", warehouse_id="WH-TEST-COL", task_type="PICK", product_id="ITM-COL", source_location_id="LOC-COL-1", destination_location_id="LOC-COL-1", requested_quantity=1, status="IN_PROGRESS", priority_score=50) # Rob B has lower priority task
    db.add_all([t_a, t_b])
    db.commit()

    r_a.assigned_task_id = t_a.id
    r_b.assigned_task_id = t_b.id
    db.commit()

    # Setup routes that force head-on swap collision: (1,2) -> (2,2) -> (3,2) vs (3,2) -> (2,2) -> (1,2)
    route_a = RobotRoute(robot_id=r_a.id, task_id=t_a.id, warehouse_id="WH-TEST-COL", start_x=1, start_y=2, goal_x=3, goal_y=2, path_data="[[1,2], [2,2], [3,2]]", distance=2.0, cost=2.0, status="ACTIVE")
    route_b = RobotRoute(robot_id=r_b.id, task_id=t_b.id, warehouse_id="WH-TEST-COL", start_x=3, start_y=2, goal_x=1, goal_y=2, path_data="[[3,2], [2,2], [1,2]]", distance=2.0, cost=2.0, status="ACTIVE")
    db.add_all([route_a, route_b])
    db.commit()

    # Tick 1: ROB-A moves to (2,2). ROB-B (lower priority) detects conflict (vertex swap) and WAITS.
    execute_simulation_tick(db, routing_strategy="A_STAR")

    # Refresh
    db.refresh(r_a)
    db.refresh(r_b)

    assert r_a.current_x == 2.0  # ROB-A moved
    assert r_b.current_x == 3.0  # ROB-B waited
    assert r_b.status == "WAITING"
    assert WAIT_TICKS[r_b.id] == 1

    # Fake multiple ticks of conflict to trigger replan (3 ticks) and deadlock pause (5 ticks)
    # We set wait ticks directly to simulate continuous blocks
    WAIT_TICKS[r_b.id] = 2
    execute_simulation_tick(db, routing_strategy="A_STAR")
    db.refresh(r_b)
    # At tick 3, route_b gets marked REPLANNED
    assert route_b.status == "REPLANNED"

    # Let ROB-B replan a new route
    execute_simulation_tick(db, routing_strategy="A_STAR")
    db.refresh(r_b)

    # Force ROB-A to remain static at (2, 2)
    r_a_db = db.query(Robot).filter(Robot.robot_code == "ROB-A").first()
    r_a_db.current_x = 1.0
    r_a_db.current_y = 2.0
    r_a_db.status = "PAUSED"
    db.commit()

    # Set wait ticks to 5 to trigger corridor deadlock pause
    WAIT_TICKS[r_b.id] = 5
    execute_simulation_tick(db, routing_strategy="A_STAR")
    db.refresh(r_b)
    assert r_b.status == "PAUSED"
