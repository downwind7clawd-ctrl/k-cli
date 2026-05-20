"""
k-cli — CLI-Anything harness for k-skill.

86+ Korean utility skills accessible from any AI agent.
Zero-config for proxy-based skills; auto dependency detection for others.

Quick start:
    pip install cli-anything-k-skill
    k-cli weather fine-dust --region "서울 강남구" --json
    k-cli finance stock-search --query "삼성전자" --json

Environment variables:
    KSKILL_PROXY_BASE_URL  Override default k-skill-proxy URL
                           (default: https://k-skill-proxy.nomadamas.org)
"""

__version__ = "0.1.0"
