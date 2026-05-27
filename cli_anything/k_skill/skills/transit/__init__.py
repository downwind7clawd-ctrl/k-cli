"""대중교통 스킬 — 서울 지하철 실시간 도착정보."""

import asyncio
import click

from cli_anything.k_skill.proxy import safe_proxy_get
from cli_anything.k_skill.runner import run_script, run_pip_import
from cli_anything.k_skill.output import emit


@click.group()
def cli():
    """대중교통 (서울 지하철 실시간 도착정보).

    서울 열린데이터 광장 Open API를 k-skill-proxy로 경유 조회.
    """
    pass


@cli.command()
@click.argument("station_name")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def subway(station_name, as_json):
    """서울 지하철 실시간 도착정보.

    역명으로 도착 예정 열차 정보를 조회합니다.

    예시:
      k-skill transit subway "강남"
      k-skill transit subway "서울역" -j
    """
    if not station_name or not station_name.strip():
        emit({"skill": "seoul-subway", "status": "error",
              "error": {"code": "INVALID_INPUT", "message": "역명을 입력하세요"}},
             as_json=as_json)
        return
    params = {"stationName": station_name}
    resp = safe_proxy_get("seoul-subway", "/v1/seoul-subway/arrival", params)
    emit(resp, as_json=as_json)

@cli.command(name='subway-lost', help='서울교통공사 지하철 분실물 검색')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def subway_lost(query, as_json, timeout):
    """지하철 분실물."""
    args = [query] if query else []
    result = asyncio.run(run_script('subway_lost_property.py', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='intercity-bus', help='Tmoney 시외버스 시간표/잔여석 조회')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def intercity_bus(query, as_json, timeout):
    """시외버스 예매."""
    args = [query] if query else []
    result = asyncio.run(run_script('intercity_bus_search.py', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='express-bus', help='KOBUS 고속버스 시간표/잔여석 조회')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def express_bus(query, as_json, timeout):
    """고속버스 예매."""
    args = [query] if query else []
    result = asyncio.run(run_script('kobus_express_booking.py', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='flight-search', help='Google Flights 항공권 가격/일정 검색')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def flight_search(query, as_json, timeout):
    """항공권 검색."""
    result = asyncio.run(run_pip_import('fast_flights', 'search_flights', packages=["fast-flights"], timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='srt', help='SRT 열차 조회/예매')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def srt(query, as_json, timeout):
    """SRT 예매."""
    result = asyncio.run(run_pip_import('SRTrain', 'search_train', packages=["SRTrain"], timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='ktx', help='KTX/코레일 열차 조회/예매')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def ktx(query, as_json, timeout):
    """KTX 예매."""
    result = asyncio.run(run_pip_import('korail2', 'search_train', packages=["korail2-ncard", "pycryptodome"], timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='transit-route', help='ODSay 대중교통 길찾기')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def transit_route(query, as_json, timeout):
    """대중교통 길찾기."""
    import os
    env_vars = {k: os.environ[k] for k in ["ODSAY_API_KEY"] if k in os.environ}
    args = [query] if query else []
    result = asyncio.run(run_script('transit_route.py', args, env_vars=env_vars, timeout=timeout))
    emit(result, as_json=as_json)
