from app.chat.utils.schemas import (
    SearchResults,
    VectorSearchResults,
    NewsSearchResults,
)
import traceback
from typing import List


def parse_composio_search_results(composio_result: dict) -> dict:
    """Parse COMPOSIO_SEARCH_SEARCH results into UnifiedSearchResponse format."""
    try:
        search_data = composio_result.get("data", {}).get("results", {})

        results = List[search_data]

        news_search_results = SearchResults(results=results)
        return news_search_results.model_dump()
    except Exception as e:
        print(traceback.format_exc())
        return {"error": f"Failed to parse COMPOSIO news search results: {str(e)}"}


def parse_composio_news_search_results(composio_result: dict) -> dict:
    """Parse COMPOSIO_SEARCH_NEWS_SEARCH results into UnifiedSearchResponse format."""
    try:
        search_data = composio_result.get("data", {}).get("results", {})

        # Parse News Results as Organic Results
        news_data = search_data.get("news_results", [])
        news = []
        for news_item in news_data:
            result = NewsSearchResults(
                title=news_item.get("title"),
                date=news_item.get("date"),
                snippet=news_item.get("snippet"),
                link=news_item.get("link"),
                source=news_item.get("source"),
                favicon=news_item.get("favicon"),
                position=str(news_item.get("position")),
            )
            news.append(result)
        news_search_results = SearchResults(results=news)
        return news_search_results.model_dump()

    except Exception as e:
        print(traceback.format_exc())
        return {"error": f"Failed to parse COMPOSIO news search results: {str(e)}"}


def parse_vector_search_results(result: list):
    """Parse COMPOSIO_SEARCH_SEARCH results into UnifiedSearchResponse format."""
    movies = []
    for movie_item in result:
        movie = movie_item.get("movie")
        movies.append(VectorSearchResults(title=movie))

    vector_search_results = SearchResults(results=movies)
    return vector_search_results.model_dump()
