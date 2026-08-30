"""
alembic/env.py — Alembic migration environment for Smart Warehouse Platform.

Reads database URL from environment variables (same as the main application).
Imports SQLAlchemy models so autogenerate can detect schema changes.
"""
import os
import sys
from logging.config import fileConfig
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool
from alembic import context

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load .env for local development
load_dotenv()

# Alembic Config object
config = context.config

# Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import models metadata so autogenerate works
from backend.models import Base  # noqa: E402
target_metadata = Base.metadata

# ---- Database URL ----
# Priority: DATABASE_URL env var > individual DB_* env vars
def get_database_url() -> str:
    url = os.getenv("DATABASE_URL", "").strip()
    if url:
        # Normalize postgres:// to postgresql://
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        # Normalize mysql:// to mysql+pymysql://
        elif url.startswith("mysql://") and not url.startswith("mysql+pymysql://"):
            url = url.replace("mysql://", "mysql+pymysql://", 1)
        return url
    from urllib.parse import quote_plus
    user = os.getenv("DB_USER", "warehouse_app")
    password = quote_plus(os.getenv("DB_PASSWORD", ""))
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "3306")
    name = os.getenv("DB_NAME", "warehouse_db")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"


# Override sqlalchemy.url in alembic.ini with env var
# configparser uses % for interpolation — escape %% to pass URL-encoded values
_db_url = get_database_url().replace("%", "%%")
config.set_main_option("sqlalchemy.url", _db_url)



def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (generates SQL scripts without a DB connection)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (connects to the DB and applies changes)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,      # Detect column type changes
            compare_server_default=True,  # Detect default value changes
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
