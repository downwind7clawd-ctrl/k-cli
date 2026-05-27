"""
k-skill — CLI-Anything harness for k-skill.

80+ Korean utility skills accessible from any AI agent.
Zero-config for proxy-based skills; auto dependency detection for others.

Quick start:
    pip install k-skill-cli
    k-skill weather dust "서울 강남구" --json
    k-skill finance stock "삼성전자" --json

Environment variables:
    KSKILL_PROXY_BASE_URL  Override default k-skill-proxy URL
                           (default: https://k-skill-proxy.nomadamas.org)
"""

import importlib.metadata
try:
    __version__ = importlib.metadata.version("k-skill-cli")
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"
