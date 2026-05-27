"""Test map domain skills."""

import json
from unittest.mock import patch
from click.testing import CliRunner
from cli_anything.k_skill.cli import main

def test_map_commands_registered():
    """map 도메인의 명령어들이 정상적으로 등록되었는지 확인합니다."""
    runner = CliRunner()
    result = runner.invoke(main, ['map', '--help'])
    
    assert result.exit_code == 0
    assert 'kakao-search' in result.output
    assert 'kakao-directions' in result.output
    assert 'naver-directions' in result.output
    assert 'naver-geocode' in result.output


def test_kakao_search_missing_keyword():
    """kakao-search 명령어가 검색어 누락 시 에러를 반환하는지 테스트."""
    runner = CliRunner()
    result = runner.invoke(main, ['map', 'kakao-search', ' ', '-j'])
    
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["status"] == "error"
    assert data["error"]["message"] == "검색어를 입력하세요"


@patch("cli_anything.k_skill.skills.map.safe_proxy_get")
def test_kakao_search_valid(mock_proxy_get):
    """kakao-search 명령어 정상 호출 테스트."""
    mock_proxy_get.return_value = {"status": "success", "data": {"documents": []}}
    
    runner = CliRunner()
    result = runner.invoke(main, ['map', 'kakao-search', '강남역', '-j'])
    
    assert result.exit_code == 0
    mock_proxy_get.assert_called_once_with(
        "kakao-map", 
        "/v1/kakao-map/search/keyword", 
        {"query": "강남역"}
    )
    
    data = json.loads(result.output)
    assert data["status"] == "success"


@patch("cli_anything.k_skill.skills.map.safe_proxy_get")
def test_kakao_directions_valid(mock_proxy_get):
    """kakao-directions 명령어 파라미터 바인딩 테스트."""
    mock_proxy_get.return_value = {"status": "success", "data": {}}
    
    runner = CliRunner()
    result = runner.invoke(main, ['map', 'kakao-directions', '--origin', '127.1,37.1', '--destination', '127.2,37.2', '-j'])
    
    assert result.exit_code == 0
    mock_proxy_get.assert_called_once_with(
        "kakao-map",
        "/v1/kakao-mobility/directions",
        {"origin": "127.1,37.1", "destination": "127.2,37.2"}
    )


@patch("cli_anything.k_skill.skills.map.safe_proxy_get")
def test_naver_directions_valid(mock_proxy_get):
    """naver-directions 명령어 파라미터 바인딩 테스트."""
    mock_proxy_get.return_value = {"status": "success", "data": {}}
    
    runner = CliRunner()
    result = runner.invoke(main, ['map', 'naver-directions', '--start', '127.1,37.1', '--goal', '127.2,37.2', '-j'])
    
    assert result.exit_code == 0
    mock_proxy_get.assert_called_once_with(
        "naver-map-route",
        "/v1/naver-map/directions",
        {"start": "127.1,37.1", "goal": "127.2,37.2"}
    )


def test_naver_geocode_missing_query():
    """naver-geocode 명령어가 쿼리 누락 시 에러를 반환하는지 테스트."""
    runner = CliRunner()
    result = runner.invoke(main, ['map', 'naver-geocode', ' ', '-j'])
    
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["status"] == "error"
    assert data["error"]["message"] == "주소를 입력하세요"
