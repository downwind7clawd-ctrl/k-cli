"""생활/편의 스킬 — 주유소, 쓰레기, 주차장, 도서관, 급식, 의약품, 식품."""

import asyncio
import click

from cli_anything.k_skill.proxy import safe_proxy_get
from cli_anything.k_skill.output import emit, error_response
from cli_anything.k_skill.runner import run_mcp, run_npm, run_script


@click.group()
def cli():
    """생활/편의 (주유소, 쓰레기, 주차장, 도서관, 급식, 의약품, 식품안전).
    
    모든 명령은 k-skill-proxy를 경유하며 별도 API 키 불필요.
    """
    pass


@cli.command(name='cheap-gas-nearby', help='최저가 주유소 조회 (cheap-gas-nearby)')
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
      k-skill life gas --lat 37.5665 --lon 126.9780
      k-skill life gas --lat 37.5665 --lon 126.9780 --product D047 --radius 2000 -j
    """
    params = {
        "lat": lat, "lon": lon,
        "radius": min(max(radius, 100), 5000),
        "prodcd": prodcd,
    }
    resp = safe_proxy_get("cheap-gas-nearby", "/v1/opinet/around", params)
    emit(resp, as_json=as_json)


cli.add_command(gas, name='gas')


@cli.command(name='household-waste-info', help='분리배출/생활폐기물 안내 (household-waste-info)')
@click.argument("region")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def waste(region, as_json):
    """쓰레기 분리수거 정보.
    
    시군구명으로 생활쓰레기 배출 요일/시간/장소를 조회합니다.
    
    예시:
      k-skill life waste "강남구"
      k-skill life waste "수원시 영통구" -j
    """
    if not region or not region.strip():
        emit(error_response("household-waste-info", "INVALID_INPUT", "시군구명을 입력하세요"),
             as_json=as_json)
        return
    params = {
        "cond[SGG_NM::LIKE]": region,
        "pageNo": 1,
        "numOfRows": 100,
    }
    resp = safe_proxy_get("household-waste-info", "/v1/household-waste/info", params)
    emit(resp, as_json=as_json)


cli.add_command(waste, name='waste')


@cli.command()
@click.option("--lat", type=float, required=True, help="위도")
@click.option("--lon", type=float, required=True, help="경도")
@click.option("--radius", default=1000, help="반경(m, 기본 1000)")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def parking(lat, lon, radius, as_json):
    """공영주차장 검색.
    
    좌표 기준으로 근처 공영주차장을 검색합니다.
    
    예시:
      k-skill life parking --lat 37.5665 --lon 126.9780
      k-skill life parking --lat 37.5665 --lon 126.9780 --radius 500 -j
    """
    params = {"lat": lat, "lon": lon, "radius": min(max(radius, 100), 5000)}
    resp = safe_proxy_get("parking-lot", "/v1/parking-lots/search", params)
    emit(resp, as_json=as_json)


@cli.command(name='library-book-search', help='도서관 도서/정보 조회 (library-book-search)')
@click.argument("keyword")
@click.option("--page", default=1, help="페이지 (기본 1)")
@click.option("--page-size", "page_size", default=10, help="페이지당 건수 (기본 10)")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def library(keyword, page, page_size, as_json):
    """도서관 도서 검색.
    
    키워드로 도서관 정보나루 도서를 검색합니다.
    
    예시:
      k-skill life library "역사"
      k-skill life library "파이썬 프로그래밍" --page-size 20 -j
    """
    if not keyword or not keyword.strip():
        emit(error_response("library-book-search", "INVALID_INPUT", "검색 키워드를 입력하세요"),
             as_json=as_json)
        return
    params = {"keyword": keyword, "pageNo": max(page, 1), "pageSize": min(max(page_size, 1), 100)}
    resp = safe_proxy_get("library-book-search", "/v1/data4library/book-search", params)
    emit(resp, as_json=as_json)


cli.add_command(library, name='library')


@cli.command(name='k-schoollunch-menu', help='학교 급식 메뉴 조회 (k-schoollunch-menu)')
@click.option("--edu-office", required=True, help="교육청명 (예: 서울특별시교육청)")
@click.option("--school", "school_name", required=True, help="학교명")
@click.option("--date", "meal_date", help="급식일자 (YYYYMMDD, 기본: 오늘)")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def lunch(edu_office, school_name, meal_date, as_json):
    """학교 급식 식단.
    
    교육청명과 학교명으로 급식 식단을 조회합니다 (2단계: 학교검색→식단조회).
    
    예시:
      k-skill life lunch --edu-office "서울특별시교육청" --school "미래초등학교"
      k-skill life lunch --edu-office "서울특별시교육청" --school "미래초등학교" --date 20260521 -j
    """
    # Step 1: Search school
    school_resp = safe_proxy_get("k-schoollunch-menu", "/v1/neis/school-search", {"educationOffice": edu_office, "schoolName": school_name})
    if school_resp.get("status") == "error":
        emit(school_resp, as_json=as_json)
        return

    school_data = school_resp.get("data", {})
    rows = school_data.get("schoolInfo", school_data.get("rows", school_data.get("data", [])))
    if isinstance(rows, dict):
        rows = rows.get("row", rows.get("items", []))

    if not rows or (isinstance(rows, list) and len(rows) == 0):
        emit(error_response("k-schoollunch-menu", "INVALID_INPUT",
                            f"학교를 찾을 수 없습니다: {edu_office} {school_name}"),
             as_json=as_json)
        return

    school = rows[0] if isinstance(rows, list) else rows
    atpt_code = school.get("ATPT_OFCDC_SC_CODE", school.get("atpt_ofcdc_sc_code", ""))
    sd_code = school.get("SD_SCHUL_CODE", school.get("sd_schul_code", ""))

    if not atpt_code or not sd_code:
        emit(error_response("k-schoollunch-menu", "UNKNOWN", "학교 코드를 추출할 수 없습니다"),
             as_json=as_json)
        return

    # Step 2: Fetch meal
    meal_params = {"ATPT_OFCDC_SC_CODE": atpt_code, "SD_SCHUL_CODE": sd_code}
    if meal_date:
        meal_params["MLSV_YMD"] = meal_date
    try:
        resp = safe_proxy_get("k-schoollunch-menu", "/v1/neis/school-meal", meal_params)
        emit(resp, as_json=as_json)
    except Exception as e:
        emit(error_response("k-schoollunch-menu", "NETWORK_ERROR",
                            f"급식 정보 조회 중 오류 발생: {str(e)}"),
             as_json=as_json)


cli.add_command(lunch, name='lunch')


@cli.command()
@click.argument("drug_name")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def drug(drug_name, as_json):
    """의약품 안전 조회.
    
    약품명으로 식약처 e약은요 정보를 조회합니다.
    
    예시:
      k-skill life drug "타이레놀"
      k-skill life drug "판콜" -j
    """
    if not drug_name or not drug_name.strip():
        emit(error_response("mfds-drug", "INVALID_INPUT", "약품명을 입력하세요"),
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
      k-skill life food "차전자피"
      k-skill life food "홍삼" -j
    """
    if not query or not query.strip():
        emit(error_response("mfds-food", "INVALID_INPUT", "검색어를 입력하세요"),
             as_json=as_json)
        return
    params = {"searchText": query}
    resp = safe_proxy_get("mfds-food", "/v1/mfds/food-safety/search", params)
    emit(resp, as_json=as_json)


