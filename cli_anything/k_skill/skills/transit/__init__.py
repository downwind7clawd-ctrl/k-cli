"""대중교통 스킬 — 서울 지하철 실시간 도착정보."""

import click

from cli_anything.k_skill.proxy import safe_proxy_get
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
      k-cli transit subway "강남"
      k-cli transit subway "서울역" -j
    """
    if not station_name or not station_name.strip():
        emit({"skill": "seoul-subway", "status": "error",
              "error": {"code": "INVALID_INPUT", "message": "역명을 입력하세요"}},
             as_json=as_json)
        return
    params = {"stationName": station_name}
    resp = safe_proxy_get("seoul-subway", "/v1/seoul-subway/arrival", params)
    emit(resp, as_json=as_json)
