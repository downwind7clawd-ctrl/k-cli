"""Sync test: shopping naver-shopping command name + alias."""

import pytest
from click.testing import CliRunner

from cli_anything.k_skill.skills import shopping


def test_shopping_naver_shopping_primary():
    runner = CliRunner()
    res = runner.invoke(shopping.cli, ["naver-shopping", "--help"])
    assert res.exit_code == 0, res.output


def test_shopping_naver_shop_alias():
    runner = CliRunner()
    res = runner.invoke(shopping.cli, ["naver-shop", "--help"])
    assert res.exit_code == 0, res.output
