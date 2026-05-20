"""금융/공부 스킬 — 사업자등록, 주식, 창업공고."""

import re
import asyncio
import click

from cli_anything.k_skill.proxy import safe_proxy_get, safe_proxy_post
from cli_anything.k_skill.output import emit, error_response


@click.group()
def cli():
    """금융/공부 (사업자등록, 주식, 창업공고).
    
    모든 명령은 k-skill-proxy를 경유하며 별도 API 키 불필요.
    """
    pass


# ── NTS 사업자등록 ──────────────────────────────────────────

@cli.group()
def nts():
    """국세청 사업자등록 진위확인."""
    pass


@nts.command("status")
@click.option("--b-no", "b_nos", multiple=True, required=True, help="사업자등록번호 (10자리, 복수 가능)")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def nts_status(b_nos, as_json):
    """사업자등록 상태조회.
    
    사업자등록번호로 계속사업자/휴업자/폐업자 상태를 조회합니다.
    
    예시:
      k-cli finance nts status --b-no 1234567890
      k-cli finance nts status --b-no 1234567890 --b-no 9876543210 -j
    """
    # Normalize: strip hyphens, keep only digits
    cleaned = []
    for b_no in b_nos:
        digits = re.sub(r"[^0-9]", "", b_no)
        if len(digits) == 10:
            cleaned.append(digits)
    if not cleaned:
        emit(error_response("nts-business", "INVALID_INPUT",
                             "유효한 사업자등록번호(10자리)를 입력하세요"),
             as_json=as_json)
        return
    resp = safe_proxy_post("nts-business", "/v1/nts-business/status", {"b_no": cleaned})
    emit(resp, as_json=as_json)


@nts.command("validate")
@click.option("--b-no", required=True, help="사업자등록번호 (10자리)")
@click.option("--p-nm", required=True, help="대표자명")
@click.option("--start-dt", required=True, help="개업일자 YYYYMMDD")
@click.option("--b-nm", help="상호 (선택)")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def nts_validate(b_no, p_nm, start_dt, b_nm, as_json):
    """사업자등록 진위확인.
    
    사업자등록번호+개업일자+대표자명으로 진위확인합니다.
    
    예시:
      k-cli finance nts validate --b-no 1234567890 --p-nm "홍길동" --start-dt 20200101 -j
    """
    b_no_clean = re.sub(r"[^0-9]", "", b_no)
    start_dt_clean = re.sub(r"[^0-9]", "", start_dt)
    if len(b_no_clean) != 10 or len(start_dt_clean) != 8:
        emit(error_response("nts-business", "INVALID_INPUT",
                             "사업자등록번호(10자리)와 개업일자(YYYYMMDD)를 확인하세요"),
             as_json=as_json)
        return
    body = {"b_no": b_no_clean, "p_nm": p_nm, "start_dt": start_dt_clean}
    if b_nm:
        body["b_nm"] = b_nm
    resp = safe_proxy_post("nts-business", "/v1/nts-business/validate", body)
    emit(resp, as_json=as_json)


# ── 주식 ──────────────────────────────────────────────────

@cli.command("stock")
@click.argument("query")
@click.option("--date", "bas_dd", help="기준일 YYYYMMDD (기본: 오늘)")
@click.option("--limit", default=10, help="검색결과 수 (기본 10, 최대 20)")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def stock(query, bas_dd, limit, as_json):
    """한국 주식 조회 (KRX).
    
    종목명 또는 종목코드로 KRX 상장종목을 검색합니다.
    
    예시:
      k-cli finance stock "삼성전자"
      k-cli finance stock "005930" --date 20260501 -j
    """
    if not query or not query.strip():
        emit(error_response("korean-stock", "INVALID_INPUT", "종목명 또는 종목코드를 입력하세요"),
             as_json=as_json)
        return
    params = {"q": query, "limit": min(max(limit, 1), 20)}
    if bas_dd:
        params["bas_dd"] = bas_dd
    resp = safe_proxy_get("korean-stock", "/v1/korean-stock/search", params)
    emit(resp, as_json=as_json)


# ── K-Startup ─────────────────────────────────────────────

@cli.command("kstartup")
@click.option("--region", "supt_regin", help="지역 (예: 서울특별시, 부산광역시)")
@click.option("--open", "rcrt_prgs_yn", help="모집진행여부 (Y/N)")
@click.option("--keyword", "pan_nm", help="공고명 검색어")
@click.option("--page", default=1, help="페이지 (기본 1)")
@click.option("--per-page", "per_page", default=10, help="페이지당 건수 (기본 10, 최대 100)")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def kstartup(supt_regin, rcrt_prgs_yn, pan_nm, page, per_page, as_json):
    """K-Startup 창업공고 검색.
    
    창업진흥원 창업지원사업 공고를 조회합니다.
    
    예시:
      k-cli finance kstartup --region "서울특별시" --open Y
      k-cli finance kstartup --keyword "청년" --per-page 5 -j
    """
    params = {"page": max(page, 1), "perPage": min(max(per_page, 1), 100)}
    if supt_regin:
        params["supt_regin"] = supt_regin
    if rcrt_prgs_yn:
        params["rcrt_prgs_yn"] = rcrt_prgs_yn
    if pan_nm:
        params["panNm"] = pan_nm
    resp = safe_proxy_get("kstartup", "/v1/kstartup/announcements", params)
    emit(resp, as_json=as_json)
from cli_anything.k_skill.runner import run_mcp, run_npm, run_script


@cli.command(name='dart', help='금융감독원 DART 전자공시 조회')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def dart(query, as_json, timeout):
    """DART 전자공시."""
    args = [query] if query else []
    result = asyncio.run(run_script('k_dart.py', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='kosis', help='KOSIS 국가통계포털 통계 조회')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def kosis(query, as_json, timeout):
    """KOSIS 통계."""
    args = [query] if query else []
    result = asyncio.run(run_script('run_kosis_stats.py', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='korean-law', help='대한민국 법령/판례/유권해석 검색')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def korean_law(query, as_json, timeout):
    """법령/판례 검색."""
    result = asyncio.run(run_mcp('korean-law-search', server_url='local://korean-law-mcp', timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='gongsijiga', help='개별공시지가(토지가격) 조회')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def gongsijiga(query, as_json, timeout):
    """개별공시지가."""
    args = [query] if query else []
    result = asyncio.run(run_npm('gongsijiga-search', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='toss-stock', help='토스증권 주식 시세/정보 조회')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def toss_stock(query, as_json, timeout):
    """토스증권 주식."""
    args = [query] if query else []
    result = asyncio.run(run_npm('toss-securities', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='daishin-report', help='대신증권 리서치 리포트 검색')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def daishin_report(query, as_json, timeout):
    """대신 리포트."""
    args = [query] if query else []
    result = asyncio.run(run_npm('daishin-report-search', args, timeout=timeout))
    emit(result, as_json=as_json)

