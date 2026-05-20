"""쇼핑 스킬 — 네이버 쇼핑 검색."""

import click

from cli_anything.k_skill.proxy import safe_proxy_get
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
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def naver_shop(query, limit, sort, page, as_json):
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
    resp = safe_proxy_get("naver-shopping", "/v1/naver-shopping/search", params)
    emit(resp, as_json=as_json)
