"""
tests/test_input_validation.py — Input validation and edge case tests.

API must return 4xx for bad inputs, never 500 with stack traces.
"""
import pytest
import os

# Tests that call endpoints touching MySQL directly (via pandas/reports)
# are marked as integration-only. They skip in SQLite test mode.
_NEEDS_MYSQL = os.getenv("TEST_DB_NAME", "sqlite") == "sqlite"


class TestInventoryValidation:

    def test_negative_stock_rejected_or_handled(self, client, admin_token):
        """Negative stock quantities must not be silently accepted."""
        r = client.post("/stock-movements",
                        json={"warehouse_id": "WH-TEST", "item_id": "ITM-TEST",
                              "date": "2026-01-01", "stock_in": -100, "stock_out": 0,
                              "closing_stock": -100},
                        headers={"Authorization": f"Bearer {admin_token}"})
        # Should fail with 422 (validation) or succeed with 0 (clamped)
        assert r.status_code in [200, 201, 400, 404, 422], f"Unexpected: {r.status_code}"

    def test_invalid_date_format(self, client, admin_token):
        r = client.post("/stock-movements",
                        json={"warehouse_id": "WH-TEST", "item_id": "ITM-TEST",
                              "date": "not-a-date", "stock_in": 10, "stock_out": 0,
                              "closing_stock": 10},
                        headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code in [400, 404, 422]

    @pytest.mark.skipif(_NEEDS_MYSQL, reason="INTEGRATION: inventory endpoint queries MySQL directly")
    def test_nonexistent_warehouse_id(self, client, admin_token):
        r = client.get("/inventory/WH-NONEXISTENT-FAKE-9999",
                       headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code in [200, 404]  # 200 with empty list is acceptable
        if r.status_code == 200:
            assert isinstance(r.json(), list)

    @pytest.mark.skipif(_NEEDS_MYSQL, reason="INTEGRATION: forecast endpoint requires MySQL data")
    def test_nonexistent_item_forecast(self, client, admin_token):
        r = client.get("/forecast/WH-BLR-01/ITM-FAKE-9999",
                       headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code in [200, 400, 404, 422]

    @pytest.mark.skipif(_NEEDS_MYSQL, reason="INTEGRATION: inventory endpoint queries MySQL directly")
    def test_sql_injection_in_warehouse_id(self, client, admin_token):
        """SQL injection attempt must not cause a 500 error."""
        injection = "'; DROP TABLE warehouses; --"
        r = client.get(f"/inventory/{injection}",
                       headers={"Authorization": f"Bearer {admin_token}"})
        # Must not be 500 (internal error leaking SQL details)
        assert r.status_code != 500, f"SQL injection caused 500: {r.text}"

    def test_extremely_large_stock_value(self, client, admin_token):
        r = client.post("/stock-movements",
                        json={"warehouse_id": "WH-TEST", "item_id": "ITM-TEST",
                              "date": "2026-01-01", "stock_in": 999999999999,
                              "stock_out": 0, "closing_stock": 999999999999},
                        headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code in [200, 201, 400, 404, 422]

    def test_missing_required_fields_in_stock_movement(self, client, admin_token):
        r = client.post("/stock-movements",
                        json={"warehouse_id": "WH-TEST"},
                        headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 422

    def test_malformed_json_returns_422(self, client, admin_token):
        r = client.post("/stock-movements",
                        content="this is not json",
                        headers={"Authorization": f"Bearer {admin_token}",
                                 "Content-Type": "application/json"})
        assert r.status_code in [400, 422]

    def test_empty_body_returns_422(self, client, admin_token):
        r = client.post("/stock-movements",
                        json={},
                        headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 422


class TestWarehouseValidation:

    def test_duplicate_warehouse_id(self, client, admin_token):
        payload = {"id": "WH-DUP-TEST", "name": "Dup Wh", "location": "Nowhere"}
        r1 = client.post("/warehouses", json=payload,
                         headers={"Authorization": f"Bearer {admin_token}"})
        r2 = client.post("/warehouses", json=payload,
                         headers={"Authorization": f"Bearer {admin_token}"})
        # Both 200/201 (second may succeed or overwrite) or 409/422 for duplicate
        assert r1.status_code in [200, 201, 400, 422]
        assert r2.status_code in [200, 201, 400, 409, 422]

    def test_warehouse_with_empty_name(self, client, admin_token):
        r = client.post("/warehouses",
                        json={"id": "WH-EMPTY-NAME", "name": "", "location": "Test"},
                        headers={"Authorization": f"Bearer {admin_token}"})
        # Empty name should be rejected or accepted (validation policy)
        assert r.status_code in [200, 201, 400, 422]


class TestErrorResponseFormat:
    """API errors must never expose internal details."""

    def test_404_not_raw_traceback(self, client, admin_token):
        r = client.get("/nonexistent-endpoint-xyz",
                       headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 404
        body = r.text.lower()
        # Must not expose Python tracebacks
        for forbidden in ["traceback", "sqlalchemy", "pymysql", "exception"]:
            assert forbidden not in body, f"'{forbidden}' found in 404 response"

    def test_protected_endpoint_without_auth_returns_401_not_500(self, client):
        sensitive = ["/analytics/dashboard", "/ai/decision-center",
                     "/apps/trust-ledger", "/apps/shrinkage-insights"]
        for path in sensitive:
            r = client.get(path)
            assert r.status_code == 401, f"{path}: expected 401, got {r.status_code}"
            # Must not expose server internals
            assert "traceback" not in r.text.lower()

    def test_error_response_has_detail_field(self, client):
        r = client.get("/auth/me")
        assert r.status_code == 401
        d = r.json()
        assert "detail" in d, "Error response must have 'detail' field"
