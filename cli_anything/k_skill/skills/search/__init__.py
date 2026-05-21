"""검색 스킬 — 네이버 뉴스 검색."""

import asyncio
import click

from cli_anything.k_skill.proxy import safe_proxy_get
from cli_anything.k_skill.output import emit
from cli_anything.k_skill.runner import run_script


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


@cli.command(name='naver-blog', help='네이버 블로그 검색 및 요약')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def naver_blog(query, as_json, timeout):
    """네이버 블로그 리서치."""
    args = [query] if query else []
    result = asyncio.run(run_script('naver_blog.py', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='geeknews', help='긱뉴스 테크 뉴스 조회')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def geeknews(query, as_json, timeout):
    """긱뉴스."""
    args = [query] if query else []
    result = asyncio.run(run_script('geeknews_search.py', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='patent', help='KIPIRIS 한국 특허 검색')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def patent(query, as_json, timeout):
    """특허 검색."""
    args = [query] if query else []
    result = asyncio.run(run_script('patent_search.py', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='sillok', help='조선왕조실록 검색')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def sillok(query, as_json, timeout):
    """조선왕조실록."""
    args = [query] if query else []
    result = asyncio.run(run_script('sillok_search.py', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='scholarship', help='한국 장학금 검색')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def scholarship(query, as_json, timeout):
    """장학금 검색."""
    args = [query] if query else []
    result = asyncio.run(run_script('scholarship_search.py', args, timeout=timeout))
    emit(result, as_json=as_json)

