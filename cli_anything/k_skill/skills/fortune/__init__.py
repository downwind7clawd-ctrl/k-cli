"""사주/작명 스킬 — 사주 운세, 이름 짓기."""

import asyncio
import click

from cli_anything.k_skill.runner import run_npm
from cli_anything.k_skill.output import emit


@click.group(name='fortune', help='사주/작명: 사주 운세, 작명소')
def cli():
    pass


@cli.command(name='saju-fortune', help='사주 운세 (생년월일시/성별)')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.option('--sex', type=click.Choice(['M', 'F']), help='성별 (M/F → male/female)')
@click.option('--birth', 'birth', help='생년월일 YYYY-MM-DD')
@click.option('--birth-time', 'birth_time', help='태어난 시간 HH:mm')
@click.option('--name', 'name', help='이름 (한글)')
@click.option('--calendar', type=click.Choice(['solar', 'lunar']), default='solar', help='양력/음력 (기본 solar)')
@click.option('--lunar', is_flag=True, help='음력 생일 (--calendar lunar 과 동일)')
@click.argument('query', required=False)
def saju_fortune(query, as_json, timeout, sex, birth, birth_time, name, calendar, lunar):
    """사주 운세 조회.

    upstream saju-fortune npm package 를 래핑합니다.
    생년월일시와 성별을 플래그로 넘기며, query 위치인자는
    "YYYY-MM-DD HH:mm" 또는 "YYYY-MM-DD" 형태로 받아 분리합니다.

    예시:
      k-skill fortune saju-fortune "1990-05-15 14:30" --sex M -j
      k-skill fortune saju-fortune --birth 1990-05-15 --birth-time 14:30 --sex F -j
    """
    args = []
    if query:
        if ' ' in query:
            bd, bt = query.split(' ', 1)
            args += ['--birth-date', bd, '--birth-time', bt]
        else:
            args += ['--birth-date', query]
    if sex:
        args += ['--gender', 'male' if sex == 'M' else 'female']
    if birth and '--birth-date' not in args:
        args += ['--birth-date', birth]
    if birth_time and '--birth-time' not in args:
        args += ['--birth-time', birth_time]
    if name:
        args += ['--name', name]
    if lunar:
        args += ['--calendar', 'lunar']
    elif calendar and calendar != 'solar':
        args += ['--calendar', calendar]
    result = asyncio.run(run_npm('saju-fortune', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='naming-house', help='작명소 (이름 짓기)')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.option('--birth', 'birth', help='생년월일 YYYY-MM-DD')
@click.option('--birth-time', 'birth_time', help='태어난 시간 HH:mm')
@click.option('--sex', type=click.Choice(['M', 'F']), help='성별 (M/F → male/female)')
@click.option('--calendar', type=click.Choice(['solar', 'lunar']), default='solar', help='양력/음력 (기본 solar)')
@click.option('--lunar', is_flag=True, help='음력 생일 (--calendar lunar 과 동일)')
@click.argument('query', required=False)
def naming_house(query, as_json, timeout, birth, birth_time, sex, calendar, lunar):
    """작명소 (이름 추천).

    upstream naming-house npm package 를 래핑합니다.
    query 위치인자는 성씨(한글)이며 --surname 로 전달됩니다.

    예시:
      k-skill fortune naming-house 김철수 --birth 1990-05-15 --sex M -j
    """
    args = []
    if query:
        args += ['--surname', query]
    if birth:
        args += ['--birth-date', birth]
    if birth_time:
        args += ['--birth-time', birth_time]
    if sex:
        args += ['--gender', 'male' if sex == 'M' else 'female']
    if lunar:
        args += ['--calendar', 'lunar']
    elif calendar and calendar != 'solar':
        args += ['--calendar', calendar]
    result = asyncio.run(run_npm('naming-house', args, timeout=timeout))
    emit(result, as_json=as_json)
