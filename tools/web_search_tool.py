from typing import Any

from langchain_core.tools import tool

from utils.web_search import search_web as query_web


@tool
def search_web(query: str, max_results: int = 5) -> dict[str, Any]:
    """Search current web pages for official travel information, prices, schedules, and visitor details."""
    return query_web(query, max_results)
