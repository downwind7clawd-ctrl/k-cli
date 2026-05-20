"""부동산 스킬 — 실거래가/전월세 조회, LH 청약공고."""

import click

from cli_anything.k_skill.proxy import safe_proxy_get
from cli_anything.k_skill.output import emit, error_response


@click.group()
def cli():
    """부동산 (실거래가/전월세, LH 청약공고).
    
    국토교통부 실거래가 데이터와 LH 공고를 k-skill-proxy로 경유 조회.
    """
    pass


# ── 실거래가/전월세 ────────────────────────────────────────

@cli.group()
def realestate():
    """부동산 실거래가/전월세 조회."""
    pass


@realestate.command("code")
@click.argument("query")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def realestate_code(query, as_json):
    """지역코드 조회.
    
    지역명으로 법정동 코드를 검색합니다. 실거래가 조회에 필요합니다.
    
    예시:
      k-cli realestate realestate code "서울 강남구"
      k-cli realestate realestate code "마포구" -j
    """
    if not query or not query.strip():
        emit(error_response("real-estate", "INVALID_INPUT", "지역명을 입력하세요"),
             as_json=as_json)
        return
    resp = safe_proxy_get("real-estate", "/v1/real-estate/region-code", {"q": query})
    emit(resp, as_json=as_json)


@realestate.command("search")
@click.option("--lawd-cd", "lawd_cd", required=True, help="법정동코드 (5자리, code 명령으로 조회)")
@click.option("--date", "deal_ymd", required=True, help="거래년월 YYYYMM")
@click.option("--asset-type", "asset_type", default="apartment",
              type=click.Choice(["apartment", "officetel", "villa", "single-house", "commercial"]),
              help="자산유형 (기본: apartment)")
@click.option("--deal-type", "deal_type", default="trade",
              type=click.Choice(["trade", "rent"]),
              help="거래유형 (trade=매매, rent=전월세, 기본: trade)")
@click.option("--rows", "num_of_rows", default=100, help="조회 건수 (기본 100, 최대 1000)")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def realestate_search(lawd_cd, deal_ymd, asset_type, deal_type, num_of_rows, as_json):
    """실거래가/전월세 조회.
    
    법정동코드와 거래년월로 실거래가 데이터를 조회합니다.
    
    예시:
      k-cli realestate realestate search --lawd-cd 11680 --date 202403
      k-cli realestate realestate search --lawd-cd 11680 --date 202403 --asset-type officetel --deal-type rent -j
    """
    lawd_cd_clean = lawd_cd.strip()
    deal_ymd_clean = deal_ymd.strip()
    if len(lawd_cd_clean) != 5 or not lawd_cd_clean.isdigit():
        emit(error_response("real-estate", "INVALID_INPUT",
                             "법정동코드는 5자리 숫자입니다 (code 명령으로 조회하세요)"),
             as_json=as_json)
        return
    if len(deal_ymd_clean) != 6 or not deal_ymd_clean.isdigit():
        emit(error_response("real-estate", "INVALID_INPUT", "거래년월은 YYYYMM 형식입니다"),
             as_json=as_json)
        return
    path = f"/v1/real-estate/{asset_type}/{deal_type}"
    params = {
        "lawd_cd": lawd_cd_clean,
        "deal_ymd": deal_ymd_clean,
        "num_of_rows": min(max(num_of_rows, 1), 1000),
    }
    resp = safe_proxy_get("real-estate", path, params)
    emit(resp, as_json=as_json)


# ── LH 청약공고 ───────────────────────────────────────────

@cli.group()
def lh():
    """LH 청약 공고문 조회."""
    pass


@lh.command("search")
@click.option("--status", "pan_ss", help="공고상태 (공고중/접수중/접수마감/당첨자발표/추정공고)")
@click.option("--region", "cnp_cd_nm", help="지역명 (예: 서울특별시, 부산광역시)")
@click.option("--keyword", "pan_nm", help="공고명 검색어")
@click.option("--category", "upp_ais_tp_cd", default="",
              type=click.Choice(["", "01", "05", "06", "13", "22"]),
              help="대분류 (01=토지, 05=분양주택, 06=임대주택, 13=주거복지, 22=상가)")
@click.option("--start-date", "pan_nt_st_dt", help="공고게시일 시작 YYYY-MM-DD")
@click.option("--end-date", "clsg_dt", help="접수마감일 종료 YYYY-MM-DD")
@click.option("--page", default=1, help="페이지 (기본 1)")
@click.option("--page-size", "page_size", default=50, help="페이지당 건수 (기본 50, 최대 1000)")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def lh_search(pan_ss, cnp_cd_nm, pan_nm, upp_ais_tp_cd, pan_nt_st_dt, clsg_dt, page, page_size, as_json):
    """LH 청약 공고 목록 검색.
    
    지역/상태/키워드로 LH 공고를 검색합니다.
    
    예시:
      k-cli realestate lh search --status "공고중" --region "서울특별시"
      k-cli realestate lh search --keyword "행복주택" --category 06 -j
    """
    params = {"page": max(page, 1), "pageSize": min(max(page_size, 1), 1000)}
    if pan_ss:
        params["panSs"] = pan_ss
    if cnp_cd_nm:
        params["cnpCdNm"] = cnp_cd_nm
    if pan_nm:
        params["panNm"] = pan_nm
    if upp_ais_tp_cd:
        params["uppAisTpCd"] = upp_ais_tp_cd
    if pan_nt_st_dt:
        params["panNtStDt"] = pan_nt_st_dt
    if clsg_dt:
        params["clsgDt"] = clsg_dt
    resp = safe_proxy_get("lh-notice", "/v1/lh-notice/search", params)
    emit(resp, as_json=as_json)


@lh.command("detail")
@click.option("--pan-id", "pan_id", required=True, help="공고ID (목록 응답의 pan_id)")
@click.option("--ccr-code", "ccr_cnnt_sys_ds_cd", required=True, help="연계시스템코드 (목록 응답의 ccr_cnnt_sys_ds_cd)")
@click.option("--spl-code", "spl_inf_tp_cd", required=True, help="공급정보유형코드 (목록 응답의 spl_inf_tp_cd)")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def lh_detail(pan_id, ccr_cnnt_sys_ds_cd, spl_inf_tp_cd, as_json):
    """LH 청약 공고 상세 조회.
    
    공고ID로 상세 정보를 조회합니다. search 응답의 ID 값을 그대로 사용하세요.
    
    예시:
      k-cli realestate lh detail --pan-id 2015122300019828 --ccr-code ... --spl-code ... -j
    """
    params = {
        "panId": pan_id,
        "ccrCnntSysDsCd": ccr_cnnt_sys_ds_cd,
        "splInfTpCd": spl_inf_tp_cd,
    }
    resp = safe_proxy_get("lh-notice", "/v1/lh-notice/detail", params)
    emit(resp, as_json=as_json)
