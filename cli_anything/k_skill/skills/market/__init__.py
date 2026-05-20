"""중고거래 도메인 스킬."""

import asyncio
import click

from cli_anything.k_skill.runner import run_npm, run_script, run_pip_import, run_mcp
from cli_anything.k_skill.output import emit


@click.group(name='market', help='중고거래: 당근마켓, 번개장터 등')
def cli():
    pass

@cli.command(name='bunjang', help='번개장터 중고상품 검색')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def bunjang(query, as_json, timeout):
    """번개장터 검색."""
    args = [query] if query else []
    result = asyncio.run(run_npm('bunjang-cli', args, npx=True, timeout=timeout))
    emit(result, as_json=as_json)

@cli.command(name='daangn-market', help='당근마켓 중고거래 검색')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def daangn_market(query, as_json, timeout):
    """당근 중고거래."""
    args = [query] if query else []
    result = asyncio.run(run_script('daangn_used_goods.py', args, timeout=timeout))
    emit(result, as_json=as_json)

@cli.command(name='daangn-cars', help='당근마켓 중고차 매물 검색')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def daangn_cars(query, as_json, timeout):
    """당근중고차."""
    args = [query] if query else []
    result = asyncio.run(run_script('daangn_cars.py', args, timeout=timeout))
    emit(result, as_json=as_json)

@cli.command(name='used-car-price', help='SK렌터카 중고차 가격 조회')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def used_car_price(query, as_json, timeout):
    """중고차 가격."""
    args = [query] if query else []
    result = asyncio.run(run_script('used_car_price_search.py', args, timeout=timeout))
    emit(result, as_json=as_json)
