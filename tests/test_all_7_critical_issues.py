"""
tests/test_all_7_critical_issues.py

Comprehensive Integration Verification Test Suite for Warehouse OS.
Verifies all 7 critical integration issues using standard pytest fixtures against test database.
"""
import pytest
from backend.models import (
    User, Item, Inventory, Order, OrderItem, Task, Warehouse,
    ABCClassification, AnomalyResult, WarehouseGridCell, Robot
)


def _get_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


def test_issue_1_new_inventory_item_propagates_to_abc(client, db, admin_token):
    """
    ISSUE 1 Verification:
    Add a new inventory item called "Maggi", run ABC classification,
    and verify Maggi is persisted in PostgreSQL ABCClassification table and included in ABC results.
    """
    headers = _get_headers(admin_token)
    
    # 1. Add new item Maggi
    item_id = "ITM-MAGGI-01"
    # Cleanup if exists
    db.query(ABCClassification).filter(ABCClassification.item_id == item_id).delete()
    db.query(Inventory).filter(Inventory.item_id == item_id).delete()
    db.query(Item).filter(Item.id == item_id).delete()
    db.commit()

    # Ensure WH-CHN-01 warehouse exists
    wh = db.query(Warehouse).filter(Warehouse.id == "WH-CHN-01").first()
    if not wh:
        db.add(Warehouse(id="WH-CHN-01", name="Chennai Port Logistics Hub", location="Chennai"))
        db.commit()

    maggi_payload = {
        "id": item_id,
        "name": "Maggi 2-Minute Noodles 12-Pack",
        "category": "Groceries",
        "unit_cost": 140.0,
        "lead_time_days": 2,
        "safety_stock": 20,
        "reorder_threshold": 30,
        "initial_stock": 500,
        "warehouse_id": "WH-CHN-01"
    }

    res = client.post("/items", json=maggi_payload, headers=headers)
    assert res.status_code in (200, 201), f"Failed to create item: {res.text}"

    # Verify item persisted in database
    db_item = db.query(Item).filter(Item.id == item_id).first()
    assert db_item is not None, "Maggi item not found in items table"
    assert db_item.name == maggi_payload["name"]

    db_inv = db.query(Inventory).filter(Inventory.item_id == item_id, Inventory.warehouse_id == "WH-CHN-01").first()
    assert db_inv is not None, "Maggi inventory record not found in inventory table"
    assert db_inv.on_hand == 500

    # 2. Trigger ABC classification for WMS dataset
    res_abc_run = client.post("/analytics/abc/run?source=wms&threshold_a=80&threshold_b=95&warehouse_id=WH-CHN-01", headers=headers)
    assert res_abc_run.status_code == 200, f"ABC classification failed: {res_abc_run.text}"
    data_run = res_abc_run.json()
    assert data_run["status"] == "success"

    # 3. Retrieve ABC classification results from DB
    res_abc_get = client.get("/analytics/abc?source=wms&warehouse_id=WH-CHN-01", headers=headers)
    assert res_abc_get.status_code == 200, f"Get ABC failed: {res_abc_get.text}"
    data_get = res_abc_get.json()
    
    classified_item_ids = [r["item_id"] for r in data_get["results"]]
    assert item_id in classified_item_ids, f"Maggi ({item_id}) was NOT included in ABC classification results! Found: {classified_item_ids}"

    # Verify classification saved in DB
    db_abc = db.query(ABCClassification).filter(ABCClassification.item_id == item_id, ABCClassification.source == "wms").first()
    assert db_abc is not None, "Maggi missing from ABCClassification table"
    assert db_abc.abc_class in ("A", "B", "C")


