"""쇼핑 스킬 — 네이버 쇼핑 검색."""

import asyncio
import click

from cli_anything.k_skill.proxy import safe_proxy_get
from cli_anything.k_skill.runner import run_npm, run_script, run_pip_import, run_mcp
from cli_anything.k_skill.output import emit


@click.group()
def cli():
    """쇼핑 검색 (네이버 쇼핑).

    네이버 쇼핑 검색 API를 경유해 상품 후보, 가격, 판매처를 조회.
    """
    pass


@cli.command("naver-shop")
@click.argument("query")
@click.option("--limit", default=10, help="반환 건수 (기본 10, 최대 40)")
@click.option("--sort", default="rel", type=click.Choice(["rel", "date", "price_asc", "price_dsc", "review"]),
              help="정렬 (rel=관련도, date=최신, price_asc=낮은가격, price_dsc=높은가격, review=리뷰많은순)")
@click.option("--page", default=1, help="페이지 (기본 1)")
@click.option("--timeout", "-t", default=30, type=int, help="타임아웃(초)")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def naver_shop(query, limit, sort, page, as_json, timeout):
    """네이버 쇼핑 검색.

    상품명/검색어로 네이버 쇼핑 후보를 검색합니다.

    예시:
      k-cli shopping naver-shop "에어팟 프로 2세대"
      k-cli shopping naver-shop "커피머신" --sort price_asc --limit 5 -j
    """
    if not query or not query.strip():
        emit({"skill": "naver-shopping", "status": "error",
              "error": {"code": "INVALID_INPUT", "message": "검색어를 입력하세요 (2글자 이상)"}},
             as_json=as_json)
        return
    params = {"q": query, "limit": min(max(limit, 1), 40), "sort": sort, "page": max(page, 1)}
    resp = safe_proxy_get("naver-shopping", "/v1/naver-shopping/search", params, timeout=timeout)
    emit(resp, as_json=as_json)

@cli.command(name='olive-young', help='올리브영 상품 검색 및 재고 확인')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def olive_young(query, as_json, timeout):
    """올리브영 검색."""
    args = [query] if query else []
    result = asyncio.run(run_npm('olive-young-search', args, npx=True, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='market-kurly', help='마켓컬리 상품 검색')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def market_kurly(query, as_json, timeout):
    """마켓컬리 검색."""
    args = [query] if query else []
    result = asyncio.run(run_npm('market-kurly-search', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='daiso', help='다이소몰 상품 재고 조회')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def daiso(query, as_json, timeout):
    """다이소몰 검색."""
    args = [query] if query else []
    result = asyncio.run(run_npm('daiso-product-search', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='danawa', help='다나와 최저가 검색/비교')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def danawa(query, as_json, timeout):
    """다나와 가격비교."""
    args = [query] if query else []
    result = asyncio.run(run_script('danawa_search.py', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='ohou-deal', help='오늘의집 데일리특가 조회')
@click.option('--query', '-q', 'search_query', help='상품명/브랜드 키워드')
@click.option('--min-discount', 'min_discount', type=int, help='최소 할인율 (0~100)')
@click.option('--free-delivery', 'free_delivery', is_flag=True, help='무료배송 상품만')
@click.option('--sort', 'sort_by', default='discount', type=click.Choice(['discount', 'price', 'review', 'annual-sales']), help='정렬 기준 (기본: discount)')
@click.option('--limit', default=10, type=int, help='결과 개수 (기본 10)')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
def ohou_deal(search_query, min_discount, free_delivery, sort_by, limit, as_json, timeout):
    """오늘의집 데일리딜 조회.

    오늘의집 공개 오늘의딜 페이지에서 특가 상품을 조회합니다.

    예시:
      k-cli shopping ohou-deal
      k-cli shopping ohou-deal --query 러그 --min-discount 30 --free-delivery --limit 5 -j
    """
    args = ["list"]
    if search_query:
        args.extend(["--query", search_query])
    if min_discount is not None:
        args.extend(["--min-discount", str(min_discount)])
    if free_delivery:
        args.append("--free-delivery")
    if sort_by:
        args.extend(["--sort", sort_by])
    args.extend(["--limit", str(limit)])
    result = asyncio.run(run_script('ohou_today_deal.py', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='coupang', help='쿠팡 파트너스 API 상품 검색')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def coupang(query, as_json, timeout):
    """쿠팡 상품 검색."""
    result = asyncio.run(run_mcp('coupang-product-search', server_url='local://coupang-mcp', timeout=timeout))
    emit(result, as_json=as_json)
