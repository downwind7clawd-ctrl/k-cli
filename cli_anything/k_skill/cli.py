"""
k-skill — Main CLI entry point.

All AI agents discover this CLI through SKILL.md or CLI-Anything registry.
The --help/-h output is the primary interface for agents — it must be
comprehensive enough for an agent to execute commands without additional docs.

Usage:
    k-skill [OPTIONS] COMMAND [ARGS]...

Commands:
    weather     날씨/환경 (미세먼지, 한강수위, 날씨, 혼잡도)
    finance     법률/금융 (주식, DART, 법령, 코시스, 사업자등록)
    transit     교통/이동 (SRT, KTX, 지하철, 버스, 항공)
    shopping    쇼핑 (쿠팡, 올리브영, 마켓컬리, 다이소, 당근)
    realestate  부동산 (실거래가, 공시가, 감정평가, 공고문)
    sports      스포츠/엔터 (KBO, KBL, K리그, LCK, 영화관, 로또)
    market      중고거래 (당근중고, 번개장터, 중고차)
    search      검색 (네이버뉴스, 블로그, 긱뉴스, 특허, 실록)
    document    문서 (HWP, 맞춤법, 글자수)
    delivery    배송 (택배송장 추적)
    life        생활 (쓰레기배출, 응급실, 주유소, 공중화장실, 기부처)
    travel      여행 (마이리얼트립 항공권/숙소/투어)
    list        설치된 스킬 목록 조회
    setup       의존성 확인 및 설치

Options:
    --json, -j   JSON 출력 모드 (에이전트 자동처리용)
    --version     버전 정보
    --help, -h    이 도움말
"""

import asyncio
import json
import shutil
import subprocess
import sys
from typing import Optional

import click

from . import __version__
from .loader import discover_cli_groups, list_all_skills


@click.group(invoke_without_command=True)
@click.option(
    "--json", "-j", "as_json",
    is_flag=True,
    default=False,
    help="JSON 출력 모드. AI 에이전트가 구조화된 데이터를 파싱할 때 사용.",
)
@click.version_option(__version__, prog_name="k-skill")
@click.pass_context
def main(ctx: click.Context, as_json: bool):
    """k-skill — 한국인을 위한 CLI 스킬 모음 (86개 스킬)

    다양한 한국 특화 유틸리티를 단일 CLI로 제공합니다.
    프록시 기반 스킬은 추가 설치 없이 즉시 사용 가능합니다.

    ─────────────────────────────────────────────
    🤖 에이전트 빠른 실행 가이드 (Agent Quick Reference)
    ─────────────────────────────────────────────
    모든 명령에 -j (--json) 플래그를 붙이면 구조화 JSON이 반환됩니다.
    에이전트는 JSON 응답의 data 필드를 파싱하여 사용하세요.

    날씨/환경:
      k-skill weather dust "서울 강남구" -j
      k-skill weather forecast "서울" -j
      k-skill weather han-river -j

    금융/법률:
      k-skill finance stock "삼성전자" -j
      k-skill finance nts status --b-no 1234567890 -j
      k-skill finance nts validate --b-no 1234567890 --p-nm "홍길동" --start-dt 20200101 -j
      k-skill finance kstartup announcements --region "서울특별시" --open Y -j
      k-skill finance kstartup business-info --biz-yr 2024 -j
      k-skill finance dart -j
      k-skill finance kosis "통계명" -j
      k-skill finance korean-law "검색어" -j
      k-skill finance gongsijiga "지역명" -j

    교통:
      k-skill transit subway "강남" -j
      k-skill transit ktx "서울" "부산" --date 20260523 -j
      k-skill transit srt "수서" "부산" --date 20260523 -j

    쇼핑:
      k-skill shopping naver-shop "에어팟" -j
      k-skill shopping ohou-deal --query "러그" --min-discount 30 --free-delivery -j
      k-skill shopping coupang "검색어" -j
      k-skill shopping olive-young "검색어" -j

    부동산:
      k-skill realestate realestate code "서울 강남구" -j
      k-skill realestate realestate search --lawd-cd 11680 --date 202403 -j
      k-skill realestate lh search --status "공고중" --region "서울특별시" -j
      k-skill realestate sh-notice "행복주택" --category 임대 -j

    스포츠/엔터:
      k-skill sports kbo --date 2026-05-23 -j
      k-skill sports kbl --date 2026-05-23 -j
      k-skill sports kleague --date 2026-05-23 -j
      k-skill sports lck -j
      k-skill sports cinema theaters --chain cgv --keyword "강남" -j
      k-skill sports cinema movies --chain cgv --keyword "강남" --date 20260523 -j
      k-skill sports cinema timetable --chain cgv --keyword "강남" --date 20260523 -j
      k-skill sports lotto -j

    중고거래:
      k-skill market daangn-market --region "서울" -j
      k-skill market bunjang "검색어" -j

    검색:
      k-skill search naver-news "AI" -j
      k-skill search naver-blog "키워드" -j
      k-skill search patent "특허명" -j
      k-skill search sillok "검색어" -j

    생활:
      k-skill life emergency-room "광화문" --limit 5 -j
      k-skill life election "오세훈" --election 시도지사 -j
      k-skill life waste "강남구" -j
      k-skill life gas --lat 37.5665 --lon 126.9780 -j
      k-skill life drug "타이레놀" -j

    여행:
      k-skill travel myrealtrip --query "제주도" -j
      k-skill travel foresttrip --region "지역" -j

    문서:
      k-skill document spell-check "문장" -j
      k-skill document char-count "텍스트" -j

    유틸리티:
      k-skill list --all -j                # 전체 스킬 목록
      k-skill list -d weather -j           # 도메인별 스킬
      k-skill setup check -j               # 의존성 상태
      k-skill setup proxy -j               # 프록시 연결 상태

    ─────────────────────────────────────────────
    🔧 환경변수
    ─────────────────────────────────────────────
    KSKILL_PROXY_BASE_URL  프록시 URL 오버라이드
                          (기본: https://k-skill-proxy.nomadamas.org)

    ─────────────────────────────────────────────
    📦 JSON 응답 형식 (모든 스킬 공통)
    ─────────────────────────────────────────────
    성공 시: {"skill": "...", "status": "success", "data": {...}, "meta": {"source": "...", "response_time_ms": N}}
    실패 시: {"skill": "...", "status": "error", "error": {"code": "...", "message": "...", "fix": "..."}}

    ─────────────────────────────────────────────
    🔄 스킬 업데이트
    ─────────────────────────────────────────────
    스킬 추가/수정 시 기존 코드 변경 불필요:
      manifest.yaml만 추가하면 로더가 자동 발견합니다.
    """
    ctx.ensure_object(dict)
    ctx.obj["as_json"] = as_json

    # Show help when no command is given
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# ============================================================
# Built-in commands (not loaded from skills/)
# ============================================================


