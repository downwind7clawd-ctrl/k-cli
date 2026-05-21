"""범용 스킬 실행 모듈 — npm, pip, Python script, MCP 러너.

모든 공개 함수는 async.
"""

from __future__ import annotations

import asyncio
import importlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from cli_anything.k_skill.dependency import check_dependency, SkillDependency
from cli_anything.k_skill.output import success_response, error_response


# ── Constants ──────────────────────────────────────────────

_K_SKILL_ROOT_ENV = os.environ.get("K_SKILL_ROOT")
if _K_SKILL_ROOT_ENV:
    K_SKILL_ROOT = Path(_K_SKILL_ROOT_ENV).expanduser()
else:
    K_SKILL_ROOT = Path(__file__).resolve().parent.parent.parent.parent / "k-skill"
K_SKILL_SCRIPTS = K_SKILL_ROOT / "scripts"
K_SKILL_PACKAGES = K_SKILL_ROOT / "packages"
NODE_BIN = shutil.which("node") or shutil.which("nodejs") or "node"
NPX_BIN = shutil.which("npx") or shutil.which("npx.cmd") or "npx"
PYTHON_BIN = sys.executable

_NPM_BIN_CACHE: dict[str, str] = {}


def _ensure_k_skill_root() -> str | None:
    """Validate K_SKILL_ROOT exists. Returns error message or None if OK."""
    if not K_SKILL_ROOT.exists():
        return (
            f"K_SKILL_ROOT 경로가 존재하지 않습니다: {K_SKILL_ROOT}\n"
            f"K_SKILL_ROOT 환경변수로 올바른 k-skill 디렉토리 경로를 설정하세요."
        )
    return None

# Environment variable whitelist for subprocess execution
# Only these keys (or prefixes) are passed to child processes
_SUBPROCESS_ENV_ALLOWLIST = frozenset({
    "PATH", "HOME", "USER", "SHELL", "LANG", "LC_ALL", "LC_CTYPE",
    "TERM", "TMPDIR", "XDG_RUNTIME_DIR", "DISPLAY", "WAYLAND_DISPLAY",
    "NODE_PATH", "PYTHONPATH", "K_SKILL_ROOT",
    "KSKILL_PROXY_BASE_URL",
    "ODSAY_API_KEY",
    "NAVER_CLIENT_ID",
    "NAVER_CLIENT_SECRET",
    "COUPANG_ACCESS_KEY",
    "COUPANG_SECRET_KEY",
    "DART_API_KEY",
    "KOSIS_API_KEY",
})
_SUBPROCESS_ENV_ALLOWLIST_PREFIXES = ("LC_", "XDG_")


def _find_npm_bin(package_name: str) -> str | None:
    """k-skill workspaces에서 로컬 npm 패키지의 bin 경로 찾기."""
    if package_name in _NPM_BIN_CACHE:
        return _NPM_BIN_CACHE[package_name]

    pkg_dir = K_SKILL_PACKAGES / package_name
    if pkg_dir.is_dir():
        pkg_json = pkg_dir / "package.json"
        if pkg_json.is_file():
            try:
                data = json.loads(pkg_json.read_text())
                bins = data.get("bin", {})
                if isinstance(bins, str):
                    abs_path = str((pkg_dir / bins).resolve())
                    _NPM_BIN_CACHE[package_name] = abs_path
                    return abs_path
                elif isinstance(bins, dict) and bins:
                    val = list(bins.values())[0]
                    abs_path = str((pkg_dir / val).resolve())
                    _NPM_BIN_CACHE[package_name] = abs_path
                    return abs_path
            except Exception:
                pass

    nm_bin = K_SKILL_ROOT / "node_modules" / ".bin" / package_name.replace("@", "").replace("/", "-")
    if nm_bin.is_file():
        _NPM_BIN_CACHE[package_name] = str(nm_bin)
        return str(nm_bin)

    return None


def _filter_env(additional: dict[str, str] | None = None) -> dict[str, str]:
    """Build a filtered environment dict, allowing only safe keys plus explicit additions."""
    env: dict[str, str] = {}
    for k, v in os.environ.items():
        if k in _SUBPROCESS_ENV_ALLOWLIST or any(k.startswith(p) for p in _SUBPROCESS_ENV_ALLOWLIST_PREFIXES):
            env[k] = v
    if additional:
        env.update(additional)
    return env


async def _run_subprocess(
    cmd: list[str],
    timeout: int,
    cwd: Path,
    env: dict[str, str],
) -> tuple[str, str, int]:
    """subprocess를 비동기로 실행."""
    loop = asyncio.get_running_loop()
    process = await loop.run_in_executor(
        None,
        lambda: subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd, env=env),
    )
    return process.stdout.strip(), process.stderr.strip(), process.returncode


# ── npm runner ────────────────────────────────────────────

