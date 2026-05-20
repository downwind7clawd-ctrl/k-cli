"""
Remote MCP (Model Context Protocol) HTTP client.

Communicates with remote MCP servers via Streamable HTTP JSON-RPC.
No external MCP SDK required — uses httpx directly.

Protocol: https://modelcontextprotocol.io/specification

Usage:
    client = RemoteMCPClient("https://mcp-servers.myrealtrip.com/mcp")
    tools = await client.list_tools()
    result = await client.call_tool("searchDomesticFlights", {"origin": "GMP"})
"""

import time
from typing import Any, Optional

import httpx


class MCPError(Exception):
    """Raised when MCP server returns an error."""

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


class RemoteMCPClient:
    """Client for remote MCP servers using Streamable HTTP transport.

    Handles MCP initialization, tool listing, and tool invocation.
    Each call creates a new HTTP connection (stateless mode).
    """

    def __init__(self, endpoint: str, timeout: float = 30.0):
        """Initialize MCP client.

        Args:
            endpoint: Remote MCP server URL
                       (e.g., https://mcp-servers.myrealtrip.com/mcp).
            timeout: Request timeout in seconds.
        """
        self.endpoint = endpoint.rstrip("/")
        self.timeout = timeout
        self._request_id = 0
        self._protocol_version = "2025-03-26"

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id

    async def _jsonrpc(self, method: str, params: Optional[dict] = None) -> dict:
        """Send a JSON-RPC request to the MCP server.

        Args:
            method: JSON-RPC method name (e.g., "initialize", "tools/call").
            params: Method parameters.

        Returns:
            Parsed JSON-RPC response.

        Raises:
            MCPError: On MCP-level errors.
            httpx.HTTPError: On transport errors.
        """
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": self._next_id(),
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                self.endpoint,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
            resp.raise_for_status()
            data = resp.json()

        if "error" in data:
            err = data["error"]
            raise MCPError(
                code=err.get("code", "MCP_UNKNOWN"),
                message=err.get("message", "Unknown MCP error"),
            )

        return data.get("result", data)

    async def initialize(self) -> dict:
        """Perform MCP handshake — negotiate protocol version.

        Returns:
            Server info dict with name, version, capabilities.
        """
        result = await self._jsonrpc("initialize", {
            "protocolVersion": self._protocol_version,
            "clientInfo": {"name": "cli-anything-k-skill", "version": "0.1.0"},
            "capabilities": {},
        })
        # Acknowledge initialization
        await self._jsonrpc("notifications/initialized")
        return result.get("serverInfo", {})

    async def list_tools(self) -> list[dict]:
        """List available MCP tools.

        Returns:
            List of tool descriptors with name, description, inputSchema.
        """
        result = await self._jsonrpc("tools/list")
        return result.get("tools", [])

    async def call_tool(
        self,
        tool_name: str,
        arguments: Optional[dict] = None,
    ) -> tuple[Any, float]:
        """Invoke an MCP tool.

        Args:
            tool_name: Name of the tool to call.
            arguments: Tool-specific input arguments.

        Returns:
            Tuple of (tool result content, response time in ms).

        Raises:
            MCPError: If tool returns isError=true.
        """
        start = time.monotonic()
        result = await self._jsonrpc("tools/call", {
            "name": tool_name,
            "arguments": arguments or {},
        })
        elapsed_ms = (time.monotonic() - start) * 1000

        if result.get("isError"):
            texts = [
                c.get("text", "")
                for c in result.get("content", [])
                if c.get("type") == "text"
            ]
            raise MCPError(
                code="MCP_TOOL_ERROR",
                message="; ".join(texts) or "MCP tool returned an error",
            )

        return result.get("content", []), elapsed_ms

    async def health_check(self) -> bool:
        """Check if the MCP server is reachable."""
        try:
            await self.initialize()
            return True
        except Exception:
            return False
