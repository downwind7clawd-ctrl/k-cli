import httpx
from click.testing import CliRunner
from cli_anything.k_skill.skills.recruiting import cli as recruiting_cli


def test_jobkorea_talent_renamed(monkeypatch):
    captured = {}
    def fake_err(code, kind, msg, fix=None):
        captured["code"] = code
        return {"status": "error", "error": {"code": code, "kind": kind}}
    monkeypatch.setattr("cli_anything.k_skill.skills.recruiting.error_response", fake_err)

    class FakeResp:
        status_code = 500
    def fake_get(*a, **k):
        raise httpx.HTTPStatusError("x", request=None, response=FakeResp())
    monkeypatch.setattr(httpx.Client, "get", lambda self, *a, **k: fake_get())

    res = CliRunner().invoke(recruiting_cli, ["jobkorea-talent", "--keyword", "x", "-j"])
    assert res.exit_code == 0, res.output
    assert captured.get("code") == "jobkorea-talent-search"
