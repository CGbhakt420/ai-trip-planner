from typing import Any

from langchain_core.tools import tool

from utils.place_info_search import search_places as find_places


@tool
def search_places(
    query: str,
    location: str | None = None,
    limit: int = 5,
) -> dict[str, Any]:
    """Find real hotels, restaurants, attractions, and other businesses near a location."""
    return find_places(query, location, limit)