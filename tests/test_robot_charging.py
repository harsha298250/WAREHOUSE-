"""
test_robot_charging.py — Phase 11: Production Verification of AGV Charging & Deterministic Queue Manager
"""

import pytest
from datetime import datetime, UTC
from backend.models import Warehouse, Robot, WarehouseLocation, Task, DigitalTwinSimulation
from backend.charging_manager import evaluate_warehouse_charging_system, get_warehouse_charging_queue_info

@pytest.fixture
def setup_charging_warehouse(db):
    """Fixture providing a clean test warehouse with 2 charging ports and 6 test robots."""
    wh_id = "WH-CHG-TEST"
    
    # Clean old data if any
    db.query(Robot).filter(Robot.warehouse_id == wh_id).delete()
    db.query(WarehouseLocation).filter(WarehouseLocation.warehouse_id == wh_id).delete()
    db.query(Warehouse).filter(Warehouse.id == wh_id).delete()
    db.commit()

    # Create warehouse
    wh = Warehouse(id=wh_id, name="Charging Test Facility", city="Test City")
    db.add(wh)
    db.commit()

    # Create 2 charging ports at (11, 5) and (12, 5)
    p1 = WarehouseLocation(id=f"{wh_id}-CP-1", warehouse_id=wh_id, zone="CHARGING", aisle="C-1", rack="CR-1", shelf="CS-1", x=11.0, y=5.0, location_type="CHARGING")
    p2 = WarehouseLocation(id=f"{wh_id}-CP-2", warehouse_id=wh_id, zone="CHARGING", aisle="C-1", rack="CR-2", shelf="CS-1", x=12.0, y=5.0, location_type="CHARGING")
    db.add_all([p1, p2])
    db.commit()

    # Create 6 robots with varying battery levels
    # RB-01 (30%), RB-02 (8%), RB-03 (18%), RB-04 (12%), RB-05 (25%), RB-06 (5%)
    robots_data = [
        ("RB-T-01", 30.0, 1.0, 1.0),
        ("RB-T-02", 8.0, 2.0, 1.0),
        ("RB-T-03", 18.0, 3.0, 1.0),
        ("RB-T-04", 12.0, 4.0, 1.0),
        ("RB-T-05", 25.0, 5.0, 1.0),
        ("RB-T-06", 5.0, 6.0, 1.0),
    ]

    robots = []
    for code, bat, x, y in robots_data:
        r = Robot(
            robot_code=code,
            name=f"Robot {code}",
            warehouse_id=wh_id,
            status="AVAILABLE",
            battery_level=bat,
            current_x=x,
            current_y=y,
            enabled=True
        )
        db.add(r)
        robots.append(r)

    db.commit()
    return wh_id, [p1.id, p2.id], [r.robot_code for r in robots]


def test_lowest_battery_priority_and_capacity_bound(db, setup_charging_warehouse):
    """Verifies that only 2 robots get charging ports, and they are the LOWEST BATTERY robots (RB-T-06 @ 5%, RB-T-02 @ 8%)."""
    wh_id, ports, robot_codes = setup_charging_warehouse

    # Evaluate charging system with low_battery_threshold = 20.0%
    evaluate_warehouse_charging_system(db, wh_id, low_battery_threshold=20.0)

    # Fetch updated queue info
    info = get_warehouse_charging_queue_info(db, wh_id)

    assert info["total_ports"] == 2
    assert info["occupied_ports"] == 2
    assert info["available_ports"] == 0

    # The 2 robots receiving ports MUST be RB-T-06 (5%) and RB-T-02 (8%)
    charging_robots = db.query(Robot).filter(
        Robot.warehouse_id == wh_id,
        Robot.status == "CHARGING"
    ).all()

    assigned_codes = {r.robot_code for r in charging_robots}
    assert assigned_codes == {"RB-T-06", "RB-T-02"}, f"Expected RB-T-06 and RB-T-02 to get ports, got {assigned_codes}"

    # Verify waiting queue contains RB-T-04 (12%) at position #1 and RB-T-03 (18%) at position #2
    waiting_queue = info["waiting_queue"]
    assert len(waiting_queue) == 2, f"Expected 2 waiting robots, got {len(waiting_queue)}"
    assert waiting_queue[0]["robot_code"] == "RB-T-04"  # 12% battery
    assert waiting_queue[1]["robot_code"] == "RB-T-03"  # 18% battery


