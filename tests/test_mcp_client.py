"""Tests for mcp_client.py — Remote MCP HTTP client."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

import httpx

from cli_anything.k_skill.mcp_client import RemoteMCPClient, MCPError


def _make_response(status_code: int, json_data: dict):
    """Create a mock httpx.Response with a request attached."""
    request = httpx.Request("POST", "http://test")
    return httpx.Response(status_code, json=json_data, request=request)


def _mock_client_with_response(mock_resp):
    """Create a mock AsyncClient that returns the given response on .post()."""
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    return mock_client


class TestRemoteMCPClient:
    def test_init(self):
        client = RemoteMCPClient("https://example.com/mcp")
        assert client.endpoint == "https://example.com/mcp"
        assert client.timeout == 30.0

    def test_init_custom_timeout(self):
        client = RemoteMCPClient("https://example.com", timeout=10.0)
        assert client.timeout == 10.0

    def test_trailing_slash_stripped(self):
        client = RemoteMCPClient("https://example.com/mcp/")
        assert client.endpoint == "https://example.com/mcp"

    @pytest.mark.asyncio
    async def test_initialize(self):
        client = RemoteMCPClient("https://example.com/mcp")
        mock_resp = _make_response(200, {
            "jsonrpc": "2.0", "id": 1,
            "result": {
                "serverInfo": {"name": "test-server", "version": "1.0"},
                "capabilities": {},
            },
        })
        mock_client = _mock_client_with_response(mock_resp)

        with patch("cli_anything.k_skill.mcp_client.httpx.AsyncClient", return_value=mock_client):
            info = await client.initialize()
            assert info["name"] == "test-server"
            assert info["version"] == "1.0"

    @pytest.mark.asyncio
    async def test_list_tools(self):
        client = RemoteMCPClient("https://example.com/mcp")
        mock_resp = _make_response(200, {
            "jsonrpc": "2.0", "id": 1,
            "result": {
                "tools": [
                    {"name": "search", "description": "Search tool", "inputSchema": {}},
                ],
            },
        })
        mock_client = _mock_client_with_response(mock_resp)

        with patch("cli_anything.k_skill.mcp_client.httpx.AsyncClient", return_value=mock_client):
            tools = await client.list_tools()
            assert len(tools) == 1
            assert tools[0]["name"] == "search"

    @pytest.mark.asyncio
    async def test_call_tool_success(self):
        client = RemoteMCPClient("https://example.com/mcp")
        mock_resp = _make_response(200, {
            "jsonrpc": "2.0", "id": 1,
            "result": {
                "content": [{"type": "text", "text": "result data"}],
                "isError": False,
            },
        })
        mock_client = _mock_client_with_response(mock_resp)

        with patch("cli_anything.k_skill.mcp_client.httpx.AsyncClient", return_value=mock_client):
            content, ms = await client.call_tool("search", {"q": "test"})
            assert ms > 0
            assert isinstance(content, list)

    @pytest.mark.asyncio
    async def test_call_tool_error(self):
        client = RemoteMCPClient("https://example.com/mcp")
        mock_resp = _make_response(200, {
            "jsonrpc": "2.0", "id": 1,
            "result": {
                "content": [{"type": "text", "text": "Tool error occurred"}],
                "isError": True,
            },
        })
        mock_client = _mock_client_with_response(mock_resp)

        with patch("cli_anything.k_skill.mcp_client.httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(MCPError, match="Tool error occurred"):
                await client.call_tool("search")

    @pytest.mark.asyncio
    async def test_jsonrpc_error(self):
        client = RemoteMCPClient("https://example.com/mcp")
        mock_resp = _make_response(200, {
            "jsonrpc": "2.0", "id": 1,
            "error": {"code": -32600, "message": "Invalid Request"},
        })
        mock_client = _mock_client_with_response(mock_resp)

        with patch("cli_anything.k_skill.mcp_client.httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(MCPError, match="Invalid Request"):
                await client.initialize()


class TestMCPError:
    def test_message(self):
        err = MCPError("CODE", "something went wrong")
        assert str(err) == "something went wrong"
        assert err.code == "CODE"
