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


def test_realestate_group_aliases():
    runner = CliRunner()
    new_name = runner.invoke(realestate_cli, ["real-estate", "search", "--help"])
    old_name = runner.invoke(realestate_cli, ["realestate", "search", "--help"])
    assert new_name.exit_code == 0, new_name.output
    assert old_name.exit_code == 0, old_name.output


def test_lh_group_aliases():
    runner = CliRunner()
    new_name = runner.invoke(realestate_cli, ["lh-notice", "search", "--help"])
    old_name = runner.invoke(realestate_cli, ["lh", "search", "--help"])
    assert new_name.exit_code == 0, new_name.output
    assert old_name.exit_code == 0, old_name.output
