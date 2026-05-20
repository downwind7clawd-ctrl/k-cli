"""생성 스크립트 - Phase 2 프록시 스킬 도메인 파일 생성

사용법: python scripts/generate_proxy_skills.py
"""
import subprocess, sys
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent / "cli_anything" / "k_skill" / "skills"

def run():
    """manifest.yaml + __init__.py 생성"""
    for d in (SKILLS_DIR).iterdir():
        if d.is_dir() and (d / "manifest.yaml").exists():
            print(f"  {d.name}/ already exists, skipping")
    print("Run domain creation manually or use write_file for each domain.")

if __name__ == "__main__":
    run()
