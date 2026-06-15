#!/usr/bin/env python3
"""지방행정 인허가 영업상태 조회.

지방행정 인허가데이터(LOCALDATA)로 동네 사업장의 영업/휴업/폐업 상태를 조회합니다.
인증키 불필요.

사용법:
    python3 localdata_business_status.py --name "상호" --region "시군구" --industry "업종"
"""

import argparse
import csv
import io
import json
import os
import sys
import urllib.request
from pathlib import Path
from datetime import datetime, timedelta


# 업종 매핑 (한글명 -> 슬러그)
INDUSTRY_MAP = {
    "음식점": "rest",
    "휴게음식점": "snack",
    "숙박업": "hotel",
    "일반숙박": "hotel",
    "의원": "hospital",
    "병원": "hospital",
    "약국": "pharmacy",
    "미용실": "beauty",
    "학원": "academy",
    "체육시설": "sports",
    "유흥주점": "entertainment",
    "단란주점": "entertainment",
    "레저업": "leisure",
    "서비스업": "service",
    "도매업": "wholesale",
    "소매업": "retail",
    "운수업": "transport",
    "건설업": "construction",
    "제조업": "manufacturing",
    "부동산": "realestate",
}

# 기본 업종
DEFAULT_INDUSTRIES = ["rest", "snack", "hotel"]

# 시군구 코드 매핑 (간략화)
REGION_MAP = {
    "서울종로구": "11110",
    "서울중구": "11140",
    "서울용산구": "11170",
    "서울성동구": "11200",
    "서울광진구": "11215",
    "서울동대문구": "11230",
    "서울중랑구": "11260",
    "서울성북구": "11290",
    "서울강북구": "11305",
    "서울도봉구": "11320",
    "서울노원구": "11350",
    "서울은평구": "11380",
    "서울서대문구": "11410",
    "서울마포구": "11440",
    "서울양천구": "11470",
    "서울강서구": "11500",
    "서울구로구": "11530",
    "서울금천구": "11545",
    "서울영등포구": "11560",
    "서울동작구": "11590",
    "서울관악구": "11620",
    "서울서초구": "11650",
    "서울강남구": "11680",
    "서울송파구": "11710",
    "서울강동구": "11740",
    "부산중구": "26110",
    "부산서구": "26140",
    "부산동구": "26170",
    "부산영도구": "26200",
    "부산부산진구": "26230",
    "부산동래구": "26260",
    "부산남구": "26290",
    "부산북구": "26320",
    "부산해운대구": "26350",
    "부산사하구": "26380",
    "부산금정구": "26410",
    "부산강서구": "26440",
    "부산연제구": "26470",
    "부산수영구": "26500",
    "부산사상구": "26530",
    "부산기장군": "26710",
    "대구중구": "27110",
    "대구동구": "27140",
    "대구서구": "27170",
    "대구남구": "27200",
    "대구북구": "27230",
    "대구수성구": "27260",
    "대구달서구": "27290",
    "대구달성군": "27710",
    "인천중구": "28110",
    "인천동구": "28140",
    "인천남동구": "28237",
    "인천미추홀구": "28177",
    "인천연수구": "28200",
    "인천부평구": "28245",
    "인천계양구": "28265",
    "인천서구": "28270",
    "인천강화군": "28710",
    "인천옹진군": "28720",
    "광주동구": "29110",
    "광주서구": "29140",
    "광주남구": "29155",
    "광주북구": "29170",
    "광주광산구": "29200",
    "대전동구": "30110",
    "대전서구": "30140",
    "대전유성구": "30200",
    "대전대덕구": "30230",
    "울산중구": "31110",
    "울산남구": "31140",
    "울산동구": "31170",
    "울산북구": "31200",
    "울산울주군": "31710",
    "세종": "36110",
    "제주제주시": "50110",
    "제주시": "50110",
    "제주서귀포시": "50130",
    "서귀포시": "50130",
    "경기수원시": "41110",
    "경기고양시": "41280",
    "경기도양주시": "41800",
    "경기용인시": "41460",
    "경기성남시": "41130",
    "경기부천시": "41190",
    "경기안양시": "41210",
    "경기남양주시": "41360",
    "경기화성시": "41220",
    "경기김포시": "41570",
    "경기파주시": "41480",
    "강원춘천시": "42110",
    "강원원주시": "42130",
    "충북청주시": "43110",
    "충남천안시": "44150",
    "전북전주시": "45110",
    "전남목포시": "46110",
    "경북포항시": "47130",
    "경남창원시": "48120",
}


