import asyncio
from unittest.mock import patch
from click.testing import CliRunner
from cli_anything.k_skill.cli import main


class TestFortune:
    @patch("cli_anything.k_skill.skills.fortune.run_npm")
    def test_saju_calls_npm(self, mock_run):
        mock_run.return_value = {"status": "success", "data": {}}
        r = CliRunner()
        res = r.invoke(main, ["fortune", "saju-fortune", "1990-05-15 14:30", "--sex", "M", "-j"])
        assert res.exit_code == 0
        mock_run.assert_called_once()
        assert mock_run.call_args[0][0] == "saju-fortune"

    @patch("cli_anything.k_skill.skills.fortune.run_npm")
    def test_naming_calls_npm(self, mock_run):
        mock_run.return_value = {"status": "success", "data": {}}
        r = CliRunner()
        res = r.invoke(main, ["fortune", "naming-house", "김철수", "--birth", "1990-05-15", "-j"])
        assert res.exit_code == 0
        assert mock_run.call_args[0][0] == "naming-house"
