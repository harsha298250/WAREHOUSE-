import pytest
from sqlalchemy.orm import Session
from backend.models import Robot, Task, Warehouse, WarehouseLocation, Item
from backend.routers.or_tools_scheduler import (
    benchmark_ortools_assignment, optimize_and_assign_tasks, optimize_single_task
)


def test_ortools_batch_and_single_optimization(db: Session):
    """Verifies OR-Tools CP-SAT scheduler optimization endpoints and constraint validation."""
    wh = Warehouse(id="WH-TEST-ORT", name="Test ORTools WH")
    db.add(wh)
    db.commit()

    item = Item(id="ITM-ORT", name="ORT Item", weight_kg=5.0)
    db.add(item)
    db.commit()

    loc_src = WarehouseLocation(id="LOC-ORT-SRC", warehouse_id="WH-TEST-ORT", x=1.0, y=1.0, zone="A", aisle="01", rack="01", shelf="01")
    loc_dst = WarehouseLocation(id="LOC-ORT-DST", warehouse_id="WH-TEST-ORT", x=3.0, y=1.0, zone="A", aisle="01", rack="01", shelf="01")
    db.add_all([loc_src, loc_dst])
    db.commit()

    # Robot available
    robot = Robot(
        robot_code="ROB-ORT-A", name="Rob ORT A", warehouse_id="WH-TEST-ORT",
        current_x=1.0, current_y=1.0, battery_level=100.0, max_payload=200.0, enabled=True, status="AVAILABLE"
    )
    db.add(robot)
    db.commit()

    # Task pending
    task = Task(
        task_number="TSK-ORT-1", warehouse_id="WH-TEST-ORT", task_type="PICK", product_id="ITM-ORT",
        source_location_id="LOC-ORT-SRC", destination_location_id="LOC-ORT-DST", requested_quantity=2, status="QUEUED", priority="MEDIUM"
    )
    db.add(task)
    db.commit()

    class SystemUser:
        id = 1
        username = "test_admin"
        role = "admin"

    user = SystemUser()

    # 1. Single Task Optimization assignment
    res_single = optimize_single_task(task_id=task.id, db=db, user=user)
    assert res_single["status"] == "success"
    assert res_single["assigned_robot"] == "ROB-ORT-A"

    # Reset assignment to test batch optimize
    robot_db = db.query(Robot).filter(Robot.robot_code == "ROB-ORT-A").first()
    task_db = db.query(Task).filter(Task.task_number == "TSK-ORT-1").first()
    robot_db.assigned_task_id = None
    robot_db.status = "AVAILABLE"
    task_db.status = "QUEUED"
    task_db.assigned_robot_id = None
    db.commit()

    # 2. Batch Optimization assignment
    res_batch = optimize_and_assign_tasks(warehouse_id="WH-TEST-ORT", db=db, user=user)
    print("BATCH RESULT IS:", res_batch)
    assert res_batch["status"] == "success"
    assert res_batch["assigned_count"] == 1
    assert res_batch["assignments"][0]["robot_code"] == "ROB-ORT-A"
