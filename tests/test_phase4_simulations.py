import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException

from backend.models import Base, Scenario, Experiment, ExperimentRun, Warehouse, User
from backend.routers.scenarios import create_scenario, duplicate_scenario, rerun_experiment, get_scenarios

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(name="db")
def fixture_db():
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db_session = TestingSessionLocal()

    # Seed warehouses
    wh1 = Warehouse(id="WH-BLR-01", name="Bangalore Hub", location="Bangalore")
    wh2 = Warehouse(id="WH-DEL-01", name="Delhi Hub", location="Delhi")
    db_session.add_all([wh1, wh2])
    db_session.commit()

    # Seed users
    admin = User(id=1, username="admin_user", role="admin", password_hash="dummy")
    manager = User(id=2, username="manager_user", role="manager", password_hash="dummy")
    operator = User(id=3, username="operator_user", role="operator", password_hash="dummy")
    db_session.add_all([admin, manager, operator])
    db_session.commit()

    yield db_session

    db_session.close()
    Base.metadata.drop_all(bind=engine)


def test_scenario_creation_unique_rules(db):
    admin = db.query(User).filter(User.username == "admin_user").first()
    operator = db.query(User).filter(User.username == "operator_user").first()

    # Case 1: Insufficient privilege check
    with pytest.raises(HTTPException) as exc:
        create_scenario({"name": "Test Scen", "warehouse_id": "WH-BLR-01"}, db, operator)
    assert exc.value.status_code == 403

    # Case 2: Validation of name and warehouse_id
    with pytest.raises(HTTPException) as exc:
        create_scenario({"name": "", "warehouse_id": "WH-BLR-01"}, db, admin)
    assert exc.value.status_code == 400

    # Case 3: Create scenario once successfully
    payload = {
        "name": "Surge Flow Simulation",
        "warehouse_id": "WH-BLR-01",
        "scenario_type": "HIGH_DEMAND",
        "configuration": {}
    }
    scen = create_scenario(payload, db, admin)
    assert scen["id"] is not None
    assert scen["name"] == "Surge Flow Simulation"

    # Case 4: Trying to create the scenario with same name in same warehouse again should throw 400
    with pytest.raises(HTTPException) as exc:
        create_scenario(payload, db, admin)
    assert exc.value.status_code == 400

    # Case 5: Creating scenario with same name in a DIFFERENT warehouse should succeed
    payload_del = {
        "name": "Surge Flow Simulation",
        "warehouse_id": "WH-DEL-01",
        "scenario_type": "HIGH_DEMAND",
        "configuration": {}
    }
    scen_del = create_scenario(payload_del, db, admin)
    assert scen_del["id"] is not None
    assert scen_del["warehouse_id"] == "WH-DEL-01"


def test_scenario_duplication(db):
    admin = db.query(User).filter(User.username == "admin_user").first()

    payload = {
        "name": "Original Test Scenario",
        "warehouse_id": "WH-BLR-01",
        "scenario_type": "BASELINE",
        "configuration": {"robots": {"robot_count": 3}}
    }
    scen = create_scenario(payload, db, admin)

    # Duplicate scenario
    dup = duplicate_scenario(scen["id"], db, admin)
    assert dup.id is not None
    assert dup.id != scen["id"]
    assert dup.name == "Copy of Original Test Scenario"
    assert dup.configuration["robots"]["robot_count"] == 3


def test_scenario_selection_and_listing(db):
    admin = db.query(User).filter(User.username == "admin_user").first()

    # Create distinct scenarios
    create_scenario({"name": "Scen A", "warehouse_id": "WH-BLR-01"}, db, admin)
    create_scenario({"name": "Scen B", "warehouse_id": "WH-BLR-01"}, db, admin)

    # Retrieve scenario listing
    scens = get_scenarios("WH-BLR-01", db, admin)
    assert len(scens) == 2
    names = [s.name for s in scens]
    assert "Scen A" in names
    assert "Scen B" in names


def test_experiment_rerun_isolation(db):
    admin = db.query(User).filter(User.username == "admin_user").first()

    payload = {
        "name": "Experiment Scen",
        "warehouse_id": "WH-BLR-01",
        "scenario_type": "BASELINE",
        "configuration": {}
    }
    scen = create_scenario(payload, db, admin)

    # Initialize first experiment
    exp = Experiment(
        scenario_id=scen["id"],
        experiment_name="Baseline Strategy Run",
        description="First execution",
        status="COMPLETED",
        algorithm_name="A_STAR_CONGESTION_AWARE",
        random_seed=42,
        repetitions=2,
        created_by="admin_user"
    )
    db.add(exp)
    db.commit()

    # Rerun experiment should create a new distinct experiment run
    rerun = rerun_experiment(exp.id, db, admin)
    assert rerun.id is not None
    assert rerun.id != exp.id
    assert rerun.experiment_name == "Baseline Strategy Run (Rerun)"
    assert rerun.status == "QUEUED"

    # Verify both remain in database history
    all_exps = db.query(Experiment).all()
    assert len(all_exps) == 2
