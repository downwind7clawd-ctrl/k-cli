"""문서 도메인 스킬."""

import asyncio
import click

from cli_anything.k_skill.runner import run_npm, run_script, run_pip_import, run_mcp
from cli_anything.k_skill.output import emit


@click.group(name='document', help='문서: HWP, 맞춤법, 글자수')
def cli():
    pass

@cli.command(name='hwp-convert', help='HWP/HWPX 문서를 PDF 등으로 변환')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def hwp_convert(query, as_json, timeout):
    """HWP 변환."""
    args = [query] if query else []
    result = asyncio.run(run_npm('kordoc', args, timeout=timeout))
    emit(result, as_json=as_json)

@cli.command(name='rhwp-debug', help='rhwp Rust CLI로 HWP 레이아웃 디버깅')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def rhwp_debug(query, as_json, timeout):
    """HWP 레이아웃 디버그."""
    args = [query] if query else []
    result = asyncio.run(run_script('rhwp', args, timeout=timeout, is_binary=True))
    emit(result, as_json=as_json)

@cli.command(name='rhwp-edit', help='HWP 문서 편집 (k-skill-rhwp)')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def rhwp_edit(query, as_json, timeout):
    """HWP 편집."""
    args = [query] if query else []
    result = asyncio.run(run_npm('k-skill-rhwp', args, timeout=timeout))
    emit(result, as_json=as_json)

@cli.command(name='spell-check', help='한국어 맞춤법/문법 검사')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def spell_check(query, as_json, timeout):
    """맞춤법 검사."""
    args = [query] if query else []
    result = asyncio.run(run_script('korean_spell_check.py', args, timeout=timeout))
    emit(result, as_json=as_json)

@cli.command(name='char-count', help='한국어 글자/어절/문단 수 카운트')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def char_count(query, as_json, timeout):
    """글자 수 세기."""
    args = [query] if query else []
    result = asyncio.run(run_npm('korean-character-count', args, timeout=timeout))
    emit(result, as_json=as_json)
