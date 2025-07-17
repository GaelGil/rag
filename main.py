import os
import json
import asyncio
from LLM.OpenAi import OpenAi
from dotenv import load_dotenv
from pathlib import Path
from schemas import Answer
from mcp_server_client.client import MCPClient
import aioconsole  # Import aioconsole

load_dotenv(Path("./.env"))


async def execute():
    client = MCPClient(base_url="http://localhost:8050/sse")
    await client.connect()
    tools = await client.get_tools()
    print(f"TOOLS: {tools}")
    llm = OpenAi(model_name="gpt-4.1-mini", api_key=os.getenv("OPENAI_API_KEY"))

    while True:
        query = await aioconsole.ainput("\nYour question (or type 'exit'): ")
        query = query.strip()
        if query.lower() in ("exit", "quit"):
            await client.aclose()
            print("Session done")
            break

        messages = [
            {
                "role": "developer",
                "content": "You are a helpful AI assistant tasked with answering anything the user asks. If you need to call a function include that in the text response so the user knows",
            },
            {
                "role": "user",
                "content": query,
            },
        ]

        response = llm.create_response(
            messages=messages,
            tools=tools,
        )
        # response
        if response.output[0].type != "function_call":
            continue
        for tool_call in response.output:
            name = tool_call.name
            # get the arguments for the tool
            args = json.loads(tool_call.arguments)
            # add the output to the messages (tool_call = item in response.output)
            messages.append(tool_call)
            # call the function
            result = await client.call_tool(tool_name=name, arguments=args)
            print(response)
            # add the tool result to the messages
            messages.append(
                {
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": str(result),
                }
            )

        follow_up_response = llm.parse_response(
            messages=messages, tools=tools, response_format=Answer
        )

    print(follow_up_response.output_parsed)


if __name__ == "__main__":
    asyncio.run(execute())
