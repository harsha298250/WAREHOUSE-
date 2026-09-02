"""
database.py — PostgreSQL connection layer via SQLAlchemy.

PostgreSQL is the primary production database (via DATABASE_URL),
with SQLite used only when ENVIRONMENT=="testing".
"""
import os
import logging
from urllib.parse import quote_plus
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

# Build connection URL
env_db_url = os.getenv("DATABASE_URL")

if env_db_url:
    if env_db_url.startswith("postgres://"):
        DATABASE_URL = env_db_url.replace("postgres://", "postgresql://", 1)
    else:
        DATABASE_URL = env_db_url
else:
    if os.getenv("ENVIRONMENT") == "testing":
        DATABASE_URL = "sqlite:///:memory:"
    else:
        DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///warehouse.db")


# Setup connection arguments
connect_args = {}
engine_kwargs = {"pool_pre_ping": True}
if "sqlite" in DATABASE_URL:
    connect_args["check_same_thread"] = False
    # Use StaticPool for SQLite memory database or testing to share connection in-memory
    if "memory" in DATABASE_URL or os.getenv("ENVIRONMENT") == "testing":
        from sqlalchemy.pool import StaticPool
        engine_kwargs["poolclass"] = StaticPool
else:
    # Setup PostgreSQL optimized connection pooling parameters
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20
    engine_kwargs["pool_recycle"] = 1800
    engine_kwargs["pool_timeout"] = 30

logger = logging.getLogger("warehouse")
logger.info(f"Connecting to database: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")

engine_kwargs["connect_args"] = connect_args

engine = create_engine(DATABASE_URL, **engine_kwargs)

# Enable foreign keys in SQLite
if "sqlite" in DATABASE_URL:
    from sqlalchemy import event
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



def get_db():
    """FastAPI dependency: yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
