"""Phase 3 코드 제너레이터 — 간단 템플릿 기반."""

import json
import os
import sys
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = PROJECT_ROOT / "cli_anything" / "k_skill" / "skills"

# ── 스킬 정의 (domain → [skill_configs]) ─────────────────
# 각 config: {cmd, name, display, desc, runner, extra}

SKILLS = {
    # ── transit (추가 스킬 — Phase 2에 이미 subway 있음) ──
    "transit": [
        {"cmd": "subway-lost", "name": "subway-lost-property", "display": "지하철 분실물",
         "desc": "서울교통공사 지하철 분실물 검색", "runner": "script",
         "script": "subway_lost_property.py"},
        {"cmd": "intercity-bus", "name": "intercity-bus-booking", "display": "시외버스 예매",
         "desc": "Tmoney 시외버스 시간표/잔여석 조회", "runner": "script",
         "script": "intercity_bus_search.py"},
        {"cmd": "express-bus", "name": "express-bus-booking", "display": "고속버스 예매",
         "desc": "KOBUS 고속버스 시간표/잔여석 조회", "runner": "script",
         "script": "kobus_express_booking.py"},
        {"cmd": "flight-search", "name": "flight-ticket-search", "display": "항공권 검색",
         "desc": "Google Flights 항공권 가격/일정 검색", "runner": "pip",
         "pip_mod": "fast_flights", "pip_func": "search_flights",
         "pip_pkgs": ["fast-flights"]},
        {"cmd": "srt", "name": "srt-booking", "display": "SRT 예매",
         "desc": "SRT 열차 조회/예매", "runner": "pip",
         "pip_mod": "SRTrain", "pip_func": "search_train",
         "pip_pkgs": ["SRTrain"]},
        {"cmd": "ktx", "name": "ktx-booking", "display": "KTX 예매",
         "desc": "KTX/코레일 열차 조회/예매", "runner": "pip",
         "pip_mod": "korail2", "pip_func": "search_train",
         "pip_pkgs": ["korail2-ncard", "pycryptodome"]},
        {"cmd": "transit-route", "name": "korean-transit-route", "display": "대중교통 길찾기",
         "desc": "ODSay 대중교통 길찾기 (지하철/버스/도보)", "runner": "script",
         "script": "transit_route.py", "env_keys": ["ODSAY_API_KEY"]},
    ],
    # ── shopping (추가 — Phase 2에 naver-shop 있음) ──
    "shopping": [
        {"cmd": "olive-young", "name": "olive-young-search", "display": "올리브영 검색",
         "desc": "올리브영 상품 검색 및 재고 확인", "runner": "npm",
         "npm_pkg": "olive-young-search", "npm_npx": True},
        {"cmd": "market-kurly", "name": "market-kurly-search", "display": "마켓컬리 검색",
         "desc": "마켓컬리 상품 검색", "runner": "npm",
         "npm_pkg": "market-kurly-search"},
        {"cmd": "daiso", "name": "daiso-product-search", "display": "다이소몰 검색",
         "desc": "다이소몰 상품 재고 조회", "runner": "npm",
         "npm_pkg": "daiso-product-search"},
        {"cmd": "danawa", "name": "danawa-price-search", "display": "다나와 가격비교",
         "desc": "다나와 최저가 검색/비교", "runner": "script",
         "script": "danawa_search.py", "script_subdir": "danawa-price-search"},
        {"cmd": "ohou-deal", "name": "ohou-today-deal", "display": "오늘의집 데일리딜",
         "desc": "오늘의집 데일리특가 조회", "runner": "script",
         "script": "ohou_today_deal.py", "script_subdir": "ohou-today-deal"},
        {"cmd": "coupang", "name": "coupang-product-search", "display": "쿠팡 상품 검색",
         "desc": "쿠팡 파트너스 API 상품 검색", "runner": "mcp",
         "mcp_url": "local://coupang-mcp"},
    ],
    # ── finance (추가 — Phase 2에 nts/stock/kstartup 있음) ──
    "finance": [
        {"cmd": "dart", "name": "k-dart", "display": "DART 전자공시",
         "desc": "금융감독원 DART 전자공시 조회", "runner": "script",
         "script": "k_dart.py", "env_keys": ["API_K_DART"]},
        {"cmd": "kosis", "name": "kosis-stats", "display": "KOSIS 통계",
         "desc": "KOSIS 국가통계포털 통계 조회", "runner": "script",
         "script": "run_kosis_stats.py", "script_subdir": "kosis-stats"},
        {"cmd": "korean-law", "name": "korean-law-search", "display": "법령/판례 검색",
         "desc": "대한민국 법령/판례/유권해석 검색", "runner": "mcp",
         "mcp_url": "local://korean-law-mcp"},
        {"cmd": "gongsijiga", "name": "gongsijiga-search", "display": "개별공시지가",
         "desc": "개별공시지가(토지가격) 조회", "runner": "npm",
         "npm_pkg": "gongsijiga-search"},
        {"cmd": "toss-stock", "name": "toss-securities", "display": "토스증권 주식",
         "desc": "토스증권 주식 시세/정보 조회", "runner": "npm",
         "npm_pkg": "toss-securities"},
        {"cmd": "daishin-report", "name": "daishin-report-search", "display": "대신 리포트",
         "desc": "대신증권 리서치 리포트 검색", "runner": "npm",
         "npm_pkg": "daishin-report-search"},
    ],
    # ── realestate (추가 — Phase 2에 realestate/lh 있음) ──
    "realestate": [
        {"cmd": "sh-notice", "name": "sh-notice-search", "display": "서울주택도시공사 공고",
         "desc": "서울주택도시공사 분양/입주 공고 검색", "runner": "npm",
         "npm_pkg": "sh-notice-search"},
        {"cmd": "court-auction", "name": "court-auction-notice-search", "display": "법원 경매 공고",
         "desc": "법원 경매 공고문 검색", "runner": "npm",
         "npm_pkg": "court-auction-notice-search"},
        {"cmd": "daangn-realty", "name": "daangn-realty-search", "display": "당근부동산 매물",
         "desc": "당근부동산 매물 검색", "runner": "script",
         "script": "daangn_realty.py"},
    ],
    # ── search (추가 — Phase 2에 naver-news 있음) ──
    "search": [
        {"cmd": "naver-blog", "name": "naver-blog-research", "display": "네이버 블로그 리서치",
         "desc": "네이버 블로그 검색 및 요약", "runner": "script",
         "script": "naver_blog.py", "script_subdir": "naver-blog-research"},
        {"cmd": "geeknews", "name": "geeknews-search", "display": "긱뉴스",
         "desc": "긱뉴스 테크 뉴스 조회", "runner": "script",
         "script": "geeknews_search.py"},
        {"cmd": "patent", "name": "korean-patent-search", "display": "특허 검색",
         "desc": "KIPIRIS 한국 특허 검색", "runner": "script",
         "script": "patent_search.py", "env_keys": ["KIPRIS_PLUS_API_KEY"]},
        {"cmd": "sillok", "name": "joseon-sillok-search", "display": "조선왕조실록",
         "desc": "조선왕조실록 검색", "runner": "script",
         "script": "sillok_search.py"},
        {"cmd": "scholarship", "name": "korean-scholarship-search", "display": "장학금 검색",
         "desc": "한국 장학금 검색", "runner": "script",
         "script": "scholarship_search.py", "script_subdir": "korean-scholarship-search"},
    ],
    # ── market (새 도메인) ──
    "market": [
        {"cmd": "bunjang", "name": "bunjang-search", "display": "번개장터 검색",
         "desc": "번개장터 중고상품 검색", "runner": "npm",
         "npm_pkg": "bunjang-cli", "npm_npx": True},
        {"cmd": "daangn-market", "name": "daangn-used-goods-search", "display": "당근 중고거래",
         "desc": "당근마켓 중고거래 검색", "runner": "script",
         "script": "daangn_used_goods.py"},
        {"cmd": "daangn-cars", "name": "daangn-cars-search", "display": "당근중고차",
         "desc": "당근마켓 중고차 매물 검색", "runner": "script",
         "script": "daangn_cars.py"},
        {"cmd": "used-car-price", "name": "used-car-price-search", "display": "중고차 가격",
         "desc": "SK렌터카 중고차 가격 조회", "runner": "script",
         "script": "used_car_price_search.py"},
    ],
    # ── document (새 도메인) ──
    "document": [
        {"cmd": "hwp-convert", "name": "hwp", "display": "HWP 변환",
         "desc": "HWP/HWPX 문서를 PDF 등으로 변환", "runner": "npm",
         "npm_pkg": "kordoc"},
        {"cmd": "rhwp-debug", "name": "rhwp-advanced", "display": "HWP 레이아웃 디버그",
         "desc": "rhwp Rust CLI로 HWP 레이아웃 디버깅", "runner": "script",
         "script": "rhwp", "is_binary": True},
        {"cmd": "rhwp-edit", "name": "rhwp-edit", "display": "HWP 편집",
         "desc": "HWP 문서 편집 (k-skill-rhwp)", "runner": "npm",
         "npm_pkg": "k-skill-rhwp"},
        {"cmd": "spell-check", "name": "korean-spell-check", "display": "맞춤법 검사",
         "desc": "한국어 맞춤법/문법 검사", "runner": "script",
         "script": "korean_spell_check.py"},
        {"cmd": "char-count", "name": "korean-character-count", "display": "글자 수 세기",
         "desc": "한국어 글자/어절/문단 수 카운트", "runner": "npm",
         "npm_pkg": "korean-character-count"},
    ],
    # ── life (추가 — Phase 2에 gas/waste/parking/library/lunch/drug/food 있음) ──
    "life": [
        {"cmd": "plastic-surgery", "name": "gangnamunni-clinic-search", "display": "강남유니 성형외과",
         "desc": "강남유니 성형외과 정보 검색", "runner": "npm",
         "npm_pkg": "gangnamunni-clinic-search", "npm_npx": True},
        {"cmd": "blue-ribbon", "name": "blue-ribbon-nearby", "display": "블루리본 맛집",
         "desc": "블루리본 인증 맛집 검색", "runner": "npm",
         "npm_pkg": "blue-ribbon-nearby"},
        {"cmd": "public-restroom", "name": "public-restroom-nearby", "display": "공중화장실",
         "desc": "근처 공중화장실 검색", "runner": "npm",
         "npm_pkg": "public-restroom-nearby"},
        {"cmd": "emergency-room", "name": "emergency-room-beds", "display": "응급실 병상",
         "desc": "근처 응급실 실시간 병상 조회", "runner": "npm",
         "npm_pkg": "emergency-room-beds"},
        {"cmd": "election", "name": "local-election-candidate-search", "display": "선거 후보",
         "desc": "지방선거 후보자 검색", "runner": "npm",
         "npm_pkg": "local-election-candidate-search", "npm_npx": True},
        {"cmd": "hipass", "name": "hipass-receipt", "display": "하이패스 영수증",
         "desc": "하이패스 통행료 영수증 조회", "runner": "npm",
         "npm_pkg": "hipass-receipt"},
        {"cmd": "donation", "name": "donation-place-search", "display": "기부처",
         "desc": "기부처 검색", "runner": "npm",
         "npm_pkg": "donation-place-search"},
        {"cmd": "kakao-bar", "name": "kakao-bar-nearby", "display": "근처 술집",
         "desc": "카카오맵 근처 술집 검색", "runner": "npm",
         "npm_pkg": "kakao-bar-nearby"},
        {"cmd": "daangn-jobs", "name": "daangn-jobs-search", "display": "당근알바",
         "desc": "당근마켓 알바 구인 검색", "runner": "script",
         "script": "daangn_jobs.py"},
        {"cmd": "zipcode", "name": "zipcode-search", "display": "우편번호",
         "desc": "우편번호 검색", "runner": "script",
         "script": "zipcode_search.py"},
        {"cmd": "slang", "name": "korean-slang-writing", "display": "신조어/유행어",
         "desc": "신조어/유행어 생성 및 검색", "runner": "script",
         "script": "slang_search.py", "script_subdir": "korean-slang-writing"},
        {"cmd": "kakaotalk", "name": "kakaotalk-mac", "display": "카카오톡 자동화",
         "desc": "카카오톡 macOS 자동화", "runner": "script",
         "script": "kakaotalk_mac.py"},
        {"cmd": "seoul-density", "name": "seoul-density", "display": "서울 인구밀도",
         "desc": "서울 실시간 인구밀도 조회", "runner": "script",
         "script": "seoul_density.py"},
        {"cmd": "corp-registration", "name": "corporate-registration-consulting", "display": "법인설립 상담",
         "desc": "법인설립 서류 작성 자동화", "runner": "script",
         "script": "fill_official_hwp.py", "script_subdir": "corporate-registration-consulting"},
        {"cmd": "catchtable", "name": "catchtable-sniper", "display": "캐치테이블 캡처",
         "desc": "캐치테이블 예약 자동 캡처", "runner": "mcp",
         "mcp_url": "local://chrome-mcp"},
        {"cmd": "cleaner", "name": "k-skill-cleaner", "display": "스킬 정리",
         "desc": "k-skill 사용량 정리", "runner": "script",
         "script": "k_skill_cleaner.py"},
    ],
    # ── sports (새 도메인) ──
    "sports": [
        {"cmd": "kbo", "name": "kbo-results", "display": "KBO 경기결과",
         "desc": "KBO 한국야구 경기 결과 조회", "runner": "npm",
         "npm_pkg": "kbo-game", "npm_global": True},
        {"cmd": "kbl", "name": "kbl-results", "display": "KBL 농구결과",
         "desc": "KBL 프로농구 경기 결과 조회", "runner": "npm",
         "npm_pkg": "kbl-results", "npm_global": True},
        {"cmd": "kleague", "name": "kleague-results", "display": "K리그 결과",
         "desc": "K리그 축구 경기 결과 조회", "runner": "npm",
         "npm_pkg": "kleague-results", "npm_global": True},
        {"cmd": "lck", "name": "lck-analytics", "display": "LCK 분석",
         "desc": "LCK 리그오브레전드 경기/분석", "runner": "npm",
         "npm_pkg": "lck-analytics", "npm_global": True},
        {"cmd": "cinema", "name": "korean-cinema-search", "display": "영화관 검색",
         "desc": "CGV/메가박스/롯데시네마 영화관/상영작 검색", "runner": "npm",
         "npm_pkg": "daiso", "npm_npx": True},
        {"cmd": "lotto", "name": "lotto-results", "display": "로또 당첨번호",
         "desc": "로또 당첨번호 조회", "runner": "npm",
         "npm_pkg": "k-lotto", "npm_global": True},
        {"cmd": "marathon", "name": "korean-marathon-schedule", "display": "마라톤 일정",
         "desc": "한국 마라톤 대회 일정 검색", "runner": "npm",
         "npm_pkg": "korean-marathon-schedule"},
        {"cmd": "ticket", "name": "ticket-availability", "display": "공연 잔여석",
         "desc": "공연/전시 티켓 잔여석 조회", "runner": "script",
         "script": "ticket_availability.py", "script_subdir": "ticket-availability"},
    ],
    # ── travel (새 도메인) ──
    "travel": [
        {"cmd": "myrealtrip", "name": "myrealtrip-search", "display": "마이리얼트립",
         "desc": "마이리얼트립 숙소/패키지 검색", "runner": "mcp",
         "mcp_url": "https://mcp-servers.myrealtrip.com/mcp"},
        {"cmd": "hola-poke", "name": "hola-poke-yeoksam", "display": "올라포케 역삼점",
         "desc": "올라포케 역삼점 메뉴/영업시간", "runner": "mcp",
         "mcp_url": "https://hola-poke-yeoksam-skill.onrender.com/mcp"},
        {"cmd": "foresttrip", "name": "foresttrip-vacancy", "display": "숲나들예약",
         "desc": "산림청 숲나들예약 잔여석 조회", "runner": "pip",
         "pip_mod": "playwright", "pip_func": "sync_api",
         "pip_pkgs": ["playwright"]},
    ],
    # ── delivery (새 도메인) ──
    "delivery": [
        {"cmd": "delivery", "name": "delivery-tracking", "display": "택배 송장 조회",
         "desc": "택배 송장번호로 배송 조회", "runner": "script",
         "script": "delivery_tracking.py"},
    ],
    # ── other (새 도메인) ──
    "other": [
        {"cmd": "iros", "name": "iros-registry-automation", "display": "지식재산권 등록",
         "desc": "지식재산권 등록 자동화", "runner": "script",
         "script": "main.py", "script_subdir": "iros-registry-automation"},
        {"cmd": "setup", "name": "k-skill-setup", "display": "k-skill 초기설정",
         "desc": "k-skill 초기 설정 마법사", "runner": "mcp",
         "mcp_url": "local://korean-law-mcp"},
        {"cmd": "jangbu", "name": "korean-jangbu-for", "display": "장부/가계부",
         "desc": "한국식 장부/가계부", "runner": "script",
         "script": "install.sh", "is_binary": True},
        {"cmd": "privacy-terms", "name": "korean-privacy-terms", "display": "개인정보처리방침",
         "desc": "개인정보처리방침 생성", "runner": "script",
         "script": "install.sh", "is_binary": True},
    ],
}