# npm 패키지명 검증 패턴: 알파벳, 숫자, 하이픈, 언더스코어, @, /, . 만 허용
_SAFE_NPM_PKG = re.compile(r'^[a-zA-Z0-9_\-@/.]+$')

async def run_npm(
    package: str,
    args: list[str] | None = None,
    *,
    npx: bool = False,
    global_install: bool = False,
    timeout: int = 30,
    cwd: Path | None = None,
) -> dict[str, Any]:
    """npm 패키지를 실행하고 결과를 반환."""
    args = args or []
    start = time.monotonic()

    err = _ensure_k_skill_root()
    if err:
        return error_response(package, "CONFIG_ERROR", err)

    if not _SAFE_NPM_PKG.match(package):
        return error_response(
            package, "INVALID_INPUT",
            f"잘못된 npm 패키지명: {package}",
        )

    bin_cmd = _find_npm_bin(package)

    if bin_cmd and os.path.isfile(bin_cmd):
        cmd = [PYTHON_BIN, bin_cmd] if bin_cmd.endswith(".py") else [NODE_BIN, bin_cmd]
        cmd.extend(args)
    elif npx or not global_install:
        cmd = [NPX_BIN, "--yes", package] + args
    else:
        cmd = [package] + args

    try:
        env = _filter_env({"NODE_PATH": str(K_SKILL_ROOT / "node_modules")})

        stdout, stderr, rc = await _run_subprocess(
            cmd, timeout, cwd or K_SKILL_ROOT, env,
        )

        elapsed_ms = int((time.monotonic() - start) * 1000)

        if rc != 0:
            return error_response(
                package, "COMMAND_FAILED",
                stderr or f"exit code {rc}",
                fix=f"npm 패키지 '{package}' 실행 실패. 설치 상태를 확인하세요.",
            )

        try:
            data = json.loads(stdout)
        except json.JSONDecodeError:
            data = {"raw_output": stdout}

        return success_response(package, data, response_time_ms=elapsed_ms)

    except FileNotFoundError:
        return error_response(
            package, "MISSING_DEPENDENCY",
            f"npm/node가 없거나 패키지 '{package}'를 찾을 수 없습니다.",
            fix=f"npm install -g {package} 또는 cd {K_SKILL_ROOT} && npm install",
        )
    except subprocess.TimeoutExpired:
        return error_response(package, "TIMEOUT", f"실행이 {timeout}초 초과되었습니다.")
    except Exception as e:
        return error_response(package, "UNKNOWN", str(e))


# ── Python script runner ──────────────────────────────────

async def run_script(
    script_name: str,
    args: list[str] | None = None,
    *,
    timeout: int = 30,
    cwd: Path | None = None,
    python_path: str | None = None,
    env_vars: dict[str, str] | None = None,
    script_dirs: list[Path] | None = None,
) -> dict[str, Any]:
    """Python 스크립트를 실행하고 결과를 반환."""
    args = args or []
    err = _ensure_k_skill_root()
    if err:
        return error_response(script_name, "CONFIG_ERROR", err)
    start = time.monotonic()

    search_roots = script_dirs or [K_SKILL_SCRIPTS, K_SKILL_ROOT / script_name / "scripts"]

    script_path = None
    for root in search_roots:
        candidates = [
            root / script_name,
            root / script_name.replace("-", "_"),
            root / f"{script_name.replace('-', '_')}.py",
            root / f"{script_name}.py",
        ]
        for c in candidates:
            if c.is_file():
                script_path = c
                break
        if script_path:
            break

    if script_path is None:
        pattern = f"*{script_name.replace('-', '_')}*"
        for root in search_roots:
            if root.is_dir():
                found = [f for f in root.glob(pattern) if f.suffix == ".py" and not f.name.startswith("test_")]
                if found:
                    script_path = found[0]
                    break

    if script_path is None:
        return error_response(
            script_name, "MISSING_DEPENDENCY",
            f"스크립트 '{script_name}'을 찾을 수 없습니다.",
            fix=f"k-skill 리포에 스크립트가 있는지 확인: {K_SKILL_SCRIPTS}",
        )

    try:
        env = _filter_env({
            "PYTHONPATH": str(K_SKILL_SCRIPTS),
            "K_SKILL_ROOT": str(K_SKILL_ROOT),
            **(env_vars or {}),
        })

        cmd = [python_path or PYTHON_BIN, str(script_path)] + args
        stdout, stderr, rc = await _run_subprocess(cmd, timeout, cwd or K_SKILL_ROOT, env)

        elapsed_ms = int((time.monotonic() - start) * 1000)

        if rc != 0:
            return error_response(
                script_name, "COMMAND_FAILED",
                stderr or stdout or f"exit code {rc}",
            )

        try:
            data = json.loads(stdout)
        except json.JSONDecodeError:
            data = {"raw_output": stdout}

        return success_response(script_name, data, response_time_ms=elapsed_ms)

    except subprocess.TimeoutExpired:
        return error_response(script_name, "TIMEOUT", f"실행이 {timeout}초 초과되었습니다.")
    except Exception as e:
        return error_response(script_name, "UNKNOWN", str(e))


