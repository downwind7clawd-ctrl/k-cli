"""검색 스킬 — 네이버 뉴스 검색."""

import click

from cli_anything.k_skill.proxy import safe_proxy_get
from cli_anything.k_skill.output import emit


@click.group()
def cli():
    """검색 (네이버 뉴스).

    네이버 뉴스 검색 API를 경유해 최신 뉴스 기사를 조회.
    """
    pass


@cli.command("naver-news")
@click.argument("query")
@click.option("--display", default=10, help="반환 건수 (기본 10, 1~100)")
@click.option("--start", default=1, help="검색 시작 위치 (기본 1, 최대 1000)")
@click.option("--sort", default="sim", type=click.Choice(["sim", "date"]),
              help="정렬 (sim=유사도, date=최신순)")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def naver_news(query, display, start, sort, as_json):
    """네이버 뉴스 검색.

    검색어로 최신 뉴스 기사를 조회합니다.

    예시:
      k-cli search naver-news "삼성전자 실적"
      k-cli search naver-news "AI 규제" --sort date --display 5 -j
    """
    if not query or not query.strip() or len(query.strip()) < 2:
        emit({"skill": "naver-news", "status": "error",
              "error": {"code": "INVALID_INPUT", "message": "검색어를 입력하세요 (2글자 이상)"}},
             as_json=as_json)
        return
    # Naver API constraint: start + display - 1 <= 1000
    display = min(max(display, 1), 100)
    start = min(max(start, 1), 1000)
    if start + display - 1 > 1000:
        display = 1000 - start + 1
    params = {"q": query, "display": display, "start": start, "sort": sort}
    resp = safe_proxy_get("naver-news", "/v1/naver-news/search", params)
    emit(resp, as_json=as_json)