@cli.command(name="korean-holiday-calendar", help="한국 공휴일 달력 조회 (korean-holiday-calendar)")
@click.option("--year", required=True, type=int, help="연도(YYYY)")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def holiday(year, as_json):
    """한국 공휴일 조회 (korean-holiday-calendar)."""
    resp = safe_proxy_get("korean-holiday-calendar", "/v1/korean-holiday/calendar", {"year": year})
    emit(resp, as_json=as_json)


cli.add_command(holiday, name='holiday')


@cli.command(name='plastic-surgery', help='강남유니 성형외과 정보 검색')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def plastic_surgery(query, as_json, timeout):
    """강남유니 성형외과."""
    args = [query] if query else []
    result = asyncio.run(run_npm('gangnamunni-clinic-search', args, npx=True, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='public-restroom', help='근처 공중화장실 검색')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def public_restroom(query, as_json, timeout):
    """공중화장실."""
    args = [query] if query else []
    result = asyncio.run(run_npm('public-restroom-nearby', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='emergency-room', help='근처 응급실 실시간 병상 조회')
@click.option('--limit', default=3, type=int, help='결과 개수 (기본 3, 최대 10)')
@click.option('--radius', default=5, type=int, help='검색 반경(km, 기본 5, 최대 20)')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=True)
def emergency_room(query, limit, radius, as_json, timeout):
    """응급실 병상 조회.

    위치 기준 근처 응급실과 E-Gen 운영 플래그를 조회합니다.

    예시:
      k-skill life emergency-room "광화문"
      k-skill life emergency-room "강남역" --limit 5 --radius 10 -j
    """
    args = [query, f"--limit", str(min(max(limit, 1), 10)), f"--radius", str(min(max(radius, 1), 20))]
    result = asyncio.run(run_npm('emergency-room-beds', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='election', help='지방선거 후보자 검색')
@click.option('--election', 'election_type', help='선거 종류 (시도지사/기초단체장/광역의원/기초의원/광역비례/기초비례/교육감)')
@click.option('--date', 'election_date', help='선거일 (YYYY, YYYYMMDD, YYYY.MM.DD)')
@click.option('--region', 'election_region', help='지역 필터')
@click.option('--limit', default=10, type=int, help='결과 개수 (기본 10, 최대 100)')
@click.option('--all', 'include_all', is_flag=True, help='지방선거 외 전체 선거 결과 포함')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=True)
def election(query, election_type, election_date, election_region, limit, include_all, as_json, timeout):
    """지방선거 후보자 검색.

    중앙선거관리위원회 공개 통합검색으로 후보자 정보를 조회합니다.

    예시:
      k-skill life election "오세훈" --election 시도지사
      k-skill life election "김동연" --date 2014 --region 동작 -j
    """
    args = [query]
    if election_type:
        args.extend(["--election", election_type])
    if election_date:
        args.extend(["--date", election_date])
    if election_region:
        args.extend(["--region", election_region])
    args.extend(["--limit", str(min(max(limit, 1), 100))])
    if include_all:
        args.append("--all")
    result = asyncio.run(run_npm('local-election-candidate-search', args, npx=True, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='hipass', help='하이패스 통행료 영수증 조회')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def hipass(query, as_json, timeout):
    """하이패스 영수증."""
    args = [query] if query else []
    result = asyncio.run(run_npm('hipass-receipt', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='donation', help='기부처 검색')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def donation(query, as_json, timeout):
    """기부처."""
    args = [query] if query else []
    result = asyncio.run(run_npm('donation-place-search', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='kakao-bar', help='주변 카카오 맥주/술집 검색')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.option('--query', help='지역명/키워드')
def kakao_bar(query, as_json, timeout):
    """근처 술집."""
    args = [query] if query else []
    result = asyncio.run(run_npm('kakao-bar-nearby', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='daangn-jobs', help='당근마켓 알바 구인 검색')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def daangn_jobs(query, as_json, timeout):
    """당근알바."""
    args = [query] if query else []
    result = asyncio.run(run_script('daangn_jobs.py', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='zipcode', help='우편번호 검색')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def zipcode(query, as_json, timeout):
    """우편번호."""
    args = [query] if query else []
    result = asyncio.run(run_script('zipcode_search.py', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='slang', help='신조어/유행어 생성 및 검색')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def slang(query, as_json, timeout):
    """신조어/유행어."""
    args = [query] if query else []
    result = asyncio.run(run_script('slang_search.py', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='kakaotalk', help='카카오톡 macOS 자동화')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def kakaotalk(query, as_json, timeout):
    """카카오톡 자동화."""
    args = [query] if query else []
    result = asyncio.run(run_script('kakaotalk_mac.py', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='seoul-density', help='서울 실시간 인구밀도 조회')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def seoul_density(query, as_json, timeout):
    """서울 인구밀도."""
    args = [query] if query else []
    result = asyncio.run(run_script('seoul_density.py', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='corp-registration', help='법인설립 서류 작성 자동화')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def corp_registration(query, as_json, timeout):
    """법인설립 상담."""
    args = [query] if query else []
    result = asyncio.run(run_script('fill_official_hwp.py', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='catchtable', help='캐치테이블 예약 자동 캡처')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def catchtable(query, as_json, timeout):
    """캐치테이블 캡처."""
    result = asyncio.run(run_mcp('catchtable-sniper', server_url='local://chrome-mcp', tool_name='예약', timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='cleaner', help='k-skill 사용량 정리')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def cleaner(query, as_json, timeout):
    """스킬 정리."""
    args = [query] if query else []
    result = asyncio.run(run_script('k_skill_cleaner.py', args, timeout=timeout))
    emit(result, as_json=as_json)


# ── 인허가 영업상태 조회 ──────────────────────────────────────

@cli.command(name='localdata-biz', help='지방행정 인허가 영업상태 조회')
@click.option('--name', required=True, help='상호/사업장명')
@click.option('--region', required=True, help='시군구 (예: 서울종로구, 제주제주시)')
@click.option('--industry', multiple=True, help='업종 (기본: 음식점+휴게음식점+숙박업)')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=60, type=int, help='타임아웃(초)')
def localdata_biz(name, region, industry, as_json, timeout):
    """인허가 영업상태 조회.

    지방행정 인허가데이터로 동네 사업장의 영업/휴업/폐업 상태를 조회합니다.

    예시:
      k-skill life localdata-biz --name "호텔샬롬" --region 제주제주시
      k-skill life localdata-biz --name "카페" --region 서울종로구 --industry 음식점 -j
    """
    args = ["--name", name, "--region", region]
    for ind in industry:
        args.extend(["--industry", ind])
    result = asyncio.run(run_script("localdata_business_status.py", args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='lovebug-report', help='lovebug.com 모기 지수/제보 검색')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.option('--query', help='지역명/키워드')
@click.argument('action', required=False)
def lovebug_report(action, query, as_json, timeout):
    """러브버그 출몰 지수/제보 검색.

    예시:
      k-skill life lovebug-report search --query 중랑
      k-skill life lovebug-report list --query 강남 -j
    """
    args = []
    if action:
        args.append(action)
    if query:
        args += ['--query', query]
    result = asyncio.run(run_npm('lovebug-report', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='yebigun-training', help='예비군 훈련일정/메뉴 조회 (playwright 필요)')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=60, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def yebigun_training(query, as_json, timeout):
    """예비군 훈련정보 조회.

    예시:
      k-skill life yebigun-training training-info
      k-skill life yebigun-training view -j
    """
    args = [query] if query else []
    result = asyncio.run(run_npm('yebigun-training', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.group(name="nhis-care-checkup-search", help="국민건강보험 건강검진/보험료 조회 (nhis-care-checkup-search)")
def nhis():
    """국민건강보험 조회 (nhis-care-checkup-search)."""
    pass


cli.add_command(nhis, name='nhis')


@nhis.command(name="checkup")
@click.option("--operation", required=True, help="조회 작업 (예: list)")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def nhis_checkup(operation, as_json):
    """건강검진 정보 조회."""
    resp = safe_proxy_get("nhis-care-checkup-search", "/v1/nhis/checkup/%s" % operation, {})
    emit(resp, as_json=as_json)


@nhis.command(name="long-term-care")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def nhis_ltc(as_json):
    """장기요양 정보 조회."""
    resp = safe_proxy_get("nhis-care-checkup-search", "/v1/nhis/long-term-care", {})
    emit(resp, as_json=as_json)


@cli.group(name="assembly")
def assembly():
    """열린국회 의안/표결 조회 (assembly-bill-vote-search)."""
    pass


@assembly.command(name="bills")
@click.option("--query", help="의안 검색어")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def asm_bills(query, as_json):
    """의안 검색."""
    params = {"query": query} if query else {}
    resp = safe_proxy_get("assembly-bill-vote-search", "/v1/assembly/bills", params)
    emit(resp, as_json=as_json)


@assembly.command(name="votes")
@click.option("--bill-id", required=True, help="의안 ID")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def asm_votes(bill_id, as_json):
    """본회의 표결정보 조회."""
    resp = safe_proxy_get("assembly-bill-vote-search", "/v1/assembly/votes", {"billId": bill_id})
    emit(resp, as_json=as_json)


@assembly.command(name="bill-detail")
@click.option("--bill-id", required=True, help="의안 ID")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def asm_bill_detail(bill_id, as_json):
    """의안 상세 조회."""
    resp = safe_proxy_get("assembly-bill-vote-search", "/v1/assembly/bill-detail", {"billId": bill_id})
    emit(resp, as_json=as_json)

