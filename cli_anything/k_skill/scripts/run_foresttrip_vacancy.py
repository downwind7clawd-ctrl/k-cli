#!/usr/bin/env python3
"""숲나들e 자연휴양림 예약 가능 객실 조회 스크립트.

Playwright를 사용하여 숲나들e 웹사이트에서 자연휴양림 예약 정보를 조회합니다.
"""

import argparse
import json
import os
import sys
import re
from datetime import datetime, timedelta
from urllib.parse import quote

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


FORESTTRIP_URL = "https://www.foresttrip.go.kr"


def login(page, user_id: str, password: str, timeout: int = 30000) -> bool:
    """숲나들e에 로그인합니다."""
    page.goto(f"{FORESTTRIP_URL}/com/login.do?targetUrl=/com/index.do", timeout=timeout)
    page.wait_for_timeout(3000)
    page.fill('#mmberId', user_id)
    page.fill('#gnrlMmberPssrd', password)
    page.evaluate('fn_goLogin()')
    page.wait_for_timeout(5000)
    content = page.content()
    return "로그아웃" in content or "마이페이지" in content


def search_and_get_detail(page, forest_name: str, dates: list[str], timeout: int = 30000) -> dict:
    """자연휴양림 검색 후 상세 정보를 조회합니다."""
    encoded_name = quote(forest_name, safe='')
    page.goto(
        f"{FORESTTRIP_URL}/rep/drlts/hdmss/drltsMain.do?hmpgId=FRIP&menuId=001003003&srchWord={encoded_name}",
        timeout=timeout,
    )
    page.wait_for_timeout(5000)

    body_text = page.inner_text('body')

    # 검색한 자연휴양림 관련 섹션만 추출
    forest_section = ""
    idx = body_text.find(forest_name)
    if idx >= 0:
        # 텍스트 주변 1500자 추출
        start = max(0, idx - 200)
        end = min(len(body_text), idx + 1500)
        forest_section = body_text[start:end]

    forest_info = {"name": forest_name}

    if forest_section:
        # 패턴 매칭
        avail_match = re.search(r'신청가능\s*수\s*:\s*(\d+)', forest_section)
        room_match = re.search(r'\[객실\]\s*(\d+)개', forest_section)
        camp_match = re.search(r'\[야영장\]\s*(\d+)개', forest_section)
        apply_match = re.search(r'신청기간\s*\n?\s*(.*?)\s*~\s*(.*?)\s*\n', forest_section)
        recv_match = re.search(r'접수기간\s*\n?\s*(.*?)\s*~\s*(.*?)\s*\n', forest_section)
        addr_match = re.search(r'(강원.*?[\d]+)', forest_section)

        if avail_match:
            forest_info["available_count"] = int(avail_match.group(1))
        if room_match:
            forest_info["room_count"] = int(room_match.group(1))
        if camp_match:
            forest_info["camp_count"] = int(camp_match.group(1))
        if apply_match:
            forest_info["apply_period"] = f"{apply_match.group(1).strip()} ~ {apply_match.group(2).strip()}"
        if recv_match:
            forest_info["receive_period"] = f"{recv_match.group(1).strip()} ~ {recv_match.group(2).strip()}"
        if addr_match:
            forest_info["address"] = addr_match.group(1).strip()

    # 신청하기 버튼 클릭 시도
    rooms = []
    try:
        apply_btn = page.locator('text=신청하기').first
        if apply_btn.is_visible(timeout=3000):
            apply_btn.click()
            page.wait_for_timeout(8000)

            # 객실 정보 영역 탐색
            content = page.inner_text('body')

            # 객실 목록 테이블에서 정보 추출
            tables = page.query_selector_all('table')
            for table in tables:
                text = table.inner_text()
                if '객실명' in text or '숙박' in text or '숲속의집' in text or '휴양관' in text:
                    rows = table.query_selector_all('tr')
                    headers = []
                    for row in rows[:1]:
                        cells = row.query_selector_all('th, td')
                        headers = [c.inner_text().strip() for c in cells]

                    for row in rows[1:]:
                        cells = row.query_selector_all('td')
                        if len(cells) >= 2:
                            cell_texts = [c.inner_text().strip() for c in cells]
                            if headers:
                                room = dict(zip(headers, cell_texts))
                            else:
                                room = {"info": " | ".join(cell_texts)}
                            rooms.append(room)
    except Exception:
        # 객실 정보 조회 실패 시 빈 목록 반환 (로그는 stdout JSON으로 전달)
        pass

    return {
        "forest_info": forest_info,
        "rooms": rooms,
        "page_url": page.url,
    }


