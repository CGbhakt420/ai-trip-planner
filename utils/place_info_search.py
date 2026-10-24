from typing import Any

import requests

from utils.api_utils import get_api_key


GOOGLE_PLACES_URL = "https://places.googleapis.com/v1/places:searchText"
FOURSQUARE_PLACES_URL = "https://api.foursquare.com/v3/places/search"
GOOGLE_FIELD_MASK = (
    "places.displayName,places.formattedAddress,places.rating,"
    "places.userRatingCount,places.priceLevel,places.websiteUri,"
    "places.googleMapsUri,places.primaryTypeDisplayName"
)


def _checked_json(response: requests.Response, provider: str) -> dict[str, Any]:
    if response.status_code >= 400:
        raise RuntimeError(f"{provider} returned HTTP {response.status_code}.")
    try:
        data = response.json()
    except ValueError:
        raise RuntimeError(f"{provider} returned invalid JSON.") from None
    if not isinstance(data, dict):
        raise RuntimeError(f"{provider} returned an unexpected response.")
    return data


def _google_places(
    query: str,
    location: str | None,
    limit: int,
    api_key: str,
) -> dict[str, Any]:
    text_query = f"{query} near {location}" if location else query
    try:
        response = requests.post(
            GOOGLE_PLACES_URL,
            headers={
                "Content-Type": "application/json",
                "X-Goog-Api-Key": api_key,
                "X-Goog-FieldMask": GOOGLE_FIELD_MASK,
            },
            json={"textQuery": text_query, "pageSize": limit},
            timeout=15,
        )
    except requests.RequestException:
        raise RuntimeError("Could not connect to Google Places.") from None
    data = _checked_json(response, "Google Places")

    places_data = data.get("places", [])
    if not isinstance(places_data, list):
        raise RuntimeError("Google Places returned malformed place results.")
    places = []
    for item in places_data:
        if not isinstance(item, dict):
            continue
        display_name = item.get("displayName", {})
        primary_type = item.get("primaryTypeDisplayName", {})
        places.append(
            {
                "name": display_name.get("text")
                if isinstance(display_name, dict)
                else None,
                "address": item.get("formattedAddress"),
                "category": primary_type.get("text")
                if isinstance(primary_type, dict)
                else None,
                "rating": item.get("rating"),
                "rating_count": item.get("userRatingCount"),
                "price_level": item.get("priceLevel"),
                "website": item.get("websiteUri"),
                "maps_url": item.get("googleMapsUri"),
            }
        )
    return {"provider": "Google Places", "query": text_query, "places": places}


def _foursquare_places(
    query: str,
    location: str | None,
    limit: int,
    api_key: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {
        "query": query,
        "limit": limit,
        "fields": "name,location,categories,rating,price,website,link,distance",
    }
    if location:
        params["near"] = location
    try:
        response = requests.get(
            FOURSQUARE_PLACES_URL,
            headers={"Authorization": api_key},
            params=params,
            timeout=15,
        )
    except requests.RequestException:
        raise RuntimeError("Could not connect to Foursquare Places.") from None
    data = _checked_json(response, "Foursquare Places")

    places_data = data.get("results", [])
    if not isinstance(places_data, list):
        raise RuntimeError("Foursquare Places returned malformed place results.")
    places = []
    for item in places_data:
        if not isinstance(item, dict):
            continue
        address = item.get("location", {})
        categories = item.get("categories", [])
        places.append(
            {
                "name": item.get("name"),
                "address": address.get("formatted_address")
                if isinstance(address, dict)
                else None,
                "category": categories[0].get("name")
                if categories and isinstance(categories[0], dict)
                else None,
                "rating": item.get("rating"),
                "distance_meters": item.get("distance"),
                "price_level": item.get("price"),
                "website": item.get("website"),
                "maps_url": item.get("link"),
            }
        )
    return {"provider": "Foursquare Places", "query": query, "places": places}


def search_places(
    query: str,
    location: str | None = None,
    limit: int = 5,
) -> dict[str, Any]:
    """Search for businesses and points of interest using Google Places or Foursquare."""
    query = query.strip()
    location = location.strip() if location else None
    if not query:
        raise ValueError("A place search query is required.")
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 10:
        raise ValueError("Result limit must be between 1 and 10.")

    google_api_key = get_api_key("GPLACES_API_KEY", "GOOGLE_API_KEY")
    if google_api_key:
        google_results = _google_places(query, location, limit, google_api_key)
        if google_results["places"]:
            return google_results

    foursquare_api_key = get_api_key("FOURSQUARE_API_KEY")
    if foursquare_api_key:
        return _foursquare_places(query, location, limit, foursquare_api_key)

    if google_api_key:
        return google_results

    raise ValueError(
        "Place search requires GPLACES_API_KEY or GOOGLE_API_KEY, "
        "or FOURSQUARE_API_KEY in the environment or project .env file."
    )