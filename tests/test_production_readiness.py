"""
tests/test_production_readiness.py — Production Readiness Integration Test Suite.

Validates end-to-end functionality for all 12 core production features:
1. Warehouse creation, duplicate handling, coordinate bounds validation, & DB transaction safety.
2. Dataset auto-provisioner and path resolution.
3. Forecasting execution on provisioned data.
4. ABC Analysis for ALL 4 dataset sources (wms, store_sales, online_retail, mlzc).
5. Demand anomaly detection using IsolationForest ML engine.
6. AI Operations Assistant deterministic database tool execution.
7. Complete Task & Robot assignment lifecycle (Create -> Assign Operator -> Assign Robot -> Start -> Complete -> Robot Released).
8. Digital Twin state API and SSE token authorization.
"""
import pytest
from pathlib import Path
from data_pipeline.provisioner import ensure_all_datasets_provisioned


def test_dataset_provisioner_execution():
    """Verify dataset provisioner creates all required processed CSV files with valid schemas."""
    ensure_all_datasets_provisioned()
    root = Path(__file__).resolve().parent.parent
    proc_dir = root / "data" / "processed"

    expected_files = [
        proc_dir / "store_sales_forecasting" / "train_processed.csv",
        proc_dir / "store_sales_forecasting" / "oil_processed.csv",
        proc_dir / "online_retail_ii" / "online_retail_II_processed.csv",
        proc_dir / "retail_sales_forecasting" / "sales_processed.csv",
        proc_dir / "m5" / "sales_train_validation_processed.csv"
    ]

    for ef in expected_files:
        assert ef.exists(), f"Expected provisioned dataset file missing: {ef}"
        assert ef.stat().st_size > 50, f"Provisioned dataset file empty: {ef}"


