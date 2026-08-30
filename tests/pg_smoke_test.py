import sys
import os
import requests
import time

# Add root directory to python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.auth import hash_password
from backend.database import SessionLocal, engine
from backend.models import User, Warehouse, Item

BASE_URL = "http://127.0.0.1:8000"

def run_smoke_test():
    print("=== STARTING POSTGRESQL SMOKE TEST ===")
    
    # Step 1: Create a test user directly in the database
    print("\n[Step 1] Creating a test admin user directly in PostgreSQL...")
    db = SessionLocal()
    try:
        # Delete if exists
        db.query(User).filter(User.username == "pg_smoke_admin").delete()
        db.commit()
        
        # Create
        user = User(
            username="pg_smoke_admin",
            password_hash=hash_password("SmokeTest@123"),
            role="admin",
            full_name="Smoke Test Admin"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Created test user: {user.username} with role {user.role}")
    except Exception as e:
        print(f"FAILED to create test user: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

    # Step 2: Login via API
    print("\n[Step 2] Logging in via FastAPI /auth/login endpoint...")
    login_data = {
        "username": "pg_smoke_admin",
        "password": "SmokeTest@123"
    }
    
    try:
        res = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if res.status_code != 200:
            print(f"FAILED to login (status {res.status_code}): {res.text}")
            sys.exit(1)
        
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("Logged in successfully. JWT Token retrieved.")
    except Exception as e:
        print(f"API Login call failed: {e}")
        sys.exit(1)

    # Step 3: CRUD operations on Warehouse
    print("\n[Step 3] Performing CRUD operations on Warehouse via API...")
    wh_payload = {
        "id": "WH-SMOKE-99",
        "name": "Smoke Test Warehouse",
        "location": "Test City",
        "latitude": 12.97,
        "longitude": 77.59
    }
    
    try:
        # Create
        res = requests.post(f"{BASE_URL}/warehouses", json=wh_payload, headers=headers)
        if res.status_code != 200:
            print(f"FAILED to create warehouse (status {res.status_code}): {res.text}")
            sys.exit(1)
        print("Created warehouse WH-SMOKE-99.")

        # Read
        res = requests.get(f"{BASE_URL}/warehouses", headers=headers)
        if res.status_code != 200:
            print(f"FAILED to fetch warehouses (status {res.status_code}): {res.text}")
            sys.exit(1)
        
        whs = [w["id"] for w in res.json()]
        if "WH-SMOKE-99" not in whs:
            print("FAILED: WH-SMOKE-99 not found in warehouses list.")
            sys.exit(1)
        print("Read and verified warehouse existence.")

        # Update (coordinates lock/update)
        coords_payload = {"latitude": 13.0, "longitude": 78.0}
        res = requests.put(f"{BASE_URL}/warehouses/WH-SMOKE-99/coordinates", json=coords_payload, headers=headers)
        if res.status_code != 200:
            print(f"FAILED to update coordinates (status {res.status_code}): {res.text}")
            sys.exit(1)
        print("Updated coordinates for WH-SMOKE-99.")
        
        # Verify update
        res = requests.get(f"{BASE_URL}/warehouses", headers=headers)
        wh_details = [w for w in res.json() if w["id"] == "WH-SMOKE-99"][0]
        if wh_details["latitude"] != 13.0 or wh_details["longitude"] != 78.0:
            print(f"FAILED: Coordinates update did not persist. Got: {wh_details}")
            sys.exit(1)
        print("Verified update persisted successfully.")

    except Exception as e:
        print(f"CRUD execution failed: {e}")
        sys.exit(1)

    # Step 4: Database persistence check after restart simulation
    # (Since PostgreSQL runs locally, the data exists inside the PG database).
    # We will query directly from database layer to ensure persistence.
    print("\n[Step 4] Verifying data persistence directly from database session...")
    db = SessionLocal()
    try:
        wh_db = db.query(Warehouse).filter(Warehouse.id == "WH-SMOKE-99").first()
        if not wh_db or wh_db.latitude != 13.0:
            print(f"FAILED: Persistence check failed in PostgreSQL database. Warehouse: {wh_db}")
            sys.exit(1)
        print(f"Verified persistence in PostgreSQL: ID={wh_db.id}, Location={wh_db.location}")
    except Exception as e:
        print(f"Database query failed: {e}")
        sys.exit(1)
    finally:
        db.close()

    # Step 5: Delete/Cleanup test records
    print("\n[Step 5] Cleaning up smoke test records...")
    db = SessionLocal()
    try:
        db.query(Warehouse).filter(Warehouse.id == "WH-SMOKE-99").delete()
        db.query(User).filter(User.username == "pg_smoke_admin").delete()
        db.commit()
        print("Smoke test records cleaned up successfully.")
    except Exception as e:
        print(f"Cleanup failed: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

    print("\n=== POSTGRESQL SMOKE TEST COMPLETED SUCCESSFULLY (100% PASS) ===")

if __name__ == "__main__":
    run_smoke_test()
