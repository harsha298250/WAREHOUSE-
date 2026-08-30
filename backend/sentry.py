import os
import logging
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

logger = logging.getLogger("warehouse.sentry")

def sanitize_event_data(event, hint):
    """
    Sentry before_send hook to filter out sensitive values.
    Scrubs passwords, auth tokens, OTP keys, and secrets from request payloads
    and exception trace variables.
    """
    # Scrub request headers or request body details
    if "request" in event:
        request = event["request"]
        # Scrub authorization header
        if "headers" in request:
            headers = request["headers"]
            for key in list(headers.keys()):
                if key.lower() in ["authorization", "cookie", "x-auth-token", "proxy-authorization"]:
                    headers[key] = "[SCRUBBED]"
        
        # Scrub request body payload values
        if "data" in request:
            data = request["data"]
            if isinstance(data, dict):
                for key in list(data.keys()):
                    if any(sensitive in key.lower() for sensitive in ["password", "passkey", "otp", "secret", "token"]):
                        data[key] = "[SCRUBBED]"
            elif isinstance(data, str):
                # Simple string check/replace for passwords/secrets
                for sensitive in ["password", "passkey", "otp", "secret"]:
                    if sensitive in data.lower():
                        event["request"]["data"] = "[SCRUBBED BODY CONTAINING SENSITIVE DATA]"
                        break

    # Scrub exception local variables
    if "exception" in event:
        exc_values = event["exception"].get("values", [])
        for val in exc_values:
            if "stacktrace" in val:
                frames = val["stacktrace"].get("frames", [])
                for frame in frames:
                    if "vars" in frame:
                        vars_dict = frame["vars"]
                        for var_key in list(vars_dict.keys()):
                            if any(sensitive in var_key.lower() for sensitive in ["password", "passkey", "otp", "secret", "token", "key"]):
                                vars_dict[var_key] = "[SCRUBBED]"
                                
    return event

def init_sentry():
    sentry_dsn = os.getenv("SENTRY_DSN")
    env = os.getenv("ENVIRONMENT", "development")
    
    if env in ("testing", "development"):
        logger.info("Sentry initialization bypassed in %s environment.", env)
        return
        
    if not sentry_dsn:
        logger.info("Sentry DSN not configured; error monitoring is inactive.")
        return
        
    try:
        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=env,
            integrations=[FastApiIntegration()],
            before_send=sanitize_event_data,
            # Set traces_sample_rate to 1.0 to capture 100% of transactions for performance monitoring.
            traces_sample_rate=0.1 if env == "production" else 1.0,
            # Set profiles_sample_rate to 1.0 to profile 100% of transactions.
            profiles_sample_rate=0.1 if env == "production" else 1.0,
        )
        logger.info("Sentry SDK successfully initialized for environment: %s", env)
    except Exception as e:
        logger.error("Failed to initialize Sentry SDK: %s", e)
