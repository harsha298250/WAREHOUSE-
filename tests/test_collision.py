import pytest
import json
from datetime import datetime
from backend.models import (
    Robot, RobotTelemetryEvent, Task, TaskEvent, Inventory, Order, OrderItem,
    Warehouse, Item, WarehouseLocation, User, RobotRoute, RobotReservation
)
from backend.routers.robots import execute_simulation_tick, WAIT_TICKS
from backend.auth import hash_password

def setup_collision_test_data(db):
    # Purge
    db.query(RobotTelemetryEvent).delete()
    db.query(RobotReservation).delete()
    db.query(RobotRoute).delete()
    db.query(Robot).delete()
    db.query(TaskEvent).delete()
    db.query(Task).delete()
    db.query(OrderItem).delete()
    db.query(Order).delete()
    db.query(Inventory).delete()
    db.query(WarehouseLocation).filter(WarehouseLocation.warehouse_id == "WH-COL-01").delete()
    db.query(Item).filter(Item.id == "ITM-COL-01").delete()
    db.query(Warehouse).filter(Warehouse.id == "WH-COL-01").delete()
    db.commit()

    wh = Warehouse(id="WH-COL-01", name="Collision Warehouse", location="Col Loc")
    db.add(wh)
    db.commit()

    # Create the item referenced by tasks
    item = Item(id="ITM-COL-01", name="Collision Test Item", unit_cost=10.0, safety_stock=5, reorder_threshold=10)
    db.add(item)
    db.commit()

    # Walkable locations
    loc1 = WarehouseLocation(id="LOC-COL-01", warehouse_id="WH-COL-01", zone="A", aisle="01", rack="01", shelf="01", location_type="PICKING", x=1.0, y=1.0)
    loc2 = WarehouseLocation(id="LOC-COL-02", warehouse_id="WH-COL-01", zone="A", aisle="01", rack="01", shelf="02", location_type="PICKING", x=3.0, y=1.0)
    db.add(loc1)
    db.add(loc2)
    db.commit()

def test_same_cell_conflict_resolution(db):
    setup_collision_test_data(db)
    
    # 1. Create two robots
    bot_a = Robot(robot_code="ROB-A", name="Robot A", warehouse_id="WH-COL-01", status="AVAILABLE", current_x=1.0, current_y=1.0, enabled=True, battery_level=100.0)
    bot_b = Robot(robot_code="ROB-B", name="Robot B", warehouse_id="WH-COL-01", status="AVAILABLE", current_x=3.0, current_y=1.0, enabled=True, battery_level=100.0)
    db.add(bot_a)
    db.add(bot_b)
    db.commit()

    # 2. Create tasks with different priority scores
    task_a = Task(
        task_number="TSK-A", warehouse_id="WH-COL-01", task_type="PICK", status="QUEUED",
        product_id="ITM-COL-01", source_location_id="LOC-COL-02", destination_location_id="LOC-COL-02",
        requested_quantity=1, priority_score=100
    )
    task_b = Task(
        task_number="TSK-B", warehouse_id="WH-COL-01", task_type="PICK", status="QUEUED",
        product_id="ITM-COL-01", source_location_id="LOC-COL-01", destination_location_id="LOC-COL-01",
        requested_quantity=1, priority_score=500  # Higher priority!
    )
    db.add(task_a)
    db.add(task_b)
    db.commit()

    # Assign tasks to transition state
    bot_a.assigned_task_id = task_a.id
    bot_a.status = "ASSIGNED"
    bot_b.assigned_task_id = task_b.id
    bot_b.status = "ASSIGNED"
    db.commit()

    # 3. Inject pre-computed active routes that want the same center cell (2, 1) on next step
    # ROB-A: (1, 1) -> (2, 1) -> (3, 1)
    route_a = RobotRoute(
        robot_id=bot_a.id, task_id=task_a.id, warehouse_id="WH-COL-01",
        start_x=1, start_y=1, goal_x=3, goal_y=1,
        path_data=json.dumps([[1, 1], [2, 1], [3, 1]]), status="ACTIVE"
    )
    # ROB-B: (3, 1) -> (2, 1) -> (1, 1)
    route_b = RobotRoute(
        robot_id=bot_b.id, task_id=task_b.id, warehouse_id="WH-COL-01",
        start_x=3, start_y=1, goal_x=1, goal_y=1,
        path_data=json.dumps([[3, 1], [2, 1], [1, 1]]), status="ACTIVE"
    )
    db.add(route_a)
    db.add(route_b)
    db.commit()

    # Clear wait ticks dictionary
    WAIT_TICKS.clear()

    # 4. Trigger simulation step
    execute_simulation_tick(db)
    
    db.refresh(bot_a)
    db.refresh(bot_b)

    # Robot B has higher priority (500 > 100), so it should proceed to (2, 1)
    # Robot A should wait (remain at (1, 1) and status should be WAITING)
    assert bot_b.current_x == 2.0
    assert bot_b.status == "MOVING"
    assert bot_a.current_x == 1.0
    assert bot_a.status == "WAITING"
    assert WAIT_TICKS[bot_a.id] == 1

