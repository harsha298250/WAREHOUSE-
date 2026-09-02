"""
seed_demo_data.py — Seeds a highly realistic, rich Kaggle-style dataset
into the PostgreSQL database to demonstrate full functionality.
"""
import sys, os
from datetime import datetime, date, timedelta, timezone
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal, engine
from backend.models import Base, Warehouse, Item, StockMovement, ShrinkageFlag, AccessLog, WarehouseLocation, Inventory, Robot, AuditLedger
try:
    from backend.models import FinancialTransaction
    _HAS_FINANCIAL = True
except ImportError:
    _HAS_FINANCIAL = False
from backend.audit_ledger import append_entry

# Legitimate Kaggle-style hardware / logistics dataset
WAREHOUSES = [
    {"id": "WH-BLR-01", "name": "Bangalore Fulfillment Center", "location": "Bangalore, Karnataka", "city": "Bengaluru", "state": "Karnataka", "country": "India", "latitude": 12.971598, "longitude": 77.594566},
    {"id": "WH-CHN-01", "name": "Chennai Port Logistics Hub", "location": "Chennai, Tamil Nadu", "city": "Chennai", "state": "Tamil Nadu", "country": "India", "latitude": 13.082680, "longitude": 80.270718},
    {"id": "WH-BOM-01", "name": "Mumbai Container Terminal", "location": "Mumbai, Maharashtra", "city": "Mumbai", "state": "Maharashtra", "country": "India", "latitude": 19.076090, "longitude": 72.877701},
    {"id": "WH-DEL-01", "name": "Delhi NCR Logistics Park", "location": "Noida, Uttar Pradesh", "city": "Noida", "state": "Uttar Pradesh", "country": "India", "latitude": 28.535517, "longitude": 77.391029},
    {"id": "WH-CCU-01", "name": "Kolkata Gateway Depot", "location": "Kolkata, West Bengal", "city": "Kolkata", "state": "West Bengal", "country": "India", "latitude": 22.572646, "longitude": 88.363895},
]

ITEMS = [
    {"id": "ITM-CPU-01", "name": "AMD Ryzen 9 7900X Processor", "category": "Electronics", "unit_cost": 38000.0, "lead_time_days": 5, "safety_stock": 15},
    {"id": "ITM-GPU-01", "name": "Nvidia RTX 4080 Founders Edition", "category": "Electronics", "unit_cost": 95000.0, "lead_time_days": 7, "safety_stock": 10},
    {"id": "ITM-RAM-01", "name": "Corsair DDR5 32GB 6000MHz RAM", "category": "Electronics", "unit_cost": 8500.0, "lead_time_days": 4, "safety_stock": 25},
    {"id": "ITM-SSD-01", "name": "Samsung 990 Pro 2TB NVMe SSD", "category": "Storage", "unit_cost": 12000.0, "lead_time_days": 3, "safety_stock": 30},
    {"id": "ITM-HDD-01", "name": "WD Red Pro 8TB NAS Hard Drive", "category": "Storage", "unit_cost": 16500.0, "lead_time_days": 5, "safety_stock": 20},
    {"id": "ITM-CHG-01", "name": "Anker 100W GaN Wall Charger", "category": "Accessories", "unit_cost": 2500.0, "lead_time_days": 2, "safety_stock": 50},
    {"id": "ITM-CBL-01", "name": "Apple USB-C Braided Cable 2m", "category": "Accessories", "unit_cost": 800.0, "lead_time_days": 1, "safety_stock": 100},
]


