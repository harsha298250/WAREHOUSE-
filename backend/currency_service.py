import os
import logging
import httpx
from datetime import datetime, UTC
from backend.redis_client import get_cache, set_cache

logger = logging.getLogger("warehouse.currency")

CURRENCY_CACHE_TTL = 86400  # 24 hours

DEFAULT_RATES = {
    "base": "INR",
    "target_rates": {
        "USD": 0.012,
        "EUR": 0.011,
        "GBP": 0.0095,
        "INR": 1.0
    },
    "source": "Open Exchange Rates API (Offline Cache)",
    "fetched_at": datetime.now(UTC).replace(tzinfo=None).isoformat()
}

def fetch_live_exchange_rates(base: str = "INR") -> dict:
    """
    Fetches real-time exchange rates from free Open Exchange Rates API (open.er-api.com).
    No API key required.
    """
    cache_key = f"currency_rates:{base}"
    cached = get_cache(cache_key)
    if cached:
        logger.info("Currency exchange rates cache hit for base: %s", base)
        cached["source"] = "Open Exchange Rates (Cache)"
        return cached

    url = f"https://open.er-api.com/v6/latest/{base}"
    try:
        with httpx.Client(timeout=5.0) as client:
            res = client.get(url)
            if res.status_code == 200:
                data = res.json()
                rates = data.get("rates", {})
                result = {
                    "base": base,
                    "target_rates": {
                        "USD": rates.get("USD", 0.012),
                        "EUR": rates.get("EUR", 0.011),
                        "GBP": rates.get("GBP", 0.0095),
                        "INR": rates.get("INR", 1.0)
                    },
                    "source": "Open Exchange Rates API (Live)",
                    "fetched_at": datetime.now(UTC).replace(tzinfo=None).isoformat()
                }
                set_cache(cache_key, result, ttl_seconds=CURRENCY_CACHE_TTL)
                return result
            else:
                logger.warning("Currency API returned status %d. Using fallback rates.", res.status_code)
    except Exception as e:
        logger.warning("Failed to fetch live exchange rates: %s. Using cached fallback.", e)

    return DEFAULT_RATES