def test_queue_promotion_after_charging_completion(db, setup_charging_warehouse):
    """Verifies that when one robot completes charging (100%), its port is freed and immediately given to the next lowest-battery waiting robot."""
    wh_id, ports, robot_codes = setup_charging_warehouse

    # Initial evaluation
    evaluate_warehouse_charging_system(db, wh_id, low_battery_threshold=20.0)

    # Set RB-T-06's battery to 99.0% at port 1 location (11, 5)
    r6 = db.query(Robot).filter(Robot.robot_code == "RB-T-06").first()
    r6.current_x = 11.0
    r6.current_y = 5.0
    r6.battery_level = 99.0
    db.add(r6)
    db.commit()

    # Next tick: R6 reaches 100% -> freed -> next lowest (RB-T-04 @ 12%) gets port!
    evaluate_warehouse_charging_system(db, wh_id, low_battery_threshold=20.0, charge_rate_per_tick=5.0)

    r6_after = db.query(Robot).filter(Robot.robot_code == "RB-T-06").first()
    assert r6_after.status == "AVAILABLE"
    assert r6_after.battery_level == 100.0

    r4_after = db.query(Robot).filter(Robot.robot_code == "RB-T-04").first()
    assert r4_after.status == "CHARGING"


def test_charger_release_on_robot_failure(db, setup_charging_warehouse):
    """Verifies that if a charging robot fails, its charger reservation is released and assigned to the waiting queue."""
    wh_id, ports, robot_codes = setup_charging_warehouse

    evaluate_warehouse_charging_system(db, wh_id, low_battery_threshold=20.0)

    # Mark RB-T-02 as FAILED
    r2 = db.query(Robot).filter(Robot.robot_code == "RB-T-02").first()
    r2.status = "FAILED"
    r2.target_location_id = None
    db.add(r2)
    db.commit()

    # Re-evaluate charging
    evaluate_warehouse_charging_system(db, wh_id, low_battery_threshold=20.0)

    # RB-T-04 (12%) should now be promoted to CHARGING
    r4 = db.query(Robot).filter(Robot.robot_code == "RB-T-04").first()
    assert r4.status == "CHARGING"


def test_multi_warehouse_charging_isolation(db, setup_charging_warehouse):
    """Verifies that charging ports and queues are 100% isolated between warehouses."""
    wh1_id, ports1, codes1 = setup_charging_warehouse

    # Create Warehouse 2
    wh2_id = "WH-CHG-ISO-2"
    wh2 = Warehouse(id=wh2_id, name="Isolated Warehouse", city="Iso City")
    db.add(wh2)
    p_iso = WarehouseLocation(id=f"{wh2_id}-CP-1", warehouse_id=wh2_id, zone="CHARGING", aisle="C-1", rack="CR-1", shelf="CS-1", x=11.0, y=5.0, location_type="CHARGING")
    db.add(p_iso)

    r_iso = Robot(robot_code="RB-ISO-01", name="Iso Robot", warehouse_id=wh2_id, status="AVAILABLE", battery_level=10.0, current_x=1.0, current_y=1.0, enabled=True)
    db.add(r_iso)
    db.commit()

    # Evaluate WH1 and WH2
    evaluate_warehouse_charging_system(db, wh1_id, low_battery_threshold=20.0)
    evaluate_warehouse_charging_system(db, wh2_id, low_battery_threshold=20.0)

    info1 = get_warehouse_charging_queue_info(db, wh1_id)
    info2 = get_warehouse_charging_queue_info(db, wh2_id)

    assert info1["warehouse_id"] == wh1_id
    assert info2["warehouse_id"] == wh2_id
    assert info2["total_ports"] == 1
    assert info2["occupied_ports"] == 1
    assert info2["ports"][0]["robot_code"] == "RB-ISO-01"
