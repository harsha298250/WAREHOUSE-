import os
import logging
import json
from typing import Any, Optional
import redis
from backend.timeout_policy import REDIS_CONNECT_TIMEOUT, REDIS_SOCKET_TIMEOUT

logger = logging.getLogger("warehouse.redis")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Setup safe connection variables
_client: Optional[redis.Redis] = None
redis_available = False

if os.getenv("ENVIRONMENT") == "testing":
    redis_available = False
    logger.info("Redis test bypass: caching disabled for testing.")
else:
    try:
        _client = redis.Redis.from_url(
            REDIS_URL, 
            socket_connect_timeout=REDIS_CONNECT_TIMEOUT, 
            socket_timeout=REDIS_SOCKET_TIMEOUT,
            decode_responses=True
        )
        # Ping to check if connection is active
        _client.ping()
        redis_available = True
        logger.info("Connected to Redis successfully at: %s", REDIS_URL.split("@")[-1])
    except Exception as e:
        redis_available = False
        logger.warning("Redis connection failed. Caching will run in fail-safe/bypass mode: %s", e)


def get_redis_client() -> Optional[redis.Redis]:
    global redis_available, _client
    if not redis_available or _client is None:
        return None
    return _client


def get_cache(key: str) -> Optional[Any]:
    """Retrieve key value from Redis. Safely falls back to None if offline."""
    global redis_available
    client = get_redis_client()
    if not client:
        return None
    try:
        val = client.get(key)
        if val:
            try:
                return json.loads(val)
            except json.JSONDecodeError:
                return val
    except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
        logger.warning("Redis connection lost during get: %s", e)
        redis_available = False
    except Exception as e:
        logger.error("Redis get failed for key '%s': %s", key, e)
    return None


def set_cache(key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
    """Write key value to Redis with optional TTL expiration. Safely returns False if offline."""
    global redis_available
    client = get_redis_client()
    if not client:
        return False
    try:
        serialized = json.dumps(value)
        if ttl_seconds:
            client.setex(key, ttl_seconds, serialized)
        else:
            client.set(key, serialized)
        return True
    except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
        logger.warning("Redis connection lost during set: %s", e)
        redis_available = False
        return False
    except Exception as e:
        logger.error("Redis set failed for key '%s': %s", key, e)
        return False


def delete_cache(key: str) -> bool:
    """Remove key from Redis cache. Safely returns False if offline."""
    global redis_available
    client = get_redis_client()
    if not client:
        return False
    try:
        client.delete(key)
        return True
    except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
        logger.warning("Redis connection lost during delete: %s", e)
        redis_available = False
        return False
    except Exception as e:
        logger.error("Redis delete failed for key '%s': %s", key, e)
        return False


def check_redis_health() -> dict:
    """Returns connectivity details for diagnostic dashboards."""
    global redis_available, _client
    if os.getenv("ENVIRONMENT") == "testing":
        return {"status": "offline", "connected": False, "provider": "Redis (Test Mock)"}
    try:
        if _client is not None:
            _client.ping()
            redis_available = True
            return {"status": "healthy", "connected": True, "provider": "Redis"}
    except Exception:
        redis_available = False
        
    # Attempt reconnection
    try:
        temp_client = redis.Redis.from_url(
            REDIS_URL, 
            socket_connect_timeout=REDIS_CONNECT_TIMEOUT,
            socket_timeout=REDIS_SOCKET_TIMEOUT,
            decode_responses=True
        )
        temp_client.ping()
        _client = temp_client
        redis_available = True
        return {"status": "healthy", "connected": True, "provider": "Redis"}
    except Exception:
        pass
        
    return {"status": "offline", "connected": False, "provider": "Redis"}
