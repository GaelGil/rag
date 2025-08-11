from typing import Any, Dict, Optional, Union
from fastmcp.client.client import Client
from contextlib import asynccontextmanager


class MCPClient:
    def __init__(self, config: Union[str, dict] = "http://localhost:8050/sse"):
        """Initialize the MCP client.

        Args:
            config (Union[str, dict]): Either a URL string or a configuration dictionary.
                If string: Treated as the URL of the MCP server.
                If dict: Should follow the MCP configuration format with 'mcpServers' key.
        """
        self.config = config
        self._client = None
        self._is_connected = False

    async def connect(self):
        """Connect to the MCP server(s)."""
        if self._is_connected:
            return

        if isinstance(self.config, str):
            # For SSE transport, we just need the URL
            self._client = Client(self.config)
        else:
            # Configuration mode with multiple servers
            self._client = Client(self.config)

        await self._client.__aenter__()
        self._is_connected = True

    async def disconnect(self):
        """Disconnect from the MCP server(s)."""
        if self._is_connected and self._client:
            await self._client.__aexit__(None, None, None)
            self._is_connected = False
            self._client = None

    @asynccontextmanager
    async def session(self):
        """Context manager for session management."""
        try:
            await self.connect()
            yield self
        finally:
            await self.disconnect()

    async def list_servers(self) -> list:
        """List available MCP servers."""
        if not self._is_connected:
            raise RuntimeError("Not connected to MCP server(s)")
        return list(self._client.servers.keys())

    async def list_tools(self) -> list:
        """List available tools.

        Returns:
            list: List of available tools.
        """
        if not self._is_connected:
            raise RuntimeError("Not connected to MCP server(s)")
        return await self._client.list_tools()

    async def get_tools(self) -> list[dict[str, Any]]:
        """Retrieve tools in a format compatible with OpenAI function calling.

        Returns:
            list[dict[str, Any]]: List of tools in OpenAI function calling format.
        """
        if not self._is_connected:
            raise RuntimeError("Not connected to MCP server(s)")

        tools = await self.list_tools()
        openai_tools = []

        for tool in tools:
            openai_tools.append(
                {
                    "type": "function",
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": tool.inputSchema.get("properties", {}),
                        "required": tool.inputSchema.get("required", []),
                    },
                }
            )

        return openai_tools

    async def call_tool(
        self, tool_name: str, arguments: Dict[str, Any], server: Optional[str] = None
    ) -> Any:
        """Call a tool.

        Args:
            tool_name (str): The name of the tool to call.
            arguments (Dict[str, Any]): The arguments to pass to the tool.
            server (str, optional): Specific server to call the tool on.
                                 If None, the client will try to find the tool
                                 in any of the available servers.

        Returns:
            Any: The result of the tool call.
        """
        if not self._is_connected:
            raise RuntimeError("Not connected to MCP server(s)")

        result = await self._client.call_tool(tool_name, arguments, server)
        return result.content[0].text if result.content else None
