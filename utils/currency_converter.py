import math
import re
from typing import Any

import requests

from utils.api_utils import require_api_key


EXCHANGE_RATE_API_URL = "https://v6.exchangerate-api.com/v6"
CURRENCY_CODE_PATTERN = re.compile(r"^[A-Za-z]{3}$")


def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str,
) -> dict[str, Any]:
    """Convert an amount between currencies using ExchangeRate-API."""
    if isinstance(amount, bool) or not isinstance(amount, (int, float)):
        raise ValueError("Amount must be a number.")
    if amount < 0:
        raise ValueError("Amount cannot be negative.")
    if not math.isfinite(amount):
        raise ValueError("Amount must be finite.")

    base = from_currency.strip().upper()
    target = to_currency.strip().upper()
    if not CURRENCY_CODE_PATTERN.fullmatch(base):
        raise ValueError("Source currency must be a three-letter ISO code.")
    if not CURRENCY_CODE_PATTERN.fullmatch(target):
        raise ValueError("Target currency must be a three-letter ISO code.")

    api_key = require_api_key("EXCHANGE_RATE_API_KEY")
    url = f"{EXCHANGE_RATE_API_URL}/{api_key}/pair/{base}/{target}/{amount}"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code >= 400:
            raise RuntimeError(
                f"ExchangeRate-API returned HTTP {response.status_code}."
            )
        data = response.json()
    except requests.RequestException:
        raise RuntimeError("Could not connect to ExchangeRate-API.") from None
    except ValueError:
        raise RuntimeError("ExchangeRate-API returned invalid JSON.") from None

    if not isinstance(data, dict):
        raise RuntimeError("ExchangeRate-API returned an unexpected response.")
    if data.get("result") != "success":
        error_type = data.get("error-type", "unknown provider error")
        raise ValueError(f"Currency conversion failed: {error_type}.")

    conversion_rate = data.get("conversion_rate")
    converted_amount = data.get("conversion_result")
    if (
        isinstance(conversion_rate, bool)
        or not isinstance(conversion_rate, (int, float))
        or isinstance(converted_amount, bool)
        or not isinstance(converted_amount, (int, float))
        or not math.isfinite(conversion_rate)
        or not math.isfinite(converted_amount)
    ):
        raise RuntimeError("ExchangeRate-API omitted the conversion result.")

    return {
        "provider": "ExchangeRate-API",
        "amount": amount,
        "from_currency": base,
        "to_currency": target,
        "conversion_rate": conversion_rate,
        "converted_amount": converted_amount,
        "rate_updated_at": data.get("time_last_update_utc"),
    }