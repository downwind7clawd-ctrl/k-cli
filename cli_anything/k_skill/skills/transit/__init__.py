"""대중교통 스킬 — 서울 지하철 실시간 도착정보."""

import asyncio
import os
import click

from cli_anything.k_skill.proxy import safe_proxy_get
from cli_anything.k_skill.runner import run_script, run_pip_import
from cli_anything.k_skill.output import emit, error_response


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
        emit(error_response("seoul-subway-arrival", "INVALID_INPUT", "역명을 입력하세요"),
             as_json=as_json)
        return
    params = {"stationName": station_name}
    resp = safe_proxy_get("seoul-subway-arrival", "/v1/seoul-subway/arrival", params)
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
    args = [query] if query else []
    result = asyncio.run(run_pip_import('fast_flights', 'search_flights', args=args, packages=["fast-flights"], timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='srt', help='SRT 열차 조회/예매')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def srt(query, as_json, timeout):
    """SRT 예매."""
    args = [query] if query else []
    result = asyncio.run(run_pip_import('SRTrain', 'search_train', args=args, packages=["SRTrain"], timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='ktx', help='KTX/코레일 열차 조회/예매')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=60, type=int, help='타임아웃(초)')
@click.argument('from_station')
@click.argument('to_station')
@click.option('--date', required=True, help='출발일 (YYYYMMDD)')
@click.option('--time', 'start_time', default='000000', help='희망 시작 시각 (HHMMSS, 기본 000000)')
@click.option('--train-type', 'train_type', default='ktx', help='열차 종류 (ktx/itx-saemaeul/mugunghwa/nuriro/tonggeun/itx-cheongchun/airport/all)')
@click.option('--limit', default=5, type=int, help='결과 개수 (기본 5)')
@click.option('--include-no-seats', 'include_no_seats', is_flag=True, help='좌석 없는 열차도 포함')
@click.option('--include-waiting-list', 'include_waiting_list', is_flag=True, help='예약 대기 가능 열차도 포함')
def ktx(from_station, to_station, date, start_time, train_type, limit, include_no_seats, include_waiting_list, as_json, timeout):
    """KTX 예매.

    KTX/Korail 열차 조회, 호차별 좌석번호 확인, 예약 흐름을 처리합니다.
    upstream k-skill/scripts/ktx_booking.py helper를 호출합니다.

    필요 환경변수: KSKILL_KTX_ID, KSKILL_KTX_PASSWORD

    예시:
      k-skill transit ktx 서울 부산 --date 20260607 --time 090000
      k-skill transit ktx 서울 부산 --date 20260607 --train-type ktx --limit 10 -j
    """
    env_vars = {k: os.environ[k] for k in ["KSKILL_KTX_ID", "KSKILL_KTX_PASSWORD"] if k in os.environ}
    args = [from_station, to_station, date, start_time,
            "--train-type", train_type,
            "--limit", str(min(max(limit, 1), 30))
            ]
    if include_no_seats:
        args.append("--include-no-seats")
    if include_waiting_list:
        args.append("--include-waiting-list")
    result = asyncio.run(run_script('ktx_booking.py', args, env_vars=env_vars, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='transit-route', help='ODSay 대중교통 길찾기')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def transit_route(query, as_json, timeout):
    """대중교통 길찾기."""
    env_vars = {k: os.environ[k] for k in ["ODSAY_API_KEY"] if k in os.environ}
    args = [query] if query else []
    result = asyncio.run(run_script('transit_route.py', args, env_vars=env_vars, timeout=timeout))
    emit(result, as_json=as_json)


@cli.group(name='seoul-bike', help='서울 따릉이(공공자전거) 대여소 조회')
def seoul_bike():
    """따릉이 대여소 위치, 정보, 잔여 자전거 수를 조회합니다.

    upstream NomaDamas/k-skill의 seoul-bike 스킬을 래핑합니다.
    모든 호출은 k-skill-proxy를 경유하므로 별도 API 키가 필요 없습니다.

    예시:
      k-skill transit seoul-bike nearby --lat 37.5665 --lon 126.9780 -j
      k-skill transit seoul-bike info --station-id ST-1001 -j
      k-skill transit seoul-bike availability --lat 37.5665 --lon 126.9780 -j
    """
    pass


@seoul_bike.command(name='nearby', help='좌표 주변 대여소 조회')
@click.option('--lat', required=True, type=float, help='위도 (WGS84)')
@click.option('--lon', required=True, type=float, help='경도 (WGS84)')
@click.option('--radius', default=500, type=int, help='검색 반경(미터, 기본 500)')
@click.option('--limit', default=20, type=int, help='결과 개수 (1~50, 기본 20)')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
def seoul_bike_nearby(lat, lon, radius, limit, as_json):
    """좌표 주변의 따릉이 대여소 목록을 조회합니다."""
    radius = max(50, min(radius, 2000))
    limit = max(1, min(limit, 50))
    params = {"lat": lat, "lon": lon, "radius": radius, "limit": limit}
    resp = safe_proxy_get("seoul-bike", "/v1/seoul-bike/nearby", params)
    emit(resp, as_json=as_json)


@seoul_bike.command(name='info', help='대여소 상세 정보 조회')
@click.option('--station-id', required=True, help='대여소 ID')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
def seoul_bike_info(station_id, as_json):
    """특정 대여소의 상세 정보(주소, 거치대 수 등)를 조회합니다."""
    resp = safe_proxy_get("seoul-bike", "/v1/seoul-bike/info", {"stationId": station_id})
    emit(resp, as_json=as_json)


@seoul_bike.command(name='availability', help='좌표 주변 잔여 자전거 수 조회')
@click.option('--lat', required=True, type=float, help='위도 (WGS84)')
@click.option('--lon', required=True, type=float, help='경도 (WGS84)')
@click.option('--radius', default=500, type=int, help='검색 반경(미터, 기본 500)')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
def seoul_bike_availability(lat, lon, radius, as_json):
    """좌표 주변 대여소들의 잔여 자전거 수를 조회합니다."""
    radius = max(50, min(radius, 2000))
    params = {"lat": lat, "lon": lon, "radius": radius}
    resp = safe_proxy_get("seoul-bike", "/v1/seoul-bike/availability", params)
    emit(resp, as_json=as_json)
