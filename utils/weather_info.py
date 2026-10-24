
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Literal

import requests

from utils.api_utils import require_api_key


OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"
WeatherUnits = Literal["metric", "imperial", "standard"]


def _validate_location(city: str, units: str) -> None:
    if not city.strip():
        raise ValueError("A city or location is required.")
    if units not in {"metric", "imperial", "standard"}:
        raise ValueError("Units must be metric, imperial, or standard.")


def _request_weather(endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
    try:
        response = requests.get(
            f"{OPENWEATHER_BASE_URL}/{endpoint}",
            params=params,
            timeout=15,
        )
        if response.status_code >= 400:
            raise RuntimeError(
                f"OpenWeatherMap returned HTTP {response.status_code}."
            )
        data = response.json()
    except ValueError:
        raise RuntimeError("OpenWeatherMap returned invalid JSON.") from None
    except requests.RequestException:
        raise RuntimeError("Could not connect to OpenWeatherMap.") from None

    if not isinstance(data, dict):
        raise RuntimeError("OpenWeatherMap returned an unexpected response.")
    if data.get("cod") not in (None, 200, "200"):
        message = data.get("message", "request failed")
        raise RuntimeError(f"OpenWeatherMap error: {message}")
    return data


def _weather_location(city: str, country_code: str | None) -> str:
    city = city.strip()
    country_code = country_code.strip() if country_code else ""
    if country_code and "," not in city:
        return f"{city},{country_code}"
    return city


def get_current_weather(
    city: str,
    country_code: str | None = None,
    units: WeatherUnits = "metric",
) -> dict[str, Any]:
    """Return current conditions for a city using OpenWeatherMap."""
    _validate_location(city, units)
    data = _request_weather(
        "weather",
        {
            "q": _weather_location(city, country_code),
            "appid": require_api_key("OPENWEATHERMAP_API_KEY"),
            "units": units,
        },
    )

    weather = data.get("weather")
    main = data.get("main")
    system = data.get("sys", {})
    wind = data.get("wind", {})
    if (
        not isinstance(weather, list)
        or not weather
        or not isinstance(main, dict)
        or not isinstance(system, dict)
        or not isinstance(wind, dict)
        or not isinstance(weather[0], dict)
    ):
        raise RuntimeError("OpenWeatherMap omitted current weather details.")

    description = weather[0].get("description", "No description available")
    return {
        "provider": "OpenWeatherMap",
        "location": data.get("name", city),
        "country": system.get("country"),
        "observed_at_utc": datetime.fromtimestamp(
            data["dt"], tz=timezone.utc
        ).isoformat()
        if isinstance(data.get("dt"), (int, float))
        else None,
        "conditions": description,
        "temperature": main.get("temp"),
        "feels_like": main.get("feels_like"),
        "temperature_min": main.get("temp_min"),
        "temperature_max": main.get("temp_max"),
        "humidity_percent": main.get("humidity"),
        "wind_speed": wind.get("speed"),
        "units": units,
    }


def get_weather_forecast(
    city: str,
    country_code: str | None = None,
    days: int = 5,
    units: WeatherUnits = "metric",
) -> dict[str, Any]:
    """Return the available 3-hour forecast, grouped by local calendar day."""
    _validate_location(city, units)
    if isinstance(days, bool) or not isinstance(days, int) or not 1 <= days <= 5:
        raise ValueError("Forecast days must be between 1 and 5.")

    data = _request_weather(
        "forecast",
        {
            "q": _weather_location(city, country_code),
            "appid": require_api_key("OPENWEATHERMAP_API_KEY"),
            "units": units,
        },
    )
    forecast_items = data.get("list")
    city_data = data.get("city", {})
    if not isinstance(forecast_items, list) or not isinstance(city_data, dict):
        raise RuntimeError("OpenWeatherMap omitted forecast details.")

    timezone_offset = city_data.get("timezone", 0)
    if isinstance(timezone_offset, bool) or not isinstance(timezone_offset, int):
        timezone_offset = 0
    local_offset = timezone(timedelta(seconds=timezone_offset))
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for item in forecast_items:
        if not isinstance(item, dict) or not isinstance(item.get("dt"), (int, float)):
            continue
        local_time = datetime.fromtimestamp(item["dt"], tz=local_offset)
        main = item.get("main", {})
        weather_list = item.get("weather", [])
        wind = item.get("wind", {})
        if (
            not isinstance(main, dict)
            or not isinstance(weather_list, list)
            or not isinstance(wind, dict)
        ):
            continue
        conditions = (
            weather_list[0].get("description")
            if weather_list and isinstance(weather_list[0], dict)
            else None
        )
        grouped[local_time.date().isoformat()].append(
            {
                "time_local": local_time.strftime("%H:%M"),
                "conditions": conditions,
                "temperature": main.get("temp"),
                "feels_like": main.get("feels_like"),
                "precipitation_probability": item.get("pop"),
                "wind_speed": wind.get("speed"),
            }
        )

    days_forecast = []
    for date in sorted(grouped)[:days]:
        entries = grouped[date]
        temperatures = [
            entry["temperature"]
            for entry in entries
            if isinstance(entry["temperature"], (int, float))
        ]
        days_forecast.append(
            {
                "date": date,
                "temperature_min": min(temperatures) if temperatures else None,
                "temperature_max": max(temperatures) if temperatures else None,
                "intervals": entries,
            }
        )

    return {
        "provider": "OpenWeatherMap",
        "location": city_data.get("name", city),
        "country": city_data.get("country"),
        "forecast_available_through": (
            days_forecast[-1]["date"] if days_forecast else None
        ),
        "units": units,
        "days": days_forecast,
    }
