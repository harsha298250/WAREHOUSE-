# timeout_policy.py — Centralized timeout values for all external service integrations.
import os

# 1. Critical/Synchronous interactive services (Fast response, fail fast)
OAUTH_TIMEOUT = float(os.getenv("OAUTH_TIMEOUT", "4.0"))            # Google OAuth tokeninfo call
WEATHER_TIMEOUT = float(os.getenv("WEATHER_TIMEOUT", "2.0"))        # Open-Meteo current weather API

# 2. Redis Caching & Support service (Bypass cache on lag)
REDIS_CONNECT_TIMEOUT = float(os.getenv("REDIS_CONNECT_TIMEOUT", "2.0"))  # Time to establish socket connection
REDIS_SOCKET_TIMEOUT = float(os.getenv("REDIS_SOCKET_TIMEOUT", "2.0"))    # Time to receive command response

# 3. RabbitMQ & Messaging (Non-blocking publishing)
RABBITMQ_CONNECT_TIMEOUT = float(os.getenv("RABBITMQ_CONNECT_TIMEOUT", "2.0"))
RABBITMQ_SOCKET_TIMEOUT = float(os.getenv("RABBITMQ_SOCKET_TIMEOUT", "2.0"))

# 4. Asynchronous / Background processing / Large API payloads
GEMINI_TIMEOUT = float(os.getenv("GEMINI_TIMEOUT", "15.0"))         # Gemini AI Assistant generation timeout
RESEND_TIMEOUT = float(os.getenv("RESEND_TIMEOUT", "8.0"))          # Resend API email dispatch
S3_CONNECT_TIMEOUT = float(os.getenv("S3_CONNECT_TIMEOUT", "4.0"))   # Backblaze B2 connection timeout
S3_READ_TIMEOUT = float(os.getenv("S3_READ_TIMEOUT", "12.0"))        # Backblaze B2 upload/download/read timeout

# 5. Diagnostic Health Checks (Minimal delay to prevent endpoint hanging)
HEALTH_CHECK_TIMEOUT = float(os.getenv("HEALTH_CHECK_TIMEOUT", "1.5"))