def test_head_on_swap_conflict_resolution(db):
    setup_collision_test_data(db)

    bot_a = Robot(robot_code="ROB-C", name="Robot C", warehouse_id="WH-COL-01", status="AVAILABLE", current_x=1.0, current_y=1.0, enabled=True, battery_level=100.0)
    bot_b = Robot(robot_code="ROB-D", name="Robot D", warehouse_id="WH-COL-01", status="AVAILABLE", current_x=2.0, current_y=1.0, enabled=True, battery_level=100.0)
    db.add(bot_a)
    db.add(bot_b)
    db.commit()

    task_a = Task(
        task_number="TSK-C", warehouse_id="WH-COL-01", task_type="PICK", status="QUEUED",
        product_id="ITM-COL-01", source_location_id="LOC-COL-02", destination_location_id="LOC-COL-02",
        requested_quantity=1, priority_score=100
    )
    task_b = Task(
        task_number="TSK-D", warehouse_id="WH-COL-01", task_type="PICK", status="QUEUED",
        product_id="ITM-COL-01", source_location_id="LOC-COL-01", destination_location_id="LOC-COL-01",
        requested_quantity=1, priority_score=10  # ROB-C has higher priority (100 > 10)
    )
    db.add(task_a)
    db.add(task_b)
    db.commit()

    bot_a.assigned_task_id = task_a.id
    bot_a.status = "ASSIGNED"
    bot_b.assigned_task_id = task_b.id
    bot_b.status = "ASSIGNED"
    db.commit()

    # Head-on swap: ROB-C wants to go to (2, 1) from (1, 1). ROB-D wants to go to (1, 1) from (2, 1).
    route_c = RobotRoute(
        robot_id=bot_a.id, task_id=task_a.id, warehouse_id="WH-COL-01",
        start_x=1, start_y=1, goal_x=2, goal_y=1,
        path_data=json.dumps([[1, 1], [2, 1]]), status="ACTIVE"
    )
    route_d = RobotRoute(
        robot_id=bot_b.id, task_id=task_b.id, warehouse_id="WH-COL-01",
        start_x=2, start_y=1, goal_x=1, goal_y=1,
        path_data=json.dumps([[2, 1], [1, 1]]), status="ACTIVE"
    )
    db.add(route_c)
    db.add(route_d)
    db.commit()

    WAIT_TICKS.clear()

    execute_simulation_tick(db)

    db.refresh(bot_a)
    db.refresh(bot_b)

    # Robot C has higher priority (100 > 10), so it proceeds to (2, 1)
    # Robot D waits at (2, 1) -> Actually, Robot D remains at (2,1) and Robot C arrives at (2,1).
    # Since Robot C advances, it reaches (2, 1).
    assert bot_a.current_x == 2.0
    assert bot_b.current_x == 2.0
    assert bot_b.status == "WAITING"
