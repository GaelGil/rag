import os
from LLM.OpenAi import OpenAi
from dotenv import load_dotenv
from pathlib import Path
from schemas import Answer
from mcp_server_client.client import MCPClient


load_dotenv(Path("./.env"))


async def execute():
    client = MCPClient(base_url="http://localhost:8050/sse")
    await client.call_tool()
    tools = await client.get_tools()
    llm = OpenAi(model_name="gpt_4.1-mini", api_key=os.getenv("OPENAI_API_KEY"))

    response = llm.parse_response(
        messages=[
            {
                "role": "developer",
                "content": "",
            },
            {
                "role": "user",
                "content": "Write a thoughtful essay about the cultural impact of star wars. The essay should be at least 500 words long and include references to the original trilogy, the prequels, and the sequels. Include the sources",
            },
        ],
        tools=tools,
        response_format=Answer,
    )

    print(response.output_parsed)
