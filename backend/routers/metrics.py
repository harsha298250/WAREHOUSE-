import os
from fastapi import APIRouter, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest, Counter, Histogram, Gauge

router = APIRouter()

# ---- Metric Declarations ----

# API Metrics
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total count of HTTP requests processed",
    ["method", "endpoint", "status"]
)

HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency histogram",
    ["method", "endpoint"]
)

# Database Metrics
DATABASE_POOL_SIZE = Gauge(
    "database_pool_size",
    "Current configuration size of database connection pool"
)

DATABASE_POOL_OVERFLOW = Gauge(
    "database_pool_overflow",
    "Current configuration overflow count of database connection pool"
)

# Background Jobs Metrics
CELERY_TASKS_TOTAL = Counter(
    "celery_tasks_total",
    "Total count of background Celery tasks triggered",
    ["task_name", "status"]
)

CELERY_TASK_DURATION = Histogram(
    "celery_task_duration_seconds",
    "Celery task run duration histogram",
    ["task_name"]
)

# Simulation Metrics
SIMULATION_TICKS_TOTAL = Counter(
    "simulation_ticks_total",
    "Total simulation ticks executed",
    ["warehouse_id"]
)

SIMULATION_TICK_DURATION = Histogram(
    "simulation_tick_duration_seconds",
    "Duration of a simulation tick in seconds",
    ["warehouse_id"]
)

# Warehouse Metrics
WAREHOUSE_ACTIVE_TASKS = Gauge(
    "warehouse_active_tasks_total",
    "Number of active tasks currently in processing",
    ["warehouse_id", "priority"]
)

ROBOT_UTILIZATION = Gauge(
    "robot_utilization_ratio",
    "Utilization ratio of the robot fleet",
    ["warehouse_id"]
)

CONGESTION_EVENTS = Counter(
    "warehouse_congestion_events_total",
    "Total number of grid congestion warnings triggered",
    ["warehouse_id"]
)

# AI Metrics
AI_INFERENCE_DURATION = Histogram(
    "ai_inference_duration_seconds",
    "AI forecasting or anomaly detection run duration",
    ["intelligence_type"]  # forecast | anomaly | ABC
)

# Initialize static configurations
DATABASE_POOL_SIZE.set(10) # Matches database.py pool_size
DATABASE_POOL_OVERFLOW.set(20) # Matches database.py max_overflow

@router.get("/metrics")
def get_metrics():
    """Endpoint scraped by Prometheus to collect system metrics."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