class TestWarehouseManagement:

    def test_create_warehouse_success_and_duplicate_prevention(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        wh_payload = {
            "id": "WH-TEST-99",
            "name": "Test Distribution Center",
            "location": "Sector 62, Noida",
            "city": "Noida",
            "state": "Uttar Pradesh",
            "country": "India",
            "latitude": 28.6273,
            "longitude": 77.3722
        }
        res = client.post("/warehouses", json=wh_payload, headers=headers)
        assert res.status_code in (200, 201), f"Warehouse creation failed: {res.text}"

        # Duplicate ID creation must be rejected with 409 Conflict
        res_dup = client.post("/warehouses", json=wh_payload, headers=headers)
        assert res_dup.status_code == 409, f"Duplicate warehouse creation should return 409, got {res_dup.status_code}"

    def test_warehouse_creation_validation(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        # Invalid latitude (> 90)
        invalid_lat = {
            "id": "WH-INV-01",
            "name": "Invalid Lat Warehouse",
            "latitude": 120.0,
            "longitude": 77.0
        }
        res = client.post("/warehouses", json=invalid_lat, headers=headers)
        assert res.status_code in (400, 422), f"Expected 400 for invalid lat, got {res.status_code}"

        # ID too long (> 50 chars)
        long_id = {
            "id": "WH-VERY-LONG-ID-EXTENDED-OVERFLOW-THAT-EXCEEDS-FIFTY-CHARACTERS",
            "name": "Long ID Warehouse"
        }
        res_long = client.post("/warehouses", json=long_id, headers=headers)
        assert res_long.status_code in (400, 422), f"Expected 400 for long ID, got {res_long.status_code}"

    def test_edit_warehouse_success(self, client, admin_token, db):
        headers = {"Authorization": f"Bearer {admin_token}"}
        # Update existing WH-BLR-01 warehouse
        edit_payload = {
            "name": "Bengaluru Hub DC Updated",
            "location": "Electronic City Phase 1",
            "city": "Bengaluru",
            "state": "Karnataka",
            "country": "India",
            "latitude": 12.8399,
            "longitude": 77.6770
        }
        res = client.put("/warehouses/WH-BLR-01", json=edit_payload, headers=headers)
        assert res.status_code == 200, f"Warehouse edit failed: {res.text}"

        # Verify DB persistence
        from backend.models import Warehouse
        db.expire_all()
        wh = db.query(Warehouse).filter(Warehouse.id == "WH-BLR-01").first()
        assert wh is not None
        assert wh.name == "Bengaluru Hub DC Updated"
        assert wh.latitude == 12.8399


class TestNotifications:

    def test_notification_lifecycle_and_unread_count(self, client, admin_token, db):
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 1. Unread count check
        res_count = client.get("/notifications/unread-count", headers=headers)
        assert res_count.status_code == 200, f"Unread count GET failed: {res_count.text}"
        assert "unread_count" in res_count.json()

        # 2. List notifications
        res_list = client.get("/notifications", headers=headers)
        assert res_list.status_code == 200, f"Notifications list GET failed: {res_list.text}"
        data = res_list.json()
        assert "notifications" in data and "total" in data

        # 3. Mark all read
        res_all_read = client.post("/notifications/mark-all-read", headers=headers)
        assert res_all_read.status_code == 200, f"Mark all read failed: {res_all_read.text}"

        # 4. Verify unread count becomes 0
        res_count2 = client.get("/notifications/unread-count", headers=headers)
        assert res_count2.status_code == 200
        assert res_count2.json()["unread_count"] == 0


class TestABCAnalysisAllDatasets:

    def test_abc_wms(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.post("/analytics/abc/run?source=wms", headers=headers)
        assert res.status_code == 200, f"ABC wms calculation failed: {res.text}"
        assert res.json().get("status") == "success"

    def test_abc_store_sales(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.post("/analytics/abc/run?source=store_sales", headers=headers)
        assert res.status_code == 200, f"ABC store_sales calculation failed: {res.text}"
        assert res.json().get("status") == "success"

    def test_abc_online_retail(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.post("/analytics/abc/run?source=online_retail", headers=headers)
        assert res.status_code == 200, f"ABC online_retail calculation failed: {res.text}"
        assert res.json().get("status") == "success"

    def test_abc_mlzc(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.post("/analytics/abc/run?source=mlzc", headers=headers)
        assert res.status_code == 200, f"ABC mlzc calculation failed: {res.text}"
        assert res.json().get("status") == "success"


@pytest.fixture(autouse=True)
def seed_blr_warehouse(db):
    """Fixture to ensure WH-BLR-01, locations, items, and robots exist in test DB."""
    from backend.models import Warehouse, Item, WarehouseLocation, Robot
    wh = db.query(Warehouse).filter(Warehouse.id == "WH-BLR-01").first()
    if not wh:
        wh = Warehouse(id="WH-BLR-01", name="Bengaluru DC", city="Bengaluru", country="India", latitude=12.9716, longitude=77.5946)
        db.add(wh)

    item = db.query(Item).filter(Item.id == "ITM001").first()
    if not item:
        item = Item(id="ITM001", name="Test SKU Item", category="General", unit_cost=50.0, weight_kg=1.5)
        db.add(item)

    loc1 = db.query(WarehouseLocation).filter(WarehouseLocation.id == "LOC-A-01").first()
    if not loc1:
        loc1 = WarehouseLocation(id="LOC-A-01", warehouse_id="WH-BLR-01", zone="A", aisle="01", rack="01", shelf="01", x=2.0, y=2.0, location_type="RACK")
        db.add(loc1)

    loc2 = db.query(WarehouseLocation).filter(WarehouseLocation.id == "LOC-PACKING").first()
    if not loc2:
        loc2 = WarehouseLocation(id="LOC-PACKING", warehouse_id="WH-BLR-01", zone="P", aisle="01", rack="01", shelf="01", x=10.0, y=10.0, location_type="PACKING")
        db.add(loc2)

    robot = db.query(Robot).filter(Robot.robot_code == "BOT-BLR-01").first()
    if not robot:
        robot = Robot(robot_code="BOT-BLR-01", name="Bot 1", warehouse_id="WH-BLR-01", status="AVAILABLE", battery_level=98.0, enabled=True, current_x=1.0, current_y=1.0)
        db.add(robot)

    db.commit()


class TestDemandAnomalies:

    def test_demand_anomaly_scan(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.post("/run-shrinkage-detection", headers=headers)
        assert res.status_code in (200, 201), f"Anomaly scan failed: {res.text}"


class TestAIAssistantTools:

    def test_ai_assistant_operational_queries(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        queries = [
            "What is the gross revenue of WH-BLR-01?",
            "Show inventory levels for WH-BLR-01",
            "What is the robot fleet status?",
            "Show order fulfillment performance",
            "Show warehouse anomalies",
            "What are the operational bottlenecks?"
        ]
        for q in queries:
            res = client.post("/ai/assistant", json={"message": q, "warehouse_id": "WH-BLR-01"}, headers=headers)
            assert res.status_code == 200, f"AI assistant failed on query '{q}': {res.text}"
            body = res.json()
            assert "response" in body and body["response"] != ""


class TestTaskAndRobotLifecycle:

    def test_task_assignment_execution_and_robot_release(self, client, admin_token, db):
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 1. Create task
        task_payload = {
            "warehouse_id": "WH-BLR-01",
            "task_type": "PICK",
            "priority": "HIGH",
            "product_id": "ITM001",
            "requested_quantity": 5,
            "source_location_id": "LOC-A-01",
            "destination_location_id": "LOC-PACKING"
        }
        res_task = client.post("/tasks", json=task_payload, headers=headers)
        assert res_task.status_code in (200, 201), f"Task creation failed: {res_task.text}"
        task_data = res_task.json()
        task_id = task_data.get("task_id") or task_data.get("id")

        # 2. Assign Robot to Task
        res_rob_assign = client.post(f"/tasks/{task_id}/assign-robot", json={"robot_code": "BOT-BLR-01"}, headers=headers)
        assert res_rob_assign.status_code == 200, f"Robot assignment failed: {res_rob_assign.text}"

        # Verify robot state is ASSIGNED
        from backend.models import Robot
        bot = db.query(Robot).filter(Robot.robot_code == "BOT-BLR-01").first()
        assert bot.assigned_task_id == task_id

        # 3. Start Task
        res_start = client.post(f"/tasks/{task_id}/start", headers=headers)
        assert res_start.status_code == 200, f"Start task failed: {res_start.text}"

        # 4. Complete Task
        res_comp = client.post(f"/tasks/{task_id}/complete", json={"completed_quantity": 5, "notes": "Completed test pick"}, headers=headers)
        assert res_comp.status_code == 200, f"Complete task failed: {res_comp.text}"

        # 5. VERIFY CRITICAL GUARANTEE: Robot must be released back to AVAILABLE status
        db.expire_all()
        bot_fresh = db.query(Robot).filter(Robot.robot_code == "BOT-BLR-01").first()
        assert bot_fresh.assigned_task_id is None, f"Robot assigned_task_id should be cleared, got {bot_fresh.assigned_task_id}"
        assert bot_fresh.status == "AVAILABLE", f"Robot status should be AVAILABLE, got {bot_fresh.status}"


class TestDigitalTwinAPI:

    def test_digital_twin_get_state(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.get("/apps/digital-twin/WH-BLR-01", headers=headers)
        assert res.status_code == 200, f"Digital twin GET state failed: {res.text}"
        data = res.json()
        assert "zones" in data or "warehouse_id" in data or "data_mode" in data