# 도메인 메타
DOMAIN_META = {
    "transit": ("대중교통", "지하철, 버스, 기차, 항공편 등 대중교통"),
    "shopping": ("쇼핑", "온라인 쇼핑 검색 및 가격 비교"),
    "finance": ("금융/공공", "금융, 공시, 통계, 법률"),
    "realestate": ("부동산", "부동산 매물, 경매, 공고"),
    "search": ("검색/조사", "블로그, 특허, 실록 등 검색"),
    "market": ("중고거래", "당근마켓, 번개장터 등"),
    "document": ("문서", "HWP, 맞춤법, 글자수"),
    "life": ("생활/편의", "음식점, 병원, 화장실, 알바 등"),
    "sports": ("스포츠/레저", "스포츠 경기, 로또, 영화관"),
    "travel": ("여행", "여행지, 숙소 검색"),
    "delivery": ("배송", "택배 송장 조회"),
    "other": ("기타", "기타 유틸리티"),
}


def gen_manifest(domain: str, skills: list[dict]) -> str:
    label, desc = DOMAIN_META.get(domain, (domain, ""))
    lines = [
        f"domain: {domain}",
        f'label: "{label}"',
        f'description: "{desc}"',
        "dependencies:",
        "  proxy: false",
        "  npm: []",
        "  python: []",
        "  env_keys: []",
        "skills:",
    ]
    for s in skills:
        lines.append(f"  {s['cmd']}:")
        lines.append(f'    name: "{s["name"]}"')
        lines.append(f'    display_name: "{s["display"]}"')
        lines.append(f'    description: "{s["desc"]}"')
        npm = s.get("npm_pkg", [])
        pip = s.get("pip_pkgs", [])
        env = s.get("env_keys", [])
        if npm:
            lines.append(f"    npm: {json.dumps([npm])}")
        if pip:
            lines.append(f"    python: {json.dumps(pip)}")
        if env:
            lines.append(f"    env_keys: {json.dumps(env)}")
    return "\n".join(lines) + "\n"


