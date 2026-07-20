from pathlib import Path

from click.testing import CliRunner
from cli_anything.k_skill.skills.other import cli as other_cli


def test_whois_domain_proxy(monkeypatch):
    captured = {}

    def fake_proxy(name, path, params):
        captured["name"] = name
        captured["path"] = path
        return {"ok": True}

    monkeypatch.setattr("cli_anything.k_skill.skills.other.safe_proxy_get", fake_proxy)
    runner = CliRunner()
    result = runner.invoke(other_cli, ["whois", "domain", "--q", "example.com", "-j"])
    assert result.exit_code == 0, result.output
    assert captured["name"] == "kr-whois-lookup"
    assert captured["path"] == "/v1/kr-whois/domain"


def test_gov_overseas_providers_script(monkeypatch):
    captured = {}

    async def fake_run(script, args, **kwargs):
        captured["script"] = script
        captured["script_dirs"] = kwargs.get("script_dirs", [])
        return {"ok": True}

    monkeypatch.setattr("cli_anything.k_skill.skills.other.run_script", fake_run)
    runner = CliRunner()
    result = runner.invoke(other_cli, ["gov-overseas", "providers", "-j"])
    assert result.exit_code == 0, result.output
    assert captured["script"] == "gov_overseas_trip_report.py"
    assert any("gov-overseas-trip-report" in Path(p).parts for p in captured["script_dirs"])


def test_naver_ad_campaigns_script(monkeypatch):
    captured = {}

    async def fake_run(script, args, **kwargs):
        captured["script"] = script
        captured["script_dirs"] = kwargs.get("script_dirs", [])
        return {"ok": True}

    monkeypatch.setattr("cli_anything.k_skill.skills.other.run_script", fake_run)
    runner = CliRunner()
    result = runner.invoke(other_cli, ["naver-ad", "campaigns", "-j"])
    assert result.exit_code == 0, result.output
    assert captured["script"] == "naver_ad_performance.py"
    assert any("naver-ad-performance" in Path(p).parts for p in captured["script_dirs"])
