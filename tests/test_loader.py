"""Tests for loader.py — manifest loading and skill discovery."""

import pytest
from pathlib import Path

from cli_anything.k_skill.loader import (
    SkillManifest,
    ManifestLoadError,
    load_manifest,
    discover_domains,
    list_all_skills,
)


class TestSkillManifest:
    def test_init(self):
        data = {
            "domain": "weather",
            "description": "날씨/환경",
            "skills": {
                "fine_dust": {
                    "name": "fine-dust",
                    "display_name": "미세먼지",
                    "requires": {"proxy": True},
                },
            },
        }
        m = SkillManifest("weather", data)
        assert m.domain == "weather"
        assert m.description == "날씨/환경"
        assert "fine_dust" in m.skill_names()
        skill = m.get_skill("fine_dust")
        assert skill is not None and skill["name"] == "fine-dust"
        assert m.get_skill("nonexistent") is None

    def test_to_dict(self):
        data = {
            "domain": "test",
            "description": "desc",
            "skills": {
                "s1": {"name": "s1", "display_name": "S1"},
            },
        }
        m = SkillManifest("test", data)
        d = m.to_dict()
        assert d["domain"] == "test"
        assert len(d["skills"]) == 1


class TestLoadManifest:
    def test_missing_file(self):
        with pytest.raises(ManifestLoadError, match="manifest.yaml not found"):
            load_manifest(Path("/tmp/nonexistent_xyz"))

    def test_missing_domain_key(self, tmp_path):
        mf = tmp_path / "manifest.yaml"
        mf.write_text("description: no domain key\n")
        with pytest.raises(ManifestLoadError, match="missing 'domain'"):
            load_manifest(tmp_path)

    def test_valid_manifest(self, tmp_path):
        mf = tmp_path / "manifest.yaml"
        mf.write_text(
            "domain: weather\n"
            "description: 날씨\n"
            "skills:\n"
            "  fine_dust:\n"
            "    name: fine-dust\n"
            "    display_name: 미세먼지\n"
            "    requires:\n"
            "      proxy: true\n"
        )
        m = load_manifest(tmp_path)
        assert m.domain == "weather"
        assert "fine_dust" in m.skills


class TestDiscoverDomains:
    def test_empty_dir(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "cli_anything.k_skill.loader.SKILLS_DIR", tmp_path
        )
        assert discover_domains() == {}

    def test_with_valid_manifest(self, tmp_path, monkeypatch):
        domain_dir = tmp_path / "weather"
        domain_dir.mkdir()
        (domain_dir / "manifest.yaml").write_text(
            "domain: weather\nskills:\n  fd:\n    name: fine-dust\n"
        )
        monkeypatch.setattr(
            "cli_anything.k_skill.loader.SKILLS_DIR", tmp_path
        )
        domains = discover_domains()
        assert "weather" in domains


class TestListAllSkills:
    def test_empty(self, monkeypatch):
        monkeypatch.setattr(
            "cli_anything.k_skill.loader.SKILLS_DIR", Path("/nonexistent_xyz")
        )
        assert list_all_skills() == []

    def test_with_skills(self, tmp_path, monkeypatch):
        d = tmp_path / "test_domain"
        d.mkdir()
        (d / "manifest.yaml").write_text(
            "domain: test_domain\n"
            "description: test\n"
            "skills:\n"
            "  s1:\n"
            "    name: skill-1\n"
            "    display_name: Skill One\n"
            "    category: utility\n"
            "    requires:\n"
            "      proxy: true\n"
        )
        monkeypatch.setattr(
            "cli_anything.k_skill.loader.SKILLS_DIR", tmp_path
        )
        skills = list_all_skills()
        assert len(skills) == 1
        assert skills[0]["name"] == "skill-1"
        assert skills[0]["category"] == "utility"
