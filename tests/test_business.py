import asyncio
from unittest.mock import patch
from click.testing import CliRunner
from cli_anything.k_skill.cli import main

class TestBusiness:
    @patch("cli_anything.k_skill.skills.business.run_npm")
    def test_court_calls_npm(self, mock_run):
        mock_run.return_value = {"status": "success", "data": {}}
        r = CliRunner()
        res = r.invoke(main, ["business", "court-payment", "--case-no", "2024가단12345", "-j"])
        assert res.exit_code == 0 and mock_run.call_args[0][0] == "court-payment-order-assitat"

    @patch("cli_anything.k_skill.skills.business.run_npm")
    def test_d2b_calls_npm(self, mock_run):
        mock_run.return_value = {"status": "success", "data": {}}
        r = CliRunner()
        res = r.invoke(main, ["business", "d2b-notice", "--keyword", "AI", "-j"])
        assert res.exit_code == 0 and mock_run.call_args[0][0] == "d2b-notice-search"

    @patch("cli_anything.k_skill.skills.business.run_npm")
    def test_s2b_calls_npm(self, mock_run):
        mock_run.return_value = {"status": "success", "data": {}}
        r = CliRunner()
        res = r.invoke(main, ["business", "s2b-notice", "--keyword", "AI", "-j"])
        assert res.exit_code == 0 and mock_run.call_args[0][0] == "s2b-notice-search"

    @patch("cli_anything.k_skill.skills.business.safe_proxy_get")
    def test_g2b_calls_proxy(self, mock_get):
        mock_get.return_value = {"status": "success", "data": {}}
        r = CliRunner()
        res = r.invoke(main, ["business", "g2b-order-plan", "--instNm", "조달청", "-j"])
        assert res.exit_code == 0
        assert mock_get.call_args[0][1] == "/v1/g2b/order-plans"

    @patch("cli_anything.k_skill.skills.business.httpx.Client")
    def test_localdata_direct_http(self, mock_client):
        import cli_anything.k_skill.skills.business as b
        resp = type("R", (), {"raise_for_status": lambda self: None, "json": lambda self: {"status":"success","data":{}}})()
        mock_client.return_value.__enter__.return_value.get.return_value = resp
        r = CliRunner()
        res = r.invoke(main, ["business", "localdata-status", "--biz-name", "커피월드", "-j"])
        assert res.exit_code == 0
