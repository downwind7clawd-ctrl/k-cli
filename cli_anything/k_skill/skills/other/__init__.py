"""기타 도메인 스킬."""

import asyncio
import click

from cli_anything.k_skill.runner import run_script, K_SKILL_ROOT
from cli_anything.k_skill.proxy import safe_proxy_get
from cli_anything.k_skill.output import emit, error_response


@click.group(name='other', help='기타: 기타 유틸리티')
def cli():
    pass

@cli.command(name='iros', help='지식재산권 등록 자동화')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def iros(query, as_json, timeout):
    """지식재산권 등록."""
    args = [query] if query else []
    result = asyncio.run(run_script('main.py', args, timeout=timeout, script_dirs=[K_SKILL_ROOT / "iros-registry-automation"]))
    emit(result, as_json=as_json)

@cli.command(name='setup', help='k-skill 초기 설정 마법사')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def setup(query, as_json, timeout):
    """k-skill 초기설정."""
    emit(error_response(
        "k-skill-setup", "NOT_IMPLEMENTED",
        "setup 명령은 k-skill setup check/install/proxy를 사용하세요.",
        fix="k-skill setup check -j 로 의존성 상태를 확인하세요.",
    ), as_json=as_json)

@cli.command(name='jangbu', help='한국식 장부/가계부')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def jangbu(query, as_json, timeout):
    """장부/가계부."""
    args = [query] if query else []
    result = asyncio.run(run_script('jangbu_main.py', args, timeout=timeout))
    emit(result, as_json=as_json)

