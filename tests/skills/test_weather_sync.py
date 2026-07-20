import pytest
from click.testing import CliRunner
from cli_anything.k_skill.skills.weather import cli as weather_cli


def _fake_get_factory(captured):
    def fake_get(name, path, params=None, timeout=None):
        captured["name"] = name
        captured["path"] = path
        return {"status": "success", "data": {}}
    return fake_get


def test_fine_dust_primary_name(monkeypatch):
    captured = {}
    monkeypatch.setattr(
        "cli_anything.k_skill.skills.weather.safe_proxy_get",
        _fake_get_factory(captured),
    )
    runner = CliRunner()
    res = runner.invoke(weather_cli, ["fine-dust", "서울 강남구", "-j"])
    assert res.exit_code == 0, res.output
    assert captured["name"] == "fine-dust-location"
    assert captured["path"] == "/v1/fine-dust/report"


def test_fine_dust_alias(monkeypatch):
    captured = {}
    monkeypatch.setattr(
        "cli_anything.k_skill.skills.weather.safe_proxy_get",
        _fake_get_factory(captured),
    )
    runner = CliRunner()
    res = runner.invoke(weather_cli, ["dust", "서울 강남구", "-j"])
    assert res.exit_code == 0, res.output
    assert captured["name"] == "fine-dust-location"
    assert captured["path"] == "/v1/fine-dust/report"


def test_han_river_primary_name(monkeypatch):
    captured = {}
    monkeypatch.setattr(
        "cli_anything.k_skill.skills.weather.safe_proxy_get",
        _fake_get_factory(captured),
    )
    runner = CliRunner()
    res = runner.invoke(weather_cli, ["han-river", "한강대교", "-j"])
    assert res.exit_code == 0, res.output
    assert captured["name"] == "han-river-water-level"
    assert captured["path"] == "/v1/han-river/water-level"


def test_han_river_alias(monkeypatch):
    captured = {}
    monkeypatch.setattr(
        "cli_anything.k_skill.skills.weather.safe_proxy_get",
        _fake_get_factory(captured),
    )
    runner = CliRunner()
    res = runner.invoke(weather_cli, ["han_river", "한강대교", "-j"])
    assert res.exit_code == 0, res.output
    assert captured["name"] == "han-river-water-level"
    assert captured["path"] == "/v1/han-river/water-level"


def test_all_command_help():
    runner = CliRunner()
    for name in ("fine-dust", "dust", "han-river", "han_river"):
        res = runner.invoke(weather_cli, [name, "--help"])
        assert res.exit_code == 0, f"{name}: {res.output}"
