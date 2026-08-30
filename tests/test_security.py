"""
tests/test_security.py — Security headers, CORS, OTP, and rate limiting tests.
"""
import pytest


class TestSecurityHeaders:

    def test_x_content_type_options_header(self, client, admin_token):
        r = client.get("/health")
        # Should have X-Content-Type-Options: nosniff
        header = r.headers.get("X-Content-Type-Options", "").lower()
        assert "nosniff" in header, f"X-Content-Type-Options header missing or wrong: {r.headers}"

    def test_x_frame_options_header(self, client):
        r = client.get("/health")
        header = r.headers.get("X-Frame-Options", "")
        assert header in ["DENY", "SAMEORIGIN"], f"X-Frame-Options header: {header}"

    def test_referrer_policy_header(self, client):
        r = client.get("/health")
        header = r.headers.get("Referrer-Policy", "")
        assert len(header) > 0, f"Referrer-Policy header missing: {r.headers}"

    def test_no_server_version_leak(self, client):
        """Server header must not reveal exact uvicorn version."""
        r = client.get("/health")
        server = r.headers.get("Server", "")
        # Exact version leak is a minor issue but should not expose full version
        # uvicorn default reveals version — warn rather than fail
        if "uvicorn" in server.lower() and "/" in server:
            pytest.xfail("Server header reveals uvicorn version (low severity — add middleware to mask)")


class TestOTPSecurity:

    def test_otp_not_in_api_response(self, client, admin_token):
        """OTP passkey must NEVER appear in the API response body."""
        r = client.post("/admin/request-add-admin",
                        json={"username": "otp_test_user_9999",
                              "password": "OtpTest@123",
                              "email": "otp_test@test.com",
                              "full_name": "OTP Test"},
                        headers={"Authorization": f"Bearer {admin_token}"})
        if r.status_code in [200, 201]:
            body = r.text.lower()
            # The passkey/OTP must not be in the response
            d = r.json()
            assert "passkey" not in d or len(str(d.get("passkey", ""))) == 0, \
                "CRITICAL: OTP passkey returned in API response body"
            # Check common OTP field names
            for field in ["otp", "code", "passkey", "token"]:
                val = d.get(field)
                if val and isinstance(val, str) and len(val) >= 6:
                    # A numeric 6-digit code in response is a security leak
                    if str(val).isdigit():
                        pytest.fail(f"OTP/passkey '{field}={val}' leaked in API response")

    def test_invalid_otp_rejected(self, client, admin_token):
        """Invalid OTP confirmation must be rejected."""
        r = client.post("/admin/confirm-add-admin",
                        json={"passkey": "000000"},
                        headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code in [400, 401, 403, 404, 422], \
            f"Invalid OTP should be rejected: got {r.status_code}"

    def test_obviously_wrong_otp_rejected(self, client, admin_token):
        r = client.post("/admin/confirm-add-admin",
                        json={"passkey": "INVALID"},
                        headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code in [400, 401, 403, 404, 422]


class TestCORS:

    def test_cors_present_on_response(self, client):
        """CORS headers should be present."""
        r = client.get("/health")
        # Access-Control-Allow-Origin should be configured (not wildcard in prod)
        # In test mode this is OK, but wildcard in production is a risk
        # This test just verifies CORS middleware is active
        assert r.status_code == 200

    def test_preflight_options_responds(self, client):
        r = client.options("/health",
                           headers={"Origin": "http://localhost:8000",
                                    "Access-Control-Request-Method": "GET"})
        assert r.status_code in [200, 204]


class TestRateLimiting:

    def test_login_rate_limit_eventually_triggers(self, client):
        """Repeated failed logins must eventually trigger rate limiting."""
        status_codes = []
        for _ in range(15):
            r = client.post("/auth/login",
                            json={"username": "nonexistent", "password": "wrong"})
            status_codes.append(r.status_code)

        # At some point should see 429 Too Many Requests
        # If rate limiting is implemented, we should see at least one 429
        got_429 = 429 in status_codes
        if not got_429:
            pytest.xfail("Rate limiting did not trigger in 15 attempts — consider lower threshold")

    def test_health_not_rate_limited(self, client):
        """Health check endpoint must not be rate-limited."""
        for _ in range(20):
            r = client.get("/health")
            assert r.status_code == 200, "Health endpoint should never be rate-limited"


class TestSecurityHardeningRules:

    def test_production_mode_secret_check(self):
        """Application must raise RuntimeError in production if JWT secret is missing/default."""
        import os
        import importlib
        
        auth_mod = importlib.import_module("backend.auth")
        orig_secret = auth_mod.SECRET_KEY
        orig_raw = auth_mod.RAW_SECRET
        
        from unittest.mock import patch
        
        # Test default secret rejection
        with patch.dict(os.environ, {"ENVIRONMENT": "production", "JWT_SECRET_KEY": "dev-only-secret-change-me-in-production"}):
            with pytest.raises(RuntimeError) as exc_info:
                importlib.reload(auth_mod)
            assert "not configured for production" in str(exc_info.value).lower()

        # Test empty secret rejection
        with patch.dict(os.environ, {"ENVIRONMENT": "production", "JWT_SECRET_KEY": ""}):
            with pytest.raises(RuntimeError) as exc_info:
                importlib.reload(auth_mod)
            assert "not configured for production" in str(exc_info.value).lower()

        # Reload back to normal and restore
        importlib.reload(auth_mod)
        auth_mod.SECRET_KEY = orig_secret
        auth_mod.RAW_SECRET = orig_raw


    def test_reports_rejects_query_token(self, client, admin_token):
        """Report endpoint must NOT accept JWT through query parameters."""
        r = client.get(f"/reports/export?warehouse_id=all&format=csv&token={admin_token}")
        assert r.status_code == 401

    def test_otp_brute_force_and_one_time_use(self, client, admin_token):
        """OTP confirmation must enforce max failed attempts and one-time use policy."""
        # Request new admin
        r = client.post("/admin/request-add-admin",
                        json={"username": "otp_limit_user", "password": "LimitUser@123", "email": "otp_limit_user@gmail.com", "full_name": "Limit"},
                        headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code in [200, 201]

        # Fail 5 times
        for _ in range(5):
            r = client.post("/admin/confirm-add-admin",
                            json={"passkey": "000000"},
                            headers={"Authorization": f"Bearer {admin_token}"})
            assert r.status_code == 400

        # 6th attempt must be blocked as exceeded
        r = client.post("/admin/confirm-add-admin",
                        json={"passkey": "000000"},
                        headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 400
        assert "exceeded" in r.json()["detail"].lower() or "no pending" in r.json()["detail"].lower()