def gen_command(s: dict) -> str:
    """Click 커맨드 함수 코드 생성."""
    cmd = s["cmd"].replace("-", "_")
    desc = s["desc"].replace("'", "\\'")
    runner = s["runner"]

    lines = [
        f"@cli.command(name='{s['cmd']}', help='{desc}')",
        "@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')",
        "@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')",
        "@click.argument('query', required=False)",
        f"def {cmd}(query, as_json, timeout):",
        f'    """{s["display"]}."""',
    ]

    if runner == "npm":
        pkg = s["npm_pkg"]
        opts = []
        if s.get("npm_npx"):
            opts.append("npx=True")
        if s.get("npm_global"):
            opts.append("global_install=True")
        opts.append(f"timeout=timeout")
        opt_str = ", ".join(opts)
        lines.append(f"    args = [query] if query else []")
        lines.append(f"    result = asyncio.run(run_npm('{pkg}', args, {opt_str}))")
    elif runner == "script":
        script = s["script"]
        opts = [f"timeout=timeout"]
        if s.get("script_subdir"):
            opts.append(f"script_subdir='{s['script_subdir']}'")
        if s.get("env_keys"):
            opts.append(f"env_keys={json.dumps(s['env_keys'])}")
        if s.get("is_binary"):
            opts.append("is_binary=True")
        opt_str = ", ".join(opts)
        lines.append(f"    args = [query] if query else []")
        lines.append(f"    result = asyncio.run(run_script('{script}', args, {opt_str}))")
    elif runner == "pip":
        mod = s["pip_mod"]
        func = s["pip_func"]
        pkgs = json.dumps(s.get("pip_pkgs", [mod]))
        lines.append(f"    result = asyncio.run(run_pip_import('{mod}', '{func}', packages={pkgs}, timeout=timeout))")
    elif runner == "mcp":
        url = s["mcp_url"]
        lines.append(f"    result = asyncio.run(run_mcp('{s['name']}', server_url='{url}', timeout=timeout))")

    lines.append("    emit(result, as_json=as_json)")
    return "\n".join(lines)


