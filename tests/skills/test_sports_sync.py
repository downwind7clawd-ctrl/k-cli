"""Sync verification: kopis-performance-search proxy commands."""
from unittest.mock import patch

from click.testing import CliRunner

from cli_anything.k_skill.skills.sports import cli as sports_cli


def test_kopis_performances_uses_proxy():
    captured = {}

    def fake_safe_proxy_get(skill, path, params=None, timeout=15):
        captured["name"] = skill
        captured["path"] = path
        return {"skill": skill, "status": "ok", "data": {}}

    with patch(
        "cli_anything.k_skill.skills.sports.safe_proxy_get",
        side_effect=fake_safe_proxy_get,
    ):
        runner = CliRunner()
        result = runner.invoke(sports_cli, ["kopis", "performances", "--keyword", "햄릿", "-j"])

    assert result.exit_code == 0
    assert captured["name"] == "kopis-performance-search"
    assert captured["path"] == "/v1/kopis/performances"


def test_kopis_facilities_uses_proxy():
    captured = {}

    def fake_safe_proxy_get(skill, path, params=None, timeout=15):
        captured["name"] = skill
        captured["path"] = path
        return {"skill": skill, "status": "ok", "data": {}}

    with patch(
        "cli_anything.k_skill.skills.sports.safe_proxy_get",
        side_effect=fake_safe_proxy_get,
    ):
        runner = CliRunner()
        result = runner.invoke(sports_cli, ["kopis", "facilities", "-j"])

    assert result.exit_code == 0
    assert captured["name"] == "kopis-performance-search"
    assert captured["path"] == "/v1/kopis/facilities"
