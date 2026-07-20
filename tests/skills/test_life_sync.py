import pytest
from unittest import mock

from click.testing import CliRunner

from cli_anything.k_skill.skills.life import cli as life_cli


def _make_capture():
    calls = []

    def fake_safe_proxy_get(name, path, params=None, timeout=None):
        calls.append((name, path, params))
        return {"status": "ok", "data": {}}

    return calls, fake_safe_proxy_get


def test_gas_rename():
    calls, fake = _make_capture()
    with mock.patch(
        "cli_anything.k_skill.skills.life.safe_proxy_get", side_effect=fake
    ):
        result = CliRunner().invoke(
            life_cli, ["gas", "--lat", "37.5", "--lon", "127.0", "-j"]
        )
    assert result.exit_code == 0
    assert calls[0][0] == "cheap-gas-nearby"
    assert calls[0][1] == "/v1/opinet/around"


def test_waste_rename():
    calls, fake = _make_capture()
    with mock.patch(
        "cli_anything.k_skill.skills.life.safe_proxy_get", side_effect=fake
    ):
        result = CliRunner().invoke(life_cli, ["waste", "강남구", "-j"])
    assert result.exit_code == 0
    assert calls[0][0] == "household-waste-info"
    assert calls[0][1] == "/v1/household-waste/info"


def test_library_rename():
    calls, fake = _make_capture()
    with mock.patch(
        "cli_anything.k_skill.skills.life.safe_proxy_get", side_effect=fake
    ):
        result = CliRunner().invoke(life_cli, ["library", "역사", "-j"])
    assert result.exit_code == 0
    assert calls[0][0] == "library-book-search"
    assert calls[0][1] == "/v1/data4library/book-search"


def test_lunch_rename_first_call():
    calls, fake = _make_capture()
    with mock.patch(
        "cli_anything.k_skill.skills.life.safe_proxy_get", side_effect=fake
    ):
        result = CliRunner().invoke(
            life_cli, ["lunch", "--edu-office", "x", "--school", "y", "-j"]
        )
    assert result.exit_code == 0
    assert calls[0][0] == "k-schoollunch-menu"
    assert calls[0][1] == "/v1/neis/school-search"


def test_holiday_new():
    calls, fake = _make_capture()
    with mock.patch(
        "cli_anything.k_skill.skills.life.safe_proxy_get", side_effect=fake
    ):
        result = CliRunner().invoke(life_cli, ["holiday", "--year", "2026", "-j"])
    assert result.exit_code == 0
    assert calls[0][0] == "korean-holiday-calendar"
    assert calls[0][1] == "/v1/korean-holiday/calendar"


def test_nhis_checkup_new():
    calls, fake = _make_capture()
    with mock.patch(
        "cli_anything.k_skill.skills.life.safe_proxy_get", side_effect=fake
    ):
        result = CliRunner().invoke(
            life_cli, ["nhis", "checkup", "--operation", "list", "-j"]
        )
    assert result.exit_code == 0
    assert calls[0][0] == "nhis-care-checkup-search"
    assert calls[0][1] == "/v1/nhis/checkup/list"


def test_assembly_bills(monkeypatch):
    captured = {}
    def fake(name, path, params=None, timeout=None):
        captured["name"] = name; captured["path"] = path
        return {"status": "success", "data": {}}
    monkeypatch.setattr("cli_anything.k_skill.skills.life.safe_proxy_get", fake)
    from cli_anything.k_skill.skills.life import cli as life_cli
    from click.testing import CliRunner
    r = CliRunner().invoke(life_cli, ["assembly", "bills", "--query", "기후", "-j"])
    assert r.exit_code == 0, r.output
    assert captured["name"] == "assembly-bill-vote-search"
    assert captured["path"] == "/v1/assembly/bills"


def test_assembly_votes(monkeypatch):
    captured = {}
    def fake(name, path, params=None, timeout=None):
        captured["name"] = name; captured["path"] = path
        return {"status": "success", "data": {}}
    monkeypatch.setattr("cli_anything.k_skill.skills.life.safe_proxy_get", fake)
    from cli_anything.k_skill.skills.life import cli as life_cli
    from click.testing import CliRunner
    r = CliRunner().invoke(life_cli, ["assembly", "votes", "--bill-id", "ABC123", "-j"])
    assert r.exit_code == 0, r.output
    assert captured["name"] == "assembly-bill-vote-search"
    assert captured["path"] == "/v1/assembly/votes"