# ── pip package runner ────────────────────────────────────

async def run_pip_import(
    module_name: str,
    function_name: str,
    args: dict[str, Any] | list[Any] | None = None,
    *,
    packages: list[str] | None = None,
    timeout: int = 30,
) -> dict[str, Any]:
    """pip 패키지를 import하여 함수를 호출."""
    start = time.monotonic()
    packages = packages or [module_name]

    dep = SkillDependency(name=module_name, python=packages)
    report = await check_dependency(dep)
    if report.missing_python:
        pkg_str = ", ".join(report.missing_python)
        return error_response(
            module_name, "MISSING_DEPENDENCY",
            f"pip 패키지 미설치: {pkg_str}",
            fix=f"pip install {' '.join(report.missing_python)}",
        )

    try:
        mod = importlib.import_module(module_name)
        func = getattr(mod, function_name, None)
        if func is None:
            return error_response(
                module_name, "INVALID_INPUT",
                f"모듈 '{module_name}'에 함수 '{function_name}'이 없습니다.",
            )

        if isinstance(args, dict):
            result = func(**args)
        elif isinstance(args, list):
            result = func(*args)
        else:
            result = func()

        elapsed_ms = int((time.monotonic() - start) * 1000)
        if isinstance(result, dict):
            return success_response(module_name, result, response_time_ms=elapsed_ms)
        return success_response(module_name, {"result": str(result)}, response_time_ms=elapsed_ms)

    except Exception as e:
        elapsed_ms = int((time.monotonic() - start) * 1000)
        return error_response(module_name, "COMMAND_FAILED", str(e))


# ── MCP runner ────────────────────────────────────────────

async def run_mcp(
    skill_name: str,
    server_url: str | None = None,
    tool_name: str | None = None,
    arguments: dict[str, Any] | None = None,
    *,
    timeout: int = 30,
) -> dict[str, Any]:
    """MCP 서버를 통해 도구를 호출."""
    start = time.monotonic()
    arguments = arguments or {}

    try:
        if server_url and server_url.startswith("http"):
            from cli_anything.k_skill.mcp_client import RemoteMCPClient
            client = RemoteMCPClient(server_url, timeout=timeout)
            await client.initialize()
            tools = await client.list_tools()
            if not tools:
                return error_response(skill_name, "MCP_ERROR", "MCP 서버에 도구가 없습니다.")

            if not tool_name:
                return error_response(
                    skill_name, "INVALID_INPUT",
                    f"tool_name이 필요합니다. 사용 가능한 도구: {', '.join(t.get('name', '') for t in tools)}",
                )
            content, _ = await client.call_tool(tool_name, arguments)
            elapsed_ms = int((time.monotonic() - start) * 1000)
            return success_response(skill_name, {"content": content}, response_time_ms=elapsed_ms)

        elif server_url and server_url.startswith("local://"):
            from cli_anything.k_skill.local_mcp_bridge import LocalMCPBridge, _SAFE_COMMAND_PATTERN
            command_str = server_url[8:]
            command = command_str.split() if command_str else []
            if not command:
                return error_response(
                    skill_name, "INVALID_INPUT",
                    "local:// MCP 서버 URL에 명령어가 필요합니다.",
                )
            if not shutil.which(command[0]):
                return error_response(
                    skill_name, "MISSING_DEPENDENCY",
                    f"MCP 서버 명령어를 찾을 수 없습니다: '{command[0]}'",
                    fix="k-skill setup install 로 설치 가이드를 확인하세요.",
                )
            for part in command:
                if ".." in part:
                    return error_response(
                        skill_name, "INVALID_INPUT",
                        f"MCP 서버 명령어에 '..'은 허용되지 않습니다: '{part}'",
                    )
                if not _SAFE_COMMAND_PATTERN.match(part):
                    return error_response(
                        skill_name, "INVALID_INPUT",
                        f"허용되지 않은 MCP 서버 명령어: '{part}'",
                    )
            bridge = LocalMCPBridge(command=command)
            await bridge.start()
            try:
                if not tool_name:
                    return error_response(
                        skill_name, "INVALID_INPUT",
                        "local:// MCP 서버 호출 시 tool_name이 필요합니다.",
                    )
                content, _ = await bridge.call_tool(tool_name, arguments)
                elapsed_ms = int((time.monotonic() - start) * 1000)
                return success_response(skill_name, {"content": content}, response_time_ms=elapsed_ms)
            finally:
                await bridge.stop()

        else:
            return error_response(
                skill_name, "INVALID_INPUT",
                "MCP 서버 URL이 필요합니다. (http://... 또는 local://...)",
            )

    except Exception as e:
        elapsed_ms = int((time.monotonic() - start) * 1000)
        return error_response(skill_name, "MCP_ERROR", str(e))
