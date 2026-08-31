"""
init_db.py — Run this once to set up the database.

Creates all tables in MySQL and a default admin account. It does NOT
generate fake historical data — this project is meant to be filled in
by you, either by adding warehouses/items/stock through the dashboard,
or by running data/seed_demo_data.py if you want a working demo dataset
to explore before you have your own.
"""
import sys, os, time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import engine, SessionLocal
from backend.models import Base, User
from backend.auth import hash_password

DEFAULT_ADMIN_USERNAME = os.getenv("INITIAL_ADMIN_USERNAME", "admin")
DEFAULT_ADMIN_PASSWORD = os.getenv("INITIAL_ADMIN_PASSWORD", "")



def init():
    print("Creating tables...")
    retries = 3
    delay = 2
    for attempt in range(retries):
        try:
            Base.metadata.create_all(bind=engine)
            print("Tables created successfully.")
            break
        except Exception as e:
            if attempt == retries - 1:
                print(f"Error creating database tables after {retries} attempts: {e}")
                raise e
            print(f"Database connection failed: {e}. Retrying in {delay} seconds (attempt {attempt+1}/{retries})...")
            time.sleep(delay)
            delay *= 2

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == DEFAULT_ADMIN_USERNAME).first()
        default_email = os.getenv("ALERT_EMAIL_TO", "admin@example.com")
        if existing:
            print(f"Admin user '{DEFAULT_ADMIN_USERNAME}' already exists — skipping initial admin creation.")
            if not existing.email and default_email:
                existing.email = default_email
                db.commit()
                print(f"Updated existing admin user email to '{default_email}'")
        else:
            # Enforce non-empty password for initial creation
            if not DEFAULT_ADMIN_PASSWORD:
                raise ValueError(
                    "INITIAL_ADMIN_PASSWORD environment variable is missing or empty! "
                    "Please configure INITIAL_ADMIN_PASSWORD in your environment or Render dashboard before initializing."
                )
            if len(DEFAULT_ADMIN_PASSWORD) < 8:
                raise ValueError(
                    "INITIAL_ADMIN_PASSWORD is too weak! It must be at least 8 characters long."
                )

            admin = User(
                username=DEFAULT_ADMIN_USERNAME,
                password_hash=hash_password(DEFAULT_ADMIN_PASSWORD),
                role="admin",
                full_name="System Administrator",
                email=default_email,
                is_active=True,
            )
            db.add(admin)
            db.commit()
            print(f"Created default admin account '{DEFAULT_ADMIN_USERNAME}' securely.")
            print(f"  IMPORTANT: change this password after your first login.")
    finally:
        db.close()

    print("Database ready.")


if __name__ == "__main__":
    init()