@main.command()
@click.option("--all", "list_all", is_flag=True, help="모든 스킬 상세 목록 조회")
@click.option("--domain", "-d", help="특정 도메인의 스킬만 조회")
@click.option("--category", "-c", help="특정 카테고리의 스킬만 조회")
@click.pass_context
def list(ctx: click.Context, list_all: bool, domain: Optional[str], category: Optional[str]):
    """설치된 스킬 목록 조회.

    스킬 도메인, 이름, 설명, 카테고리를 출력합니다.
    --json 모드에서는 구조화된 배열을 반환합니다.

    예시:
      k-skill list                     # 도메인별 요약
      k-skill list --all               # 전체 스킬 목록
      k-skill list -d weather          # 날씨 도메인 스킬
      k-skill list -c utility          # 유틸리티 카테고리
      k-skill -j list                  # JSON 출력 (전역 -j 플래그)
      k-skill -j list --all            # 전체 목록 JSON
    """
    skills = list_all_skills()

    if domain:
        skills = [s for s in skills if s["domain"] == domain]
    if category:
        skills = [s for s in skills if s.get("category") == category]

    if not list_all and not domain and not category:
        # 기본: 도메인별 요약
        domains_seen: set[str] = set()
        domain_list: list[dict] = []
        for s in skills:
            if s["domain"] not in domains_seen:
                domains_seen.add(s["domain"])
                domain_skills = [sk for sk in skills if sk["domain"] == s["domain"]]
                domain_list.append({
                    "domain": s["domain"],
                    "description": s.get("description", ""),
                    "count": len(domain_skills),
                })

        if ctx.obj["as_json"]:
            click.echo(json.dumps(domain_list, ensure_ascii=False, indent=2))
        else:
            for d in domain_list:
                click.echo(f"  {d['domain']:12s} ({d['count']}개) {d['description']}")
            click.echo(
                f"\n총 {len(skills)}개 스킬 | k-skill list --all 전체목록 | k-skill list -d <domain> 도메인별"
            )
    else:
        if ctx.obj["as_json"]:
            click.echo(json.dumps(skills, ensure_ascii=False, indent=2))
        else:
            for s in skills:
                click.echo(
                    f"  {s['domain']}/{s['name']:25s} {s['display_name']}  [{s.get('category', '')}]"
                )
            click.echo(f"\n총 {len(skills)}개")


@main.group(chain=True)
@click.pass_context
def setup(ctx: click.Context):
    """의존성 확인 및 설치.

    하위 명령:
      check      시스템/패키지/런타임 의존성 상태 확인
      install    누락된 의존성 설치 안내
      proxy      프록시 연결 상태 확인
    """
    pass


