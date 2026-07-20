import pytest
from click.testing import CliRunner
from cli_anything.k_skill.skills.finance import cli as finance_cli


def _capture(monkeypatch):
    captured = []
    def fake_get(name, path, params=None, timeout=None):
        captured.append((name, path))
        return {"status": "success", "data": {}}
    def fake_post(name, path, body=None, timeout=None):
        captured.append((name, path))
        return {"status": "success", "data": {}}
    monkeypatch.setattr("cli_anything.k_skill.skills.finance.safe_proxy_get", fake_get)
    monkeypatch.setattr("cli_anything.k_skill.skills.finance.safe_proxy_post", fake_post)
    return captured


def test_nts_status_rename(monkeypatch):
    captured = _capture(monkeypatch)
    runner = CliRunner()
    res = runner.invoke(finance_cli, ["nts", "status", "--b-no", "1234567890", "-j"])
    assert res.exit_code == 0, res.output
    assert captured[0] == ("nts-business-registration", "/v1/nts-business/status")


def test_nts_status_primary_name(monkeypatch):
    captured = _capture(monkeypatch)
    runner = CliRunner()
    res = runner.invoke(finance_cli, ["nts-business", "status", "--b-no", "1234567890", "-j"])
    assert res.exit_code == 0, res.output
    assert captured[0] == ("nts-business-registration", "/v1/nts-business/status")


def test_nts_validate_rename(monkeypatch):
    captured = _capture(monkeypatch)
    runner = CliRunner()
    res = runner.invoke(finance_cli, [
        "nts", "validate", "--b-no", "1234567890", "--p-nm", "홍길동",
        "--start-dt", "20200101", "-j",
    ])
    assert res.exit_code == 0, res.output
    assert captured[0] == ("nts-business-registration", "/v1/nts-business/validate")


def test_nts_validate_primary_name(monkeypatch):
    captured = _capture(monkeypatch)
    runner = CliRunner()
    res = runner.invoke(finance_cli, [
        "nts-business", "validate", "--b-no", "1234567890", "--p-nm", "홍길동",
        "--start-dt", "20200101", "-j",
    ])
    assert res.exit_code == 0, res.output
    assert captured[0] == ("nts-business-registration", "/v1/nts-business/validate")


def test_stock_rename(monkeypatch):
    captured = _capture(monkeypatch)
    runner = CliRunner()
    res = runner.invoke(finance_cli, ["stock", "삼성전자", "-j"])
    assert res.exit_code == 0, res.output
    assert captured[0] == ("korean-stock-search", "/v1/korean-stock/search")


def test_stock_primary_name(monkeypatch):
    captured = _capture(monkeypatch)
    runner = CliRunner()
    res = runner.invoke(finance_cli, ["korean-stock", "삼성전자", "-j"])
    assert res.exit_code == 0, res.output
    assert captured[0] == ("korean-stock-search", "/v1/korean-stock/search")


def test_help_names(monkeypatch):
    runner = CliRunner()
    for args in (["korean-stock", "--help"], ["stock", "--help"],
                 ["nts-business", "status", "--help"], ["nts", "status", "--help"]):
        res = runner.invoke(finance_cli, args)
        assert res.exit_code == 0, (args, res.output)
