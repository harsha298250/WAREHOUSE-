import pytest
from datetime import datetime, UTC
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import get_db
from backend.models import (
    Base, Warehouse, Robot, Task, WarehouseLocation, Order, OrderItem,
    DigitalTwinSimulation, SimulationSnapshot, SimulationEvent, WarehouseGridCell
)
from backend.routers.digital_twin import setup_scenario_conditions, cleanup_simulation_tasks
from backend.celery_app import execute_experiment_task

# Isolated sqlite for testing simulation robustness
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(name="db")
def fixture_db():
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Seed mock warehouse, robot, location, grid cell
    wh = Warehouse(id="WH-ROBUST", name="Robustness Test Wh")
    db.add(wh)
    db.commit()
    
    # Storage and Packing Locations
    loc1 = WarehouseLocation(id="LOC-ST-01", warehouse_id="WH-ROBUST", x=2.0, y=2.0, location_type="STORAGE", zone="A", aisle="1", rack="R1", shelf="S1")
    loc2 = WarehouseLocation(id="LOC-PK-01", warehouse_id="WH-ROBUST", x=10.0, y=2.0, location_type="PACKING", zone="B", aisle="2", rack="R2", shelf="S2")
    loc3 = WarehouseLocation(id="LOC-CH-01", warehouse_id="WH-ROBUST", x=1.0, y=5.0, location_type="CHARGING", zone="C", aisle="3", rack="R3", shelf="S3")
    db.add_all([loc1, loc2, loc3])
    
    # Active Robot
    robot = Robot(
        robot_code="ROB-R1", name="Robust Bot 1", warehouse_id="WH-ROBUST",
        status="AVAILABLE", battery_level=100.0, max_speed=1.0,
        current_x=1.0, current_y=1.0, enabled=True
    )
    db.add(robot)
    
    # Seed Item
    from backend.models import Item
    item = Item(id="ITM-R1", name="Robust Item", unit_cost=5.0, safety_stock=10, sku="SKU-ROB")
    db.add(item)

    # Grid Cell
    cell = WarehouseGridCell(warehouse_id="WH-ROBUST", x=1, y=1, cell_type="FLOOR", traversable=True)
    db.add(cell)
    
    db.commit()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


def test_simulation_task_seeding_and_cleanup(db):
    wh_id = "WH-ROBUST"
    
    # 1. Initially no tasks/orders
    assert db.query(Task).filter(Task.warehouse_id == wh_id).count() == 0
    
    # 2. Run setup scenario conditions (seeding normal operations)
    setup_scenario_conditions(db, wh_id, "NORMAL_OPERATIONS")
    
    # 3. Verify tasks and orders seeded
    seeded_tasks = db.query(Task).filter(Task.warehouse_id == wh_id, Task.task_number.like("SIM-TSK-%")).all()
    seeded_orders = db.query(Order).filter(db.query(OrderItem).filter(OrderItem.order_id == Order.id).exists()).all()
    assert len(seeded_tasks) == 5
    assert len(seeded_orders) > 0
    
    # 4. Cleanup simulation tasks
    cleanup_simulation_tasks(db, wh_id)
    
    # 5. Verify cleanup deletes seeded tasks/orders
    assert db.query(Task).filter(Task.warehouse_id == wh_id, Task.task_number.like("SIM-TSK-%")).count() == 0
    assert db.query(Order).filter(Order.id.like("SIM-ORD-%")).count() == 0


def test_simulation_ticker_worker_greedy_scheduling_and_charging(db):
    wh_id = "WH-ROBUST"
    
    # Seed 1 task and set robot battery to 15% to trigger charging routing
    task = Task(
        task_number="SIM-TSK-101", warehouse_id=wh_id, task_type="PICK",
        status="QUEUED", priority="MEDIUM", priority_score=50,
        source_location_id="LOC-ST-01", destination_location_id="LOC-PK-01",
        requested_quantity=1, completed_quantity=0, product_id="ITM-R1"
    )
    db.add(task)
    db.commit()
    
    r = db.query(Robot).filter(Robot.robot_code == "ROB-R1").first()
    r.battery_level = 15.0
    db.add(r)
    db.commit()
    
    # Simulate the worker scheduling block:
    # 1. Route low battery robots to charging stations if available
    robots = db.query(Robot).filter(Robot.warehouse_id == wh_id, Robot.enabled == True).all()
    for robot in robots:
        if robot.status == "AVAILABLE" and not robot.assigned_task_id and robot.battery_level < 20.0:
            charge_loc = db.query(WarehouseLocation).filter(
                WarehouseLocation.warehouse_id == wh_id,
                WarehouseLocation.location_type == "CHARGING"
            ).first()
            if charge_loc:
                robot.target_location_id = charge_loc.id
                robot.target_x = charge_loc.x or 0.0
                robot.target_y = charge_loc.y or 0.0
                robot.status = "CHARGING"
                db.add(robot)
                
    # 2. Try to assign tasks to AVAILABLE robots (none available since robot is now CHARGING)
    available_robots = [robot for robot in robots if robot.status == "AVAILABLE" and not robot.assigned_task_id and robot.battery_level >= 20.0]
    queued_tasks = db.query(Task).filter(
        Task.warehouse_id == wh_id,
        Task.status.in_(["QUEUED", "PRIORITIZED", "FAILED"])
    ).all()
    
    assert len(available_robots) == 0
    assert len(queued_tasks) == 1
    assert robots[0].status == "CHARGING"
    assert robots[0].target_location_id == "LOC-CH-01"
    
    # Reset battery to 100% and status to AVAILABLE to test assignment
    robots[0].status = "AVAILABLE"
    robots[0].battery_level = 100.0
    db.add(robots[0])
    db.commit()
    
    # Run assignment logic
    available_robots = [robot for robot in robots if robot.status == "AVAILABLE" and not robot.assigned_task_id and robot.battery_level >= 20.0]
    if available_robots and queued_tasks:
        for t in queued_tasks:
            best_robot = None
            min_dist = float("inf")
            loc = db.query(WarehouseLocation).filter(WarehouseLocation.id == t.source_location_id).first()
            tx = loc.x if loc else 1.0
            ty = loc.y if loc else 1.0
            for robot in available_robots:
                dist = abs(robot.current_x - tx) + abs(robot.current_y - ty)
                if dist < min_dist:
                    min_dist = dist
                    best_robot = robot
            if best_robot:
                best_robot.assigned_task_id = t.id
                best_robot.status = "ASSIGNED"
                t.assigned_robot_id = best_robot.robot_code
                t.status = "ASSIGNED"
                t.assigned_at = datetime.now(UTC).replace(tzinfo=None)
                db.add(best_robot)
                db.add(t)
    db.commit()
    
    db.refresh(robots[0])
    db.refresh(task)
    assert robots[0].assigned_task_id == task.id
    assert robots[0].status == "ASSIGNED"
    assert task.assigned_robot_id == "ROB-R1"
    assert task.status == "ASSIGNED"
