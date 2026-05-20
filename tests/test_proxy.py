"""Tests for proxy.py — proxy routing."""

import os
from unittest.mock import AsyncMock, patch, MagicMock

import httpx
import pytest

from cli_anything.k_skill.proxy import get_proxy_base, DEFAULT_PROXY


def _make_response(status_code: int, json_data: dict):
    """Create a mock httpx.Response with a request attached (for raise_for_status)."""
    request = httpx.Request("GET", "http://test")
    return httpx.Response(status_code, json=json_data, request=request)


class TestGetProxyBase:
    """get_proxy_base environment variable handling."""

    def test_default_value(self):
        os.environ.pop("KSKILL_PROXY_BASE_URL", None)
        assert get_proxy_base() == DEFAULT_PROXY

    def test_custom_value(self):
        os.environ["KSKILL_PROXY_BASE_URL"] = "http://localhost:3456"
        try:
            assert get_proxy_base() == "http://localhost:3456"
        finally:
            os.environ.pop("KSKILL_PROXY_BASE_URL", None)

    def test_trailing_slash_stripped(self):
        os.environ["KSKILL_PROXY_BASE_URL"] = "http://localhost:3456/"
        try:
            assert get_proxy_base() == "http://localhost:3456"
        finally:
            os.environ.pop("KSKILL_PROXY_BASE_URL", None)


class TestProxyGet:
    """proxy_get HTTP request tests."""

    @pytest.mark.asyncio
    async def test_success(self):
        mock_response = _make_response(200, {"result": "ok"})
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("cli_anything.k_skill.proxy.httpx.AsyncClient", return_value=mock_client):
            from cli_anything.k_skill.proxy import proxy_get
            data, ms = await proxy_get("/test", {"q": "1"})
            assert data == {"result": "ok"}
            assert ms > 0

    @pytest.mark.asyncio
    async def test_http_error(self):
        mock_response = _make_response(500, {"error": "server error"})

        def raise_500():
            raise httpx.HTTPStatusError(
                "500", request=httpx.Request("GET", "http://x"), response=mock_response
            )
        mock_response.raise_for_status = raise_500

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("cli_anything.k_skill.proxy.httpx.AsyncClient", return_value=mock_client):
            from cli_anything.k_skill.proxy import proxy_get
            with pytest.raises(httpx.HTTPStatusError):
                await proxy_get("/test")
