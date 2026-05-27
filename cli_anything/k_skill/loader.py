"""
Dynamic skill loader — discovers and registers CLI commands from manifest.yaml.

Core extensibility mechanism:
  1. Scan skills/ subdirectories for manifest.yaml files
  2. For each manifest, import the domain module and register Click commands
  3. New skills = new manifest entry + Python file, no core code changes

Manifest format (skills/<domain>/manifest.yaml):
  domain: weather
  description: 날씨/환경 조회 스킬
  skills:
    fine_dust:
      name: fine-dust
      display_name: 미세먼지 조회
      description: 지역 기준 PM10/PM2.5 미세먼지 조회
      commands:
        - name: fine-dust
          help: "지역 미세먼지/초미세먼지 조회"
          args:
            - name: region
              help: "지역명 (예: 서울 강남구)"
              required: true
      requires:
        proxy: true
        category: utility
"""

import importlib
import logging
import re
from pathlib import Path
from typing import Any, Optional

import yaml

logger = logging.getLogger("k_cli.loader")

SKILLS_DIR = Path(__file__).parent / "skills"

# Security: only allow safe Python module names
_SAFE_MODULE_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*$")


class SkillManifest:
    """Parsed manifest for a skill domain."""

    def __init__(self, domain: str, data: dict):
        self.domain = domain
        self.description: str = data.get("description", "")
        self.skills: dict[str, dict] = data.get("skills", {})

    def skill_names(self) -> list[str]:
        return list(self.skills.keys())

    def get_skill(self, skill_id: str) -> Optional[dict]:
        return self.skills.get(skill_id)

    def to_dict(self) -> dict:
        return {
            "domain": self.domain,
            "description": self.description,
            "skills": {
                sid: {
                    "name": s.get("name", sid),
                    "display_name": s.get("display_name", ""),
                }
                for sid, s in self.skills.items()
            },
        }


class ManifestLoadError(Exception):
    """Raised when a manifest file cannot be parsed."""


def load_manifest(domain_path: Path) -> SkillManifest:
    """Load and parse a manifest.yaml from a domain directory.

    Args:
        domain_path: Path to the domain directory containing manifest.yaml.

    Returns:
        Parsed SkillManifest.

    Raises:
        ManifestLoadError: If the file is missing or malformed.
    """
    manifest_file = domain_path / "manifest.yaml"
    if not manifest_file.exists():
        raise ManifestLoadError(f"manifest.yaml not found in {domain_path}")

    try:
        with open(manifest_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ManifestLoadError(f"YAML parse error in {manifest_file}: {e}")

    if not isinstance(data, dict) or "domain" not in data:
        raise ManifestLoadError(
            f"Invalid manifest: missing 'domain' key in {manifest_file}"
        )

    return SkillManifest(data["domain"], data)


def discover_domains() -> dict[str, SkillManifest]:
    """Scan skills/ directory and load all manifests.

    Returns:
        Dict mapping domain name -> SkillManifest.
    """
    domains: dict[str, SkillManifest] = {}
    if not SKILLS_DIR.exists():
        return domains

    for domain_dir in sorted(SKILLS_DIR.iterdir()):
        if not domain_dir.is_dir() or domain_dir.name.startswith("_"):
            continue
        if not _SAFE_MODULE_PATTERN.match(domain_dir.name):
            continue
        if domain_dir.is_symlink():
            continue
        try:
            manifest = load_manifest(domain_dir)
            domains[manifest.domain] = manifest
        except ManifestLoadError as e:
            logger.warning("스킬 디렉토리 '%s'의 manifest.yaml 로딩 실패: %s", domain_dir.name, e)
            continue

    return domains


def discover_cli_groups() -> dict[str, Any]:
    """Import skill domain modules and extract Click CLI groups.

    Each domain module should expose a `cli` attribute that is a Click group.

    Returns:
        Dict mapping domain name -> Click group object.
    """
    groups: dict[str, Any] = {}
    if not SKILLS_DIR.exists():
        return groups

    for domain_dir in sorted(SKILLS_DIR.iterdir()):
        if not domain_dir.is_dir() or domain_dir.name.startswith("_"):
            continue
        # Security: validate domain name is a safe Python identifier
        if not _SAFE_MODULE_PATTERN.match(domain_dir.name):
            continue
        # Security: skip symbolic links to prevent directory traversal
        if domain_dir.is_symlink():
            continue
        init_file = domain_dir / "__init__.py"
        if not init_file.exists():
            continue

        module_name = f"cli_anything.k_skill.skills.{domain_dir.name}"
        try:
            mod = importlib.import_module(module_name)
            if hasattr(mod, "cli"):
                groups[domain_dir.name] = mod.cli
        except ImportError:
            continue

    return groups


def list_all_skills() -> list[dict]:
    """Return a flat list of all registered skills across all domains.

    Useful for `k-skill list --all` command.

    Returns:
        List of skill info dicts.
    """
    domains = discover_domains()
    all_skills: list[dict] = []
    for domain, manifest in domains.items():
        for skill_id, skill_data in manifest.skills.items():
            all_skills.append({
                "domain": domain,
                "domain_description": manifest.description,
                "skill_id": skill_id,
                "name": skill_data.get("name", skill_id),
                "display_name": skill_data.get(
                    "display_name", skill_data.get("name", skill_id)
                ),
                "description": skill_data.get("description", ""),
                "category": skill_data.get("category", ""),
                "requires": skill_data.get("requires", {}),
            })
    return all_skills


def get_skill_dependency(skill_domain: str, skill_id: str) -> Optional[dict]:
    """Get the dependency declaration for a specific skill.

    Returns:
        The 'requires' dict from manifest, or None if not found.
    """
    domains = discover_domains()
    manifest = domains.get(skill_domain)
    if not manifest:
        return None
    skill = manifest.get_skill(skill_id)
    if not skill:
        return None
    return skill.get("requires")
