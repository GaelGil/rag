composio_tools = [
    {
        "type": "function",
        "name": "COMPOSIO_SEARCH_NEWS_SEARCH",
        "description": "The newssearch class performs a news-specific search using the composio news search api. this class extends the functionality of the base action class to specifically target news articles related to the given query. by utilizing the google news search engine through the composio news search api, it fetches the most relevant news articles based on the input query. the `newssearch` class is particularly useful for applications that need to retrieve and display the latest news articles about a specific topic. it leverages the powerful search capabilities of google's news search engine, ensuring that the returned results are current and relevant.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query for the Composio News Search API, specifying the topic for news search.",
                }
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "COMPOSIO_SEARCH_SEARCH",  # composio google search
        "description": "Perform a google search using the composio google search api.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query for the Composio Google Search API.",
                }
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "recommend_movies",
        "description": "Recommend movies based on a query.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query for the embedding database.",
                },
                "top_k": {
                    "type": "integer",
                    "description": "The number of results to return.",
                },
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
]
