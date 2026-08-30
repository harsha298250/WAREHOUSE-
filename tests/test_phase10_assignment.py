import pytest
from sqlalchemy.orm import Session
from backend.models import Robot, Task, Warehouse, WarehouseLocation, Item
from backend.routers.robots import auto_assign_task


def test_auto_assign_battery_and_payload_constraints(db: Session):
    """Verifies that robot is rejected from auto-assignment if battery is insufficient or payload is exceeded."""
    wh = Warehouse(id="WH-TEST-ASG", name="Test Assignment WH")
    db.add(wh)
    db.commit()

    # Seed Item with heavy weight
    item_heavy = Item(id="ITM-HEAVY", name="Heavy item", weight_kg=500.0)  # ROB-A has max_payload = 200.0
    item_light = Item(id="ITM-LIGHT", name="Light item", weight_kg=10.0)
    db.add_all([item_heavy, item_light])
    db.commit()

    # Coordinates
    loc_src = WarehouseLocation(id="LOC-ASG-SRC", warehouse_id="WH-TEST-ASG", location_type="STORAGE", x=1.0, y=1.0, zone="A", aisle="01", rack="01", shelf="01")
    loc_dest = WarehouseLocation(id="LOC-ASG-DST", warehouse_id="WH-TEST-ASG", location_type="STORAGE", x=5.0, y=1.0, zone="A", aisle="01", rack="01", shelf="01")
    db.add_all([loc_src, loc_dest])
    db.commit()

    # Robot: low battery
    r_low_bat = Robot(
        robot_code="ROB-LOW-BAT", name="Low Bat Rob", warehouse_id="WH-TEST-ASG",
        current_x=1.0, current_y=1.0, battery_level=5.0, max_payload=1000.0, enabled=True, status="AVAILABLE"
    )
    # Robot: normal battery but low payload capacity
    r_low_pay = Robot(
        robot_code="ROB-LOW-PAY", name="Low Pay Rob", warehouse_id="WH-TEST-ASG",
        current_x=1.0, current_y=1.0, battery_level=100.0, max_payload=100.0, enabled=True, status="AVAILABLE"
    )
    db.add_all([r_low_bat, r_low_pay])
    db.commit()

    # 1. Heavy Task: should be rejected by ROB-LOW-PAY (exceeds payload) and ROB-LOW-BAT (low battery)
    t_heavy = Task(
        task_number="TSK-ASG-H", warehouse_id="WH-TEST-ASG", task_type="PICK", product_id="ITM-HEAVY",
        source_location_id="LOC-ASG-SRC", destination_location_id="LOC-ASG-DST", requested_quantity=1, status="QUEUED", priority="CRITICAL"
    )
    db.add(t_heavy)
    db.commit()

    class SystemUser:
        id = 1
        username = "test_admin"
        role = "admin"

    user = SystemUser()

    res = auto_assign_task(warehouse_id="WH-TEST-ASG", db=db, user=user)
    assert res["status"] == "rejections_only"
    assert "Payload capacity exceeded" in res["candidates"][1]["reason"]

    # Cancel t_heavy so it doesn't block the queue
    t_heavy.status = "CANCELLED"
    db.commit()

    # 2. Light Task but long distance (needs battery return)
    t_light = Task(
        task_number="TSK-ASG-L", warehouse_id="WH-TEST-ASG", task_type="PICK", product_id="ITM-LIGHT",
        source_location_id="LOC-ASG-SRC", destination_location_id="LOC-ASG-DST", requested_quantity=1, status="QUEUED", priority="MEDIUM"
    )
    db.add(t_light)
    db.commit()

    res2 = auto_assign_task(warehouse_id="WH-TEST-ASG", db=db, user=user)
    assert res2["status"] == "success"
    assert res2["selected_robot"] == "ROB-LOW-PAY"  # It is selected because it satisfies battery and payload!
