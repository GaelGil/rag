import json
import requests
import wikipedia
from mcp.server.fastmcp import FastMCP
import xml.etree.ElementTree as ET
from mcp.server.fastmcp.utilities.logging import get_logger
# run using python -m MCP.server

ARXIV_NAMESPACE = "{http://www.w3.org/2005/Atom}"
logger = get_logger(__name__)


mcp = FastMCP(
    name="Knowledge Base",
    host="0.0.0.0",  # only used for SSE transport (localhost)
    port=8050,  # only used for SSE transport (set this to any port)
)


@mcp.tool(
    name="wiki_search",
    description="Search wikipedia for the given query and returns a summary.",
)
def wiki_search(query: str, sentences: int = 2) -> str:
    """
    Searches Wikipedia for the given query and returns a summary.

    Args:
        query (str): The search term.
        sentences (int): Number of summary sentences to return.

    Returns:
        str: Summary of the top Wikipedia page match.
    """
    try:
        summary = wikipedia.summary(query, sentences=sentences)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"DisambiguationError: The query '{query}' may refer to multiple things:\n{e.options[:5]}"
    except wikipedia.exceptions.PageError:
        return f"No Wikipedia page found for '{query}'."
    except Exception as e:
        return f"An error occurred: {e}"


@mcp.tool(name="arxiv_search", description="Search arxiv")
def arxiv_search(query: str) -> str:
    """Searches arxiv"""
    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results=1"
    res = requests.get(url)
    et_root = ET.fromstring(res.content)
    for entry in et_root.findall(f"{ARXIV_NAMESPACE}entry"):
        title = entry.find(f"{ARXIV_NAMESPACE}title").text.strip()
        summary = entry.find(f"{ARXIV_NAMESPACE}summary").text.strip()
    return json.dumps({"title": title, "summary": summary})


# Run the server
if __name__ == "__main__":
    mcp.run(transport="sse")
