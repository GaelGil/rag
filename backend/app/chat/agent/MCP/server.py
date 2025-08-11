import json
import requests
import wikipedia
from mcp.server.fastmcp import FastMCP
import xml.etree.ElementTree as ET
from mcp.server.fastmcp.utilities.logging import get_logger
from openai import OpenAI
from dotenv import load_dotenv

# from pathlib import Path
import os
from backend.app.chat.agent.utils.schemas import (
    AssembledResponse,
    ReviewResponse,
    WriteResponse,
    FinalResponse,
)

load_dotenv()
# run using python -m MCP.server

ARXIV_NAMESPACE = "{http://www.w3.org/2005/Atom}"
LLM = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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


@mcp.tool(
    name="save_txt",
    description="Save text to a .txt file",
)
def save_txt(text: str, filename: str = "output.txt") -> str:
    """Saves the provided text to a .txt file."""
    response = LLM.responses.parse(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "developer",
                "content": f"""
                        You are an expert essay writer, you take in essay writing request on a given topic and write it. 
                        You MUST effectively communicate the topic in a clear and engaging manner.
                        You MUST use the context provided to inform your response.
                        Here is an example context:
                        
                       task_id: 1
                       task: Write a paragraph on topic
                       results: A paragraph written on a topic

                       task_id: 2
                       task: Write a paragraph on topic
                       results: A paragraph written on a topic

                       ...
                        You must assmple the context into something like this:
                        "A intro paragraph written on a topic, A paragraph written on a topic with previous task results ..."
                        {text}
                        """,
            },
            {
                "role": "user",
                "content": "You must combine this into its final draft",
            },
        ],
        text_format=FinalResponse,
    )
    formatted_text = (
        f"--- Research Output ---\nTimestamp: \n\n{response.output_parsed.content}\n\n"
    )

    with open(filename, "a", encoding="utf-8") as f:
        f.write(formatted_text)

    return f"Data successfully saved to {filename}"


@mcp.tool(
    name="writer_tool",
    description="Writes an essay on a given topic",
)
def writer_tool(query: str, context: str) -> str:
    """"""
    response = LLM.responses.parse(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "developer",
                "content": f"""
                        You are an expert essay writer, you take in essay writing request on a given topic and write it. 
                        You MUST effectively communicate the topic in a clear and engaging manner.
                        You MUST use the context provided to inform your response.
                        Here is an example context:
                        
                       task_id: 1
                       task: Write a paragraph on topic
                       results: A paragraph written on a topic

                       task_id: 2
                       task: Write a paragraph on topic
                       results: A paragraph written on a topic

                       ...
                        
                        YOU MUST USE THE CONTEXT PROVIDED TO INFORM YOUR RESPONSE
                        
                        Here is the context.
                        {context}
                        """,
            },
            {
                "role": "user",
                "content": query,
            },
        ],
        text_format=WriteResponse,
    )
    return response.output_parsed.content


@mcp.tool(
    name="review_tool",
    description="Reviews content on a given topic",
)
def review_tool(content: str) -> str:
    """"""
    response = LLM.responses.parse(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "developer",
                "content": f"""
                        You are an expert content reviewer, you take in some content and review it for quality and update anything you see fit.
                        Here is the content: {content}
                        """,
            },
            {
                "role": "user",
                "content": "Ensure the content is quality and well written and communicates a point effectively. Update my content only if needed.",
            },
        ],
        text_format=ReviewResponse,
    )
    logger.info(f"THOUGHT: {response.output_parsed.thought}")
    return response.output_parsed.content


@mcp.tool(
    name="assemble_content",
    description="Assamble content from previous tasks",
)
def assemble_content(content: str) -> str:
    """"""
    response = LLM.responses.parse(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "developer",
                "content": f"""
                        You are an expert content assembler, you take in some content at its current state
                        and assemble it into well written content to effectively communitcate an idea.
                        Here is an example context:
                        
                       task_id: 1
                       task: Write a paragraph on topic
                       results: A paragraph written on a topic

                       task_id: 2
                       task: Write a paragraph on topic
                       results: A paragraph written on a topic

                       ...
                        You must assmple the context into something like this:
                        "A intro paragraph written on a topic, A paragraph written on a topic with previous task results ..."
                        Here is the context: {content}
                        """,
            },
            {
                "role": "user",
                "content": "Assemble the context into a clear and coherent narrative.",
            },
        ],
        text_format=AssembledResponse,
    )
    return response.output_parsed.content


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
