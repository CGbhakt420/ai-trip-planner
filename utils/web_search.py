from typing import Any

import requests

from utils.api_utils import require_api_key


TAVILY_SEARCH_URL = "https://api.tavily.com/search"


def search_web(query: str, max_results: int = 5) -> dict[str, Any]:
    """Search the web for current travel information using Tavily."""
    query = query.strip()
    if not query:
        raise ValueError("A web search query is required.")
    if (
        isinstance(max_results, bool)
        or not isinstance(max_results, int)
        or not 1 <= max_results <= 10
    ):
        raise ValueError("Result limit must be between 1 and 10.")

    api_key = require_api_key("TAVILY_API_KEY")
    try:
        response = requests.post(
            TAVILY_SEARCH_URL,
            json={
                "api_key": api_key,
                "query": query,
                "search_depth": "basic",
                "max_results": max_results,
                "include_answer": True,
            },
            timeout=20,
        )
    except requests.RequestException:
        raise RuntimeError("Could not connect to Tavily Search.") from None

    if response.status_code >= 400:
        raise RuntimeError(f"Tavily Search returned HTTP {response.status_code}.")
    try:
        data = response.json()
    except ValueError:
        raise RuntimeError("Tavily Search returned invalid JSON.") from None
    if not isinstance(data, dict):
        raise RuntimeError("Tavily Search returned an unexpected response.")

    result_items = data.get("results", [])
    if not isinstance(result_items, list):
        raise RuntimeError("Tavily Search returned malformed search results.")
    results = []
    for item in result_items:
        if not isinstance(item, dict):
            continue
        results.append(
            {
                "title": item.get("title"),
                "url": item.get("url"),
                "content": item.get("content"),
                "published_date": item.get("published_date"),
                "score": item.get("score"),
            }
        )
    return {
        "provider": "Tavily",
        "query": query,
        "answer": data.get("answer"),
        "results": results,
    }
