"""
Transparent proxy routing for k-skill-proxy.

All proxy-based skills route through this module.
Default: https://k-skill-proxy.nomadamas.org
Override: KSKILL_PROXY_BASE_URL environment variable

Usage from skill commands:
    from cli_anything.k_skill.proxy import proxy_get
    data = await proxy_get("/v1/fine-dust/report", {"regionHint": "강남구"})
"""

import asyncio
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


def safe_proxy_get(
    skill: str,
    path: str,
    params: dict = None,
    timeout: float = DEFAULT_TIMEOUT,
):
    """Synchronous wrapper: run proxy_get in event loop with full error handling.

    Returns a response envelope dict (success or error).
    Use this from Click commands to avoid boilerplate try/except.
    """
    from .output import success_response, error_response

    try:
        data, elapsed = asyncio.run(proxy_get(path, params, timeout))
        return success_response(skill, data, response_time_ms=elapsed)
    except httpx.ConnectError:
        return error_response(
            skill, "PROXY_DOWN",
            "k-skill-proxy 서버에 연결할 수 없습니다",
            "KSKILL_PROXY_BASE_URL 환경변수 확인 또는 네트워크 상태 점검",
        )
    except httpx.HTTPStatusError as e:
        return error_response(
            skill, "PROXY_HTTP_ERROR",
            f"프록시 HTTP 오류: {e.response.status_code}",
            f"응답: {e.response.text[:200]}",
        )
    except httpx.TimeoutException:
        return error_response(
            skill, "TIMEOUT",
            "요청 시간이 초과되었습니다",
            "잠시 후 재시도하세요",
        )
    except Exception as e:
        return error_response(
            skill, "UNKNOWN",
            f"알 수 없는 오류: {e}",
        )


def safe_proxy_post(
    skill: str,
    path: str,
    json_body: dict = None,
    timeout: float = DEFAULT_TIMEOUT,
):
    """Synchronous wrapper: run proxy_post in event loop with full error handling.

    Returns a response envelope dict (success or error).
    """
    from .output import success_response, error_response

    try:
        data, elapsed = asyncio.run(proxy_post(path, json_body, timeout))
        return success_response(skill, data, response_time_ms=elapsed)
    except httpx.ConnectError:
        return error_response(
            skill, "PROXY_DOWN",
            "k-skill-proxy 서버에 연결할 수 없습니다",
            "KSKILL_PROXY_BASE_URL 환경변수 확인 또는 네트워크 상태 점검",
        )
    except httpx.HTTPStatusError as e:
        return error_response(
            skill, "PROXY_HTTP_ERROR",
            f"프록시 HTTP 오류: {e.response.status_code}",
            f"응답: {e.response.text[:200]}",
        )
    except httpx.TimeoutException:
        return error_response(
            skill, "TIMEOUT",
            "요청 시간이 초과되었습니다",
            "잠시 후 재시도하세요",
        )
    except Exception as e:
        return error_response(
            skill, "UNKNOWN",
            f"알 수 없는 오류: {e}",
        )


async def health_check(timeout: float = 5.0) -> bool:
    """Check if the proxy is reachable."""
    base = get_proxy_base()
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{base}/health", timeout=timeout)
            return resp.status_code < 500
    except Exception:
        return False