def get_industry_slugs(industry: str) -> list:
    """한글 업종명을 슬러그로 변환합니다."""
    if not industry:
        return DEFAULT_INDUSTRIES

    slugs = []
    for ind in industry.split(","):
        ind = ind.strip()
        if ind in INDUSTRY_MAP:
            slugs.append(INDUSTRY_MAP[ind])
        elif ind.isalpha():
            slugs.append(ind)
        else:
            slugs.append(INDUSTRY_MAP.get(ind, ind))
    return slugs if slugs else DEFAULT_INDUSTRIES


def get_org_code(region: str) -> str:
    """지역명을 기관 코드로 변환합니다."""
    if region in REGION_MAP:
        return REGION_MAP[region]

    # 부분 매칭 시도
    for key, code in REGION_MAP.items():
        if region in key or key in region:
            return code

    return region


def download_csv(slug: str, org_code: str, cache_dir: Path) -> list:
    """CSV 파일을 다운로드하고 파싱합니다."""
    cache_file = cache_dir / f"{slug}_{org_code}.csv"
    cache_ttl = timedelta(days=1)

    # 캐시 확인
    if cache_file.exists():
        mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
        if datetime.now() - mtime < cache_ttl:
            with open(cache_file, "r", encoding="cp949", errors="replace") as f:
                reader = csv.DictReader(f)
                return list(reader)

    # 다운로드
    url = f"https://file.localdata.go.kr/file/download/{slug}/info?orgCode={org_code}"
    try:
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "Mozilla/5.0")
        req.add_header("Referer", "https://www.localdata.go.kr/")

        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()

        # 캐시 저장
        cache_dir.mkdir(parents=True, exist_ok=True)
        with open(cache_file, "wb") as f:
            f.write(data)

        # 파싱
        text = data.decode("cp949", errors="replace")
        reader = csv.DictReader(io.StringIO(text))
        return list(reader)
    except Exception as e:
        return [{"error": str(e)}]


def search_businesses(name: str, region: str, industries: list) -> dict:
    """사업장을 검색합니다."""
    results = {
        "query": {"name": name, "region": region, "industries": industries},
        "businesses": [],
        "total_count": 0,
    }

    org_code = get_org_code(region)
    cache_dir = Path.home() / ".cache" / "k-skill" / "localdata-business-status"

    for slug in industries:
        rows = download_csv(slug, org_code, cache_dir)

        for row in rows:
            if "error" in row:
                results["download_error"] = row["error"]
                continue

            # 상호명 매칭 (부분 일치)
            biz_name = ""
            for key in ["상호", "사업장명", "업체명", "name", "bizNm"]:
                if key in row:
                    biz_name = row[key]
                    break

            if name in biz_name or biz_name in name:
                entry = {
                    "name": biz_name,
                    "industry": slug,
                    "status": "",
                    "address": "",
                    "phone": "",
                }

                # 영업상태
                for key in ["영업상태", "영업상태명", "status", "bizStts"]:
                    if key in row:
                        entry["status"] = row[key]
                        break

                # 주소
                for key in ["소재지", "주소", "address", "rdnAdr"]:
                    if key in row:
                        entry["address"] = row[key]
                        break

                # 전화번호
                for key in ["전화번호", "phone", "telNo"]:
                    if key in row:
                        entry["phone"] = row[key]
                        break

                results["businesses"].append(entry)

    results["total_count"] = len(results["businesses"])
    results["status"] = "success" if results["total_count"] > 0 else "no_results"

    return results


def main():
    parser = argparse.ArgumentParser(description="지방행정 인허가 영업상태 조회")
    parser.add_argument("--name", required=True, help="상호/사업장명")
    parser.add_argument("--region", required=True, help="시군구 (예: 서울종로구, 제주제주시)")
    parser.add_argument("--industry", action="append", help="업종 (여러 개 가능)")
    parser.add_argument("--json", "-j", action="store_true", help="JSON 출력")
    args = parser.parse_args()

    if not args.name or not args.name.strip():
        print(json.dumps({
            "skill": "localdata-business-status",
            "status": "error",
            "error": {"code": "INVALID_INPUT", "message": "상호/사업장명을 입력하세요"}
        }, ensure_ascii=False))
        sys.exit(1)

    industries = get_industry_slugs(",".join(args.industry) if args.industry else "")
    result = search_businesses(args.name.strip(), args.region.strip(), industries)
    result["skill"] = "localdata-business-status"

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
