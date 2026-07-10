from unittest.mock import patch
from click.testing import CliRunner
from cli_anything.k_skill.cli import main

class TestLifeExt:
    @patch("cli_anything.k_skill.skills.life.run_npm")
    def test_kakao_bar(self, mock_run):
        mock_run.return_value = {"status": "success", "data": {}}
        r = CliRunner()
        res = r.invoke(main, ["life", "kakao-bar", "--query", "강남", "-j"])
        assert res.exit_code == 0 and mock_run.call_args[0][0] == "kakao-bar-nearby"

    @patch("cli_anything.k_skill.skills.life.run_npm")
    def test_lovebug(self, mock_run):
        mock_run.return_value = {"status": "success", "data": {}}
        r = CliRunner()
        res = r.invoke(main, ["life", "lovebug-report", "search", "--query", "중랑", "-j"])
        assert res.exit_code == 0 and mock_run.call_args[0][0] == "lovebug-report"

    @patch("cli_anything.k_skill.skills.life.run_npm")
    def test_yebigun(self, mock_run):
        mock_run.return_value = {"status": "success", "data": {}}
        r = CliRunner()
        res = r.invoke(main, ["life", "yebigun-training", "training-info", "-j"])
        assert res.exit_code == 0 and mock_run.call_args[0][0] == "yebigun-training"
