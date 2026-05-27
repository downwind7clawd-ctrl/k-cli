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

import contextlib
import ipaddress
import json
import socket
import time
from typing import Any, Optional
from urllib.parse import urlparse

import httpx


# Private IP ranges for SSRF protection
_PRIVATE_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),  # AWS metadata
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),  # IPv6 unique local
]


def _validate_endpoint_url(url: str) -> str:
    """Validate and sanitize an MCP endpoint URL.

    Security checks:
    - Only https: scheme allowed (prevents SSRF via http)
    - Blocks private/loopback/link-local IP addresses
    - Blocks localhost hostname

    Args:
        url: The endpoint URL to validate.

    Returns:
        Sanitized URL with trailing slash stripped.

    Raises:
        MCPError: If URL fails security validation.
    """
    parsed = urlparse(url)
    if parsed.scheme not in ("https",):
        raise MCPError(
            code="INVALID_ENDPOINT",
            message=f"Only https:// URLs are allowed, got '{parsed.scheme}://'",
        )
    hostname = parsed.hostname
    if not hostname:
        raise MCPError(code="INVALID_ENDPOINT", message="URL must have a hostname")
    # Block localhost
    if hostname.lower() in ("localhost", "localhost.localdomain"):
        raise MCPError(
            code="INVALID_ENDPOINT",
            message="localhost endpoints are not allowed",
        )
    # Block private IPs (direct IP literals)
    try:
        ip = ipaddress.ip_address(hostname)
        for network in _PRIVATE_NETWORKS:
            if ip in network:
                raise MCPError(
                    code="INVALID_ENDPOINT",
                    message=f"Private IP addresses are not allowed: {hostname}",
                )
        return url.rstrip("/")
    except ValueError:
        pass  # Not an IP literal — need DNS check

    # DNS rebinding protection: resolve hostname and check all IPs
    try:
        addr_infos = socket.getaddrinfo(hostname, None)
        for family, type_, proto, canonname, sockaddr in addr_infos:
            ip = ipaddress.ip_address(sockaddr[0])
            for network in _PRIVATE_NETWORKS:
                if ip in network:
                    raise MCPError(
                        code="INVALID_ENDPOINT",
                        message=f"DNS resolution points to private IP: {sockaddr[0]}",
                    )
    except socket.gaierror:
        raise MCPError(
            code="INVALID_ENDPOINT",
            message=f"DNS resolution failed for '{hostname}'",
        )
    return url.rstrip("/")


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

        Raises:
            MCPError: If endpoint URL fails security validation.
        """
        self.endpoint = _validate_endpoint_url(endpoint)
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

        @contextlib.contextmanager
        def prevent_dns_rebinding():
            original = socket.getaddrinfo
            def safe_getaddrinfo(*args, **kwargs):
                res = original(*args, **kwargs)
                for family, type_, proto, canonname, sockaddr in res:
                    if family in (socket.AF_INET, socket.AF_INET6):
                        ip = ipaddress.ip_address(sockaddr[0])
                        for network in _PRIVATE_NETWORKS:
                            if ip in network:
                                raise MCPError(
                                    code="INVALID_ENDPOINT",
                                    message=f"DNS Rebinding detected! Resolved to private IP: {sockaddr[0]}"
                                )
                return res
            socket.getaddrinfo = safe_getaddrinfo
            try:
                yield
            finally:
                socket.getaddrinfo = original

        with prevent_dns_rebinding():
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
