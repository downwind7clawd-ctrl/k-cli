#!/usr/bin/env python3
"""국세청 고액·상습체납자 명단공개 검색.

국세청 공개 페이지에서 법인/개인 체납 명단을 검색합니다.
인증키 불필요.

사용법:
    python3 nts_tax_delinquency.py --name "상호 또는 법인명"
"""

import argparse
import json
import sys
import urllib.parse
import urllib.request
from html.parser import HTMLParser


NTS_URL = "https://www.nts.go.kr/nts/ad/openInfo/selectList.do"


class NTSListParser(HTMLParser):
    """국세청 명단공개 페이지 HTML 파서."""

    def __init__(self):
        super().__init__()
        self.in_table = False
        self.in_row = False
        self.in_cell = False
        self.current_row = []
        self.rows = []
        self.headers = []

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.in_table = True
        elif tag == "tr" and self.in_table:
            self.in_row = True
            self.current_row = []
        elif tag in ("td", "th") and self.in_row:
            self.in_cell = True

    def handle_endtag(self, tag):
        if tag == "table":
            self.in_table = False
        elif tag == "tr" and self.in_row:
            self.in_row = False
            if self.current_row:
                if not self.headers:
                    self.headers = self.current_row
                else:
                    self.rows.append(self.current_row)
        elif tag in ("td", "th"):
            self.in_cell = False

    def handle_data(self, data):
        if self.in_cell:
            self.current_row.append(data.strip())


def search_delinquents(name: str, corp_only: bool = False) -> dict:
    """체납 명단을 검색합니다.

    Args:
        name: 검색할 상호 또는 법인명
        corp_only: 법인만 검색할지 여부

    Returns:
        검색 결과 딕셔너리
    """
    results = {"query": name, "corporations": [], "individuals": []}

    # 법인 명단 검색
    if not corp_only:
        for tcd in [1, 2]:
            try:
                params = {
                    "tcd": str(tcd),
                    "searchType": "1",
                    "searchValue": name,
                    "searchYear": "",
                    "currPage": "1",
                    "pageIndex": "1",
                    "search_order": "1",
                }
                data = urllib.parse.urlencode(params).encode("utf-8")
                req = urllib.request.Request(NTS_URL, data=data, method="POST")
                req.add_header("Content-Type", "application/x-www-form-urlencoded")
                req.add_header("User-Agent", "Mozilla/5.0")

                with urllib.request.urlopen(req, timeout=30) as resp:
                    html = resp.read().decode("utf-8", errors="replace")

                parser = NTSListParser()
                parser.feed(html)

                category = "corporations" if tcd == 1 else "individuals"
                for row in parser.rows:
                    if len(row) >= 2:
                        entry = {"name": row[0] if row else ""}
                        if len(row) >= 3:
                            entry["amount"] = row[1]
                            entry["details"] = row[2]
                        results[category].append(entry)
            except Exception as e:
                results[f"{category}_error"] = str(e)

    total = len(results["corporations"]) + len(results["individuals"])
    results["total_count"] = total
    results["status"] = "success" if total > 0 else "no_results"

    return results


def main():
    parser = argparse.ArgumentParser(description="국세청 고액·상습체납자 명단공개 검색")
    parser.add_argument("--name", required=True, help="상호 또는 법인명")
    parser.add_argument("--corp-only", action="store_true", help="법인 명단만 검색")
    parser.add_argument("--json", "-j", action="store_true", help="JSON 출력")
    args = parser.parse_args()

    if not args.name or not args.name.strip():
        print(json.dumps({
            "skill": "nts-tax-delinquency",
            "status": "error",
            "error": {"code": "INVALID_INPUT", "message": "상호 또는 법인명을 입력하세요"}
        }, ensure_ascii=False))
        sys.exit(1)

    result = search_delinquents(args.name.strip(), corp_only=args.corp_only)
    result["skill"] = "nts-tax-delinquency"

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
