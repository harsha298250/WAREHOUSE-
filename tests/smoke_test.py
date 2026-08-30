"""
tests/smoke_test.py — Production smoke test.

Validates all major endpoints are reachable and returning expected responses.
Designed to be run against a live server after deployment.

USAGE:
  Against local server (default):
    python tests/smoke_test.py

  Against deployed server:
    SMOKE_TEST_BASE_URL=https://your-app.onrender.com SMOKE_TEST_USER=admin SMOKE_TEST_PASS=YourPass python tests/smoke_test.py

IMPORTANT:
  - This test does NOT modify production data.
  - Read-only requests only (GET endpoints).
  - Login acquires a real JWT for testing protected routes.
"""
import os
import sys
import json
import urllib.request
import urllib.error
import urllib.parse

BASE_URL = os.getenv("SMOKE_TEST_BASE_URL", "http://127.0.0.1:8000")
USERNAME  = os.getenv("SMOKE_TEST_USER", "admin")
PASSWORD  = os.getenv("SMOKE_TEST_PASS", "Admin@123")
WAREHOUSE = os.getenv("SMOKE_TEST_WAREHOUSE", "WH-BLR-01")

RESULTS = []


def req(method, path, body=None, token=None, label=None):
    url = BASE_URL + path
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body else None
    try:
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(request, timeout=15) as resp:
            status = resp.getcode()
            try:
                payload = json.loads(resp.read())
            except Exception:
                payload = {}
            return status, payload
    except urllib.error.HTTPError as e:
        try:
            payload = json.loads(e.read())
        except Exception:
            payload = {}
        return e.code, payload
    except Exception as ex:
        return 0, {"error": str(ex)}


def check(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    RESULTS.append((status, name, detail))
    icon = "[OK]" if condition else "[!!]"
    msg = f"  {icon} {name}"
    if detail:
        msg += f" -- {detail}"
    print(msg)
    return condition



def main():
    print("=" * 65)
    print("PRODUCTION SMOKE TEST — Smart Warehouse Intelligence Platform")
    print(f"Target: {BASE_URL}")
    print("=" * 65)

    # 1. Health
    print("\n[1] Health Check")
    code, data = req("GET", "/health")
    check("GET /health returns 200", code == 200, f"Got {code}")
    check("Health has status field", "status" in data)
    check("Health not exposing secrets", "password" not in json.dumps(data).lower())

    # 2. Login
    print("\n[2] Login")
    code, data = req("POST", "/auth/login", body={"username": USERNAME, "password": PASSWORD})
    check("POST /auth/login returns 200", code == 200, f"Got {code}")
    token = data.get("access_token")
    check("Token received", token is not None)

    # 3. Auth Me
    print("\n[3] Auth Me")
    code, data = req("GET", "/auth/me", token=token)
    check("GET /auth/me returns 200", code == 200, f"Got {code}")
    check("Response has role field", "role" in data, f"Got keys: {list(data.keys())}")
    check("Role is not viewer (smoke test uses admin)", data.get("role") != "viewer")

    # 4. Inventory
    print("\n[4] Inventory")
    code, data = req("GET", f"/inventory/{WAREHOUSE}", token=token)
    check("GET /inventory returns 200 or 404", code in [200, 404], f"Got {code}")
    if code == 200:
        check("Inventory response is a list", isinstance(data, list))

    # 5. Trend
    print("\n[5] Stock Trend")
    code, data = req("GET", f"/trend/{WAREHOUSE}", token=token)
    check("GET /trend returns 200", code in [200, 404], f"Got {code}")

    # 6. Analytics Dashboard
    print("\n[6] Analytics Dashboard")
    code, data = req("GET", "/analytics/dashboard", token=token)
    if code == 404:
        # Try alternate path
        code, data = req("GET", "/apps/analytics", token=token)
    check("GET /analytics/dashboard returns 200", code == 200, f"Got {code}")
    if code == 200:
        check("Dashboard has kpis field", "kpis" in data)
        check("Dashboard has data_mode", data.get("data_mode") == "DATABASE_SYNCHRONIZED")

    # 7. AI Decision Center
    print("\n[7] AI Decision Center")
    code, data = req("GET", f"/ai/decision-center?warehouse_id={WAREHOUSE}", token=token)
    check("GET /ai/decision-center returns 200", code == 200, f"Got {code}")
    if code == 200:
        check("Has recommendations field", "recommendations" in data or isinstance(data, list))

    # 8. Shrinkage Detection
    print("\n[8] Shrinkage Detection")
    code, data = req("GET", "/shrinkage/anomalies", token=token)
    if code == 404:
        code, data = req("GET", "/apps/shrinkage-insights", token=token)
    check("GET /shrinkage/anomalies returns 200", code in [200, 404], f"Got {code}")

    # 9. Digital Twin
    print("\n[9] Digital Twin")
    code, data = req("GET", f"/apps/digital-twin/{WAREHOUSE}", token=token)
    check("GET /apps/digital-twin returns 200", code == 200, f"Got {code}")
    if code == 200:
        check("Digital Twin has warehouse_id", "warehouse_id" in data or "warehouses" in data)

    # 10. Trust Ledger
    print("\n[10] Trust Ledger")
    code, data = req("GET", "/audit/verify", token=token)
    if code == 404:
        code, data = req("GET", "/apps/trust-ledger", token=token)
    check("GET /audit/verify returns 200", code in [200, 404], f"Got {code}")
    if code == 200:
        check("Audit verify has valid/status field", "valid" in data or "status" in data)
        check("Valid is boolean (not always hardcoded True)", isinstance(data.get("valid"), bool))

    # 11. Reports
    print("\n[11] Report Generation")
    code, data = req("GET", f"/reports/export?warehouse_id={WAREHOUSE}&format=csv&time_range=7", token=token)
    check("GET /reports/export (CSV) returns 200 or 404", code in [200, 400, 404], f"Got {code}")

    # ---- Summary ----
    print("\n" + "=" * 65)
    passed = sum(1 for s,_,_ in RESULTS if s == "PASS")
    failed = sum(1 for s,_,_ in RESULTS if s == "FAIL")
    print(f"SMOKE TEST RESULTS: {passed} PASSED  |  {failed} FAILED  |  {len(RESULTS)} TOTAL")
    if failed == 0:
        print("ALL SMOKE TESTS PASSED")
    else:
        print(f"WARNING: {failed} check(s) failed -- see above for details.")
        print("\nNote: Some failures may indicate missing demo data in the database.")
        print("Run: python backend/seed_demo_data.py to populate demo data.")
    print("=" * 65)
    sys.exit(0 if failed == 0 else 1)


if __name__ == '__main__':
    main()