def seed(force: bool = False):
    print("Connecting to database...")
    db = SessionLocal()
    try:
        # Check if warehouse data already exists to ensure idempotency
        existing_warehouses_count = db.query(Warehouse).count()
        if existing_warehouses_count > 0 and not force and os.getenv("FORCE_RESEED", "false").lower() != "true":
            print(f"Database already contains {existing_warehouses_count} warehouse(s) — skipping seed to preserve existing production data.")
            return

        # Clear existing data (but NOT users/admin)
        print("Seeding demo data (clearing previous operational records)...")
        db.query(AuditLedger).delete()
        db.query(StockMovement).delete()
        db.query(ShrinkageFlag).delete()
        db.query(AccessLog).delete()
        db.query(Robot).delete()
        db.query(Inventory).delete()
        db.query(WarehouseLocation).delete()
        db.query(Warehouse).delete()
        db.query(Item).delete()
        db.commit()

        # Seed Warehouses
        print("Seeding warehouses...")
        for w in WAREHOUSES:
            wh = Warehouse(
                id=w["id"],
                name=w["name"],
                location=w["location"],
                city=w.get("city"),
                state=w.get("state"),
                country=w.get("country"),
                latitude=w["latitude"],
                longitude=w["longitude"]
            )
            db.add(wh)
            append_entry(db, "warehouse_created", {"warehouse_id": w["id"], "name": w["name"]})
        db.commit()

        # Seed Warehouse locations
        print("Seeding warehouse locations...")
        for w in WAREHOUSES:
            wh_id = w["id"]
            
            # 1. Dock locations (Receiving / Shipping)
            db.add(WarehouseLocation(
                id=f"WH-{wh_id}-RECEIVING",
                warehouse_id=wh_id,
                zone="RECEIVING",
                aisle="1",
                rack="1",
                shelf="1",
                x=1.0,
                y=5.0,
                location_type="RECEIVING",
                status="ACTIVE"
            ))
            db.add(WarehouseLocation(
                id=f"WH-{wh_id}-SHIPPING",
                warehouse_id=wh_id,
                zone="SHIPPING",
                aisle="1",
                rack="1",
                shelf="1",
                x=2.0,
                y=5.0,
                location_type="SHIPPING",
                status="ACTIVE"
            ))
            
            # 2. Staging location
            db.add(WarehouseLocation(
                id=f"WH-{wh_id}-STAGING",
                warehouse_id=wh_id,
                zone="STAGING",
                aisle="1",
                rack="1",
                shelf="1",
                x=6.0,
                y=5.0,
                location_type="STAGING",
                status="ACTIVE"
            ))
            
            # 3. Charging locations
            db.add(WarehouseLocation(
                id=f"WH-{wh_id}-CHARGING-1",
                warehouse_id=wh_id,
                zone="CHARGING",
                aisle="1",
                rack="1",
                shelf="1",
                x=11.0,
                y=5.0,
                location_type="CHARGING",
                status="ACTIVE"
            ))
            db.add(WarehouseLocation(
                id=f"WH-{wh_id}-CHARGING-2",
                warehouse_id=wh_id,
                zone="CHARGING",
                aisle="1",
                rack="2",
                shelf="1",
                x=12.0,
                y=5.0,
                location_type="CHARGING",
                status="ACTIVE"
            ))
            
            # 4. Storage / Rack cells (Racks in col 2-11, row 1 and 3)
            item_storage_mapping = [
                {"item_id": "ITM-CPU-01", "x": 2.0, "y": 1.0, "zone": "ZONE-A", "type": "STORAGE"},
                {"item_id": "ITM-GPU-01", "x": 3.0, "y": 1.0, "zone": "ZONE-A", "type": "STORAGE"},
                {"item_id": "ITM-RAM-01", "x": 4.0, "y": 1.0, "zone": "ZONE-A", "type": "STORAGE"},
                {"item_id": "ITM-SSD-01", "x": 6.0, "y": 1.0, "zone": "ZONE-B", "type": "STORAGE"},
                {"item_id": "ITM-HDD-01", "x": 7.0, "y": 1.0, "zone": "ZONE-B", "type": "STORAGE"},
                {"item_id": "ITM-CHG-01", "x": 9.0, "y": 1.0, "zone": "ZONE-C", "type": "STORAGE"},
                {"item_id": "ITM-CBL-01", "x": 10.0, "y": 1.0, "zone": "ZONE-C", "type": "STORAGE"},
                
                # Picking rack locations (row 3)
                {"item_id": "ITM-CPU-01", "x": 2.0, "y": 3.0, "zone": "ZONE-A", "type": "PICKING"},
                {"item_id": "ITM-GPU-01", "x": 3.0, "y": 3.0, "zone": "ZONE-A", "type": "PICKING"},
                {"item_id": "ITM-RAM-01", "x": 4.0, "y": 3.0, "zone": "ZONE-A", "type": "PICKING"},
                {"item_id": "ITM-SSD-01", "x": 6.0, "y": 3.0, "zone": "ZONE-B", "type": "PICKING"},
                {"item_id": "ITM-HDD-01", "x": 7.0, "y": 3.0, "zone": "ZONE-B", "type": "PICKING"},
                {"item_id": "ITM-CHG-01", "x": 9.0, "y": 3.0, "zone": "ZONE-C", "type": "PICKING"},
                {"item_id": "ITM-CBL-01", "x": 10.0, "y": 3.0, "zone": "ZONE-C", "type": "PICKING"},
            ]
            
            for mapping in item_storage_mapping:
                suffix = "STORAGE" if mapping["type"] == "STORAGE" else "PICKING"
                db.add(WarehouseLocation(
                    id=f"WH-{wh_id}-LOC-{mapping['item_id']}-{suffix}",
                    warehouse_id=wh_id,
                    zone=mapping["zone"],
                    aisle="1",
                    rack=mapping["item_id"].split("-")[-1],
                    shelf="1",
                    x=mapping["x"],
                    y=mapping["y"],
                    location_type=mapping["type"],
                    status="ACTIVE"
                ))
            
            # 5. Aisle cells
            for row in range(1, 6):
                for col in range(1, 13):
                    is_rack = (row in (1, 3)) and (2 <= col <= 11)
                    is_dock = (row == 5) and (col in (1, 2))
                    is_charging = (row == 5) and (col in (11, 12))
                    
                    if not (is_rack or is_dock or is_charging):
                        db.add(WarehouseLocation(
                            id=f"WH-{wh_id}-AISLE-{col}-{row}",
                            warehouse_id=wh_id,
                            zone="AISLE",
                            aisle=str(col),
                            rack="0",
                            shelf="0",
                            x=float(col),
                            y=float(row),
                            location_type="BUFFER",
                            status="ACTIVE"
                        ))
        db.commit()

        # Seed Items
        print("Seeding items...")
        for i in ITEMS:
            itm = Item(
                id=i["id"],
                name=i["name"],
                category=i["category"],
                unit_cost=i["unit_cost"],
                lead_time_days=i["lead_time_days"],
                safety_stock=i["safety_stock"]
            )
            db.add(itm)
            append_entry(db, "item_created", {"item_id": i["id"], "name": i["name"]})
        db.commit()

        # Seed Stock Movements (30 days of history: July 12, 2026 to August 11, 2026)
        print("Generating historical stock movements...")
        end_date = date(2026, 8, 11)
        start_date = end_date - timedelta(days=29)

        # Set up initial inventory levels
        inventory_levels = {}
        for wh in WAREHOUSES:
            inventory_levels[wh["id"]] = {}
            for itm in ITEMS:
                # Start at about 3x safety stock
                inventory_levels[wh["id"]][itm["id"]] = itm["safety_stock"] * 3

        current_date = start_date
        total_movements = 0
        while current_date <= end_date:
            for wh in WAREHOUSES:
                for itm in ITEMS:
                    # Daily demand: random sales
                    # High cost items sell fewer units per day
                    if itm["unit_cost"] > 50000:
                        daily_demand = random.choice([0, 0, 1, 0, 2])
                    elif itm["unit_cost"] > 10000:
                        daily_demand = random.choice([0, 1, 2, 0, 3])
                    else:
                        daily_demand = random.randint(1, 10)

                    # Trigger restock if stock drops below 1.5x safety stock
                    stock_in = 0
                    current_stock = inventory_levels[wh["id"]][itm["id"]]
                    if current_stock < itm["safety_stock"] * 1.5:
                        # Schedule a shipment to arrive
                        # (simplified here as immediate, but we can do a randomized batch restock)
                        stock_in = itm["safety_stock"] * 3
                        # Simulate a stock entry action in audit log sometimes
                        append_entry(db, "simulated_restock", {
                            "warehouse_id": wh["id"],
                            "item_id": itm["id"],
                            "quantity": stock_in,
                            "date": str(current_date)
                        })

                    # Calculate new closing stock
                    closing = current_stock + stock_in - daily_demand
                    if closing < 0:
                        closing = 0
                    
                    inventory_levels[wh["id"]][itm["id"]] = closing

                    # Determine anomaly status
                    is_anomaly = False
                    anomaly_type = "none"

                    # Seed 2 specific anomalies for ML demonstration:
                    if wh["id"] == "WH-BLR-01" and itm["id"] == "ITM-GPU-01" and current_date == date(2026, 8, 5):
                        # Sudden drop of 10 GPUs (pilferage / shrinkage simulation)
                        is_anomaly = True
                        anomaly_type = "shrinkage"
                        closing -= 10
                        inventory_levels[wh["id"]][itm["id"]] = max(0, closing)
                    
                    if wh["id"] == "WH-CHN-01" and itm["id"] == "ITM-CPU-01" and current_date == date(2026, 7, 25):
                        # Discrepancy of 15 CPUs
                        is_anomaly = True
                        anomaly_type = "shrinkage"
                        closing -= 15
                        inventory_levels[wh["id"]][itm["id"]] = max(0, closing)

                    # Write record
                    movement = StockMovement(
                        date=current_date,
                        warehouse_id=wh["id"],
                        item_id=itm["id"],
                        stock_in=stock_in,
                        stock_out=daily_demand,
                        closing_stock=inventory_levels[wh["id"]][itm["id"]],
                        is_anomaly=is_anomaly,
                        anomaly_type=anomaly_type,
                        entry_source="simulated",
                        entered_by="system_sim"
                    )
                    db.add(movement)
                    total_movements += 1

            current_date += timedelta(days=1)
        db.commit()

        # Seed Inventory table with current stock levels
        print("Seeding inventory levels at locations...")
        for wh in WAREHOUSES:
            wh_id = wh["id"]
            for itm in ITEMS:
                itm_id = itm["id"]
                final_qty = inventory_levels[wh_id][itm_id]
                
                # We place the inventory at the main STORAGE location we created
                storage_loc_id = f"WH-{wh_id}-LOC-{itm_id}-STORAGE"
                
                db.add(Inventory(
                    warehouse_id=wh_id,
                    item_id=itm_id,
                    location_id=storage_loc_id,
                    on_hand=final_qty,
                    reserved=0,
                    available=final_qty,
                    damaged=0
                ))
        db.commit()

        # Seed Robot fleet
        print("Seeding robot fleet...")
        for wh in WAREHOUSES:
            wh_id = wh["id"]
            num_robots = 3 if wh_id == "WH-BLR-01" else 1
            for r_idx in range(1, num_robots + 1):
                if r_idx == 1:
                    loc_id = f"WH-{wh_id}-CHARGING-1"
                    x, y = 11.0, 5.0
                    status = "CHARGING"
                elif r_idx == 2:
                    loc_id = f"WH-{wh_id}-CHARGING-2"
                    x, y = 12.0, 5.0
                    status = "CHARGING"
                else:
                    loc_id = f"WH-{wh_id}-RECEIVING"
                    x, y = 1.0, 5.0
                    status = "IDLE"
                
                wh_code = wh_id.split("-")[1]
                robot_code = f"RB-{wh_code}-0{r_idx}"
                name = f"{wh['name'].split(' ')[0]} AGV 0{r_idx}"
                
                robot = Robot(
                    robot_code=robot_code,
                    name=name,
                    warehouse_id=wh_id,
                    status=status,
                    battery_level=100.0 if status == "CHARGING" else 92.5,
                    current_location_id=loc_id,
                    current_x=x,
                    current_y=y,
                    enabled=True,
                    robot_type="AGV",
                    max_payload=200.0,
                    max_speed=1.5
                )
                db.add(robot)
        db.commit()

        # Seed Shrinkage Flags to populate the ML view instantly
        print("Seeding shrinkage flags...")
        flags = [
            {
                "date": date(2026, 8, 5),
                "warehouse_id": "WH-BLR-01",
                "item_id": "ITM-GPU-01",
                "item_name": "Nvidia RTX 4080 Founders Edition",
                "deviation_score": 0.85,
                "expected_quantity": 15.0,
                "actual_quantity": 5.0,
                "discrepancy_quantity": -10.0,
                "estimated_exposure": 950000.0,
                "severity": "CRITICAL",
                "likely_cause": "UNUSUAL_OUTBOUND_ACTIVITY",
                "explanation": "Sudden unrecorded drop of 10 units (Valued at ₹9,50,000) occurred outside regular stock-out operations."
            },
            {
                "date": date(2026, 7, 25),
                "warehouse_id": "WH-CHN-01",
                "item_id": "ITM-CPU-01",
                "item_name": "AMD Ryzen 9 7900X Processor",
                "deviation_score": 0.72,
                "expected_quantity": 20.0,
                "actual_quantity": 5.0,
                "discrepancy_quantity": -15.0,
                "estimated_exposure": 570000.0,
                "severity": "HIGH",
                "likely_cause": "POSSIBLE_DAMAGE_OR_WASTAGE",
                "explanation": "Discrepancy of 15 units (Valued at ₹5,70,000) reported at the dock. Unrecorded scraping suspected."
            }
        ]
        for f in flags:
            flag = ShrinkageFlag(
                date=f["date"],
                warehouse_id=f["warehouse_id"],
                item_id=f["item_id"],
                item_name=f["item_name"],
                deviation_score=f["deviation_score"],
                expected_quantity=f["expected_quantity"],
                actual_quantity=f["actual_quantity"],
                discrepancy_quantity=f["discrepancy_quantity"],
                estimated_exposure=f["estimated_exposure"],
                severity=f["severity"],
                likely_cause=f["likely_cause"],
                explanation=f["explanation"]
            )
            db.add(flag)
            append_entry(db, "shrinkage_flag", {
                "warehouse_id": f["warehouse_id"],
                "item_id": f["item_id"],
                "likely_cause": f["likely_cause"]
            })
        db.commit()

        # Seed Access Logs
        print("Seeding access logs...")
        log_actions = ["login", "view", "add_stock", "view", "view"]
        for _ in range(50):
            action = random.choice(log_actions)
            wh = random.choice(WAREHOUSES)["id"] if action != "login" else ""
            log = AccessLog(
                timestamp=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=random.randint(10, 5000)),
                username=random.choice(["admin", "harsha200797@gmail.com"]),
                warehouse_id=wh,
                action=action,
                ip_address=f"192.168.1.{random.randint(2, 254)}"
            )
            db.add(log)
        db.commit()

        # Seed Financial Transactions (SALE records for the past 60 days)
        if _HAS_FINANCIAL:
            print("Seeding financial transactions...")
            try:
                # Only seed if table is empty to avoid duplicates
                existing_count = db.query(FinancialTransaction).count()
                if existing_count == 0:
                    item_prices = {item["id"]: item["unit_cost"] for item in ITEMS}
                    for wh in WAREHOUSES:
                        wh_id = wh["id"]
                        # Generate 60 days of transactions
                        for day_offset in range(60, 0, -1):
                            txn_date = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=day_offset)
                            # 2–5 sales per day per warehouse
                            daily_sales = random.randint(2, 5)
                            for _ in range(daily_sales):
                                item = random.choice(ITEMS)
                                qty = random.randint(1, 8)
                                amount = round(item["unit_cost"] * qty, 2)
                                txn_id = f"TXN-{wh_id}-{day_offset}-{random.randint(1000,9999)}"
                                db.add(FinancialTransaction(
                                    transaction_id=txn_id,
                                    warehouse_id=wh_id,
                                    transaction_type="SALE",
                                    amount=amount,
                                    currency="INR",
                                    description=f"Sale: {item['name']} ×{qty}",
                                    created_at=txn_date
                                ))
                    db.commit()
                    print("  Financial transactions seeded successfully.")
                else:
                    print(f"  Financial transactions already present ({existing_count} records) — skipping.")
            except Exception as fe:
                print(f"  Warning: Could not seed financial transactions: {fe}")
                db.rollback()

        # Auto-export dataset files to data/datasets/
        import pandas as pd
        dataset_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "datasets")
        os.makedirs(dataset_dir, exist_ok=True)
        tables = ["warehouses", "items", "stock_movements", "shrinkage_flags", "audit_ledger", "access_log", "warehouse_locations", "inventory", "robots"]
        for t in tables:
            try:
                df = pd.read_sql(text(f"SELECT * FROM {t}"), engine)
                df.to_csv(os.path.join(dataset_dir, f"{t}.csv"), index=False)
                df.to_json(os.path.join(dataset_dir, f"{t}.json"), orient="records", indent=2, date_format="iso")
            except Exception as e:
                pass

        # Trigger demand anomaly detection and save to DB
        print("Seeding demand anomalies...")
        try:
            from ml.anomaly.demand_anomaly import detect_demand_anomalies, save_anomalies_to_db
            res_anom = detect_demand_anomalies()
            save_anomalies_to_db(db, res_anom)
        except Exception as e_anom:
            print(f"Demand anomaly seeding skipped: {e_anom}")

        # Trigger initial ABC classification
        print("Seeding ABC classifications...")
        try:
            from ml.abc.classifier import ABCClassifier
            from sqlalchemy import func
            clf = ABCClassifier()
            data_list = []
            for it in db.query(Item).all():
                q_sum = db.query(func.sum(StockMovement.stock_out)).filter(StockMovement.item_id == it.id).scalar() or 0.0
                inv_sum = db.query(func.sum(Inventory.on_hand)).filter(Inventory.item_id == it.id).scalar() or 0.0
                data_list.append({"item_id": it.id, "item_name": it.name, "qty": max(float(q_sum), float(inv_sum)), "unit_cost": float(it.unit_cost or 0.0)})
            if data_list:
                clf.fit(pd.DataFrame(data_list), item_col="item_id", qty_col="qty", value_col="unit_cost", item_name_col="item_name")
                clf.save_to_db(db, source="wms")
        except Exception as e_abc:
            print(f"ABC classification seeding skipped: {e_abc}")

        print(f"Success! Seeded:")
        print(f"  - {len(WAREHOUSES)} warehouses")
        print(f"  - {len(ITEMS)} items")
        print(f"  - {total_movements} stock movement logs")
        print(f"  - 2 shrinkage flags")
        print(f"  - 50 access log events")
        print(f"  - CSV/JSON datasets updated in data/datasets/")

    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
        raise e
    finally:
        db.close()


