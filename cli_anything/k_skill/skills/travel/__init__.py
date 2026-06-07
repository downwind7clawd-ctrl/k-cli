"""여행 도메인 스킬."""

import asyncio
import click

from cli_anything.k_skill.runner import run_script, run_mcp
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
@click.option('--text', 'as_text', is_flag=True, help='사람용 텍스트 출력 (기본과 동일)')
@click.option('--dates', 'dates', help='조회 일자 (YYYYMMDD, 여러 개면 콤마 구분, 미지정시 오늘)')
@click.option('--all', 'all_forests', is_flag=True, help='전체 자연휴양림 조회')
@click.option('--forest-id', 'forest_id', help='특정 insttId 조회')
@click.option('--forest-name', 'forest_name', help='공식 휴양림명 부분 일치 조회')
@click.option('--categories', 'categories', help='카테고리 필터 (01=숙박, 02=야영, 둘다: 01,02)')
@click.option('--timeout', '-t', default=60, type=int, help='타임아웃(초)')
def foresttrip(dates, all_forests, forest_id, forest_name, categories, as_json, as_text, timeout):
    """숲나들예약 빈 객실 조회.

    산림청 숲나들e에서 자연휴양림 예약 가능 객실을 날짜 기준으로 조회합니다.
    upstream k-skill/scripts/run_foresttrip_vacancy.py helper를 호출합니다.

    필요 환경변수: KSKILL_FORESTTRIP_ID, KSKILL_FORESTTRIP_PASSWORD
    필요 의존성: playwright, chromium browser

    예시:
      k-skill travel foresttrip --all --dates 20260607 -j
      k-skill travel foresttrip --forest-name "가야" --dates 20260607,20260608 -j
      k-skill travel foresttrip --all --categories 02 --dates 20260607
    """
    import os
    env_vars = {k: os.environ[k] for k in ["KSKILL_FORESTTRIP_ID", "KSKILL_FORESTTRIP_PASSWORD"] if k in os.environ}
    args = []
    if all_forests:
        args.append("--all")
    if forest_id:
        args.extend(["--forest-id", forest_id])
    if forest_name:
        args.extend(["--forest-name", forest_name])
    if dates:
        args.extend(["--dates", dates])
    if categories:
        args.extend(["--categories", categories])
    if as_json or not as_text:
        args.append("--json")
    else:
        args.append("--text")
    result = asyncio.run(run_script('run_foresttrip_vacancy.py', args, env_vars=env_vars, timeout=timeout))
    emit(result, as_json=as_json)
