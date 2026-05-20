"""
Local MCP server bridge — communicates via subprocess stdin/stdout JSON-RPC.

Used for MCP servers that run as local processes (e.g., coupang_mcp.py).

Usage:
    async with LocalMCPBridge(["python3", "bin/coupang_mcp.py"], cwd="/path") as bridge:
        tools = await bridge.list_tools()
        result = await bridge.call_tool("search", {"query": "에어팟"})
"""

import asyncio
import json
import os
import re
import time
from typing import Any, Optional


# Allowed command patterns for local MCP servers (security)
_SAFE_COMMAND_PATTERN = re.compile(r"^[a-zA-Z0-9_\-.+/]+$")
_READ_TIMEOUT = 30.0  # seconds for readline
_DRAIN_TIMEOUT = 10.0  # seconds for stdin drain


class MCPBridgeError(Exception):
    """Raised when local MCP bridge communication fails."""

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


class LocalMCPBridge:
    """Bridge to a local MCP server process via stdin/stdout.

    The MCP server must support stdio JSON-RPC transport.
    Supports async context manager for automatic lifecycle management.
    """

    def __init__(
        self,
        command: list[str],
        cwd: Optional[str] = None,
        env: Optional[dict] = None,
    ):
        """Initialize bridge.

        Args:
            command: Command and arguments to start the MCP server.
            cwd: Working directory for the subprocess.
            env: Additional environment variables (merged with os.environ).
        """
        # Security: validate command parts to prevent arbitrary execution
        if not command or len(command) == 0:
            raise MCPBridgeError(
                code="INVALID_COMMAND", message="Command must be a non-empty list."
            )
        for part in command:
            if not _SAFE_COMMAND_PATTERN.match(part):
                raise MCPBridgeError(
                    code="INVALID_COMMAND",
                    message=f"Disallowed command part: '{part}'. Only alphanumeric, dots, dashes, slashes, plus signs are allowed.",
                )
        self.command = command
        self.cwd = cwd
        self.env = env
        self._process: Optional[asyncio.subprocess.Process] = None
        self._request_id = 0

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id

    async def start(self):
        """Start the MCP server process and perform initialization handshake."""
        if self.env:
            safe_keys = {"PATH", "HOME", "USER", "SHELL", "LANG", "LC_ALL", "LC_CTYPE",
                         "TERM", "TMPDIR", "XDG_RUNTIME_DIR", "NODE_PATH", "PYTHONPATH"}
            env = {k: v for k, v in os.environ.items() if k in safe_keys or k.startswith("LC_") or k.startswith("XDG_")}
            env.update(self.env)
        else:
            env = None

        self._process = await asyncio.create_subprocess_exec(
            *self.command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.cwd,
            env=env,
        )

        # Send initialize
        await self._send({
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "clientInfo": {"name": "cli-anything-k-skill", "version": "0.1.0"},
                "capabilities": {},
            },
            "id": self._next_id(),
        })

        # Read initialize response
        init_resp = await self._read_response()
        if "error" in init_resp:
            raise MCPBridgeError(
                code="MCP_INIT_FAILED",
                message=f"MCP initialization failed: {init_resp['error']}",
            )

        # Send initialized notification
        await self._send({
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
        })

    async def call_tool(
        self,
        tool_name: str,
        arguments: Optional[dict] = None,
    ) -> tuple[Any, float]:
        """Invoke an MCP tool on the local server.

        Returns:
            Tuple of (tool result, elapsed time in ms).
        """
        if not self._process or self._process.returncode is not None:
            raise MCPBridgeError(
                code="MCP_NOT_RUNNING",
                message="MCP server process is not running. Call start() first.",
            )

        start = time.monotonic()
        await self._send({
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {},
            },
            "id": self._next_id(),
        })
        result = await self._read_response()
        elapsed_ms = (time.monotonic() - start) * 1000

        return result, elapsed_ms

    async def list_tools(self) -> list[dict]:
        """List available tools on the local MCP server."""
        if not self._process or self._process.returncode is not None:
            raise MCPBridgeError(
                code="MCP_NOT_RUNNING",
                message="MCP server process is not running.",
            )

        await self._send({
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": self._next_id(),
        })
        result = await self._read_response()
        return result.get("result", {}).get("tools", [])

    def _ensure_process(self) -> asyncio.subprocess.Process:
        """Return self._process, raising MCPBridgeError if not started."""
        if self._process is None or self._process.returncode is not None:
            raise MCPBridgeError(
                code="MCP_NOT_RUNNING",
                message="MCP server process is not running. Call start() first.",
            )
        return self._process

    async def _send(self, payload: dict):
        """Send JSON-RPC payload to stdin."""
        proc = self._ensure_process()
        data = json.dumps(payload) + "\n"
        proc.stdin.write(data.encode("utf-8"))
        await asyncio.wait_for(proc.stdin.drain(), timeout=_DRAIN_TIMEOUT)

    async def _read_response(self) -> dict:
        """Read one JSON-RPC response from stdout."""
        proc = self._ensure_process()
        try:
            line_bytes = await asyncio.wait_for(
                proc.stdout.readline(), timeout=_READ_TIMEOUT
            )
        except asyncio.TimeoutError:
            raise MCPBridgeError(
                code="MCP_TIMEOUT",
                message=f"MCP server did not respond within {_READ_TIMEOUT}s.",
            )
        if not line_bytes:
            raise MCPBridgeError(
                code="MCP_EOF",
                message="MCP server closed connection (process may have crashed).",
            )
        line = line_bytes.decode("utf-8").strip()
        return json.loads(line)

    async def stop(self):
        """Terminate the MCP server process gracefully."""
        if self._process and self._process.returncode is None:
            try:
                self._process.terminate()
                await asyncio.wait_for(self._process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                self._process.kill()
                await self._process.wait()
            except ProcessLookupError:
                pass
        self._process = None

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, *args):
        await self.stop()