def gen_init_py(domain: str, skills: list[dict]) -> str:
    label, desc = DOMAIN_META.get(domain, (domain, ""))
    lines = [
        f'"""{label} 도메인 스킬."""',
        "",
        "import asyncio",
        "import click",
        "",
        "from cli_anything.k_skill.runner import run_npm, run_script, run_pip_import, run_mcp",
        "from cli_anything.k_skill.output import emit",
        "",
        "",
        f"@click.group(name='{domain}', help='{label}: {desc}')",
        "def cli():",
        "    pass",
        "",
    ]
    for s in skills:
        lines.append(gen_command(s))
        lines.append("")
    return "\n".join(lines)


def main():
    dry_run = "--dry-run" in sys.argv
    total = 0

    for domain, skills in SKILLS.items():
        total += len(skills)
        domain_dir = SKILLS_DIR / domain

        # 새 도메인 or 기존 도메인
        is_new = not (domain_dir / "manifest.yaml").is_file()

        if is_new:
            print(f"[NEW] {domain}/ ({len(skills)}개)")
            if not dry_run:
                domain_dir.mkdir(parents=True, exist_ok=True)
                (domain_dir / "manifest.yaml").write_text(gen_manifest(domain, skills))
                (domain_dir / "__init__.py").write_text(gen_init_py(domain, skills))
        else:
            print(f"[APPEND] {domain}/ +{len(skills)}개")
            if not dry_run:
                # manifest에 skills append
                mf = domain_dir / "manifest.yaml"
                existing = mf.read_text()
                extra_mf = gen_manifest(domain, skills)
                # skills 섹션만 추출
                skill_lines = []
                in_skills = False
                for line in extra_mf.split("\n"):
                    if line.startswith("skills:"):
                        in_skills = True
                        continue
                    if in_skills:
                        skill_lines.append(line)
                append_block = "\n".join(skill_lines).strip()
                if "skills:" in existing:
                    updated = existing.rstrip() + "\n" + append_block + "\n"
                else:
                    updated = existing.rstrip() + "\n\nskills:\n" + append_block + "\n"
                mf.write_text(updated)

                # __init__.py에 커맨드 append
                init = domain_dir / "__init__.py"
                existing_init = init.read_text()
                new_commands = "\n\n".join(gen_command(s) for s in skills)
                if new_commands.strip() not in existing_init:
                    updated_init = existing_init.rstrip() + "\n\n" + new_commands + "\n"
                    init.write_text(updated_init)

    print(f"\n총 {total}개 스킬, {len(SKILLS)}개 도메인")
    if dry_run:
        print("(dry-run)")


if __name__ == "__main__":
    main()
