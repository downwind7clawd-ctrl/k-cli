"""
Transparent proxy routing for k-skill-proxy.

All proxy-based skills route through this module.
Default: https://k-skill-proxy.nomadamas.org
Override: KSKILL_PROXY_BASE_URL environment variable

Usage from skill commands:
    from cli_anything.k_skill.proxy import proxy_get
    data = await proxy_get("/v1/fine-dust/report", {"regionHint": "강남구"})
"""

import os
import time
from typing import Any, Optional

import httpx


DEFAULT_PROXY = "https://k-skill-proxy.nomadamas.org"
DEFAULT_TIMEOUT = 15  # seconds


def get_proxy_base() -> str:
    """Return the active proxy base URL.

    Checks KSKILL_PROXY_BASE_URL env var first, falls back to default.
    Trailing slash is stripped.
    """
    base = os.environ.get("KSKILL_PROXY_BASE_URL", DEFAULT_PROXY)
    return base.rstrip("/")


async def proxy_get(
    path: str,
    params: Optional[dict] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> tuple[dict, float]:
    """Send GET to k-skill-proxy and return (data_dict, response_time_ms).

    Args:
        path: Proxy API path, e.g. "/v1/fine-dust/report".
        params: Query parameters.
        timeout: Request timeout in seconds.

    Returns:
        Tuple of (parsed JSON response, response time in ms).

    Raises:
        httpx.HTTPStatusError: On non-2xx responses.
        httpx.ConnectError: If proxy is unreachable.
        httpx.TimeoutException: On timeout.
    """
    base = get_proxy_base()
    url = f"{base}{path}"

    start = time.monotonic()
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, timeout=timeout)
        resp.raise_for_status()
        elapsed_ms = (time.monotonic() - start) * 1000

    return resp.json(), elapsed_ms


async def proxy_post(
    path: str,
    json_body: Optional[dict] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> tuple[dict, float]:
    """Send POST to k-skill-proxy and return (data_dict, response_time_ms)."""
    base = get_proxy_base()
    url = f"{base}{path}"

    start = time.monotonic()
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=json_body, timeout=timeout)
        resp.raise_for_status()
        elapsed_ms = (time.monotonic() - start) * 1000

    return resp.json(), elapsed_ms


async def health_check(timeout: float = 5.0) -> bool:
    """Check if the proxy is reachable."""
    base = get_proxy_base()
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{base}/health", timeout=timeout)
            return resp.status_code < 500
    except Exception:
        return False
