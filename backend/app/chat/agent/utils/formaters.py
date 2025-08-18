from app.chat.agent.utils.schemas import (
    AIPreviewResult,
    ForumAnswer,
    ForumResult,
    MarketResult,
    OrganicResult,
    SearchResults,
    UnifiedSearchResponse,
    PriceMovement,
    VectorSearchResults,
)

from typing import Optional


# def parse_composio_finance_search_results(result):
#     pass
# def parse_composio_search_results(result):
#     pass


def parse_composio_search_results(composio_result: dict) -> dict:
    """Parse COMPOSIO_SEARCH_SEARCH results into UnifiedSearchResponse format."""
    try:
        # Get the search data from the result that is in the 'data' key and the 'results' key
        search_data = composio_result.get("data", {}).get("results", {})

        # Parse AI Overview
        ai_overview = None
        if search_data.get("ai_overview"):
            ai_overview = AIPreviewResult()

        # Parse Organic Results
        organic_results = []
        organic_data = search_data.get("organic_results", [])
        for result in organic_data:
            organic_result = OrganicResult(
                title=result.get("title"),
                link=result.get("link"),
                displayed_link=result.get("displayed_link"),
                snippet=result.get("snippet"),
                source=result.get("source"),
                date=result.get("date"),
                favicon=result.get("favicon"),
                position=result.get("position"),
                redirect_link=result.get("redirect_link"),
            )
            organic_results.append(organic_result)

        # Parse Discussions and Forums
        forums = []
        forum_data = search_data.get("discussions_and_forums", [])
        for forum in forum_data:
            # Parse forum answers
            answers = []
            for answer_data in forum.get("answers", []):
                answer = ForumAnswer(
                    link=answer_data.get("link"),
                    snippet=answer_data.get("snippet"),
                    extensions=answer_data.get("extensions"),
                )
                answers.append(answer)

            forum_result = ForumResult(
                title=forum.get("title"),
                link=forum.get("link"),
                source=forum.get("source"),
                date=forum.get("date"),
                extensions=forum.get("extensions", []),
                answers=answers,
            )
            forums.append(forum_result)

        # Build the unified response
        search_results = SearchResults(
            ai_overview=ai_overview,
            organic_results=organic_results if organic_results else None,
            discussions_and_forums=forums if forums else None,
            markets=None,  # Not present in the COMPOSIO results
        )

        unified_response = UnifiedSearchResponse(search_results=search_results)
        return unified_response.model_dump()

    except Exception as e:
        import traceback

        print(traceback.format_exc())
        return {"error": f"Failed to parse COMPOSIO search results: {str(e)}"}


def parse_composio_finance_search_results(composio_result: dict) -> dict:
    """Parse COMPOSIO_SEARCH_FINANCE_SEARCH results into UnifiedSearchResponse format."""
    try:
        search_data = composio_result.get("data", {}).get("results", {})

        def create_market_result(item, region: Optional[str] = None) -> MarketResult:
            """Helper function to create a MarketResult from an item."""
            # Handle price - use extracted_price if available, otherwise try to parse price string
            price = item.get("extracted_price")
            if price is None and "price" in item:
                price_val = item["price"]
                if isinstance(price_val, (int, float)):
                    price = float(price_val)
                elif isinstance(price_val, str):
                    price_str = price_val.replace(",", "").replace("$", "")
                    try:
                        price = float(price_str)
                    except (ValueError, TypeError):
                        price = None
                else:
                    price = None

            # Create price movement
            price_movement = None
            movement_data = item.get("price_movement")
            if isinstance(movement_data, dict):
                price_movement = PriceMovement(
                    movement=movement_data.get("movement"),
                    percentage=movement_data.get("percentage"),
                    value=movement_data.get("value"),
                )

            return MarketResult(
                name=item.get("name"),
                link=item.get("link"),
                stock=item.get("stock"),
                price=price,
                price_movement=price_movement,
                serpapi_link=item.get("serpapi_link"),
                region=region,
            )

        # Parse markets data by region
        markets = {}
        markets_data = search_data.get("markets", {})

        # Known market regions to avoid processing metadata
        valid_market_regions = [
            "asia",
            "crypto",
            "currencies",
            "europe",
            "futures",
            "us",
        ]

        for region, items in markets_data.items():
            # Skip non-market regions (like search_metadata, top_news, etc.)
            if region not in valid_market_regions:
                continue

            # Ensure items is a list
            if not isinstance(items, list):
                continue

            market_results = []
            for item in items:
                # Skip non-dict items (like metadata strings)
                if not isinstance(item, dict):
                    continue

                market_result = create_market_result(item, region)
                market_results.append(market_result)

            if market_results:  # Only add if we have valid results
                markets[region] = market_results

        # Parse discover_more items as "featured" region
        discover_more_data = search_data.get("discover_more", [])
        if isinstance(discover_more_data, list):
            featured_results = []
            for section in discover_more_data:
                if not isinstance(section, dict):
                    continue

                items = section.get("items", [])
                if not isinstance(items, list):
                    continue

                for item in items:
                    # Skip non-dict items
                    if not isinstance(item, dict):
                        continue

                    market_result = create_market_result(item, "featured")
                    featured_results.append(market_result)

            if featured_results:
                markets["featured"] = featured_results

        # Build the unified response (finance search typically doesn't have organic results, forums, or AI overview)
        search_results = SearchResults(
            ai_overview=None,
            organic_results=None,
            discussions_and_forums=None,
            markets=markets if markets else None,
        )

        unified_response = UnifiedSearchResponse(search_results=search_results)
        return unified_response.model_dump()

    except Exception as e:
        import traceback

        print(traceback.format_exc())
        return {"error": f"Failed to parse COMPOSIO finance search results: {str(e)}"}


