"""Tests for SSRF protection in mcp_client.py."""

import pytest

from cli_anything.k_skill.mcp_client import (
    RemoteMCPClient,
    MCPError,
    _validate_endpoint_url,
)


class TestValidateEndpointURL:
    """URL validation security tests."""

    def test_https_allowed(self):
        assert _validate_endpoint_url("https://example.com/mcp") == "https://example.com/mcp"

    def test_http_blocked(self):
        with pytest.raises(MCPError, match="Only https"):
            _validate_endpoint_url("http://localhost:8080/mcp")

    def test_localhost_blocked(self):
        with pytest.raises(MCPError, match="localhost"):
            _validate_endpoint_url("https://localhost/mcp")

    def test_127_0_0_1_blocked(self):
        with pytest.raises(MCPError, match="Private IP"):
            _validate_endpoint_url("https://127.0.0.1/mcp")

    def test_10_private_blocked(self):
        with pytest.raises(MCPError, match="Private IP"):
            _validate_endpoint_url("https://10.0.0.1/mcp")

    def test_172_private_blocked(self):
        with pytest.raises(MCPError, match="Private IP"):
            _validate_endpoint_url("https://172.16.0.1/mcp")

    def test_192_private_blocked(self):
        with pytest.raises(MCPError, match="Private IP"):
            _validate_endpoint_url("https://192.168.1.1/mcp")

    def test_aws_metadata_blocked(self):
        with pytest.raises(MCPError, match="Private IP"):
            _validate_endpoint_url("https://169.254.169.254/latest")

    def test_trailing_slash_stripped(self):
        assert _validate_endpoint_url("https://example.com/mcp/") == "https://example.com/mcp"

    def test_hostname_allowed(self):
        assert _validate_endpoint_url("https://mcp-servers.myrealtrip.com/mcp") == "https://mcp-servers.myrealtrip.com/mcp"


class TestRemoteMCPClientSSRF:
    """SSRF protection via constructor validation."""

    def test_blocks_private_ip(self):
        with pytest.raises(MCPError, match="Private IP"):
            RemoteMCPClient("https://192.168.0.1/mcp")

    def test_blocks_http(self):
        with pytest.raises(MCPError, match="Only https"):
            RemoteMCPClient("http://internal-service/mcp")

    def test_blocks_localhost(self):
        with pytest.raises(MCPError, match="localhost"):
            RemoteMCPClient("https://localhost.localdomain/mcp")