@cli.command(name='privacy-terms', help='개인정보처리방침 생성')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def privacy_terms(query, as_json, timeout):
    """개인정보처리방침."""
    args = [query] if query else []
    result = asyncio.run(run_script('privacy_terms.py', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.group(name="whois")
def whois():
    """KR 도메인/AS/IP WHOIS 조회 (kr-whois-lookup)."""
    pass


@whois.command(name="domain")
@click.option("--q", "query", required=True, help="도메인명 (예: example.com)")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def whois_domain(query, as_json):
    """도메인 WHOIS 조회."""
    resp = safe_proxy_get("kr-whois-lookup", "/v1/kr-whois/domain", {"query": query})
    emit(resp, as_json=as_json)


@whois.command(name="as")
@click.option("--q", "query", required=True, help="AS 번호 (예: AS4763)")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def whois_as(query, as_json):
    """AS WHOIS 조회."""
    resp = safe_proxy_get("kr-whois-lookup", "/v1/kr-whois/as", {"query": query})
    emit(resp, as_json=as_json)


@whois.command(name="ip")
@click.option("--q", "query", required=True, help="IP 주소")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def whois_ip(query, as_json):
    """IP WHOIS 조회."""
    resp = safe_proxy_get("kr-whois-lookup", "/v1/kr-whois/ip", {"query": query})
    emit(resp, as_json=as_json)


@cli.group(name="gov-overseas")
def gov_overseas():
    """국외출장 보고서 조회 (gov-overseas-trip-report)."""
    pass


@gov_overseas.command(name="providers")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
@click.option("--timeout", "-t", default=60, type=int, help="타임아웃(초)")
def go_providers(as_json, timeout):
    """지원 제공처 목록."""
    result = asyncio.run(run_script("gov_overseas_trip_report.py", ["providers"], timeout=timeout, script_dirs=[K_SKILL_ROOT / "gov-overseas-trip-report"]))
    emit(result, as_json=as_json)


@gov_overseas.command(name="list")
@click.option("--provider", required=True, help="제공처 (nec, acrc, open_portal, ...)")
@click.option("--max-pages", default=5, type=int, help="최대 페이지")
@click.option("--keyword", help="검색 키워드")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
@click.option("--timeout", "-t", default=60, type=int, help="타임아웃(초)")
def go_list(provider, max_pages, keyword, as_json, timeout):
    """국외출장 보고서 목록."""
    args = ["list", "--provider", provider, "--max-pages", str(max_pages)]
    if keyword:
        args += ["--keyword", keyword]
    result = asyncio.run(run_script("gov_overseas_trip_report.py", args, timeout=timeout, script_dirs=[K_SKILL_ROOT / "gov-overseas-trip-report"]))
    emit(result, as_json=as_json)


@gov_overseas.command(name="detail")
@click.option("--provider", required=True, help="제공처")
@click.option("--id", "doc_id", required=True, help="보고서 ID")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
@click.option("--timeout", "-t", default=60, type=int, help="타임아웃(초)")
def go_detail(provider, doc_id, as_json, timeout):
    """보고서 상세."""
    args = ["detail", "--provider", provider, "--id", doc_id]
    result = asyncio.run(run_script("gov_overseas_trip_report.py", args, timeout=timeout, script_dirs=[K_SKILL_ROOT / "gov-overseas-trip-report"]))
    emit(result, as_json=as_json)


@gov_overseas.command(name="search")
@click.option("--keyword", required=True, help="검색 키워드")
@click.option("--providers", help="제공처 목록 (쉼표 구분)")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
@click.option("--timeout", "-t", default=60, type=int, help="타임아웃(초)")
def go_search(keyword, providers, as_json, timeout):
    """보고서 검색."""
    args = ["search", "--keyword", keyword]
    if providers:
        args += ["--providers", providers]
    result = asyncio.run(run_script("gov_overseas_trip_report.py", args, timeout=timeout, script_dirs=[K_SKILL_ROOT / "gov-overseas-trip-report"]))
    emit(result, as_json=as_json)


@gov_overseas.command(name="discover")
@click.option("--keyword", required=True, help="검색 키워드")
@click.option("--urls", help="추가 URL 목록 (쉼표 구분)")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
@click.option("--timeout", "-t", default=60, type=int, help="타임아웃(초)")
def go_discover(keyword, urls, as_json, timeout):
    """제공처 자동 발견."""
    args = ["discover", "--keyword", keyword]
    if urls:
        args += ["--urls", urls]
    result = asyncio.run(run_script("gov_overseas_trip_report.py", args, timeout=timeout, script_dirs=[K_SKILL_ROOT / "gov-overseas-trip-report"]))
    emit(result, as_json=as_json)


@cli.group(name="naver-ad")
def naver_ad():
    """네이버 검색광고 성과 조회 (naver-ad-performance)."""
    pass


@naver_ad.command(name="doctor")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
@click.option("--timeout", "-t", default=60, type=int, help="타임아웃(초)")
def na_doctor(as_json, timeout):
    """환경 진단."""
    result = asyncio.run(run_script("naver_ad_performance.py", ["doctor"], timeout=timeout, script_dirs=[K_SKILL_ROOT / "naver-ad-performance"]))
    emit(result, as_json=as_json)


@naver_ad.command(name="campaigns")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
@click.option("--timeout", "-t", default=60, type=int, help="타임아웃(초)")
def na_campaigns(as_json, timeout):
    """캠페인 목록."""
    result = asyncio.run(run_script("naver_ad_performance.py", ["campaigns"], timeout=timeout, script_dirs=[K_SKILL_ROOT / "naver-ad-performance"]))
    emit(result, as_json=as_json)


@naver_ad.command(name="adgroups")
@click.option("--campaign", required=True, help="nccCampaignId")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
@click.option("--timeout", "-t", default=60, type=int, help="타임아웃(초)")
def na_adgroups(campaign, as_json, timeout):
    """광고그룹 목록."""
    args = ["adgroups", "--campaign", campaign]
    result = asyncio.run(run_script("naver_ad_performance.py", args, timeout=timeout, script_dirs=[K_SKILL_ROOT / "naver-ad-performance"]))
    emit(result, as_json=as_json)


@naver_ad.command(name="keywords")
@click.option("--adgroup", required=True, help="nccAdgroupId")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
@click.option("--timeout", "-t", default=60, type=int, help="타임아웃(초)")
def na_keywords(adgroup, as_json, timeout):
    """키워드 목록."""
    args = ["keywords", "--adgroup", adgroup]
    result = asyncio.run(run_script("naver_ad_performance.py", args, timeout=timeout, script_dirs=[K_SKILL_ROOT / "naver-ad-performance"]))
    emit(result, as_json=as_json)


@naver_ad.command(name="stats")
@click.option("--ids", required=True, help="ID 목록 (쉼표 구분)")
@click.option("--since", required=True, help="시작일 YYYY-MM-DD")
@click.option("--until", required=True, help="종료일 YYYY-MM-DD")
@click.option("--by", default="day", help="집계 단위 (day/month)")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
@click.option("--timeout", "-t", default=60, type=int, help="타임아웃(초)")
def na_stats(ids, since, until, by, as_json, timeout):
    """성과 통계."""
    args = ["stats", "--ids", ids, "--since", since, "--until", until, "--by", by]
    result = asyncio.run(run_script("naver_ad_performance.py", args, timeout=timeout, script_dirs=[K_SKILL_ROOT / "naver-ad-performance"]))
    emit(result, as_json=as_json)


@naver_ad.command(name="keywordtool")
@click.option("--keywords", required=True, help="키워드 목록 (쉼표 구분)")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
@click.option("--timeout", "-t", default=60, type=int, help="타임아웃(초)")
def na_keywordtool(keywords, as_json, timeout):
    """키워드 도구."""
    args = ["keywordtool", "--keywords", keywords]
    result = asyncio.run(run_script("naver_ad_performance.py", args, timeout=timeout, script_dirs=[K_SKILL_ROOT / "naver-ad-performance"]))
    emit(result, as_json=as_json)
