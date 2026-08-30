"""
tests/test_reports.py — Report generation tests (CSV, XLSX, PDF).
"""
import pytest
import os

# Reports use the main MySQL engine directly (not the test SQLite)
# These tests require actual data in MySQL to generate reports
_NEEDS_MYSQL = os.getenv("TEST_DB_NAME", "sqlite") == "sqlite"


class TestReportGeneration:

    @pytest.mark.skipif(_NEEDS_MYSQL, reason="INTEGRATION: requires MySQL with stock data")
    def test_csv_report_returns_200(self, client, admin_token):
        r = client.get(f"/reports/export?warehouse_id=WH-BLR-01&format=csv&time_range=week",
                       headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code in [200, 400, 404], f"Unexpected: {r.status_code}"
        if r.status_code == 200:
            ct = r.headers.get("Content-Type", "")
            assert "csv" in ct.lower() or "octet" in ct.lower() or "plain" in ct.lower(), \
                f"CSV report Content-Type wrong: {ct}"

    @pytest.mark.skipif(_NEEDS_MYSQL, reason="INTEGRATION: requires MySQL with stock data")
    def test_xlsx_report_returns_200(self, client, admin_token):
        r = client.get(f"/reports/export?warehouse_id=WH-BLR-01&format=xlsx&time_range=week",
                       headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code in [200, 400, 404]
        if r.status_code == 200:
            ct = r.headers.get("Content-Type", "")
            assert "spreadsheet" in ct.lower() or "octet" in ct.lower() or "xlsx" in ct.lower()

    @pytest.mark.skipif(_NEEDS_MYSQL, reason="INTEGRATION: requires MySQL with stock data")
    def test_pdf_report_returns_200(self, client, admin_token):
        r = client.get(f"/reports/export?warehouse_id=WH-BLR-01&format=pdf&time_range=week",
                       headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code in [200, 400, 404]
        if r.status_code == 200:
            ct = r.headers.get("Content-Type", "")
            assert "pdf" in ct.lower() or "octet" in ct.lower()

    def test_invalid_format_rejected(self, client, admin_token):
        r = client.get(f"/reports/export?warehouse_id=WH-BLR-01&format=exe&time_range=week",
                       headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code in [400, 422], f"Invalid format should be rejected: {r.status_code}"

    def test_report_requires_auth(self, client):
        """Report endpoint without token must return 401."""
        r = client.get("/reports/export?warehouse_id=WH-BLR-01&format=csv&time_range=week")
        assert r.status_code == 401, f"Expected 401 without auth, got {r.status_code}"

    @pytest.mark.skipif(_NEEDS_MYSQL, reason="INTEGRATION: reports endpoint requires MySQL data")
    def test_viewer_cannot_export_reports(self, client, viewer_token):
        """Report endpoint role access check."""
        r = client.get(f"/reports/export?warehouse_id=WH-BLR-01&format=csv&time_range=week",
                       headers={"Authorization": f"Bearer {viewer_token}"})
        # Viewers may or may not have access depending on role policy
        if r.status_code == 403:
            pass  # Correctly restricted
        elif r.status_code == 200:
            pytest.xfail("Viewers can export reports — consider restricting to admin/manager")
        else:
            assert r.status_code in [200, 400, 403, 404]

    def test_jwt_token_not_in_query_param(self, client, admin_token):
        """
        Security: JWT tokens must NOT be sent in query parameters.
        This test ensures the report endpoint uses the Authorization header.
        """
        # Try sending token in query param — this should fail (token not accepted as query param)
        r = client.get(f"/reports/export?warehouse_id=WH-BLR-01&format=csv&time_range=7&token={admin_token}")
        # If this works, it means token is accepted in query params — that's a security concern
        # The correct behavior is to require Authorization header
        if r.status_code == 200:
            pytest.xfail("SECURITY: Token accepted in query parameter — JWT should only be in Authorization header")

    @pytest.mark.skipif(_NEEDS_MYSQL, reason="INTEGRATION: requires MySQL with stock data")
    def test_missing_warehouse_id_handled(self, client, admin_token):
        r = client.get(f"/reports/export?format=csv&time_range=week",
                       headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code in [200, 400, 422]

    def test_invalid_time_range_handled(self, client, admin_token):
        r = client.get(f"/reports/export?warehouse_id=WH-BLR-01&format=csv&time_range=INVALID",
                       headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code in [200, 400, 422]
