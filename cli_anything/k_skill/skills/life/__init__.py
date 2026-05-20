"""생활/편의 스킬 — 주유소, 쓰레기, 주차장, 도서관, 급식, 의약품, 식품."""

import asyncio
import click

from cli_anything.k_skill.proxy import proxy_get, safe_proxy_get
from cli_anything.k_skill.output import emit, success_response, error_response


@click.group()
def cli():
    """생활/편의 (주유소, 쓰레기, 주차장, 도서관, 급식, 의약품, 식품안전).
    
    모든 명령은 k-skill-proxy를 경유하며 별도 API 키 불필요.
    """
    pass


@cli.command()
@click.option("--lat", type=float, required=True, help="위도 (KATEC 또는 WGS84)")
@click.option("--lon", type=float, required=True, help="경도 (KATEC 또는 WGS84)")
@click.option("--radius", default=1000, help="반경(m, 최대 5000, 기본 1000)")
@click.option("--product", "prodcd", default="B027",
              type=click.Choice(["B027", "D047", "B034", "C004", "K015"]),
              help="제품 (B027=휘발유, D047=경유, B034=고급휘발유, C004=등유, K015=LPG)")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def gas(lat, lon, radius, prodcd, as_json):
    """근처 주유소 가격 조회.
    
    좌표 기준으로 근처 주유소를 가격순으로 검색합니다.
    
    예시:
      k-cli life gas --lat 37.5665 --lon 126.9780
      k-cli life gas --lat 37.5665 --lon 126.9780 --product D047 --radius 2000 -j
    """
    params = {
        "lat": lat, "lon": lon,
        "radius": min(max(radius, 100), 5000),
        "prodcd": prodcd,
    }
    resp = safe_proxy_get("cheap-gas", "/v1/opinet/around", params)
    emit(resp, as_json=as_json)


@cli.command()
@click.argument("region")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def waste(region, as_json):
    """쓰레기 분리수거 정보.
    
    시군구명으로 생활쓰레기 배출 요일/시간/장소를 조회합니다.
    
    예시:
      k-cli life waste "강남구"
      k-cli life waste "수원시 영통구" -j
    """
    if not region or not region.strip():
        emit({"skill": "household-waste", "status": "error",
              "error": {"code": "INVALID_INPUT", "message": "시군구명을 입력하세요"}},
             as_json=as_json)
        return
    params = {
        "cond[SGG_NM::LIKE]": region,
        "pageNo": 1,
        "numOfRows": 100,
    }
    resp = safe_proxy_get("household-waste", "/v1/household-waste/info", params)
    emit(resp, as_json=as_json)


@cli.command()
@click.option("--lat", type=float, required=True, help="위도")
@click.option("--lon", type=float, required=True, help="경도")
@click.option("--radius", default=1000, help="반경(m, 기본 1000)")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def parking(lat, lon, radius, as_json):
    """공영주차장 검색.
    
    좌표 기준으로 근처 공영주차장을 검색합니다.
    
    예시:
      k-cli life parking --lat 37.5665 --lon 126.9780
      k-cli life parking --lat 37.5665 --lon 126.9780 --radius 500 -j
    """
    params = {"lat": lat, "lon": lon, "radius": min(max(radius, 100), 5000)}
    resp = safe_proxy_get("parking-lot", "/v1/parking-lots/search", params)
    emit(resp, as_json=as_json)


@cli.command()
@click.argument("keyword")
@click.option("--page", default=1, help="페이지 (기본 1)")
@click.option("--page-size", "page_size", default=10, help="페이지당 건수 (기본 10)")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def library(keyword, page, page_size, as_json):
    """도서관 도서 검색.
    
    키워드로 도서관 정보나루 도서를 검색합니다.
    
    예시:
      k-cli life library "역사"
      k-cli life library "파이썬 프로그래밍" --page-size 20 -j
    """
    if not keyword or not keyword.strip():
        emit({"skill": "library-book", "status": "error",
              "error": {"code": "INVALID_INPUT", "message": "검색 키워드를 입력하세요"}},
             as_json=as_json)
        return
    params = {"keyword": keyword, "pageNo": max(page, 1), "pageSize": min(max(page_size, 1), 100)}
    resp = safe_proxy_get("library-book", "/v1/data4library/book-search", params)
    emit(resp, as_json=as_json)


