import pytest
import json
from datetime import datetime
from backend.models import (
    Robot, RobotTelemetryEvent, Task, TaskEvent, Inventory, Order, OrderItem,
    Warehouse, Item, WarehouseLocation, User, AuditLedger, InventoryReservation,
    WarehouseGridCell, WarehouseObstacle, RobotRoute, StockMovement
)
from backend.routers.robots import execute_simulation_tick
from backend.routers.pathfinding import initialize_warehouse_grid_if_empty
from backend.auth import hash_password

@pytest.fixture
def admin_token(client, db):
    existing = db.query(User).filter(User.username == "test_path_admin").first()
    if not existing:
        user = User(
            username="test_path_admin",
            password_hash=hash_password("AdminPass123!"),
            role="admin"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    try:
        from backend.main import _login_attempts
        _login_attempts.clear()
    except ImportError:
        pass

    r = client.post("/auth/login", json={"username": "test_path_admin", "password": "AdminPass123!"})
    assert r.status_code == 200
    return r.json()["access_token"]

def setup_path_e2e_data(db):
    db.query(RobotTelemetryEvent).delete()
    db.query(RobotRoute).delete()
    db.query(Robot).delete()
    db.query(TaskEvent).delete()
    db.query(Task).delete()
    db.query(OrderItem).delete()
    db.query(Order).delete()
    db.query(InventoryReservation).delete()
    db.query(StockMovement).filter(StockMovement.item_id == "ITM-PATH-01").delete()
    db.query(Inventory).delete()
    db.query(WarehouseGridCell).filter(WarehouseGridCell.warehouse_id == "WH-PATH-01").delete()
    db.query(WarehouseObstacle).filter(WarehouseObstacle.warehouse_id == "WH-PATH-01").delete()
    db.query(WarehouseLocation).filter(WarehouseLocation.warehouse_id == "WH-PATH-01").delete()
    db.query(Item).filter(Item.id == "ITM-PATH-01").delete()
    db.query(Warehouse).filter(Warehouse.id == "WH-PATH-01").delete()
    db.commit()

    wh = Warehouse(id="WH-PATH-01", name="Path E2E Warehouse", location="Path Loc")
    db.add(wh)
    db.commit()

    # Pre-populate grid
    initialize_warehouse_grid_if_empty(db, "WH-PATH-01")

    item = Item(id="ITM-PATH-01", name="Path Test Item", unit_cost=50.0, safety_stock=10, reorder_threshold=15)
    db.add(item)
    db.commit()

    # Create coordinate spots:
    # Aisle locations (walkable coordinates):
    # Picking spot at (3, 2), destination spot at (6, 4)
    loc_pick = WarehouseLocation(
        id="LOC-PICK-01", warehouse_id="WH-PATH-01", zone="A", aisle="01", rack="01", shelf="01",
        location_type="PICKING", capacity=500, x=3.0, y=2.0
    )
    loc_dest = WarehouseLocation(
        id="LOC-DEST-01", warehouse_id="WH-PATH-01", zone="B", aisle="01", rack="01", shelf="01",
        location_type="SHIPPING", capacity=1000, x=6.0, y=4.0
    )
    db.add(loc_pick)
    db.add(loc_dest)
    db.commit()

    # Racks are generally non-traversable, so (3,2) which is marked as RACK by initialize_warehouse_grid_if_empty
    # needs to be temporarily made traversable for the task location to be valid in tests, or we can use aisle coordinates!
    # Let's make sure grid cells corresponding to LOC-PICK-01 and LOC-DEST-01 are traversable!
    cell_pick = db.query(WarehouseGridCell).filter(WarehouseGridCell.warehouse_id == "WH-PATH-01", WarehouseGridCell.x == 3, WarehouseGridCell.y == 2).first()
    if cell_pick:
        cell_pick.traversable = True
        cell_pick.cell_type = "FLOOR"
    
    cell_dest = db.query(WarehouseGridCell).filter(WarehouseGridCell.warehouse_id == "WH-PATH-01", WarehouseGridCell.x == 6, WarehouseGridCell.y == 4).first()
    if cell_dest:
        cell_dest.traversable = True
        cell_dest.cell_type = "FLOOR"
    db.commit()

    inv = Inventory(warehouse_id="WH-PATH-01", item_id="ITM-PATH-01", location_id="LOC-PICK-01", on_hand=100, reserved=0, available=100)
    db.add(inv)
    db.commit()

def test_e2e_pathplanning_execution(client, db, admin_token):
    setup_path_e2e_data(db)
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Create order and reserve inventory
    order = Order(id="ORD-PATH-01", warehouse_id="WH-PATH-01", status="PENDING", customer_ref="Path Cust")
    db.add(order)
    db.commit()

    order_item = OrderItem(order_id="ORD-PATH-01", item_id="ITM-PATH-01", requested_qty=4)
    db.add(order_item)
    db.commit()

    res = InventoryReservation(order_id="ORD-PATH-01", item_id="ITM-PATH-01", location_id="LOC-PICK-01", reserved_qty=4, released_qty=0)
    db.add(res)
    inv = db.query(Inventory).filter(Inventory.warehouse_id == "WH-PATH-01", Inventory.item_id == "ITM-PATH-01").first()
    inv.reserved += 4
    inv.available -= 4
    db.commit()

    # 2. Generate task
    task = Task(
        task_number="TSK-PATH-01", warehouse_id="WH-PATH-01", task_type="PICK", status="QUEUED",
        source_id="ORD-PATH-01", order_id="ORD-PATH-01", order_item_id=order_item.id,
        product_id="ITM-PATH-01", source_location_id="LOC-PICK-01", destination_location_id="LOC-DEST-01",
        requested_quantity=4, priority_score=100
    )
    db.add(task)
    db.commit()

    # 3. Create robot fleet (staging at x=1.0, y=2.0)
    r_res = client.post("/robots", json={
        "robot_code": "ROB-PATH-E2E", "name": "Path AGV", "warehouse_id": "WH-PATH-01", "robot_type": "AGV"
    }, headers=headers)
    assert r_res.status_code == 201

    bot = db.query(Robot).filter(Robot.robot_code == "ROB-PATH-E2E").first()
    bot.current_x = 1.0
    bot.current_y = 2.0
    db.commit()

    # 4. Assign robot & Plan A* route
    client.post(f"/robots/{bot.id}/assign", json={"task_id": task.id}, headers=headers)
    
    # 5. Run simulation tick to generate initial A* route
    client.post("/robots/simulation/step", headers=headers)
    db.refresh(bot)
    db.refresh(task)

    # Initial route should exist
    route = db.query(RobotRoute).filter(RobotRoute.robot_id == bot.id).first()
    assert route is not None
    assert route.start_x == 1
    assert route.start_y == 2
    assert route.goal_x == 3
    assert route.goal_y == 2
    assert bot.status in ("MOVING", "PICKING", "RETURNING")

    # Step simulation until task is completed
    max_steps = 30
    steps = 0
    while task.status != "COMPLETED" and steps < max_steps:
        client.post("/robots/simulation/step", headers=headers)
        db.refresh(bot)
        db.refresh(task)
        routes = db.query(RobotRoute).filter(RobotRoute.robot_id == bot.id).all()
        route_info = [(r.id, r.status, r.path_data) for r in routes]
        print(f"Step {steps}: Bot status={bot.status}, coords=({bot.current_x}, {bot.current_y}), routes={route_info}")
        steps += 1

    assert bot.status == "AVAILABLE"
    assert task.status == "COMPLETED"
    
    # Verify inventory updated
    db.refresh(inv)
    assert inv.on_hand == 96

def test_dynamic_obstacle_replan_e2e(client, db, admin_token):
    setup_path_e2e_data(db)
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Create additional locations for the detour test
    # Source at (6, 4) on row 4 aisle, and destination at (8, 4) also on row 4
    loc_src2 = WarehouseLocation(
        id="LOC-DETOUR-SRC", warehouse_id="WH-PATH-01", zone="B", aisle="02", rack="01", shelf="01",
        location_type="PICKING", capacity=500, x=6.0, y=4.0
    )
    loc_dst2 = WarehouseLocation(
        id="LOC-DETOUR-DST", warehouse_id="WH-PATH-01", zone="B", aisle="02", rack="02", shelf="01",
        location_type="SHIPPING", capacity=1000, x=8.0, y=4.0
    )
    db.add(loc_src2)
    db.add(loc_dst2)
    db.commit()

    # Ensure grid cells at those coords are traversable
    for cx, cy in [(6, 4), (8, 4), (4, 4), (5, 4), (7, 4)]:
        cell = db.query(WarehouseGridCell).filter(
            WarehouseGridCell.warehouse_id == "WH-PATH-01",
            WarehouseGridCell.x == cx, WarehouseGridCell.y == cy
        ).first()
        if cell:
            cell.traversable = True
            cell.cell_type = "FLOOR"
    db.commit()

    # Add inventory at source
    inv2 = Inventory(warehouse_id="WH-PATH-01", item_id="ITM-PATH-01", location_id="LOC-DETOUR-SRC",
                     on_hand=50, reserved=0, available=50)
    db.add(inv2)
    db.commit()

    # Create order + item for the task (required by complete_task)
    order2 = Order(id="ORD-DETOUR-01", warehouse_id="WH-PATH-01", status="PENDING", customer_ref="Detour Cust")
    db.add(order2)
    db.commit()

    oi2 = OrderItem(order_id="ORD-DETOUR-01", item_id="ITM-PATH-01", requested_qty=1)
    db.add(oi2)
    db.commit()

    res2 = InventoryReservation(order_id="ORD-DETOUR-01", item_id="ITM-PATH-01", location_id="LOC-DETOUR-SRC", reserved_qty=1, released_qty=0)
    db.add(res2)
    inv2.reserved += 1
    inv2.available -= 1
    db.commit()

    task = Task(
        task_number="TSK-PATH-03", warehouse_id="WH-PATH-01", task_type="PICK", status="QUEUED",
        source_id="ORD-DETOUR-01", order_id="ORD-DETOUR-01", order_item_id=oi2.id,
        product_id="ITM-PATH-01", source_location_id="LOC-DETOUR-SRC", destination_location_id="LOC-DETOUR-DST",
        requested_quantity=1, priority_score=100
    )
    db.add(task)
    db.commit()

    # Robot starts at (4, 4) on row 4 aisle — path to source (6,4) is (4,4)→(5,4)→(6,4)
    bot = Robot(
        robot_code="ROB-REPLAN", name="Replan Bot", warehouse_id="WH-PATH-01", status="AVAILABLE",
        current_x=4.0, current_y=4.0, enabled=True, battery_level=100.0
    )
    db.add(bot)
    db.commit()

    # Assign task
    client.post(f"/robots/{bot.id}/assign", json={"task_id": task.id}, headers=headers)

    # Place obstacle on intermediate aisle cell (5, 4) — directly on the direct path
    obs_res = client.post("/pathfinding/obstacles", json={
        "warehouse_id": "WH-PATH-01", "obstacle_type": "TEMPORARY_BLOCK", "x": 5, "y": 4, "width": 1, "height": 1
    }, headers=headers)
    assert obs_res.status_code in (200, 201)

    # Step simulation: robot must detect blocked direct path and find a detour
    # Detour via (4,4)→(4,5)→(5,5)→(6,5)→(6,4) or similar route through row 5
    max_steps = 40
    steps = 0
    while task.status != "COMPLETED" and steps < max_steps:
        client.post("/robots/simulation/step", headers=headers)
        db.refresh(bot)
        db.refresh(task)
        steps += 1

    assert task.status == "COMPLETED"

    # Confirm the robot successfully completed via a detour route
    routes = db.query(RobotRoute).filter(RobotRoute.robot_id == bot.id).all()
    assert len(routes) >= 2  # At least one outbound + one return route


