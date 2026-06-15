"""입력 검증 및 유틸리티 함수 모듈.

스킬 전반에서 반복되는 검증 로직을 통합하여 코드 중복을 줄입니다.
"""

import os
import re
from typing import Optional, Any


def validate_nonempty(value: Any, field_name: str = "입력값") -> Optional[dict]:
    """빈 문자열/None 검증, 에러 응답 반환.

    Args:
        value: 검증할 값
        field_name: 에러 메시지에 표시할 필드명

    Returns:
        에러 응답 dict (유효한 경우 None)
    """
    from cli_anything.k_skill.output import error_response
    if value is None or (isinstance(value, str) and not value.strip()):
        return error_response("validator", "INVALID_INPUT", f"{field_name}을 입력하세요")
    return None


def clamp(value: int | float, min_val: int | float, max_val: int | float) -> int | float:
    """숫자 범위 클램핑.

    Args:
        value: 원본 값
        min_val: 최소값
        max_val: 최대값

    Returns:
        min_val ~ max_val 범위로 클램핑된 값
    """
    return max(min_val, min(value, max_val))


def build_params(**kwargs) -> dict:
    """None 값을 자동 제거한 파라미터 딕셔너리 반환.

    Example:
        >>> build_params(lat=37.5, lon=127.0, radius=None, limit=10)
        {'lat': 37.5, 'lon': 127.0, 'limit': 10}
    """
    return {k: v for k, v in kwargs.items() if v is not None}


def collect_env_vars(*keys: str) -> dict[str, str]:
    """환경변수를 안전하게 수집합니다.

    Args:
        keys: 가져올 환경변수 이름들

    Returns:
        설정된 환경변수 딕셔너리 (설정되지 않은 키는 제외)
    """
    return {k: os.environ[k] for k in keys if k in os.environ}


def clean_business_number(b_no: str) -> Optional[str]:
    """사업자등록번호 정리 (하이픈 제거, 10자리 검증).

    Args:
        b_no: 사업자등록번호 문자열

    Returns:
        정리된 10자리 숫자 문자열 (유효하지 않은 경우 None)
    """
    digits = re.sub(r"[^0-9]", "", b_no)
    if len(digits) != 10:
        return None
    return digits


def clean_date(dt_str: str) -> Optional[str]:
    """날짜 문자열 정리 (하이픈/점 제거, 8자리 검증).

    Args:
        dt_str: 날짜 문자열 (YYYYMMDD, YYYY-MM-DD, YYYY.MM.DD)

    Returns:
        정리된 8자리 숫자 문자열 (유효하지 않은 경우 None)
    """
    digits = re.sub(r"[^0-9]", "", dt_str)
    if len(digits) != 8:
        return None
    return digits
