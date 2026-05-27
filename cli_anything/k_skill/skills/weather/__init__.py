"""날씨/환경 조회 스킬 — 기상청 예보, 미세먼지, 한강 수위."""

import click

from cli_anything.k_skill.proxy import safe_proxy_get
from cli_anything.k_skill.output import emit


@click.group()
def cli():
    """날씨/환경 조회 (기상청, 미세먼지, 한강수위).

    모든 명령은 k-skill-proxy를 경유하며 별도 API 키 불필요.
    """
    pass


@cli.command(name='forecast')
@click.option("--lat", type=float, required=True, help="위도 (WGS84)")
@click.option("--lon", type=float, required=True, help="경도 (WGS84)")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def forecast(lat, lon, as_json):
    """한국 날씨 (기상청 단기예보).

    위도/경도로 기상청 단기예보를 조회합니다.
    주요 도시 좌표: 서울(37.5665,126.9780) 부산(35.1796,129.0756) 대구(35.8714,128.6014)

    예시:
      k-skill weather forecast --lat 37.5665 --lon 126.9780
      k-skill weather forecast --lat 35.1796 --lon 129.0756 -j
    """
    params = {"lat": lat, "lon": lon}
    resp = safe_proxy_get("korea-weather", "/v1/korea-weather/forecast", params)
    emit(resp, as_json=as_json)


@cli.command()
@click.argument("region", required=False)
@click.option("--station", "station_name", help="측정소명 (정확한 이름)")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def dust(region, station_name, as_json):
    """미세먼지/초미세먼지 조회.

    지역명 또는 측정소명으로 PM10/PM2.5를 조회합니다.

    예시:
      k-skill weather dust "서울 강남구"
      k-skill weather dust --station "강남구" -j
    """
    params = {}
    if region:
        params["regionHint"] = region
    if station_name:
        params["stationName"] = station_name
    if not params:
        emit({"skill": "fine-dust", "status": "error",
              "error": {"code": "INVALID_INPUT", "message": "지역명 또는 측정소명을 입력하세요"}},
             as_json=as_json)
        return
    resp = safe_proxy_get("fine-dust", "/v1/fine-dust/report", params)
    emit(resp, as_json=as_json)


@cli.command()
@click.argument("query", required=False)
@click.option("--code", "station_code", help="관측소코드 (예: 1018683)")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def han_river(query, station_code, as_json):
    """한강 수위/유량 조회.

    관측소명(교량명) 또는 관측소코드로 현재 수위를 조회합니다.

    예시:
      k-skill weather han-river "한강대교"
      k-skill weather han-river --code 1018683 -j
    """
    params = {}
    if query:
        params["stationName"] = query
    if station_code:
        params["stationCode"] = station_code
    if not params:
        emit({"skill": "han-river", "status": "error",
              "error": {"code": "INVALID_INPUT", "message": "관측소명 또는 관측소코드를 입력하세요"}},
             as_json=as_json)
        return
    resp = safe_proxy_get("han-river", "/v1/han-river/water-level", params)
    emit(resp, as_json=as_json)
