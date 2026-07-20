import pytest
from click.testing import CliRunner
from cli_anything.k_skill.skills.realestate import cli as realestate_cli


def _capture(monkeypatch):
    captured = []
    def fake_get(name, path, params=None, timeout=None):
        captured.append((name, path))
        return {"status": "success", "data": {}}
    monkeypatch.setattr("cli_anything.k_skill.skills.realestate.safe_proxy_get", fake_get)
    return captured


def test_realestate_code_rename(monkeypatch):
    captured = _capture(monkeypatch)
    runner = CliRunner()
    res = runner.invoke(realestate_cli, ["realestate", "code", "서울 강남구", "-j"])
    assert res.exit_code == 0, res.output
    assert captured[0] == ("real-estate-search", "/v1/real-estate/region-code")


def test_realestate_search_rename(monkeypatch):
    captured = _capture(monkeypatch)
    runner = CliRunner()
    res = runner.invoke(realestate_cli, [
        "realestate", "search", "--lawd-cd", "11680", "--date", "202403", "-j",
    ])
    assert res.exit_code == 0, res.output
    assert captured[0] == ("real-estate-search", "/v1/real-estate/apartment/trade")


def test_lh_search_rename(monkeypatch):
    captured = _capture(monkeypatch)
    runner = CliRunner()
    res = runner.invoke(realestate_cli, ["lh", "search", "--region", "서울특별시", "-j"])
    assert res.exit_code == 0, res.output
    assert captured[0] == ("lh-notice-search", "/v1/lh-notice/search")
