"""비즈니스/법무/조달 스킬 — 사업체건강, 법원진행, 나라장터, 사업자등록."""

import asyncio
import click

from cli_anything.k_skill.proxy import safe_proxy_get
from cli_anything.k_skill.runner import run_npm, run_script
from cli_anything.k_skill.output import emit, error_response
from cli_anything.k_skill.dependency import SkillDependency, check_dependency


@click.group(name='business', help='비즈니스/법무/조달')
def cli():
    pass


# npm-based: court-payment, d2b, s2b
@cli.command(name='court-payment', help='법원 경매/지급명령 진행조회')
@click.option('--case-no', help='사건번호 (예: 2024가단12345)')
@click.option('--json', '-j', 'as_json', is_flag=True)
@click.option('--timeout', '-t', default=30, type=int)
@click.argument('query', required=False)
def court_payment(case_no, query, as_json, timeout):
    args = [query] if query else []
    if case_no:
        args += ['--case-no', case_no]
    result = asyncio.run(run_npm('court-payment-order-assistant', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='d2b-notice', help='D2B 나라장터 입찰공고 검색')
@click.option('--json', '-j', 'as_json', is_flag=True)
@click.option('--timeout', '-t', default=30, type=int)
@click.option('--keyword', help='검색어')
@click.option('--limit', default=10, type=int)
@click.argument('query', required=False)
def d2b_notice(query, keyword, limit, as_json, timeout):
    args = [query] if query else []
    if keyword: args += ['--keyword', keyword]
    args += ['--limit', str(limit)]
    result = asyncio.run(run_npm('d2b-notice-search', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='s2b-notice', help='S2B 나라장터 판로/사업 검색')
@click.option('--json', '-j', 'as_json', is_flag=True)
@click.option('--timeout', '-t', default=30, type=int)
@click.option('--keyword', help='검색어')
@click.option('--limit', default=10, type=int)
@click.argument('query', required=False)
def s2b_notice(query, keyword, limit, as_json, timeout):
    args = [query] if query else []
    if keyword: args += ['--keyword', keyword]
    args += ['--limit', str(limit)]
    result = asyncio.run(run_npm('s2b-notice-search', args, timeout=timeout))
    emit(result, as_json=as_json)


# proxy-based: g2b-order-plan
@cli.command(name='g2b-order-plan', help='조달청 나라장터 발주계획 조회')
@click.option('--json', '-j', 'as_json', is_flag=True)
@click.option('--instNm', help='발주기관명')
@click.option('--limit', default=10, type=int)
@click.argument('query', required=False)
def g2b_order_plan(query, instnm, limit, as_json):
    params = {"numOfRows": min(max(limit, 1), 100)}
    if query: params["q"] = query
    if instnm: params["instNm"] = instnm
    resp = safe_proxy_get("g2b-order-plan", "/v1/g2b/order-plans", params)
    emit(resp, as_json=as_json)


# script-based: localdata-business-status (downloads LOCALDATA CSV via file.localdata.go.kr)
@cli.command(name='localdata-status', help='지방행정 인허가데이터(LOCALDATA) 지역사업체 영업상태 조회')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=60, type=int, help='타임아웃(초)')
@click.option('--name', required=True, help='상호(사업장명)')
@click.option('--region', required=True, help='시군구 (예: 제주제주시, 서울종로구)')
@click.option('--industry', help='업종 (반복 지정 가능)')
def localdata_status(name, region, industry, as_json, timeout):
    args = ['--name', name, '--region', region]
    if industry:
        args += ['--industry', industry]
    result = asyncio.run(run_script('localdata-business-status', args, timeout=timeout))
    emit(result, as_json=as_json)


# proxy aggregate: biz-health-check (reuses existing finance routes, no key)
@cli.command(name='biz-health-check', help='사업체 건강진단 (국세청/국민연금/금융위/부정당 집계)')
@click.option('--json', '-j', 'as_json', is_flag=True)
@click.option('--b-no', required=True, help='사업자등록번호(10자리)')
@click.option('--name', help='상호명')
def biz_health_check(b_no, name, as_json):
    base = {"bizno": b_no}
    if name: base["bizNm"] = name
    results = {}
    for tag, path in [
        ("nts", "/v1/nts-business/status"),
        ("national_pension", "/v1/national-pension/workplace"),
        ("fsc", "/v1/fsc/corp-outline"),
        ("g2b_sanction", "/v1/g2b/sanctioned-supplier"),
    ]:
        results[tag] = safe_proxy_get(tag, path, base)
    emit({"status": "success", "data": results}, as_json=as_json)


# dependency-checked stub: popbill
@cli.command(name='popbill', help='팝빌 전자세금계산서/문서 조회 (API 키 필요)')
@click.option('--json', '-j', 'as_json', is_flag=True)
@click.option('--timeout', '-t', default=30, type=int)
@click.argument('query', required=False)
def popbill(query, as_json, timeout):
    dep = SkillDependency(
        name="popbill",
        python=["popbill"],
        env_keys=["POPBILL_LinkID", "POPBILL_SECRET_KEY", "POPBILL_CORP_NUM"],
    )
    report = asyncio.run(check_dependency(dep))
    if not report.ready:
        miss = ", ".join(report.missing_env or [])
        emit(error_response(
            "popbill", "MISSING_DEPENDENCY",
            "팝빌 SDK 또는 API 키가 없습니다.",
            fix="pip install popbill && 환경변수 설정: " + miss,
        ), as_json=as_json)
        return
    args = [query] if query else []
    result = asyncio.run(run_script("popbill_cli.py", args, timeout=timeout))
    emit(result, as_json=as_json)
