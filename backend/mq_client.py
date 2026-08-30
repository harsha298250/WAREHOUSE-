import os
import json
import logging
from typing import Any, Dict, Optional
import pika
from backend.timeout_policy import RABBITMQ_CONNECT_TIMEOUT, RABBITMQ_SOCKET_TIMEOUT

logger = logging.getLogger("warehouse.rabbitmq")

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672//")
EXCHANGE_NAME = "warehouse_events"
DLX_EXCHANGE_NAME = "dlx.warehouse_events"
DLQ_QUEUE_NAME = "dlq.warehouse_events"

_connection: Optional[pika.BlockingConnection] = None
_channel: Optional[pika.adapters.blocking_connection.BlockingChannel] = None
mq_available = False

def init_rabbitmq(fast_reconnect: bool = False):
    """Tries to connect to RabbitMQ and declare exchanges and queues."""
    global _connection, _channel, mq_available
    if os.getenv("ENVIRONMENT") == "testing":
        mq_available = False
        return
    try:
        parameters = pika.URLParameters(RABBITMQ_URL)
        if fast_reconnect:
            parameters.connection_attempts = 1
            parameters.retry_delay = 1
            parameters.socket_timeout = RABBITMQ_SOCKET_TIMEOUT
        else:
            parameters.connection_attempts = 3
            parameters.retry_delay = 2
            parameters.socket_timeout = RABBITMQ_SOCKET_TIMEOUT
        
        _connection = pika.BlockingConnection(parameters)
        _channel = _connection.channel()
        
        # Enable publisher acknowledgements
        _channel.confirm_delivery()
        
        # 1. Setup Dead Letter Exchange and Queue
        _channel.exchange_declare(exchange=DLX_EXCHANGE_NAME, exchange_type="topic", durable=True)
        _channel.queue_declare(queue=DLQ_QUEUE_NAME, durable=True)
        _channel.queue_bind(queue=DLQ_QUEUE_NAME, exchange=DLX_EXCHANGE_NAME, routing_key="dlq.#")
        
        # 2. Setup Main Topic Exchange
        _channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="topic", durable=True)
        
        # 3. Setup standard queues for simulation, analytics, and notification logging
        # We declare them and bind them to demonstrate a durable queue architecture
        _channel.queue_declare(
            queue="warehouse.billing_log",
            durable=True,
            arguments={
                "x-dead-letter-exchange": DLX_EXCHANGE_NAME,
                "x-dead-letter-routing-key": "dlq.billing"
            }
        )
        _channel.queue_bind(queue="warehouse.billing_log", exchange=EXCHANGE_NAME, routing_key="warehouse.*.ORDER_COMPLETED")
        
        mq_available = True
        logger.info("Connected to RabbitMQ successfully at: %s", RABBITMQ_URL.split("@")[-1])
    except Exception as e:
        mq_available = False
        _connection = None
        _channel = None
        logger.warning("RabbitMQ connection failed. Async messaging will run in bypass/log-only mode: %s", e)

# Trigger initialization on module import
init_rabbitmq()


def get_channel() -> Optional[pika.adapters.blocking_connection.BlockingChannel]:
    global mq_available, _connection, _channel
    if not mq_available or _connection is None or _channel is None:
        # Retry connection once (fast reconnect)
        init_rabbitmq(fast_reconnect=True)
        if not mq_available:
            return None
            
    try:
        if _connection.is_closed or _channel.is_closed:
            init_rabbitmq(fast_reconnect=True)
            if not mq_available:
                return None
        return _channel
    except Exception:
        mq_available = False
        return None


def publish_event(event_type: str, category: str, payload: Dict[str, Any]) -> bool:
    """
    Publish an event to the RabbitMQ topic exchange.
    Routing Key schema: warehouse.<category>.<event_type>
    E.g.: warehouse.orders.ORDER_CREATED
    Safely degrades to log warning and returns False if broker is down.
    """
    channel = get_channel()
    if not channel:
        logger.info("RabbitMQ bypass: logging published event '%s' locally: %s", event_type, payload)
        return False
        
    routing_key = f"warehouse.{category}.{event_type}"
    try:
        body = json.dumps({
            "event_type": event_type,
            "category": category,
            "routing_key": routing_key,
            "payload": payload
        })
        
        # Publish with persistence delivery mode 2
        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=routing_key,
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=2, # make message persistent
                content_type="application/json"
            )
        )
        logger.info("Published event to RabbitMQ: %s", routing_key)
        return True
    except Exception as e:
        logger.error("Failed to publish RabbitMQ message for '%s': %s", event_type, e)
        return False


def check_rabbitmq_health() -> dict:
    """Returns connectivity details for diagnostic dashboards."""
    global mq_available, _connection
    if os.getenv("ENVIRONMENT") == "testing":
        return {"status": "offline", "connected": False, "provider": "RabbitMQ (Test Mock)"}
    try:
        if _connection is not None and _connection.is_open:
            mq_available = True
            return {"status": "healthy", "connected": True, "provider": "RabbitMQ"}
    except Exception:
        mq_available = False
        
    # Attempt reconnection
    init_rabbitmq(fast_reconnect=True)
    if mq_available:
        return {"status": "healthy", "connected": True, "provider": "RabbitMQ"}
        
    return {"status": "offline", "connected": False, "provider": "RabbitMQ"}
