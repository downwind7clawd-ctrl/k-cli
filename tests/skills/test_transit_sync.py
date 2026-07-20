"""Sync verification: seoul-subway rename to seoul-subway-arrival."""
from unittest.mock import patch

from click.testing import CliRunner

from cli_anything.k_skill.skills.transit import cli as transit_cli


def test_subway_uses_renamed_skill_and_unchanged_path():
    captured = {}

    def fake_safe_proxy_get(skill, path, params=None, timeout=15):
        captured["name"] = skill
        captured["path"] = path
        return {"skill": skill, "status": "ok", "data": {}}

    with patch(
        "cli_anything.k_skill.skills.transit.safe_proxy_get",
        side_effect=fake_safe_proxy_get,
    ):
        runner = CliRunner()
        result = runner.invoke(transit_cli, ["subway", "강남", "-j"])

    assert result.exit_code == 0
    assert captured["name"] == "seoul-subway-arrival"
    assert captured["path"] == "/v1/seoul-subway/arrival"
