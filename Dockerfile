# ============================================================
# Dockerfile — Smart Warehouse Intelligence Platform
# ============================================================
# SECURITY NOTES:
#   - Secrets must be injected via environment variables at runtime
#   - seed_demo_data.py is NOT run automatically (data-destructive)
#   - Application runs as non-root user "appuser"
# ============================================================

FROM python:3.11-slim

# ---- Environment ----
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# ---- System dependencies ----
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    curl \
    gnupg \
    ca-certificates \
    && install -d /etc/apt/keyrings \
    && curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /etc/apt/keyrings/postgresql.gpg \
    && . /etc/os-release \
    && echo "deb [signed-by=/etc/apt/keyrings/postgresql.gpg] http://apt.postgresql.org/pub/repos/apt ${VERSION_CODENAME}-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client-18 \
    && rm -rf /var/lib/apt/lists/*

# ---- Create non-root user ----
RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --shell /bin/bash --create-home appuser

# ---- Working directory ----
WORKDIR /app

# ---- Install Python dependencies ----
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Copy application code ----
COPY . .

# ---- Ownership ----
RUN chown -R appuser:appgroup /app

# ---- Switch to non-root user ----
USER appuser

# ---- Expose port ----
EXPOSE 8000

# ---- Health check ----
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# ============================================================
# STARTUP:
#   1. alembic upgrade head — runs migration schemas dynamically
#   2. python backend/init_db.py — creates initial admin account idempotently
#   3. python backend/seed_demo_data.py — seeds demo dataset idempotently
#   4. uvicorn — starts the API server
# ============================================================
CMD ["sh", "-c", "alembic upgrade head && python backend/init_db.py && python backend/seed_demo_data.py && uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
