"""
tests/conftest.py — Shared pytest fixtures for Smart Warehouse test suite.

TEST DATABASE STRATEGY:
  - Uses SQLite in-memory database by default (fast, isolated, no MySQL needed)
  - Automatically creates all tables on session start
  - Each test function gets a fresh DB session via transactional rollback
  - Never touches the production MySQL database

CONFIGURATION:
  - Set TEST_DB_NAME=sqlite   → SQLite in-memory (default, CI-safe)
  - Set TEST_DB_NAME=warehouse_test_db → uses MySQL test DB (requires server)
    In that case also set TEST_DB_URL or standard DB_* env vars

USAGE:
  pytest tests/ -v
  pytest tests/ -k "auth" -v
  pytest tests/ --tb=short -q
"""
import os
import sys
import pytest

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ---- Configure test database BEFORE importing any backend modules ----
TEST_DB_NAME = os.getenv("TEST_DB_NAME", "sqlite")

if TEST_DB_NAME == "sqlite":
    # SQLite in-memory: fast, isolated, no external server needed
    TEST_DATABASE_URL = "sqlite:///:memory:"
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
else:
    # PostgreSQL test database: integration tests against PostgreSQL server
    db_user = os.getenv("DB_USER", "postgres")
    db_pass = os.getenv("DB_PASSWORD", "1234")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = TEST_DB_NAME if TEST_DB_NAME != "sqlite" else "warehouse_test_db"

    # Auto-create test database if not exists
    from sqlalchemy import create_engine, text
    default_url = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/postgres"
    try:
        tmp_engine = create_engine(default_url, isolation_level="AUTOCOMMIT")
        with tmp_engine.connect() as conn:
            exists = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname='{db_name}'")).scalar()
            if not exists:
                conn.execute(text(f"CREATE DATABASE {db_name}"))
        tmp_engine.dispose()
    except Exception as e:
        print(f"Warning: could not verify/create PostgreSQL test database '{db_name}': {e}")

    TEST_DATABASE_URL = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL

# Force testing environment (prevents external integrations from initializing/connecting)
os.environ["ENVIRONMENT"] = "testing"
os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret-do-not-use-in-production")

# ---- Now import backend modules ----
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from backend.models import Base, User, Warehouse, Item, StockMovement
from backend.auth import hash_password


from backend.database import engine, SessionLocal as TestSessionLocal



@pytest.fixture(scope="session", autouse=True)
def clear_rate_limiter():
    """Clear the in-memory login rate limiter before test session starts.

    The rate limiter is keyed by IP address. TestClient uses 'testclient' as
    the IP, which can accumulate failed attempts from previous test runs.
    This fixture clears that state so tests are not blocked by 429 responses.
    """
    try:
        from backend.main import _login_attempts
        _login_attempts.clear()
    except ImportError:
        pass  # OK if rate limiter not yet imported
    yield
    # Also clear after test session
    try:
        from backend.main import _login_attempts
        _login_attempts.clear()
    except ImportError:
        pass


@pytest.fixture(scope="session", autouse=True)
def create_test_tables():
    """Create all tables once per test session."""
    Base.metadata.create_all(bind=engine)
    
    # Seed demo data for database integration tests when not using SQLite
    if os.getenv("TEST_DB_NAME", "sqlite") != "sqlite":
        try:
            from backend.seed_demo_data import seed
            seed()
            print("Successfully seeded demo data for PostgreSQL database integration tests.")
        except Exception as e:
            print(f"Warning: could not seed demo data: {e}")
            
    yield
    if os.getenv("TEST_DB_NAME", "sqlite") == "sqlite":
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session", autouse=True)
def seed_test_users():
    """Seed standard test users at session start."""
    _session = TestSessionLocal()
    try:
        if not _session.query(User).filter(User.username == "test_admin").first():
            _session.add(User(
                username="test_admin",
                password_hash=hash_password("TestAdmin@123"),
                role="admin",
                email="test_admin@example.com"
            ))
        if not _session.query(User).filter(User.username == "test_manager").first():
            _session.add(User(
                username="test_manager",
                password_hash=hash_password("TestManager@123"),
                role="manager",
                email="test_manager@example.com"
            ))
        if not _session.query(User).filter(User.username == "test_viewer").first():
            _session.add(User(
                username="test_viewer",
                password_hash=hash_password("TestViewer@123"),
                role="viewer",
                email="test_viewer@example.com"
            ))
        if not _session.query(User).filter(User.username == "test_admin_hardened").first():
            _session.add(User(
                username="test_admin_hardened",
                password_hash=hash_password("AdminHardened@123"),
                role="admin",
                email="test_admin_hardened@example.com"
            ))
        _session.commit()
    except Exception as e:
        print(f"Warning: could not seed test users: {e}")
        _session.rollback()
    finally:
        _session.close()