@cli.command()
@click.option("--edu-office", "edu_office", required=True, help="교육청명 (예: 서울특별시교육청)")
@click.option("--school", "school_name", required=True, help="학교명 (예: 미래초등학교)")
@click.option("--date", "meal_date", help="급식일 YYYYMMDD (기본: 오늘)")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def lunch(edu_office, school_name, meal_date, as_json):
    """학교 급식 식단.
    
    교육청명과 학교명으로 급식 식단을 조회합니다 (2단계: 학교검색→식단조회).
    
    예시:
      k-cli life lunch --edu-office "서울특별시교육청" --school "미래초등학교"
      k-cli life lunch --edu-office "서울특별시교육청" --school "미래초등학교" --date 20260521 -j
    """
    try:
        # Step 1: Search school
        school_params = {"educationOffice": edu_office, "schoolName": school_name}
        school_data, _ = asyncio.run(proxy_get("/v1/neis/school-search", school_params))

        # Extract school codes from response
        rows = school_data
        if isinstance(school_data, dict):
            rows = school_data.get("schoolInfo", school_data.get("rows", school_data.get("data", [])))
        if isinstance(rows, dict):
            rows = rows.get("row", rows.get("items", []))

        if not rows or (isinstance(rows, list) and len(rows) == 0):
            emit(error_response("school-lunch", "INVALID_INPUT",
                                f"학교를 찾을 수 없습니다: {edu_office} {school_name}"),
                 as_json=as_json)
            return

        # Pick first school
        school = rows[0] if isinstance(rows, list) else rows
        atpt_code = school.get("ATPT_OFCDC_SC_CODE", school.get("atpt_ofcdc_sc_code", ""))
        sd_code = school.get("SD_SCHUL_CODE", school.get("sd_schul_code", ""))

        if not atpt_code or not sd_code:
            emit(error_response("school-lunch", "UNKNOWN", "학교 코드를 추출할 수 없습니다"),
                 as_json=as_json)
            return

        # Step 2: Fetch meal
        meal_params = {"ATPT_OFCDC_SC_CODE": atpt_code, "SD_SCHUL_CODE": sd_code}
        if meal_date:
            meal_params["MLSV_YMD"] = meal_date
        meal_data, elapsed = asyncio.run(proxy_get("/v1/neis/school-meal", meal_params))
        resp = success_response("school-lunch", meal_data, response_time_ms=elapsed)
    except Exception as e:
        resp = error_response("school-lunch", "UNKNOWN", f"오류: {e}")

    emit(resp, as_json=as_json)


@cli.command()
@click.argument("drug_name")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def drug(drug_name, as_json):
    """의약품 안전 조회.
    
    약품명으로 식약처 e약은요 정보를 조회합니다.
    
    예시:
      k-cli life drug "타이레놀"
      k-cli life drug "판콜" -j
    """
    if not drug_name or not drug_name.strip():
        emit({"skill": "mfds-drug", "status": "error",
              "error": {"code": "INVALID_INPUT", "message": "약품명을 입력하세요"}},
             as_json=as_json)
        return
    params = {"item_name": drug_name}
    resp = safe_proxy_get("mfds-drug", "/v1/mfds/drug-safety/lookup", params)
    emit(resp, as_json=as_json)


@cli.command()
@click.argument("query")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def food(query, as_json):
    """식품 안전 조회.
    
    검색어로 식약처 건강기능식품/부적합/회수 정보를 조회합니다.
    
    예시:
      k-cli life food "차전자피"
      k-cli life food "홍삼" -j
    """
    if not query or not query.strip():
        emit({"skill": "mfds-food", "status": "error",
              "error": {"code": "INVALID_INPUT", "message": "검색어를 입력하세요"}},
             as_json=as_json)
        return
    params = {"searchText": query}
    resp = safe_proxy_get("mfds-food", "/v1/mfds/food-safety/search", params)
    emit(resp, as_json=as_json)
