import pytest
from click.testing import CliRunner
from cli_anything.k_skill.skills.weather import cli as weather_cli


def test_fine_dust_command_registered(monkeypatch):
    captured = {}
    def fake_get(name, path, params=None, timeout=None):
        captured["name"] = name
        captured["path"] = path
        return {"status": "success", "data": {}}
    monkeypatch.setattr("cli_anything.k_skill.skills.weather.safe_proxy_get", fake_get)
    runner = CliRunner()
    res = runner.invoke(weather_cli, ["dust", "서울 강남구", "-j"])
    assert res.exit_code == 0, res.output
    assert captured["name"] == "fine-dust-location"
    assert captured["path"] == "/v1/fine-dust/report"


def test_han_river_command_registered(monkeypatch):
    captured = {}
    def fake_get(name, path, params=None, timeout=None):
        captured["name"] = name
        captured["path"] = path
        return {"status": "success", "data": {}}
    monkeypatch.setattr("cli_anything.k_skill.skills.weather.safe_proxy_get", fake_get)
    runner = CliRunner()
    res = runner.invoke(weather_cli, ["han-river", "한강대교", "-j"])
    assert res.exit_code == 0, res.output
    assert captured["name"] == "han-river-water-level"
    assert captured["path"] == "/v1/han-river/water-level"
