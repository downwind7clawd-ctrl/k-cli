"""스포츠/레저 도메인 스킬."""

import asyncio
import click

from cli_anything.k_skill.runner import run_npm, run_script, run_pip_import, run_mcp
from cli_anything.k_skill.output import emit


@click.group(name='sports', help='스포츠/레저: 스포츠 경기, 로또, 영화관')
def cli():
    pass

@cli.command(name='kbo', help='KBO 한국야구 경기 결과 조회')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def kbo(query, as_json, timeout):
    """KBO 경기결과."""
    args = [query] if query else []
    result = asyncio.run(run_npm('kbo-game', args, global_install=True, timeout=timeout))
    emit(result, as_json=as_json)

@cli.command(name='kbl', help='KBL 프로농구 경기 결과 조회')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def kbl(query, as_json, timeout):
    """KBL 농구결과."""
    args = [query] if query else []
    result = asyncio.run(run_npm('kbl-results', args, global_install=True, timeout=timeout))
    emit(result, as_json=as_json)

@cli.command(name='kleague', help='K리그 축구 경기 결과 조회')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def kleague(query, as_json, timeout):
    """K리그 결과."""
    args = [query] if query else []
    result = asyncio.run(run_npm('kleague-results', args, global_install=True, timeout=timeout))
    emit(result, as_json=as_json)

@cli.command(name='lck', help='LCK 리그오브레전드 경기/분석')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def lck(query, as_json, timeout):
    """LCK 분석."""
    args = [query] if query else []
    result = asyncio.run(run_npm('lck-analytics', args, global_install=True, timeout=timeout))
    emit(result, as_json=as_json)

@cli.command(name='cinema', help='CGV/메가박스/롯데시네마 영화관/상영작 검색')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def cinema(query, as_json, timeout):
    """영화관 검색."""
    args = [query] if query else []
    result = asyncio.run(run_npm('daiso', args, npx=True, timeout=timeout))
    emit(result, as_json=as_json)

@cli.command(name='lotto', help='로또 당첨번호 조회')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def lotto(query, as_json, timeout):
    """로또 당첨번호."""
    args = [query] if query else []
    result = asyncio.run(run_npm('k-lotto', args, global_install=True, timeout=timeout))
    emit(result, as_json=as_json)

@cli.command(name='marathon', help='한국 마라톤 대회 일정 검색')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def marathon(query, as_json, timeout):
    """마라톤 일정."""
    args = [query] if query else []
    result = asyncio.run(run_npm('korean-marathon-schedule', args, timeout=timeout))
    emit(result, as_json=as_json)

@cli.command(name='ticket', help='공연/전시 티켓 잔여석 조회')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def ticket(query, as_json, timeout):
    """공연 잔여석."""
    args = [query] if query else []
    result = asyncio.run(run_script('ticket_availability.py', args, timeout=timeout, script_subdir='ticket-availability'))
    emit(result, as_json=as_json)
