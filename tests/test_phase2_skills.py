"""Phase 2: 순수 프록시 스킬 래핑 테스트 (18개 스킬, 8개 도메인)."""

from pathlib import Path
from unittest.mock import patch

import pytest

from cli_anything.k_skill.loader import SKILLS_DIR, load_manifest, discover_domains, list_all_skills


DOMAINS = [
    ("weather", 3),
    ("transit", 1),
    ("life", 7),
    ("finance", 3),
    ("realestate", 2),
    ("shopping", 1),
    ("search", 1),
]


# ── Manifest 유효성 테스트 ────────────────────────────────

class TestManifests:
    """모든 도메인 manifest.yaml이 유효한지 검증."""

    @pytest.mark.parametrize("domain,expected_skills", DOMAINS)
    def test_manifest_loads(self, domain, expected_skills):
        manifest = load_manifest(Path(SKILLS_DIR) / domain)
        assert manifest.domain == domain
        assert len(manifest.skills) == expected_skills

    @pytest.mark.parametrize("domain,expected_skills", DOMAINS)
    def test_all_skills_have_required_fields(self, domain, expected_skills):
        manifest = load_manifest(Path(SKILLS_DIR) / domain)
        for skill_id, skill in manifest.skills.items():
            # skill은 dict 또는 SkillInfo 객체
            if isinstance(skill, dict):
                name = skill.get("name")
                display_name = skill.get("display_name")
                desc = skill.get("description")
            else:
                name = getattr(skill, "name", None)
                display_name = getattr(skill, "display_name", None)
                desc = getattr(skill, "description", None)
            assert name, f"{domain}/{skill_id}: name 누락"
            assert display_name, f"{domain}/{skill_id}: display_name 누락"
            assert desc, f"{domain}/{skill_id}: description 누락"


# ── safe_proxy_get / safe_proxy_post 테스트 ─────────────

class TestSafeProxy:
    @patch("cli_anything.k_skill.proxy.proxy_get")
    def test_get_success(self, mock_get):
        mock_get.return_value = ({"result": "ok"}, 100)
        from cli_anything.k_skill.proxy import safe_proxy_get
        resp = safe_proxy_get("test-skill", "/v1/test", {"q": "hello"})
        assert resp["status"] == "success"
        assert resp["skill"] == "test-skill"
        assert resp["data"]["result"] == "ok"

    @patch("cli_anything.k_skill.proxy.proxy_get")
    def test_get_empty_params(self, mock_get):
        mock_get.return_value = ({}, 50)
        from cli_anything.k_skill.proxy import safe_proxy_get
        resp = safe_proxy_get("test-skill", "/v1/test")
        assert resp["status"] == "success"

    @patch("cli_anything.k_skill.proxy.proxy_post")
    def test_post_success(self, mock_post):
        mock_post.return_value = ({"items": [1, 2, 3]}, 200)
        from cli_anything.k_skill.proxy import safe_proxy_post
        resp = safe_proxy_post("nts", "/v1/nts-business/status", {"b_no": ["123"]})
        assert resp["status"] == "success"
        assert resp["data"]["items"] == [1, 2, 3]

    @patch("cli_anything.k_skill.proxy.proxy_post")
    def test_post_none_body(self, mock_post):
        mock_post.return_value = ({"ok": True}, 10)
        from cli_anything.k_skill.proxy import safe_proxy_post
        resp = safe_proxy_post("test", "/v1/test")
        assert resp["status"] == "success"


# ── 도메인별 임포트 테스트 ───────────────────────────────

class TestDomainImports:
    """모든 도메인 모듈이 임포트 가능한지 검증."""

    def test_weather_import(self):
        from cli_anything.k_skill.skills.weather import cli
        assert cli is not None

    def test_transit_import(self):
        from cli_anything.k_skill.skills.transit import cli
        assert cli is not None

    def test_life_import(self):
        from cli_anything.k_skill.skills.life import cli
        assert cli is not None

    def test_finance_import(self):
        from cli_anything.k_skill.skills.finance import cli
        assert cli is not None

    def test_realestate_import(self):
        from cli_anything.k_skill.skills.realestate import cli
        assert cli is not None

    def test_shopping_import(self):
        from cli_anything.k_skill.skills.shopping import cli
        assert cli is not None

    def test_search_import(self):
        from cli_anything.k_skill.skills.search import cli
        assert cli is not None