@pytest.fixture(scope="function")
def db():
    """Provide a DB session and clean up test-created tables after each test."""
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        
        # Clean up database tables to prevent cross-test contamination
        cleanup_session = TestSessionLocal()
        try:
            if "sqlite" in TEST_DATABASE_URL:
                cleanup_session.execute(text("PRAGMA foreign_keys = OFF"))
            # Preserve session-scoped test users and seeder demo data
            cleanup_session.execute(text("DELETE FROM stock_movements WHERE warehouse_id NOT IN ('WH-BLR-01', 'WH-CHN-01', 'WH-BOM-01', 'WH-DEL-01', 'WH-CCU-01')"))
            cleanup_session.execute(text("DELETE FROM warehouses WHERE id NOT IN ('WH-BLR-01', 'WH-CHN-01', 'WH-BOM-01', 'WH-DEL-01', 'WH-CCU-01')"))
            cleanup_session.execute(text("DELETE FROM items WHERE id NOT IN ('ITM-CPU-01', 'ITM-GPU-01', 'ITM-RAM-01', 'ITM-SSD-01', 'ITM-HDD-01', 'ITM-CHG-01', 'ITM-CBL-01')"))
            cleanup_session.execute(text("DELETE FROM users WHERE username NOT IN ('admin', 'test_admin', 'test_manager', 'test_viewer', 'test_admin_hardened')"))
            
            # Clear all other tables completely
            cleanup_session.execute(text("DELETE FROM shrinkage_flags"))
            cleanup_session.execute(text("DELETE FROM ai_recommendations"))
            cleanup_session.execute(text("DELETE FROM access_log"))
            cleanup_session.execute(text("DELETE FROM audit_ledger"))
            cleanup_session.execute(text("DELETE FROM recovery_credentials"))
            cleanup_session.execute(text("DELETE FROM recovery_codes"))
            cleanup_session.execute(text("DELETE FROM backup_records"))
            try:
                cleanup_session.execute(text("DELETE FROM robot_reservations"))
                cleanup_session.execute(text("DELETE FROM robot_routes"))
                cleanup_session.execute(text("DELETE FROM robots"))
            except Exception:
                pass
            # WMS tables
            try:
                cleanup_session.execute(text("DELETE FROM order_events"))
                cleanup_session.execute(text("DELETE FROM task_events"))
                cleanup_session.execute(text("DELETE FROM tasks"))
                cleanup_session.execute(text("DELETE FROM packing_records"))
                cleanup_session.execute(text("DELETE FROM shipments"))
                cleanup_session.execute(text("DELETE FROM financial_transactions"))
                cleanup_session.execute(text("DELETE FROM inventory_reservations"))
                cleanup_session.execute(text("DELETE FROM order_items"))
                cleanup_session.execute(text("DELETE FROM orders"))
                cleanup_session.execute(text("DELETE FROM inventory"))
                cleanup_session.execute(text("DELETE FROM warehouse_locations"))
            except Exception:
                pass  # WMS tables may not exist in SQLite test mode

            # Reset seeded user passwords and roles to defaults to prevent cross-test contamination
            test_admin = cleanup_session.query(User).filter(User.username == "test_admin").first()
            if test_admin:
                test_admin.password_hash = hash_password("TestAdmin@123")
                test_admin.role = "admin"
                test_admin.is_active = True
                test_admin.failed_login_count = 0
                test_admin.locked_until = None
            
            test_manager = cleanup_session.query(User).filter(User.username == "test_manager").first()
            if test_manager:
                test_manager.password_hash = hash_password("TestManager@123")
                test_manager.role = "manager"
                test_manager.is_active = True
                test_manager.failed_login_count = 0
                test_manager.locked_until = None

            test_viewer = cleanup_session.query(User).filter(User.username == "test_viewer").first()
            if test_viewer:
                test_viewer.password_hash = hash_password("TestViewer@123")
                test_viewer.role = "viewer"
                test_viewer.is_active = True
                test_viewer.failed_login_count = 0
                test_viewer.locked_until = None

            cleanup_session.commit()
        except Exception as e:
            cleanup_session.rollback()
            print(f"Warning: database test cleanup failed: {e}")
        finally:
            cleanup_session.close()


