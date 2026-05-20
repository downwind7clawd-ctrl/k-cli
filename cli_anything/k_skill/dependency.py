"""
3-layer dependency checker for k-cli skills.

Layer 1: System dependencies (node, python3, curl, jq)
Layer 2: Package dependencies (npm global, pip packages)
Layer 3: Runtime config (API keys, proxy reachability)

Dependencies are declared in manifest.yaml files per domain.
Skills never install packages silently — they report what is missing.
"""

import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SkillDependency:
    """Declaration of a skill's prerequisites."""

    name: str
    system: list[str] = field(default_factory=list)    # e.g. ["node", "curl"]
    python: list[str] = field(default_factory=list)    # e.g. ["SRTrain", "httpx"]
    npm: list[str] = field(default_factory=list)       # e.g. ["kbo-game", "daiso"]
    proxy: bool = False                                 # requires k-skill-proxy
    mcp_remote: Optional[str] = None                    # remote MCP endpoint URL
    mcp_local: Optional[list[str]] = None               # local MCP command
    env_keys: list[str] = field(default_factory=list)   # e.g. ["KRX_API_KEY"]
    auth: bool = False                                  # requires user login


@dataclass
class DependencyReport:
    """Result of dependency check."""

    skill_name: str
    ready: bool
    missing_system: list[str] = field(default_factory=list)
    missing_python: list[str] = field(default_factory=list)
    missing_npm: list[str] = field(default_factory=list)
    proxy_reachable: Optional[bool] = None
    mcp_reachable: Optional[bool] = None
    missing_env: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "skill": self.skill_name,
            "ready": self.ready,
            "missing": {
                "system": self.missing_system,
                "python": self.missing_python,
                "npm": self.missing_npm,
                "env_keys": self.missing_env,
            },
            "checks": {
                "proxy": self.proxy_reachable,
                "mcp": self.mcp_reachable,
            },
            "notes": self.notes,
        }


def _check_system_tools(tools: list[str]) -> list[str]:
    """Check if system CLI tools are available on PATH."""
    return [tool for tool in tools if not shutil.which(tool)]


def _check_python_packages(packages: list[str]) -> list[str]:
    """Check if Python packages are importable.

    Uses importlib.util.find_spec() instead of __import__() to prevent
    arbitrary code execution from malicious manifest entries.
    Validates package name pattern (alphanumeric + dots + underscores only).
    """
    import re
    import importlib.util
    missing = []
    name_pattern = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_.]*$")
    for pkg in packages:
        if not name_pattern.match(pkg):
            missing.append(pkg)
            continue
        try:
            if importlib.util.find_spec(pkg) is None:
                missing.append(pkg)
        except (ImportError, ValueError, ModuleNotFoundError):
            missing.append(pkg)
    return missing


def _check_npm_packages(packages: list[str]) -> list[str]:
    """Check if npm global packages are installed."""
    missing = []
    for pkg in packages:
        result = subprocess.run(
            ["npm", "list", "-g", pkg, "--depth=0"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode != 0:
            missing.append(pkg)
    return missing


def _check_env_keys(keys: list[str]) -> list[str]:
    """Check if required environment variables are set."""
    return [key for key in keys if not os.environ.get(key)]


async def check_dependency(dep: SkillDependency) -> DependencyReport:
    """Run full 3-layer dependency check for a skill.

    Args:
        dep: SkillDependency declaration.

    Returns:
        DependencyReport with detailed status.
    """
    report = DependencyReport(skill_name=dep.name, ready=False)

    # Layer 1: System tools
    report.missing_system = _check_system_tools(dep.system)

    # Layer 2: Packages
    report.missing_python = _check_python_packages(dep.python)
    report.missing_npm = _check_npm_packages(dep.npm) if dep.npm else []

    # Layer 3: Runtime
    if dep.proxy:
        try:
            from .proxy import health_check
            report.proxy_reachable = await health_check()
        except Exception:
            report.proxy_reachable = False

    if dep.mcp_remote:
        try:
            from .mcp_client import RemoteMCPClient
            client = RemoteMCPClient(dep.mcp_remote, timeout=5.0)
            report.mcp_reachable = await client.health_check()
        except Exception:
            report.mcp_reachable = False

    if dep.env_keys:
        report.missing_env = _check_env_keys(dep.env_keys)

    # Determine readiness
    all_missing = (
        report.missing_system
        + report.missing_python
        + report.missing_npm
        + report.missing_env
    )
    proxy_ok = (not dep.proxy) or report.proxy_reachable
    mcp_ok = (dep.mcp_remote is None) or report.mcp_reachable

    report.ready = (len(all_missing) == 0) and proxy_ok and mcp_ok

    # Notes
    if dep.auth:
        report.notes.append("이 스킬은 사용자 인증이 필요합니다.")
    if report.missing_python:
        report.notes.append(f"pip 설치 필요: pip install {' '.join(report.missing_python)}")
    if report.missing_npm:
        report.notes.append(f"npm 설치 필요: npm install -g {' '.join(report.missing_npm)}")
    if report.missing_system:
        report.notes.append(f"시스템 도구 필요: {', '.join(report.missing_system)}")

    return report


def build_fix_instructions(report: DependencyReport) -> str:
    """Generate human-readable fix instructions from a dependency report."""
    lines = []
    if report.missing_system:
        lines.append(f"시스템 도구 설치: {', '.join(report.missing_system)}")
    if report.missing_python:
        lines.append(f"pip install {' '.join(report.missing_python)}")
    if report.missing_npm:
        lines.append(f"npm install -g {' '.join(report.missing_npm)}")
    if report.missing_env:
        lines.append(f"환경변수 설정: {', '.join(report.missing_env)}")
    if report.proxy_reachable is False:
        lines.append("k-skill-proxy 연결 불가 — KSKILL_PROXY_BASE_URL 확인")
    return " | ".join(lines) if lines else "준비 완료"