def parse_composio_news_search_results(composio_result: dict) -> dict:
    """Parse COMPOSIO_SEARCH_NEWS_SEARCH results into UnifiedSearchResponse format."""
    try:
        search_data = composio_result.get("data", {}).get("results", {})

        # Parse News Results as Organic Results
        organic_results = []
        news_data = search_data.get("news_results", [])
        for news_item in news_data:
            organic_result = OrganicResult(
                title=news_item.get("title"),
                date=news_item.get("date"),
                snippet=news_item.get("snippet"),
                link=news_item.get("link"),
                source=news_item.get("source"),
                favicon=news_item.get("favicon"),
                position=news_item.get("position"),
            )
            organic_results.append(organic_result)

        # Build the unified response (news search typically doesn't have AI overview, forums, or markets)
        search_results = SearchResults(
            ai_overview=None,
            organic_results=organic_results if organic_results else None,
            discussions_and_forums=None,
            markets=None,
        )

        unified_response = UnifiedSearchResponse(search_results=search_results)
        return unified_response.model_dump()

    except Exception as e:
        import traceback

        print(traceback.format_exc())
        return {"error": f"Failed to parse COMPOSIO news search results: {str(e)}"}


def parse_composio_event_search_results(composio_result: dict) -> dict:
    """Parse COMPOSIO_SEARCH_EVENT_SEARCH results into UnifiedSearchResponse format.

    Event search results have the same structure as news results, so we reuse the same parsing logic.
    """
    try:
        search_data = composio_result.get("data", {}).get("results", {})

        # Parse News Results as Organic Results
        organic_results = []
        events_data = search_data.get("event_results", [])
        for event_item in events_data:
            organic_result = OrganicResult(
                title=event_item.get("title"),
                date="".join(event_item.get("date")),
                address="".join(event_item.get("address")),
                description=event_item.get("description"),
                image=event_item.get("image"),
                link=event_item.get("link"),
            )
            organic_results.append(organic_result)

        # Build the unified response (news search typically doesn't have AI overview, forums, or markets)
        search_results = SearchResults(
            ai_overview=None,
            organic_results=organic_results if organic_results else None,
        )

        unified_response = UnifiedSearchResponse(search_results=search_results)
        return unified_response.model_dump()

    except Exception as e:
        import traceback

        print(traceback.format_exc())
        return {"error": f"Failed to parse COMPOSIO news search results: {str(e)}"}


def parse_vector_search_results(result: list):
    """Parse COMPOSIO_SEARCH_SEARCH results into UnifiedSearchResponse format."""

    for movie_item in result:
        movie = movie_item.get("movie")
        vector_search_result = VectorSearchResults(title=movie)

    return vector_search_result
