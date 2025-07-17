from typing import Any, Dict
import nest_asyncio

# import asyncio
from fastmcp import Client

nest_asyncio.apply()


class MCPClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = None

    async def connect(self):
        self.session = await Client(self.base_url).__aenter__()

    async def disconnect(self):
        if self.session:
            await self.session.__aexit__(None, None, None)
            self.session = None

    async def list_tools(self) -> list:
        if not self.session:
            raise RuntimeError("Session not connected")
        return await self.session.list_tools()

    async def list_resources(self) -> list:
        if not self.session:
            raise RuntimeError("Session not connected")
        return await self.session.list_resources()

    async def get_tools(self) -> list[dict[str, Any]]:
        """Retrieve tools in a format compatible with OpenAI."""
        if not self.session:
            raise RuntimeError("Session not connected")

        tools = await self.session.list_tools()
        openai_tools = []

        for tool in tools:
            openai_tools.append(
                {
                    "type": "function",
                    "name": tool.name,  # Accessing 'name' attribute
                    "description": tool.description,  # Accessing 'description' attribute
                    "parameters": {
                        "type": "object",
                        "properties": tool.inputSchema[
                            "properties"
                        ],  # Accessing 'input_schema' attribute
                        "required": tool.inputSchema.get(
                            "required", []
                        ),  # Accessing 'input_schema' attribute
                    },
                }
            )

        return openai_tools

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        if not self.session:
            raise RuntimeError("Session not connected")
        result = await self.session.call_tool(tool_name, arguments)
        return result.content[0].text if result.content else None