@setup.command("check")
@click.pass_context
def setup_check(ctx: click.Context):
    """시스템 의존성 상태 전체 확인.

    Python, Node.js, curl, jq, k-skill-proxy 연결 상태를 점검합니다.

    예시:
      k-skill setup check
      k-skill -j setup check   # JSON 출력 (전역 -j 플래그)
    """
    checks: dict[str, dict] = {}

    # Python
    checks["python"] = {
        "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "ok": sys.version_info >= (3, 10),
    }

    # Node.js
    node_path = shutil.which("node")
    if node_path:
        try:
            result = subprocess.run(
                ["node", "--version"], capture_output=True, text=True
            )
            checks["node"] = {"version": result.stdout.strip(), "ok": True}
        except Exception:
            checks["node"] = {"version": None, "ok": False}
    else:
        checks["node"] = {"version": None, "ok": False, "note": "npm 스킬 사용 시 필요"}

    # curl
    checks["curl"] = {"ok": shutil.which("curl") is not None}

    # jq
    checks["jq"] = {"ok": shutil.which("jq") is not None, "note": "선택사항"}

    # Proxy
    try:
        from .proxy import health_check
        proxy_ok = asyncio.run(health_check())
        checks["proxy"] = {"ok": proxy_ok}
    except Exception:
        checks["proxy"] = {"ok": False}

    if ctx.obj["as_json"]:
        click.echo(json.dumps(checks, ensure_ascii=False, indent=2))
    else:
        all_ok = True
        for name, status in checks.items():
            icon = "✅" if status["ok"] else "❌"
            ver = status.get("version", "")
            note = status.get("note", "")
            click.echo(f"  {icon} {name:10s} {ver:12s} {note}")
            if not status["ok"]:
                all_ok = False

        if all_ok:
            click.echo("\n✨ 모든 의존성 준비 완료")
        else:
            click.echo("\n⚠️ 일부 의존성 누락 — k-skill setup install 참고")


@setup.command("install")
def setup_install():
    """누락된 의존성 설치 안내.

    보안 정책상 자동 설치는 수행하지 않습니다.
    누락된 패키지별 수동 설치 명령어를 안내합니다.

    예시:
      k-skill setup install
    """
    click.echo("의존성 수동 설치 가이드:")
    click.echo("  pip install -e .                    # k-skill 개발 설치")
    click.echo("  pip install SRTrain                 # SRT 예매")
    click.echo("  pip install korail2                 # KTX 예매")
    click.echo("  pip install mcp                     # 마이리얼트립 (Remote MCP)")
    click.echo("  npm install -g daiso                # 올리브영/영화관 검색")
    click.echo("  npm install -g kbo-game             # KBO 경기 결과")
    click.echo("  npm install -g kbl-results          # KBL 경기 결과")
    click.echo("  npm install -g kleague-results      # K리그 경기 결과")
    click.echo("  npm install -g lck-analytics        # LCK 분석")
    click.echo("  npm install -g k-lotto              # 로또 당첨번호")
    click.echo("  k-skill setup check                    # 설치 상태 재확인")


@setup.command("proxy")
@click.pass_context
def setup_proxy(ctx: click.Context):
    """k-skill-proxy 연결 상태 확인.

    프록시 서버 가용성을 테스트합니다.
    KSKILL_PROXY_BASE_URL 환경변수로 오버라이드 가능합니다.

    예시:
      k-skill setup proxy
      k-skill -j setup proxy   # JSON 출력 (전역 -j 플래그)
    """
    from .proxy import get_proxy_base, health_check

    base = get_proxy_base()
    click.echo(f"프록시: {base}", err=True)
    try:
        ok = asyncio.run(health_check())
        if ctx.obj["as_json"]:
            click.echo(json.dumps({"proxy": base, "reachable": ok}))
        else:
            icon = "✅" if ok else "❌"
            click.echo(f"{icon} 프록시 {'연결 가능' if ok else '연결 불가'}")
    except Exception:
        if ctx.obj["as_json"]:
            click.echo(json.dumps({"proxy": base, "reachable": False, "error": "프록시 연결 확인 중 오류가 발생했습니다."}))
        else:
            click.echo("❌ 연결 실패: 프록시 서버에 접속할 수 없습니다")


# ============================================================
# Dynamic skill loading — register skill domain commands
# ============================================================


def register_skill_commands():
    """Discover and register skill domain commands from skills/ directory."""
    groups = discover_cli_groups()
    for domain_name, cli_group in groups.items():
        if main.get_command(ctx=None, cmd_name=domain_name) is None:
            main.add_command(cli_group, name=domain_name)


# Auto-register on module import
register_skill_commands()


if __name__ == "__main__":
    main()
