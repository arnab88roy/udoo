import httpx
from datetime import datetime, timezone

async def fetch_exchange_rate(
    from_currency: str,
    to_currency: str,
) -> dict:
    """
    Fetches live exchange rate from exchangerate.host (free, no API key).

    Endpoint: https://api.exchangerate.host/live
    Falls back gracefully — never crashes if API is unavailable.

    Returns:
        {
            "rate": float,
            "from": str,
            "to": str,
            "fetched_at": datetime,
            "source": str,
            "success": bool,
            "error": Optional[str]
        }
    """
    if from_currency.upper() == to_currency.upper():
        return {
            "rate": 1.0,
            "from": from_currency.upper(),
            "to": to_currency.upper(),
            "fetched_at": datetime.now(timezone.utc),
            "source": "identity",
            "success": True,
            "error": None
        }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Note: The free API might have changed or have usage limits.
            # Using the documented endpoint as per instructions.
            response = await client.get(
                "https://api.exchangerate.host/live",
                params={
                    "source": from_currency.upper(),
                    "currencies": to_currency.upper(),
                    "format": 1
                }
            )
            data = response.json()

            if data.get("success"):
                key = f"{from_currency.upper()}{to_currency.upper()}"
                rate = data["quotes"].get(key)
                if rate:
                    return {
                        "rate": float(rate),
                        "from": from_currency.upper(),
                        "to": to_currency.upper(),
                        "fetched_at": datetime.now(timezone.utc),
                        "source": "exchangerate_host",
                        "success": True,
                        "error": None
                    }

    except Exception as e:
        pass

    # Graceful fallback — return rate of 1.0 with error flag
    return {
        "rate": 1.0,
        "from": from_currency.upper(),
        "to": to_currency.upper(),
        "fetched_at": datetime.now(timezone.utc),
        "source": "fallback",
        "success": False,
        "error": "Exchange rate fetch failed. Please enter rate manually."
    }
