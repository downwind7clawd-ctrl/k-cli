"""기타 도메인 스킬."""

import asyncio
import click

from cli_anything.k_skill.runner import run_npm, run_script, run_pip_import, run_mcp
from cli_anything.k_skill.output import emit


@click.group(name='other', help='기타: 기타 유틸리티')
def cli():
    pass

@cli.command(name='iros', help='지식재산권 등록 자동화')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def iros(query, as_json, timeout):
    """지식재산권 등록."""
    args = [query] if query else []
    result = asyncio.run(run_script('main.py', args, timeout=timeout, script_subdir='iros-registry-automation'))
    emit(result, as_json=as_json)

@cli.command(name='setup', help='k-skill 초기 설정 마법사')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def setup(query, as_json, timeout):
    """k-skill 초기설정."""
    result = asyncio.run(run_mcp('k-skill-setup', server_url='local://korean-law-mcp', timeout=timeout))
    emit(result, as_json=as_json)

@cli.command(name='jangbu', help='한국식 장부/가계부')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def jangbu(query, as_json, timeout):
    """장부/가계부."""
    args = [query] if query else []
    result = asyncio.run(run_script('jangbu_main.py', args, timeout=timeout))
    emit(result, as_json=as_json)

@cli.command(name='privacy-terms', help='개인정보처리방침 생성')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def privacy_terms(query, as_json, timeout):
    """개인정보처리방침."""
    args = [query] if query else []
    result = asyncio.run(run_script('privacy_terms.py', args, timeout=timeout))
    emit(result, as_json=as_json)