def ensure_core_warehouses_exist(db):
    """Ensure all core warehouses (WH-BLR-01, WH-CHN-01, WH-BOM-01, WH-DEL-01, WH-CCU-01) exist with full working data."""
    try:
        items = db.query(Item).all()
        if not items:
            for itm in ITEMS:
                db.add(Item(
                    id=itm["id"], name=itm["name"], category=itm["category"],
                    unit_cost=itm["unit_cost"], lead_time_days=itm["lead_time_days"],
                    safety_stock=itm["safety_stock"], sku=itm["id"]
                ))
            db.commit()
            items = db.query(Item).all()

        for wh_data in WAREHOUSES:
            wh_id = wh_data["id"]
            existing_wh = db.query(Warehouse).filter(Warehouse.id == wh_id).first()
            if not existing_wh:
                print(f"Auto-restoring missing core warehouse: {wh_id} ({wh_data['name']})")
                db.add(Warehouse(
                    id=wh_id,
                    name=wh_data["name"],
                    location=wh_data["location"],
                    city=wh_data["city"],
                    state=wh_data["state"],
                    country=wh_data["country"],
                    latitude=wh_data["latitude"],
                    longitude=wh_data["longitude"],
                ))
                db.commit()

            # Ensure baseline locations exist for this warehouse
            loc_count = db.query(WarehouseLocation).filter(WarehouseLocation.warehouse_id == wh_id).count()
            if loc_count == 0:
                locations_data = [
                    {"id": f"{wh_id}-CHARGING-1", "x": 11.0, "y": 5.0, "type": "CHARGING", "zone": "CHARGING", "aisle": "C-1"},
                    {"id": f"{wh_id}-CHARGING-2", "x": 12.0, "y": 5.0, "type": "CHARGING", "zone": "CHARGING", "aisle": "C-2"},
                    {"id": f"{wh_id}-RECEIVING", "x": 1.0, "y": 5.0, "type": "RECEIVING", "zone": "RECEIVING", "aisle": "R-1"},
                    {"id": f"{wh_id}-AISLE-4-5", "x": 4.0, "y": 5.0, "type": "STORAGE", "zone": "STORAGE", "aisle": "A-4"},
                    {"id": f"{wh_id}-AISLE-6-5", "x": 6.0, "y": 5.0, "type": "STORAGE", "zone": "STORAGE", "aisle": "A-6"},
                    {"id": f"{wh_id}-AISLE-8-5", "x": 8.0, "y": 5.0, "type": "PACKING", "zone": "PACKING", "aisle": "P-8"},
                    {"id": f"{wh_id}-STORAGE-1", "x": 2.0, "y": 2.0, "type": "STORAGE", "zone": "STORAGE", "aisle": "S-1"},
                    {"id": f"{wh_id}-STORAGE-2", "x": 5.0, "y": 2.0, "type": "STORAGE", "zone": "STORAGE", "aisle": "S-2"},
                    {"id": f"{wh_id}-PACKING-1", "x": 10.0, "y": 2.0, "type": "PACKING", "zone": "PACKING", "aisle": "P-1"},
                ]
                for ld in locations_data:
                    db.add(WarehouseLocation(
                        id=ld["id"], warehouse_id=wh_id, x=ld["x"], y=ld["y"],
                        location_type=ld["type"], zone=ld["zone"], aisle=ld["aisle"],
                        rack=ld["aisle"], shelf="1", capacity=500
                    ))
                db.commit()

            # Ensure inventory records exist
            inv_count = db.query(Inventory).filter(Inventory.warehouse_id == wh_id).count()
            if inv_count == 0 and items:
                locs = db.query(WarehouseLocation).filter(WarehouseLocation.warehouse_id == wh_id).all()
                for idx, item in enumerate(items):
                    target_loc = locs[idx % len(locs)]
                    db.add(Inventory(
                        warehouse_id=wh_id,
                        location_id=target_loc.id,
                        item_id=item.id,
                        on_hand=150,
                        reserved=10,
                        available=140,
                        damaged=0
                    ))
                db.commit()

            # Ensure baseline robots exist for this warehouse
            bot_count = db.query(Robot).filter(Robot.warehouse_id == wh_id).count()
            if bot_count < 4:
                wh_code = wh_id.split("-")[1] if "-" in wh_id else wh_id[:3].upper()
                initial_robots = [
                    {"code": f"RB-{wh_code}-01", "x": 11.0, "y": 5.0, "status": "CHARGING", "loc": f"{wh_id}-CHARGING-1", "battery": 100.0},
                    {"code": f"RB-{wh_code}-02", "x": 12.0, "y": 5.0, "status": "CHARGING", "loc": f"{wh_id}-CHARGING-2", "battery": 100.0},
                    {"code": f"RB-{wh_code}-03", "x": 1.0, "y": 5.0, "status": "AVAILABLE", "loc": f"{wh_id}-RECEIVING", "battery": 92.5},
                    {"code": f"RB-{wh_code}-04", "x": 4.0, "y": 5.0, "status": "AVAILABLE", "loc": f"{wh_id}-AISLE-4-5", "battery": 88.0},
                    {"code": f"RB-{wh_code}-05", "x": 6.0, "y": 5.0, "status": "AVAILABLE", "loc": f"{wh_id}-AISLE-6-5", "battery": 95.0},
                    {"code": f"RB-{wh_code}-06", "x": 8.0, "y": 5.0, "status": "AVAILABLE", "loc": f"{wh_id}-AISLE-8-5", "battery": 90.0},
                ]
                valid_locs = {l.id for l in db.query(WarehouseLocation).filter(WarehouseLocation.warehouse_id == wh_id).all()}
                for idx, r_data in enumerate(initial_robots):
                    loc_id = r_data["loc"] if r_data["loc"] in valid_locs else None
                    if not db.query(Robot).filter(Robot.robot_code == r_data["code"]).first():
                        db.add(Robot(
                            robot_code=r_data["code"],
                            name=f"AGV 0{idx+1}",
                            warehouse_id=wh_id,
                            status=r_data["status"],
                            battery_level=r_data["battery"],
                            current_location_id=loc_id,
                            current_x=r_data["x"],
                            current_y=r_data["y"],
                            target_x=0.0, target_y=0.0,
                            enabled=True, robot_type="AGV",
                            max_payload=200.0, max_speed=1.5,
                            total_distance=0.0, total_tasks_completed=0
                        ))
                db.commit()

            # Ensure digital twin grid cells exist
            from backend.routers.pathfinding import initialize_warehouse_grid_if_empty
            initialize_warehouse_grid_if_empty(db, wh_id)

    except Exception as e:
        db.rollback()
        print(f"ensure_core_warehouses_exist warning: {e}")


if __name__ == "__main__":
    force_flag = "--force" in sys.argv
    seed(force=force_flag)