# ── CLI 명령 등록 테스트 ─────────────────────────────────

class TestCLICommands:
    """메인 CLI에 모든 도메인이 등록되어 있는지 검증.

    Click의 list_commands(ctx)는 list[str]을 반환함.
    """

    def _get_subcommand_names(self, group):
        return group.list_commands(None)

    def test_all_domains_registered(self):
        import cli_anything.k_skill.cli as cli_mod
        names = self._get_subcommand_names(cli_mod.main)
        for domain, _ in DOMAINS:
            assert domain in names, f"도메인 '{domain}'이 CLI에 등록되지 않음"

    def test_weather_commands(self):
        import cli_anything.k_skill.cli as cli_mod
        weather_cli = cli_mod.main.get_command(None, "weather")
        names = self._get_subcommand_names(weather_cli)
        assert "weather" in names
        assert "dust" in names
        assert "han-river" in names

    def test_transit_commands(self):
        import cli_anything.k_skill.cli as cli_mod
        transit_cli = cli_mod.main.get_command(None, "transit")
        names = self._get_subcommand_names(transit_cli)
        assert "subway" in names

    def test_life_commands(self):
        import cli_anything.k_skill.cli as cli_mod
        life_cli = cli_mod.main.get_command(None, "life")
        names = self._get_subcommand_names(life_cli)
        for cmd in ["gas", "waste", "parking", "library", "lunch", "drug", "food"]:
            assert cmd in names, f"life/{cmd} 누락"

    def test_finance_commands(self):
        import cli_anything.k_skill.cli as cli_mod
        finance_cli = cli_mod.main.get_command(None, "finance")
        names = self._get_subcommand_names(finance_cli)
        assert "nts" in names
        assert "stock" in names
        assert "kstartup" in names

    def test_finance_nts_subcommands(self):
        import cli_anything.k_skill.cli as cli_mod
        finance_cli = cli_mod.main.get_command(None, "finance")
        nts_cli = finance_cli.get_command(None, "nts")
        names = self._get_subcommand_names(nts_cli)
        assert "status" in names
        assert "validate" in names

    def test_realestate_commands(self):
        import cli_anything.k_skill.cli as cli_mod
        re_cli = cli_mod.main.get_command(None, "realestate")
        names = self._get_subcommand_names(re_cli)
        assert "realestate" in names
        assert "lh" in names

    def test_realestate_subcommands(self):
        import cli_anything.k_skill.cli as cli_mod
        re_cli = cli_mod.main.get_command(None, "realestate")
        re_group = re_cli.get_command(None, "realestate")
        names = self._get_subcommand_names(re_group)
        assert "code" in names
        assert "search" in names

        lh_group = re_cli.get_command(None, "lh")
        names = self._get_subcommand_names(lh_group)
        assert "search" in names
        assert "detail" in names

    def test_shopping_commands(self):
        import cli_anything.k_skill.cli as cli_mod
        shop_cli = cli_mod.main.get_command(None, "shopping")
        names = self._get_subcommand_names(shop_cli)
        assert "naver-shop" in names

    def test_search_commands(self):
        import cli_anything.k_skill.cli as cli_mod
        search_cli = cli_mod.main.get_command(None, "search")
        names = self._get_subcommand_names(search_cli)
        assert "naver-news" in names


# ── discover_domains 통합 테스트 ────────────────────────

class TestDiscoverDomainsIntegration:
    """discover_domains가 Phase 2 도메인을 모두 찾는지 검증.

    discover_domains()는 dict[str, SkillManifest] 반환.
    """

    def test_all_phase2_domains_found(self):
        domains = discover_domains()
        assert isinstance(domains, dict)
        for domain, _ in DOMAINS:
            assert domain in domains, f"discover_domains가 '{domain}'을 찾지 못함"

    def test_all_phase2_skills_found(self):
        all_skills = list_all_skills()
        skill_ids = {s["skill_id"] for s in all_skills}
        expected = [
            "weather", "dust", "han_river",
            "subway",
            "gas", "waste", "parking", "library", "lunch", "drug", "food",
            "nts", "stock", "kstartup",
            "realestate", "lh",
            "naver_shop",
            "naver_news",
        ]
        for sid in expected:
            assert sid in skill_ids, f"list_all_skills에 '{sid}' 누락"

    def test_total_skill_count(self):
        all_skills = list_all_skills()
        assert len(all_skills) >= 18
