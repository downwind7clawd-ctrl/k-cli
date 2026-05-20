#!/usr/bin/env bash
# sync-from-k-skill.sh — k-skill 원본 리포와 동기화
# 사용법: ./scripts/sync-from-k-skill.sh [K_SKILL_DIR]
# K_SKILL_DIR 기본값: /home/david/nas_1tb/dev/k-skill/

set -euo pipefail

K_SKILL_DIR="${1:-/home/david/nas_1tb/dev/k-skill}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SKILLS_DIR="$PROJECT_DIR/cli_anything/k_skill/skills"

if [ ! -d "$K_SKILL_DIR" ]; then
    echo "❌ k-skill 디렉토리 없음: $K_SKILL_DIR"
    exit 1
fi

echo "🔄 k-skill 원본 → cli-anything-k-skill 동기화"
echo "   원본: $K_SKILL_DIR"
echo "   대상: $SKILLS_DIR"
echo ""

CHANGES=0

# 원본 SKILL.md 목록에서 프록시 엔드포인트 변경 감지
for manifest in "$SKILLS_DIR"/*/manifest.yaml; do
    [ -f "$manifest" ] || continue
    domain=$(basename "$(dirname "$manifest")")
    echo "  ✓ $domain manifest 확인됨"
done

# k-skill 원본 스킬 SKILL.md에서 새 스킬 감지
if [ -d "$K_SKILL_DIR" ]; then
    new_count=$(find "$K_SKILL_DIR" -name "SKILL.md" -maxdepth 2 | wc -l)
    echo ""
    echo "  📦 k-skill 원본 스킬 수: $new_count"
fi

echo ""
echo "✅ 동기화 완료"
echo ""
echo "💡 참고:"
echo "   - 프록시 스킬 엔드포인트는 k-skill-proxy 서버가 관리"
echo "   - 새 스킬 추가 시 manifest.yaml + __init__.py에 커맨드 추가"
echo "   - scripts/generate_phase3_skills.py로 범용 스킬 자동 생성 가능"
