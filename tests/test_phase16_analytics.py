import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, UTC

from backend.models import (
    Base, Warehouse, Robot, Task, Item, Inventory, StockMovement,
    ReplenishmentRecommendation, ShrinkageFlag, DigitalTwinSimulation,
    Scenario, Experiment, User
)
from backend.services.ai_service import (
    get_executive_kpis, get_order_analytics, get_inventory_analytics,
    get_robot_analytics, get_forecast_analytics, get_anomaly_analytics,
    get_replenishment_analytics, get_simulation_analytics,
    get_scenario_analytics, get_bottleneck_analysis
)
from backend import reports

@pytest.fixture(scope="module")
def temp_db_engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    # Patch reports.engine to use our in-memory SQLite engine
    reports.engine = engine
    return engine

@pytest.fixture
def db_session(temp_db_engine):
    Session = sessionmaker(bind=temp_db_engine)
    session = Session()
    
    # Seed baseline warehouse
    wh = Warehouse(id="WH-TEST-P16", name="P16 Test Warehouse", location="Fulfillment Lab")
    session.add(wh)
    
    # Add active robot
    session.add(Robot(
        robot_code="ROB-T16", name="Analytics Bot", warehouse_id="WH-TEST-P16",
        status="AVAILABLE", battery_level=85.0, max_speed=1.5,
        current_x=1.0, current_y=1.0, utilization_percent=45.2, total_distance=100.0,
        total_tasks_completed=20
    ))
    
    # Add Item
    item = Item(id=16, name="P16 Item", sku="SKU-T16", unit_cost=50.0, safety_stock=10, reorder_threshold=5)
    session.add(item)
    
    # Add Inventory
    session.add(Inventory(
        warehouse_id="WH-TEST-P16", item_id=16, on_hand=30, reserved=5, available=25
    ))
    
    # Seed stock movements
    session.add(StockMovement(
        date=datetime.now(UTC).date(), warehouse_id="WH-TEST-P16", item_id=16,
        stock_in=10, stock_out=2, closing_stock=30, entered_by="test_user"
    ))
    
    # Seed anomaly flag
    session.add(ShrinkageFlag(
        date=datetime.now(UTC).date(), warehouse_id="WH-TEST-P16", item_id=16,
        item_name="P16 Item", discrepancy_quantity=-3, estimated_exposure=150.0,
        severity="MEDIUM", likely_cause="Mispicking", explanation="Flagged discrepancy"
    ))
    
    # Seed replenishment recommendation
    session.add(ReplenishmentRecommendation(
        warehouse_id="WH-TEST-P16", item_id=16, abc_class="B",
        current_stock=25, safety_stock=10, reorder_point=5,
        recommended_qty=20, urgency="REORDER_RECOMMENDED"
    ))
    
    session.commit()
    yield session
    
    # Clean up tables
    session.query(ReplenishmentRecommendation).delete()
    session.query(ShrinkageFlag).delete()
    session.query(StockMovement).delete()
    session.query(Inventory).delete()
    session.query(Robot).delete()
    session.query(Item).delete()
    session.query(Warehouse).delete()
    session.commit()
    session.close()

def test_kpis_and_analytics_calculations(db_session):
    # Test read-only tool permissions limits
    with pytest.raises(Exception):
         get_anomaly_analytics(db_session, "viewer", "WH-TEST-P16", "30d")
         
    # Validate get_executive_kpis values
    kpis = get_executive_kpis(db_session, "admin", "WH-TEST-P16", "30d")
    assert kpis["orders_completed"] is not None
    assert kpis["stockout_rate"] == 0.0
    assert kpis["avg_robot_utilization"] == 45.2
    
    # Validate get_order_analytics schema
    orders = get_order_analytics(db_session, "manager", "WH-TEST-P16", "30d")
    assert "throughput" in orders
    
    # Validate get_inventory_analytics schema
    inv = get_inventory_analytics(db_session, "viewer", "WH-TEST-P16", "30d")
    assert inv["on_hand"]["value"] == 30
    assert inv["available"]["value"] == 25
    
    # Validate get_robot_analytics schema
    fleet = get_robot_analytics(db_session, "operator", "WH-TEST-P16", "30d")
    assert fleet["fleet_size"]["value"] == 1
    assert fleet["avg_utilization"]["value"] == 45.2

def test_anomaly_and_replenishment_analytics(db_session):
    # Validate get_anomaly_analytics exposure
    anoms = get_anomaly_analytics(db_session, "admin", "WH-TEST-P16", "30d")
    assert anoms["potential_anomalies_count"]["value"] == 1
    assert anoms["estimated_exposure"]["value"] == 150.0
    
    # Validate get_replenishment_analytics
    recs_res = get_replenishment_analytics(db_session, "manager", "WH-TEST-P16")
    assert len(recs_res["recommendations"]) == 1
    assert recs_res["recommendations"][0]["recommended_reorder_qty"] == 20

def test_bottleneck_analysis(db_session):
    # Verify diagnostic bottleneck triggers
    bottles = get_bottleneck_analysis(db_session, "viewer", "WH-TEST-P16", "30d")
    assert "bottlenecks_detected" in bottles
    assert bottles["source"] == "Decision Intelligence Engine"

def test_multi_profile_reports(db_session):
    # Verify PDF compilation for multiple report profiles
    pdf_exec = reports.generate_pdf_report("WH-TEST-P16", "month", "executive")
    assert pdf_exec.getvalue().startswith(b"%PDF")
    
    pdf_inv = reports.generate_pdf_report("WH-TEST-P16", "month", "inventory")
    assert pdf_inv.getvalue().startswith(b"%PDF")
    
    pdf_robots = reports.generate_pdf_report("WH-TEST-P16", "month", "robots")
    assert pdf_robots.getvalue().startswith(b"%PDF")
    
    # Verify CSV and Excel formatting outputs
    csv_out = reports.generate_csv_report("WH-TEST-P16", "month", "executive")
    assert len(csv_out.getvalue()) > 0
    
    xlsx_out = reports.generate_excel_report("WH-TEST-P16", "month", "inventory")
    assert len(xlsx_out.getvalue()) > 0

def test_database_non_mutation_safety(db_session):
    # Ensure querying reports/KPIs triggers zero DB mutations
    initial_movements = db_session.query(StockMovement).count()
    initial_robots = db_session.query(Robot).count()
    
    get_executive_kpis(db_session, "admin", "WH-TEST-P16", "30d")
    reports.generate_pdf_report("WH-TEST-P16", "month", "executive")
    
    assert db_session.query(StockMovement).count() == initial_movements
    assert db_session.query(Robot).count() == initial_robots