@pytest.fixture(scope="session")
def test_app():
    """FastAPI test app with request-scoped test database dependency override."""
    from backend.main import app
    from backend.database import get_db

    def override_get_db():
        db_session = TestSessionLocal()
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield app
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(test_app):
    """HTTP test client backed by the test app."""
    with TestClient(test_app) as c:
        yield c


# ---- Seed helpers ----

def seed_admin(session) -> User:
    """Create a test admin user."""
    admin = User(
        username="test_admin",
        password_hash=hash_password("TestAdmin@123"),
        role="admin",
    )
    session.add(admin)
    session.commit()
    session.refresh(admin)
    return admin


def seed_manager(session) -> User:
    """Create a test manager user."""
    mgr = User(
        username="test_manager",
        password_hash=hash_password("TestManager@123"),
        role="manager",
    )
    session.add(mgr)
    session.commit()
    session.refresh(mgr)
    return mgr


def seed_viewer(session) -> User:
    """Create a test viewer user."""
    viewer = User(
        username="test_viewer",
        password_hash=hash_password("TestViewer@123"),
        role="viewer",
    )
    session.add(viewer)
    session.commit()
    session.refresh(viewer)
    return viewer


def seed_warehouse(session, wh_id="WH-TEST-01") -> Warehouse:
    """Create a test warehouse."""
    wh = Warehouse(id=wh_id, name="Test Warehouse", location="Test City")
    session.add(wh)
    session.commit()
    session.refresh(wh)
    return wh


