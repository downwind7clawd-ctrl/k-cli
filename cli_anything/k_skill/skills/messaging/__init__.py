"""메시징 스킬 — 카카오톡 macOS 아카이브 검색."""

import asyncio
import click

from cli_anything.k_skill.runner import run_script
from cli_anything.k_skill.output import emit


@click.group(name='messaging', help='메시징: 카카오톡 macOS 아카이브')
def cli():
    pass


@cli.group(name='kakaotalk-mac', help='카카오톡 macOS 대화 아카이브 검색 (macOS 전용)')
def kakaotalk_mac():
    pass


@kakaotalk_mac.command(name='index', help='카카오톡 아카이브 인덱싱/검색')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=60, type=int, help='타임아웃(초)')
@click.option('--query', help='검색 쿼리')
@click.option('--limit', '-l', default=10, type=int, help='결과 개수 (기본 10)')
def index(query, limit, as_json, timeout):
    """카카오톡 macOS 아카이브 인덱싱/검색."""
    args = []
    if query:
        args += ['--query', query]
    if limit:
        args += ['--limit', str(limit)]
    result = asyncio.run(run_script('kakaotalk_mac.py', args, timeout=timeout))
    emit(result, as_json=as_json)
