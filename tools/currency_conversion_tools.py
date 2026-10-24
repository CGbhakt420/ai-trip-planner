from typing import Any

from langchain_core.tools import tool

from utils.currency_converter import convert_currency as exchange_currency


@tool
def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str,
) -> dict[str, Any]:
    """Convert a travel budget between ISO 4217 currencies using the current exchange rate."""
    return exchange_currency(amount, from_currency, to_currency)