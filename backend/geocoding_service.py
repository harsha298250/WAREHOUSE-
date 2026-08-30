import logging
import urllib.parse
import time
import requests

logger = logging.getLogger("warehouse.geocoding")

def geocode_address(name: str, city: str, state: str, country: str, location: str) -> tuple:
    """
    Forward geocode an address into (latitude, longitude, display_name).
    Tries multiple fallback search queries in order of descending specificity.
    """
    headers = {
        "User-Agent": "WarehouseOS-Observability/1.0"
    }

    # Gather search queries:
    # 1. Full combination of location, city, state, country
    # 2. Location alone (since it is user-supplied address)
    # 3. City + State + Country
    # 4. State + Country
    # 5. Name (as last resort, e.g. "Amaravati")
    queries = []

    parts = [p.strip() for p in [location, city, state, country] if p and p.strip()]
    if parts:
        queries.append(", ".join(parts))

    if location and location.strip():
        queries.append(location.strip())

    city_state_country = ", ".join([p.strip() for p in [city, state, country] if p and p.strip()])
    if city_state_country:
        queries.append(city_state_country)

    state_country = ", ".join([p.strip() for p in [state, country] if p and p.strip()])
    if state_country:
        queries.append(state_country)

    if name and name.strip():
        queries.append(name.strip())

    # Deduplicate queries while preserving priority order
    unique_queries = []
    for q in queries:
        if q not in unique_queries:
            unique_queries.append(q)

    logger.info("GEOCODING: Generated geocoding candidate queries: %s", unique_queries)

    for i, q in enumerate(unique_queries):
        logger.info("GEOCODING: Attempting query %s/%s: '%s'", i + 1, len(unique_queries), q)
        try:
            # Respect rate limit of Nominatim (limit requests)
            if i > 0:
                time.sleep(0.5)

            url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(q)}&format=json&limit=1"
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    lat = float(data[0]["lat"])
                    lon = float(data[0]["lon"])
                    display_name = data[0]["display_name"]
                    logger.info("GEOCODING: Successfully resolved to (%s, %s): '%s'", lat, lon, display_name)
                    return lat, lon, display_name
                else:
                    logger.warning("GEOCODING: Empty results for query '%s'", q)
            else:
                logger.error("GEOCODING: Nominatim returned status code %s for '%s'", response.status_code, q)
        except Exception as e:
            logger.error("GEOCODING: Exception during geocoding attempt: %s", e)

    logger.error("GEOCODING: All geocoding attempts failed for address inputs.")
    return None, None, None


def reverse_geocode(lat: float, lon: float) -> str:
    """
    Reverse geocode latitude/longitude coordinates into a display address string.
    """
    headers = {
        "User-Agent": "WarehouseOS-Observability/1.0"
    }
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        logger.info("GEOCODING: Reverse geocoding (%s, %s)...", lat, lon)
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data and "display_name" in data:
                logger.info("GEOCODING: Reverse geocoded successfully to '%s'", data["display_name"])
                return data["display_name"]
            else:
                logger.warning("GEOCODING: Reverse geocoding returned no display_name in response")
        else:
            logger.error("GEOCODING: Reverse geocoding returned status code %s", response.status_code)
    except Exception as e:
        logger.error("GEOCODING: Exception during reverse geocoding: %s", e)
    return None