def test_issue_2_order_created_generates_tasks_for_chennai_and_all_warehouses(client, db, admin_token):
    """
    ISSUE 2 Verification:
    Create an order for Chennai warehouse (and every other warehouse),
    and verify a PICK task is generated, persisted in tasks table, and returned by tasks API.
    """
    headers = _get_headers(admin_token)

    # Ensure warehouses exist in test DB
    for wh_code, wh_name in [("WH-CHN-01", "Chennai Port Logistics Hub"), ("WH-BLR-01", "Bangalore Fulfillment Center")]:
        if not db.query(Warehouse).filter(Warehouse.id == wh_code).first():
            db.add(Warehouse(id=wh_code, name=wh_name, location="India"))
            db.commit()

        # Ensure item & inventory exist
        item = db.query(Item).first()
        if not item:
            item = Item(id="ITM-TEST-01", name="Test Item", unit_cost=100.0)
            db.add(item)
            db.commit()

        inv = db.query(Inventory).filter(Inventory.warehouse_id == wh_code, Inventory.item_id == item.id).first()
        if not inv:
            db.add(Inventory(warehouse_id=wh_code, item_id=item.id, on_hand=100, available=100))
            db.commit()

        order_payload = {
            "customer_ref": f"Test Order Integration {wh_code}",
            "warehouse_id": wh_code,
            "priority": "HIGH",
            "notes": f"Integration verification order for {wh_code}",
            "items": [
                {"item_id": item.id, "requested_qty": 3}
            ]
        }

        res_ord = client.post("/wms/orders", json=order_payload, headers=headers)
        assert res_ord.status_code in (200, 201), f"Order creation failed for {wh_code}: {res_ord.text}"
        ord_data = res_ord.json()
        order_id = ord_data["order_id"]

        # Verify Order stored in DB
        db_order = db.query(Order).filter(Order.id == order_id).first()
        assert db_order is not None, f"Order {order_id} not found in database"
        assert db_order.warehouse_id == wh_code

        # Verify Task stored in DB
        db_task = db.query(Task).filter(Task.order_id == order_id).first()
        assert db_task is not None, f"No task created in database for order {order_id} in warehouse {wh_code}"
        assert db_task.warehouse_id == wh_code
        assert db_task.product_id == item.id
        assert db_task.status in ("QUEUED", "PRIORITIZED", "ASSIGNED")

        # Verify Tasks page API returns the created task
        res_tasks = client.get(f"/tasks?warehouse_id={wh_code}", headers=headers)
        assert res_tasks.status_code == 200, f"Tasks API failed for {wh_code}: {res_tasks.text}"
        tasks_list = res_tasks.json()["tasks"]
        task_ids = [t["id"] for t in tasks_list]
        assert db_task.id in task_ids, f"Task {db_task.id} not present in tasks API list for {wh_code}"


def test_issue_3_and_4_digital_twin_pathfinding_multi_warehouse(client, db, admin_token):
    """
    ISSUE 3 & 4 Verification:
    Verify robot pathfinding routes avoid racks and obstacles across all configured warehouses.
    """
    headers = _get_headers(admin_token)

    for wh_code in ["WH-CHN-01", "WH-BLR-01"]:
        if not db.query(Warehouse).filter(Warehouse.id == wh_code).first():
            db.add(Warehouse(id=wh_code, name=f"Warehouse {wh_code}", location="India"))
            db.commit()

        # Request pathfinding route from start (1,5) to goal (4,5)
        pf_payload = {
            "warehouse_id": wh_code,
            "start_x": 1,
            "start_y": 5,
            "goal_x": 4,
            "goal_y": 5,
            "algorithm": "A_STAR"
        }
        res_pf = client.post("/pathfinding/plan", json=pf_payload, headers=headers)
        assert res_pf.status_code == 200, f"Pathfinding failed for warehouse {wh_code}: {res_pf.text}"
        pf_data = res_pf.json()
        assert pf_data.get("success") is True, f"Route planning failed for {wh_code}: {pf_data}"
        
        path = pf_data["path"]
        assert len(path) >= 2, f"Path should contain waypoints for {wh_code}"
        
        # Verify route waypoints do not pass through non-traversable RACK cells
        for point in path:
            px, py = point["x"], point["y"]
            is_rack = (py in (1, 3)) and (2 <= px <= 11)
            assert not is_rack, f"Robot route crossed a non-traversable RACK at ({px}, {py}) in warehouse {wh_code}! Path: {path}"

        # Check Digital Twin state endpoint for warehouse
        res_dt = client.get(f"/digital-twin/{wh_code}/state", headers=headers)
        assert res_dt.status_code == 200, f"Digital Twin state failed for {wh_code}: {res_dt.text}"
        dt_data = res_dt.json()
        assert len(dt_data["grid"]) > 0, f"Digital Twin grid empty for {wh_code}"


