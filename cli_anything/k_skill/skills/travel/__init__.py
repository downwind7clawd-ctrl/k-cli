"""여행 도메인 스킬."""

import asyncio
import click

from cli_anything.k_skill.runner import run_npm, run_script, run_pip_import, run_mcp
from cli_anything.k_skill.output import emit


@click.group(name='travel', help='여행: 여행지, 숙소 검색')
def cli():
    pass

@cli.command(name='myrealtrip', help='마이리얼트립 숙소/패키지 검색')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def myrealtrip(query, as_json, timeout):
    """마이리얼트립."""
    args = {"keyword": query} if query else {}
    result = asyncio.run(run_mcp('myrealtrip-search', server_url='https://mcp-servers.myrealtrip.com/mcp', tool_name='searchStays', arguments=args, timeout=timeout))
    emit(result, as_json=as_json)

@cli.command(name='hola-poke', help='올라포케 역삼점 메뉴/영업시간')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def hola_poke(query, as_json, timeout):
    """올라포케 역삼점."""
    result = asyncio.run(run_mcp('hola-poke-yeoksam', server_url='https://hola-poke-yeoksam-skill.onrender.com/mcp', tool_name='get_menu', timeout=timeout))
    emit(result, as_json=as_json)

@cli.command(name='foresttrip', help='산림청 숲나들예약 잔여석 조회')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def foresttrip(query, as_json, timeout):
    """숲나들예약."""
    result = asyncio.run(run_pip_import('playwright', 'sync_api', packages=["playwright"], timeout=timeout))
    emit(result, as_json=as_json)
