"""지도/길찾기 스킬 — Kakao Map, Naver Map."""

import click

from cli_anything.k_skill.proxy import safe_proxy_get
from cli_anything.k_skill.output import emit


@click.group()
def cli():
    """지도/길찾기 (Kakao, Naver).
    
    장소 검색 및 자동차 길찾기 기능을 제공합니다.
    """
    pass


@cli.command(name='kakao-search')
@click.argument('keyword')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
def kakao_search(keyword, as_json):
    """카카오맵 키워드 장소 검색."""
    if not keyword or not keyword.strip():
        emit({"skill": "kakao-map", "status": "error",
              "error": {"code": "INVALID_INPUT", "message": "검색어를 입력하세요"}},
             as_json=as_json)
        return
    params = {"query": keyword}
    resp = safe_proxy_get("kakao-map", "/v1/kakao-map/search/keyword", params)
    emit(resp, as_json=as_json)


@cli.command(name='kakao-directions')
@click.option('--origin', required=True, help='출발지 좌표 (경도,위도. 예: 127.11015314141542,37.39472714688412)')
@click.option('--destination', required=True, help='도착지 좌표 (경도,위도)')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
def kakao_directions(origin, destination, as_json):
    """카카오 모빌리티 자동차 길찾기."""
    params = {"origin": origin, "destination": destination}
    resp = safe_proxy_get("kakao-map", "/v1/kakao-mobility/directions", params)
    emit(resp, as_json=as_json)


@cli.command(name='naver-directions')
@click.option('--start', required=True, help='출발지 좌표 (경도,위도)')
@click.option('--goal', required=True, help='도착지 좌표 (경도,위도)')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
def naver_directions(start, goal, as_json):
    """네이버 지도 자동차 길찾기."""
    params = {"start": start, "goal": goal}
    resp = safe_proxy_get("naver-map-route", "/v1/naver-map/directions", params)
    emit(resp, as_json=as_json)


@cli.command(name='naver-geocode')
@click.argument('query')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
def naver_geocode(query, as_json):
    """네이버 지도 주소 -> 좌표 변환 (Geocoding)."""
    if not query or not query.strip():
        emit({"skill": "naver-map-route", "status": "error",
              "error": {"code": "INVALID_INPUT", "message": "주소를 입력하세요"}},
             as_json=as_json)
        return
    params = {"query": query}
    resp = safe_proxy_get("naver-map-route", "/v1/naver-map/geocode", params)
    emit(resp, as_json=as_json)
