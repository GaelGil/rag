from app.chat.utils.schemas import (
    SearchResults,
    VectorSearchResults,
    NewsSearchResults,
    AvailableOn,
    CastMember,
    MovieInfo,
    Review,
    PopularMovies,
    PopularMovie,
    Headlines,
)
import traceback


def parse_composio_search_results(composio_result: dict) -> dict:
    """Parse COMPOSIO_SEARCH_SEARCH results into UnifiedSearchResponse format."""
    try:
        search_data = composio_result.get("data", {}).get("results", {})
        if "available_on" in search_data:
            available_on_info = search_data.get("available_on", [])
            knowledge = search_data.get("knowledge_graph", {})
            reviews_info = knowledge.get("editorial_reviews", [])
            cast_info = knowledge.get("cast", [])
            headlines_info = knowledge.get("organic_results", [])
            headlines = []
            cast = []
            reviews = []
            availability = []
            for item in available_on_info:
                avail = AvailableOn(
                    link=item.get("link", ""),
                    name=item.get("name", ""),
                    price=item.get("price", ""),
                    thumbnail=item.get("thumbnail", ""),
                )
                availability.append(avail)

            for member in cast_info:
                cast_member = CastMember(
                    name=member.get("name", ""),
                    role=member.get("extensions", ""),
                )
                cast.append(cast_member)

            for review in reviews_info:
                rev = Review(
                    rating=review.get("rating", ""),
                    title=review.get("title", ""),
                    link=review.get("link", ""),
                )
                reviews.append(rev)
            for headline in headlines_info:
                headline = Headlines(
                    link=headline.get("link", ""),
                    source=headline.get("source", ""),
                    snippet=headline.get("snippet", ""),
                )
                headlines.append(headline)

            movie_info = MovieInfo(
                available_on=availability,
                cast=cast,
                director=knowledge.get("director", ""),
                description=knowledge.get("description", ""),
                reviews=reviews,
                headlines=headlines,
            )
            return movie_info.model_dump()
        else:
            knowledge = search_data.get("knowledge_graph", {})
            popular_movies_info = knowledge.get("popular_movies", [])
            popular_movies = []
            for movie in popular_movies_info:
                mov = PopularMovie(
                    img=movie.get("image", ""),
                    link=movie.get("link", ""),
                    name=movie.get("name", ""),
                    general_info=movie.get("extensions", []),
                )
                popular_movies.append(mov)
            popular_movies = PopularMovies(popular_movies=popular_movies)
            return popular_movies.model_dump()

        return
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
                title=news_item.get("title", ""),
                date=news_item.get("date", ""),
                snippet=news_item.get("snippet", ""),
                link=news_item.get("link", ""),
                source=news_item.get("source", ""),
                favicon=news_item.get("favicon", ""),
                position=str(news_item.get("position", "")),
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
