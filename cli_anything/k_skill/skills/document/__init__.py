"""문서 도메인 스킬."""

import asyncio
import click

from cli_anything.k_skill.runner import run_npm, run_script, run_pip_import
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
    result = asyncio.run(run_script('rhwp', args, timeout=timeout))
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


@cli.command(name='korean-middle-korean', help='중세 한국어 형태/원형/예문/번역 검색')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=60, type=int, help='타임아웃(초)')
@click.option('--limit', '-l', default=10, type=int, help='결과 개수 (1~50, 기본 10)')
@click.argument('search_type', type=click.Choice(['word', 'spelling', 'origin', 'example', 'translation']))
@click.argument('query')
def korean_middle_korean(search_type, query, limit, as_json, timeout):
    """중세 한국어 형태/원형/예문/번역 검색.

    upstream NomaDamas/k-skill의 korean-middle-korean 스킬을 래핑합니다.
    scripts/korean_middle_korean_search.js를 호출합니다.

    필요 의존성: node, npm (prebuild된 node_modules 필요)

    예시:
      k-skill document korean-middle-korean word '가다' -j
      k-skill document korean-middle-korean origin '나아가다' -j
      k-skill document korean-middle-korean example '사랑' -j
      k-skill document korean-middle-korean translation 'mountains' -j
    """
    limit = max(1, min(limit, 50))
    args = [search_type, query, "--limit", str(limit), "--json"]
    result = asyncio.run(run_script('korean_middle_korean_search.js', args, timeout=timeout))
    emit(result, as_json=as_json)
