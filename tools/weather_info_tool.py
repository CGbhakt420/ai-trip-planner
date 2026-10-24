from typing import Any, Literal

from langchain_core.tools import tool

from utils.weather_info import (
    get_current_weather as fetch_current_weather,
    get_weather_forecast as fetch_weather_forecast,
)


@tool
def get_current_weather(
    city: str,
    country_code: str | None = None,
    units: Literal["metric", "imperial", "standard"] = "metric",
) -> dict[str, Any]:
    """Get current observed weather for a city. Use metric for Celsius, imperial for Fahrenheit, or standard for Kelvin."""
    return fetch_current_weather(city, country_code, units)


@tool
def get_weather_forecast(
    city: str,
    country_code: str | None = None,
    days: int = 5,
    units: Literal["metric", "imperial", "standard"] = "metric",
) -> dict[str, Any]:
    """Get OpenWeatherMap's available five-day forecast grouped by local date."""
    return fetch_weather_forecast(city, country_code, days, units)