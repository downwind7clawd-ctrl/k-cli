from unittest.mock import patch
from click.testing import CliRunner
from cli_anything.k_skill.cli import main

class TestRecruiting:
    @patch("cli_anything.k_skill.skills.recruiting.httpx.Client")
    def test_job_posting_inline(self, mock_client):
        resp = type("R", (), {"raise_for_status": lambda self: None,
                      "json": lambda self: {"status": "success", "data": {}}})()
        mock_client.return_value.__enter__.return_value.get.return_value = resp
        r = CliRunner()
        res = r.invoke(main, ["recruiting", "job-posting-match",
                               "--resume-text", "마케터 5년", "--location", "서울", "-j"])
        assert res.exit_code == 0

    @patch("cli_anything.k_skill.skills.recruiting.httpx.Client")
    def test_jobkorea_inline(self, mock_client):
        resp = type("R", (), {"raise_for_status": lambda self: None,
                      "json": lambda self: {"status": "success", "data": {}}})()
        mock_client.return_value.__enter__.return_value.get.return_value = resp
        r = CliRunner()
        res = r.invoke(main, ["recruiting", "jobkorea-talent-search",
                               "--keyword", "마케터", "--work-area", "서울", "-j"])
        assert res.exit_code == 0

    @patch("cli_anything.k_skill.skills.recruiting.run_npm")
    def test_saramin_npm(self, mock_run):
        mock_run.return_value = {"status": "success", "data": {}}
        r = CliRunner()
        res = r.invoke(main, ["recruiting", "saramin-talent",
                               "--keyword", "백엔드", "--location", "서울", "-j"])
        assert res.exit_code == 0 and mock_run.call_args[0][0] == "saramin-talent-search"
