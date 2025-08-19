from app.chat.utils.schemas import (
    SearchResults,
    VectorSearchResults,
    EventSearchResults,
    NewsSearchResults,
    FinanceSearchResults,
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


def parse_composio_finance_search_results(composio_result: dict) -> dict:
    """Parse COMPOSIO_SEARCH_FINANCE_SEARCH results into UnifiedSearchResponse format."""
    try:
        search_data = (
            composio_result.get("data", {}).get("results", {}).get("discover_more", {})
        )

        # Parse News Results as Organic Results
        items = search_data[0].get("items", [])
        results = []
        for item in items:
            result = FinanceSearchResults(
                extracted_price=item.get("title"),
                link=item.get("link"),
                name=item.get("name"),
                price=item.get("price"),
                movement=item.get("price_movement").get("movement"),
                percentage=item.get("price_movement").get("percentage"),
                stock=item.get("title"),
            )
            results.append(result)
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
                position=news_item.get("position"),
            )
            news.append(result)
        news_search_results = SearchResults(results=news)
        return news_search_results.model_dump()

    except Exception as e:
        print(traceback.format_exc())
        return {"error": f"Failed to parse COMPOSIO news search results: {str(e)}"}


def parse_composio_event_search_results(composio_result: dict) -> dict:
    """Parse COMPOSIO_SEARCH_EVENT_SEARCH results into UnifiedSearchResponse format.

    Event search results have the same structure as news results, so we reuse the same parsing logic.
    """
    try:
        search_data = composio_result.get("data", {}).get("results", {})

        # Parse News Results as Organic Results
        events_data = search_data.get("event_results", [])
        events = []
        for event_item in events_data:
            event = EventSearchResults(
                title=event_item.get("title"),
                date="".join(event_item.get("date")),
                address="".join(event_item.get("address")),
                description=event_item.get("description"),
                image=event_item.get("image"),
                link=event_item.get("link"),
            )
            events.append(event)

        events_search_results = SearchResults(results=events)

        return events_search_results.model_dump()

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