def test_issue_5_settings_must_be_admin_only(client, admin_token, manager_token, viewer_token):
    """
    ISSUE 5 Verification:
    ADMIN -> Settings allowed
    MANAGER -> Settings denied (HTTP 403)
    OPERATOR/VIEWER -> Settings denied (HTTP 403)
    """
    admin_headers = _get_headers(admin_token)
    manager_headers = _get_headers(manager_token)
    viewer_headers = _get_headers(viewer_token)

    # ADMIN: GET /api/settings allowed
    res_admin_get = client.get("/api/settings", headers=admin_headers)
    assert res_admin_get.status_code == 200, f"Admin GET settings failed: {res_admin_get.text}"

    res_admin_defaults = client.get("/api/settings/defaults", headers=admin_headers)
    assert res_admin_defaults.status_code == 200, f"Admin GET defaults failed: {res_admin_defaults.text}"

    # NON-ADMIN: GET /api/settings denied with HTTP 403
    for role_name, headers in [("manager", manager_headers), ("viewer", viewer_headers)]:
        res_get = client.get("/api/settings", headers=headers)
        assert res_get.status_code == 403, f"Role '{role_name}' was NOT denied on GET /api/settings! Status: {res_get.status_code}"

        res_def = client.get("/api/settings/defaults", headers=headers)
        assert res_def.status_code == 403, f"Role '{role_name}' was NOT denied on GET /api/settings/defaults! Status: {res_def.status_code}"

        res_post = client.post("/api/settings", json={"theme": "dark"}, headers=headers)
        assert res_post.status_code == 403, f"Role '{role_name}' was NOT denied on POST /api/settings! Status: {res_post.status_code}"

        res_del = client.delete("/api/settings", headers=headers)
        assert res_del.status_code == 403, f"Role '{role_name}' was NOT denied on DELETE /api/settings! Status: {res_del.status_code}"


def test_issue_6_anomalies_page_data_persistence(client, db, admin_token):
    """
    ISSUE 6 Verification:
    Verify demand anomalies are persisted and returned via GET /analytics/anomalies/demand.
    """
    headers = _get_headers(admin_token)

    # Trigger anomaly run if empty
    res_run = client.post("/analytics/anomalies/run?contamination=0.05", headers=headers)
    assert res_run.status_code == 200, f"Anomaly run failed: {res_run.text}"

    res_anom = client.get("/analytics/anomalies/demand?warehouse_id=WH-CHN-01", headers=headers)
    assert res_anom.status_code == 200, f"Demand anomalies endpoint failed: {res_anom.text}"
    data = res_anom.json()
    
    assert data["total"] > 0, "No demand anomalies found in database"
    assert len(data["results"]) > 0, "Results list is empty"
    first_anom = data["results"][0]
    assert "anomaly_score" in first_anom
    assert "severity" in first_anom
    assert "features_json" in first_anom


def test_issue_7_inventory_analytics_postgres_accuracy(client, db, admin_token):
    """
    ISSUE 7 Verification:
    Verify Inventory Analytics reflect actual inventory state for selected warehouse.
    """
    headers = _get_headers(admin_token)

    for wh_id in ["WH-BLR-01", "WH-CHN-01"]:
        if not db.query(Warehouse).filter(Warehouse.id == wh_id).first():
            db.add(Warehouse(id=wh_id, name=f"Warehouse {wh_id}", location="India"))
            db.commit()

        res_inv = client.get(f"/analytics/inventory?warehouse_id={wh_id}", headers=headers)
        assert res_inv.status_code == 200, f"Inventory analytics failed for {wh_id}: {res_inv.text}"
        data = res_inv.json()

        # Compare against database aggregations
        inv_records = db.query(Inventory).filter(Inventory.warehouse_id == wh_id).all()
        expected_on_hand = sum(r.on_hand for r in inv_records)
        expected_reserved = sum(r.reserved for r in inv_records)
        expected_available = sum(r.available for r in inv_records)

        assert data["on_hand"]["value"] == expected_on_hand, f"On Hand mismatch for {wh_id}: API={data['on_hand']['value']} DB={expected_on_hand}"
        assert data["reserved"]["value"] == expected_reserved, f"Reserved mismatch for {wh_id}: API={data['reserved']['value']} DB={expected_reserved}"
        assert data["available"]["value"] == expected_available, f"Available mismatch for {wh_id}: API={data['available']['value']} DB={expected_available}"