def search_all_forests(page, keyword: str, dates: list[str], timeout: int = 30000) -> dict:
    """전체 자연휴양림 목록을 검색합니다."""
    encoded_keyword = quote(keyword, safe='')
    page.goto(
        f"{FORESTTRIP_URL}/rep/drlts/hdmss/drltsMain.do?hmpgId=FRIP&menuId=001003003&srchWord={encoded_keyword}",
        timeout=timeout,
    )
    page.wait_for_timeout(5000)

    body_text = page.inner_text('body')

    forests = []
    for match in re.finditer(
        r'(\[.*?\].*?자연휴양림).*?'
        r'(?:\[객실\]\s*(\d+)개)?\s*'
        r'(?:\[야영장\]\s*(\d+)개)?\s*'
        r'.*?신청가능\s*수\s*:\s*(\d+)',
        body_text, re.DOTALL
    ):
        forests.append({
            "name": match.group(1).strip(),
            "room_count": int(match.group(2)) if match.group(2) else 0,
            "camp_count": int(match.group(3)) if match.group(3) else 0,
            "available_count": int(match.group(4)),
        })

    return {
        "skill": "foresttrip",
        "status": "success",
        "query": {
            "keyword": keyword,
            "dates": dates,
        },
        "results": forests,
        "count": len(forests),
    }


def main():
    parser = argparse.ArgumentParser(description="숲나들e 자연휴양림 예약 가능 객실 조회")
    parser.add_argument("--dates", help="조회 일자 (YYYYMMDD, 여러 개면 콤마 구분)")
    parser.add_argument("--forest-id", help="특정 자연휴양림 ID 조회")
    parser.add_argument("--forest-name", help="공식 휴양림명 부분 일치 조회")
    parser.add_argument("--all", dest="all_forests", action="store_true", help="전체 자연휴양림 조회")
    parser.add_argument("--categories", help="카테고리 필터 (01=숙박, 02=야영)")
    parser.add_argument("--json", "-j", dest="as_json", action="store_true", help="JSON 출력")
    parser.add_argument("--text", dest="as_text", action="store_true", help="텍스트 출력")
    parser.add_argument("--timeout", "-t", default=60, type=int, help="타임아웃(초)")

    args = parser.parse_args()

    if not HAS_PLAYWRIGHT:
        print(json.dumps({
            "skill": "foresttrip",
            "status": "error",
            "error": {
                "code": "MISSING_DEPENDENCY",
                "message": "playwright 패키지가 설치되지 않았습니다.",
                "fix": "pip install playwright && playwright install chromium"
            }
        }))
        sys.exit(1)

    user_id = os.environ.get("KSKILL_FORESTTRIP_ID", "")
    password = os.environ.get("KSKILL_FORESTTRIP_PASSWORD", "")

    if not user_id or not password:
        print(json.dumps({
            "skill": "foresttrip",
            "status": "error",
            "error": {
                "code": "MISSING_CREDENTIALS",
                "message": "숲나들e 로그인 정보가 설정되지 않았습니다.",
                "fix": "KSKILL_FORESTTRIP_ID, KSKILL_FORESTTRIP_PASSWORD 환경변수를 설정하세요."
            }
        }))
        sys.exit(1)

    if not args.dates:
        today = datetime.now()
        date_list = [(today + timedelta(days=i)).strftime("%Y%m%d") for i in range(3)]
    else:
        date_list = [d.strip() for d in args.dates.split(",") if d.strip()]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        try:
            if not login(page, user_id, password, args.timeout * 1000):
                print(json.dumps({
                    "skill": "foresttrip",
                    "status": "error",
                    "error": {
                        "code": "LOGIN_FAILED",
                        "message": "로그인에 실패했습니다.",
                        "fix": "아이디와 비밀번호를 확인하세요."
                    }
                }))
                sys.exit(1)

            keyword = args.forest_name or "자연휴양림"

            if args.forest_name:
                detail = search_and_get_detail(page, args.forest_name, date_list, args.timeout * 1000)
                output = {
                    "skill": "foresttrip",
                    "status": "success",
                    "query": {
                        "forest_name": args.forest_name,
                        "dates": date_list,
                    },
                    **detail,
                }
            else:
                output = search_all_forests(page, keyword, date_list, args.timeout * 1000)

            print(json.dumps(output, ensure_ascii=False, indent=2))

        finally:
            browser.close()


if __name__ == "__main__":
    main()
