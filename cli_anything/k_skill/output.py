"""
Output formatter for k-cli.
Supports JSON and human-readable output with consistent error handling.

All skill commands output through this module for uniform format.
AI agents should use --json flag for structured data.
"""

import json
import sys
from typing import Any, Optional


def success_response(
    skill: str,
    data: Any,
    source: str = "k-skill-proxy",
    response_time_ms: Optional[float] = None,
) -> dict:
    """Build a standard success response envelope.

    Args:
        skill: Skill identifier (e.g., "fine-dust", "korean-stock-search").
        data: The actual payload from the skill/proxy/MCP call.
        source: Origin of the data ("k-skill-proxy", "mcp://...", "local-cli", etc.).
        response_time_ms: Round-trip latency in milliseconds.

    Returns:
        dict ready for json.dumps.
    """
    envelope: dict[str, Any] = {
        "skill": skill,
        "status": "success",
        "data": data,
        "meta": {
            "source": source,
        },
    }
    if response_time_ms is not None:
        envelope["meta"]["response_time_ms"] = round(response_time_ms, 1)
    return envelope


def error_response(
    skill: str,
    code: str,
    message: str,
    fix: Optional[str] = None,
) -> dict:
    """Build a standard error response envelope.

    Error codes:
        PROXY_DOWN         - k-skill-proxy unreachable
        PROXY_HTTP_ERROR   - Non-2xx from proxy
        MISSING_DEPENDENCY - Required package/tool not installed
        MCP_ERROR          - MCP server communication failure
        MCP_TOOL_ERROR     - MCP tool returned isError=true
        INVALID_INPUT      - User-provided arguments are wrong
        TIMEOUT            - Request exceeded timeout
        UNKNOWN            - Unclassified error

    Args:
        skill: Skill identifier.
        code: Machine-readable error code.
        message: Human-readable description.
        fix: Suggested remediation command or action.

    Returns:
        dict ready for json.dumps.
    """
    envelope: dict[str, Any] = {
        "skill": skill,
        "status": "error",
        "error": {
            "code": code,
            "message": message,
        },
    }
    if fix:
        envelope["error"]["fix"] = fix
    return envelope


def format_json(response: dict) -> str:
    """Serialize response as compact JSON to stdout."""
    return json.dumps(response, ensure_ascii=False, default=str)


def format_human(response: dict) -> str:
    """Convert a response envelope into a human-readable summary.

    For success: prints key-value pairs from data.
    For error: prints error message and fix suggestion.
    """
    if response.get("status") == "error":
        err = response["error"]
        lines = [f"❌ [{err['code']}] {err['message']}"]
        if "fix" in err:
            lines.append(f"💡 해결: {err['fix']}")
        return "\n".join(lines)

    data = response.get("data", {})
    meta = response.get("meta", {})
    lines: list[str] = []

    if isinstance(data, dict):
        for key, val in data.items():
            if isinstance(val, dict):
                for k2, v2 in val.items():
                    lines.append(f"{k2}: {v2}")
            elif isinstance(val, list):
                lines.append(f"{key}: {len(val)}건")
                for i, item in enumerate(val[:5]):
                    if isinstance(item, dict):
                        name = item.get("name", item.get("title", item.get("station", str(item))))
                        lines.append(f"  {i + 1}. {name}")
                if len(val) > 5:
                    lines.append(f"  ... 외 {len(val) - 5}건")
            else:
                lines.append(f"{key}: {val}")
    elif isinstance(data, list):
        lines.append(f"{len(data)}건 결과")
        for i, item in enumerate(data[:5]):
            if isinstance(item, dict):
                name = item.get("name", item.get("title", item.get("station", str(item))))
                lines.append(f"  {i + 1}. {name}")
        if len(data) > 5:
            lines.append(f"  ... 외 {len(data) - 5}건")
    else:
        lines.append(str(data))

    if "response_time_ms" in meta:
        lines.append(f"⏱ {meta['response_time_ms']}ms ({meta.get('source', '')})")

    return "\n".join(lines)


def emit(response: dict, as_json: bool = False):
    """Write formatted output to stdout."""
    if as_json:
        sys.stdout.write(format_json(response) + "\n")
    else:
        sys.stdout.write(format_human(response) + "\n")
    sys.stdout.flush()
