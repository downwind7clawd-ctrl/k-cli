"""Sync test: naver-news / naver-shopping rename (name + path)."""

import pytest
from click.testing import CliRunner

from cli_anything.k_skill.skills import search
from cli_anything.k_skill.skills import shopping


class _Capture:
    def __init__(self):
        self.calls = []

    def __call__(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return {"skill": args[0], "status": "success", "data": {}}


def test_search_naver_news_rename():
    cap = _Capture()
    runner = CliRunner()
    with (
        pytest.MonkeyPatch().context() as mp,
    ):
        mp.setattr(search, "safe_proxy_get", cap)
        result = runner.invoke(search.cli, ["naver-news", "AI 규제", "-j"])
    assert result.exit_code == 0, result.output
    assert cap.calls, "safe_proxy_get was not called"
    args, _ = cap.calls[0]
    name, path = args[0], args[1]
    assert name == "naver-news-search"
    assert path == "/v1/naver-news/search"


def test_shopping_naver_shop_rename():
    cap = _Capture()
    runner = CliRunner()
    with (
        pytest.MonkeyPatch().context() as mp,
    ):
        mp.setattr(shopping, "safe_proxy_get", cap)
        result = runner.invoke(shopping.cli, ["naver-shop", "에어팟", "-j"])
    assert result.exit_code == 0, result.output
    assert cap.calls, "safe_proxy_get was not called"
    args, _ = cap.calls[0]
    name, path = args[0], args[1]
    assert name == "naver-shopping-search"
    assert path == "/v1/naver-shopping/search"
