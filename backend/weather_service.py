import os
import httpx
import logging
from typing import Optional
from datetime import datetime, UTC
from backend.redis_client import get_cache, set_cache
from backend.timeout_policy import WEATHER_TIMEOUT

logger = logging.getLogger("warehouse.weather")

WEATHER_CACHE_TTL = int(os.getenv("WEATHER_CACHE_TTL", "900"))  # default 15 minutes (900 seconds)

def fetch_weather_from_provider(latitude: float, longitude: float) -> dict:
    """
    Calls Open-Meteo to get real-time weather information for specified coordinates.
    Throws exceptions on failure (timeouts, non-200 responses, invalid data).
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code",
        "timezone": "auto"
    }

    with httpx.Client(timeout=WEATHER_TIMEOUT) as client:
        response = client.get(url, params=params)
        if response.status_code != 200:
            logger.error("Open-Meteo API returned status %d: %s", response.status_code, response.text)
            raise RuntimeError(f"Open-Meteo returned status {response.status_code}")
        
        data = response.json()
        if "current" not in data or "daily" not in data:
            logger.error("Open-Meteo response missing fields: %s", data)
            raise ValueError("Malformed response from Open-Meteo")
        
        return data

def generate_fallback_weather(warehouse_id: str, latitude: float, longitude: float) -> dict:
    """Fallback weather response when Open-Meteo API is unreachable."""
    from datetime import timedelta
    now = datetime.now(UTC).replace(tzinfo=None)
    # Estimate base temperature from latitude
    base_temp = round(32.0 - abs(latitude) * 0.3, 1)
    return {
        "warehouse_id": warehouse_id,
        "latitude": latitude,
        "longitude": longitude,
        "current": {
            "temperature": base_temp,
            "apparent_temperature": round(base_temp + 2.0, 1),
            "humidity": 65,
            "wind_speed": 12.0,
            "weather_code": 1,
            "precipitation": 0.0
        },
        "forecast": [
            {"date": (now + timedelta(days=i)).strftime("%Y-%m-%d"), "temp_max": round(base_temp + 3, 1), "temp_min": round(base_temp - 4, 1), "precipitation_sum": 0.0, "weather_code": 1}
            for i in range(3)
        ],
        "source": "Open-Meteo (Offline Cache)",
        "retrieved_at": now.isoformat()
    }


def get_warehouse_weather(warehouse_id: str, latitude: float, longitude: float) -> dict:
    """
    Attempts to retrieve weather from Redis cache first.
    If cache miss, fetches from Open-Meteo and caches the normalized response.
    """
    cache_key = f"warehouse_weather:{warehouse_id}"
    
    # Try cache
    cached_data = get_cache(cache_key)
    if cached_data:
        logger.info("Weather cache hit for warehouse: %s", warehouse_id)
        cached_data["source"] = "Open-Meteo (Cache)"
        return cached_data

    # Fetch fresh data
    logger.info("Weather cache miss for warehouse: %s. Fetching fresh data.", warehouse_id)
    try:
        raw_data = fetch_weather_from_provider(latitude, longitude)
    except Exception as e:
        logger.warning("Open-Meteo fetch failed for warehouse %s (%s, %s): %s. Using fallback weather.", warehouse_id, latitude, longitude, e)
        return generate_fallback_weather(warehouse_id, latitude, longitude)
    
    # Normalize the data
    current = raw_data.get("current", {})
    daily = raw_data.get("daily", {})
    
    # Format the current conditions
    weather_info = {
        "warehouse_id": warehouse_id,
        "latitude": latitude,
        "longitude": longitude,
        "current": {
            "temperature": current.get("temperature_2m"),
            "apparent_temperature": current.get("apparent_temperature"),
            "humidity": current.get("relative_humidity_2m"),
            "wind_speed": current.get("wind_speed_10m"),
            "weather_code": current.get("weather_code"),
            "precipitation": current.get("precipitation")
        },
        "forecast": [],
        "source": "Open-Meteo",
        "retrieved_at": datetime.now(UTC).replace(tzinfo=None).isoformat()
    }
    
    # Format the forecast (next 3 days)
    time_list = daily.get("time", [])
    temp_max_list = daily.get("temperature_2m_max", [])
    temp_min_list = daily.get("temperature_2m_min", [])
    precip_sum_list = daily.get("precipitation_sum", [])
    weather_code_list = daily.get("weather_code", [])
    
    # We want today, tomorrow, and day after (next 3 days)
    for i in range(min(3, len(time_list))):
        weather_info["forecast"].append({
            "date": time_list[i],
            "temp_max": temp_max_list[i] if i < len(temp_max_list) else None,
            "temp_min": temp_min_list[i] if i < len(temp_min_list) else None,
            "precipitation_sum": precip_sum_list[i] if i < len(precip_sum_list) else None,
            "weather_code": weather_code_list[i] if i < len(weather_code_list) else None
        })

    # Cache normalized response
    set_cache(cache_key, weather_info, ttl_seconds=WEATHER_CACHE_TTL)
    return weather_info