def seed_item(session, item_id="ITM-TEST-01", safety_stock=10, unit_cost=100.0) -> Item:
    """Create a test item."""
    item = Item(
        id=item_id,
        name="Test Item",
        category="Electronics",
        safety_stock=safety_stock,
        lead_time_days=7,
        unit_cost=unit_cost
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@pytest.fixture(scope="session")
def admin_token(test_app):
    """Login as admin and return JWT token."""
    # Seed admin directly in the DB used by the app
    from backend.main import app
    from backend.database import get_db as real_get_db
    # Use a fresh real DB session to seed if using real MySQL
    # For SQLite, use the session factory
    _session = TestSessionLocal()
    existing = _session.query(User).filter(User.username == "test_admin").first()
    if not existing:
        admin = User(
            username="test_admin",
            password_hash=hash_password("TestAdmin@123"),
            role="admin",
            is_active=True,
            is_verified=True
        )
        _session.add(admin)
        _session.commit()
    else:
        existing.role = "admin"
        existing.is_active = True
        existing.is_verified = True
        existing.failed_login_count = 0
        existing.locked_until = None
        existing.password_hash = hash_password("TestAdmin@123")
        _session.commit()
    _session.close()

    # Clear rate limiter before login to avoid 429 from previous test run
    try:
        from backend.main import _login_attempts
        _login_attempts.clear()
    except ImportError:
        pass

    with TestClient(test_app) as client_temp:
        r = client_temp.post("/auth/login", json={"username": "test_admin", "password": "TestAdmin@123"})
        assert r.status_code == 200, f"Admin login failed: {r.text}"
        return r.json()["access_token"]


@pytest.fixture(scope="session")
def manager_token(test_app):
    """Login as manager and return JWT token."""
    _session = TestSessionLocal()
    existing = _session.query(User).filter(User.username == "test_manager").first()
    if not existing:
        mgr = User(
            username="test_manager",
            password_hash=hash_password("TestManager@123"),
            role="manager",
        )
        _session.add(mgr)
        _session.commit()
    else:
        existing.password_hash = hash_password("TestManager@123")
        existing.is_active = True
        existing.failed_login_count = 0
        _session.commit()
    _session.close()

    try:
        from backend.main import _login_attempts
        _login_attempts.clear()
    except ImportError:
        pass

    with TestClient(test_app) as client_temp:
        r = client_temp.post("/auth/login", json={"username": "test_manager", "password": "TestManager@123"})
        assert r.status_code == 200, f"Manager login failed: {r.text}"
        return r.json()["access_token"]


@pytest.fixture(scope="session")
def viewer_token(test_app):
    """Login as viewer and return JWT token."""
    _session = TestSessionLocal()
    existing = _session.query(User).filter(User.username == "test_viewer").first()
    if not existing:
        viewer = User(
            username="test_viewer",
            password_hash=hash_password("TestViewer@123"),
            role="viewer",
        )
        _session.add(viewer)
        _session.commit()
    else:
        existing.password_hash = hash_password("TestViewer@123")
        existing.is_active = True
        existing.failed_login_count = 0
        _session.commit()
    _session.close()

    try:
        from backend.routers.auth import _login_attempts
        _login_attempts.clear()
    except ImportError:
        pass

    with TestClient(test_app) as client_temp:
        r = client_temp.post("/auth/login", json={"username": "test_viewer", "password": "TestViewer@123"})
        assert r.status_code == 200, f"Viewer login failed: {r.text}"
        return r.json()["access_token"]


def pytest_configure(config):
    """Register custom test markers."""
    config.addinivalue_line("markers", "e2e: mark test as a true browser/Playwright E2E test requiring Chromium")
    config.addinivalue_line("markers", "integration: mark test as an API/TestClient integration test (no browser needed)")
    config.addinivalue_line("markers", "production: mark test as a production-only smoke test")


def pytest_collection_modifyitems(items):
    """Apply markers accurately based on actual test type.

    Only tests that literally use Playwright/browser get the 'e2e' marker.
    All other tests under tests/e2e/ that use FastAPI TestClient get the
    'integration' marker instead — they must NOT require Chromium.
    """
    import os
    for item in items:
        fspath = str(item.fspath).replace(os.sep, "/")
        filename = os.path.basename(fspath)
        # Only test_playwright.py and test_playwright_*.py are true browser tests
        is_browser_test = (filename == "test_playwright.py" or filename.startswith("test_playwright_"))
        if is_browser_test:
            item.add_marker(pytest.mark.e2e)
        elif "/tests/e2e/" in fspath:
            # API/TestClient tests that live in tests/e2e/ are integration tests
            item.add_marker(pytest.mark.integration)


@pytest.fixture(scope="session")
def browser_context():
    """Starts headless chromium browser and yields page context once per test session."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        yield context
        browser.close()


@pytest.fixture(autouse=True)
def clean_session(request):
    """Clear browser localStorage/sessionStorage before each browser E2E test.

    Only fires when ALL of these are true:
    1. The test is marked @pytest.mark.e2e (true browser test)
    2. The test explicitly requests the 'browser_context' fixture

    API/TestClient tests in tests/e2e/ are marked 'integration', not 'e2e',
    so this fixture is entirely skipped for them — no Chromium is launched.
    """
    # Gate 1: only for e2e-marked tests
    if not request.node.get_closest_marker("e2e"):
        return

    # Gate 2: only if the test actually requests browser_context
    if "browser_context" not in request.fixturenames:
        return

    try:
        browser_ctx = request.getfixturevalue("browser_context")
    except Exception as e:
        pytest.skip(f"Browser context unavailable (Chromium not installed?): {e}")
        return

    import os
    base_url = os.getenv("PLAYWRIGHT_TEST_URL", "http://127.0.0.1:8000")
    page = browser_ctx.new_page()
    try:
        page.goto(base_url)
        page.evaluate("localStorage.clear(); sessionStorage.clear();")
    except Exception:
        pass  # Ignore errors if server is not yet running or page load fails
    finally:
        page.close()


@pytest.fixture(autouse=True)
def mock_send_email_alert(monkeypatch):
    """Prevent actual outbound SMTP calls during testing."""
    import backend.notifications
    monkeypatch.setattr(backend.notifications, "send_email_alert", lambda *args, **kwargs: True)

