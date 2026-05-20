"""배송 도메인 스킬."""

import asyncio
import click

from cli_anything.k_skill.runner import run_npm, run_script, run_pip_import, run_mcp
from cli_anything.k_skill.output import emit


@click.group(name='delivery', help='배송: 택배 송장 조회')
def cli():
    pass

@cli.command(name='delivery', help='택배 송장번호로 배송 조회')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def delivery(query, as_json, timeout):
    """택배 송장 조회."""
    args = [query] if query else []
    result = asyncio.run(run_script('delivery_tracking.py', args, timeout=timeout))
    emit(result, as_json=as_json)
