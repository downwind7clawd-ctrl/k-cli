"""Tests for dependency.py — 3-layer dependency checker."""

import os
from unittest.mock import patch, MagicMock

import pytest

from cli_anything.k_skill.dependency import (
    SkillDependency,
    DependencyReport,
    _check_system_tools,
    _check_python_packages,
    _check_env_keys,
    check_dependency,
    build_fix_instructions,
)


class TestCheckSystemTools:
    def test_existing_tool(self):
        assert "python3" not in _check_system_tools(["python3"])

    def test_missing_tool(self):
        result = _check_system_tools(["nonexistent_tool_xyz_123"])
        assert "nonexistent_tool_xyz_123" in result

    def test_mixed(self):
        result = _check_system_tools(["python3", "fake_tool", "curl"])
        assert "fake_tool" in result
        assert "python3" not in result


class TestCheckPythonPackages:
    def test_existing_package(self):
        assert "json" not in _check_python_packages(["json"])

    def test_missing_package(self):
        result = _check_python_packages(["nonexistent_pkg_xyz_123"])
        assert "nonexistent_pkg_xyz_123" in result


class TestCheckEnvKeys:
    def test_set_key(self):
        os.environ["TEST_KCLI_KEY"] = "value"
        try:
            assert "TEST_KCLI_KEY" not in _check_env_keys(["TEST_KCLI_KEY"])
        finally:
            os.environ.pop("TEST_KCLI_KEY", None)

    def test_unset_key(self):
        key = "NONEXISTENT_KCLI_KEY_XYZ"
        os.environ.pop(key, None)
        assert key in _check_env_keys([key])


class TestCheckDependency:
    @pytest.mark.asyncio
    async def test_proxy_only_ready(self):
        dep = SkillDependency(name="test", proxy=True)
        with patch("cli_anything.k_skill.proxy.health_check", return_value=True):
            report = await check_dependency(dep)
        assert report.ready is True
        assert report.proxy_reachable is True

    @pytest.mark.asyncio
    async def test_proxy_unreachable(self):
        dep = SkillDependency(name="test", proxy=True)
        with patch("cli_anything.k_skill.proxy.health_check", return_value=False):
            report = await check_dependency(dep)
        assert report.ready is False
        assert report.proxy_reachable is False

    @pytest.mark.asyncio
    async def test_system_missing(self):
        dep = SkillDependency(name="test", system=["nonexistent_xyz"])
        report = await check_dependency(dep)
        assert report.ready is False
        assert "nonexistent_xyz" in report.missing_system

    @pytest.mark.asyncio
    async def test_env_keys_missing(self):
        dep = SkillDependency(name="test", env_keys=["MISSING_KEY_XYZ"])
        report = await check_dependency(dep)
        assert report.ready is False
        assert "MISSING_KEY_XYZ" in report.missing_env

    @pytest.mark.asyncio
    async def test_no_deps_always_ready(self):
        dep = SkillDependency(name="test")
        report = await check_dependency(dep)
        assert report.ready is True

    def test_report_to_dict(self):
        report = DependencyReport(
            skill_name="test", ready=False,
            missing_system=["curl"],
        )
        d = report.to_dict()
        assert d["skill"] == "test"
        assert d["ready"] is False
        assert "curl" in d["missing"]["system"]


class TestBuildFixInstructions:
    def test_missing_system(self):
        report = DependencyReport(
            skill_name="test", ready=False,
            missing_system=["node"],
        )
        fix = build_fix_instructions(report)
        assert "node" in fix

    def test_missing_python(self):
        report = DependencyReport(
            skill_name="test", ready=False,
            missing_python=["SRTrain"],
        )
        fix = build_fix_instructions(report)
        assert "pip install" in fix

    def test_ready(self):
        report = DependencyReport(skill_name="test", ready=True)
        fix = build_fix_instructions(report)
        assert "준비 완료" in fix
