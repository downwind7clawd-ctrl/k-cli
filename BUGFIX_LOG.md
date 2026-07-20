# BUGFIX LOG — k-cli / k-skill CLI

이 문서는 동기화, 버그 수정, 대규모 리팩토링 작업의 변경 이력을 누적 기록합니다.

---

## 2026-07-10 — upstream sync (110 skills, +15 new)

### Added (upstream sync, 2026-07-10)
- 신규 도메인 4개 생성: fortune, business, recruitng, messaging
- fortune(2): saju-fortune, naming-house
- business(7): biz-health-check, court-payment-order-assistant, d2b-notice-search, g2b-order-plan-search, localdata-business-status, popbill(stub), s2b-notice-search
- recruitng(3): job-posting-match, jobkorea-talent, saramin-talent-search
- messaging(1): kakaotalk-mac
- life 확장(+2): lovebug-report, yebigun-training (kakao-bar는 기존 존재)
- 합계: 95 → 110 스킬 (+15, kakao-bar는 이미 포팅됨)
- 설계/계획: docs/superpowers/specs/2026-07-10-upstream-sync-design.md, docs/superpowers/plans/2026-07-10-upstream-sync.md
- 참고: popbill/saramin-talent-search/court-payment npm 패키지·API 키는 런타임에 K_SKILL_ROOT 설치 필요(미설치 시 MISSING_DEPENDENCY 반환)

### Fixed (packaging, 2026-07-10)
- PyPI 휠에 `manifest.yaml`(비Python 데이터파일) 미포함 버그 수정: `pyproject.toml`에 `[tool.setuptools.package-data] "*" = ["*.yaml","*.yml"]` 추가
- 영향: 기존 배포(2026.7.10.1 및 이전 전체)는 `pip install` 후 `k-skill list`가 0 스킬 표시(loader가 manifest.yaml 못 찾음) — 명령은 동작하나 메타/카운트 누락
- 재배포: **2026.7.10.2** (yaml 18개 포함, 게시 휠에서 110 스킬 / 18 도메인 로드 검증 완료)
- 버전 범프 사유: PyPI는 동일 버전 재업로드 불가 → 2026.7.10.1(결함) → 2026.7.10.2(수정)

## 2026-06-15 — 코드 리뷰 반영 (1-3라운드)

**리뷰어**: 15년차 개발자 + 15년차 보완 전문가
**검증**: 3라운드 교차 검증 완료 (가짜 양성 43건 중 실제 7건 확인, 모두 non-blocking)

### Fixed (8)
- `scripts/run_foresttrip_vacancy.py` — URL 인코딩 추가 (`urllib.parse.quote()`), 하드코딩 "복주산" 버그 수정 (입력값 사용), `except Exception` 수정
- `skills/finance/__init__.py` — `start_dt` 검증 강화 (`re.sub` → `clean_date()` 사용)
- `cli.py` — 스킬 카운트 "89개" → "95개" 수정
- `proxy.py` — `json.JSONDecodeError` 핸들링 추가 (async 함수), 미사용 import (`Any`) 제거
- `dependency.py` — 미사용 import (`json`) 제거
- `skills/shopping/__init__.py` — `if sort_by:` 항상 True인 조건 제거
- `skills/transit/__init__.py` — `import os` 모듈 레벨로 이동
- `skills/document/__init__.py` — manifest 스킬명 불일치 수정 (`korean-humanizer` → `humanizer`)

### Manifest Updates (3)
- `other/manifest.yaml` — `proxy: true` → `proxy: false` (proxy 미사용 도메인)
- `sports/manifest.yaml` — `proxy: true` → `proxy: false` (proxy 미사용 도메인)
- `market/manifest.yaml` — `proxy: true` → `proxy: false` (proxy 미사용 도메인)

### Code Quality
- 10개 미사용 import 제거 (7개 도메인)
- `proxy.py` 중복 지역 import 정리

---

## 2026-06-15 — upstream sync + 리팩토링 (v2026.06.07.1 → v2026.06.15.1)

**Upstream**: NomaDamas/k-skill 최신 버전과 동기화

### Added (6)
- `finance/national-pension` — 국민연금 가입 사업장 조회 (프록시 기반)
- `finance/fsc-corp` — 금융위원회 법인 개요 조회 (프록시 기반)
- `finance/g2b-sanction` — 조달청 부정당제재업체 조회 (프록시 기반)
- `finance/nts-delinquency` — 국세 체납 명단공개 검색 (스크래핑 기반)
- `life/localdata-biz` — 지방행정 인허가 영업상태 조회 (CSV 다운로드 기반)
- `document/humanizer` — AI 한국어 글 윤문 (프롬프트 기반)

### Changed (3)
- `finance/korean-law` — MCP에서 프록시로 마이그레이션 (`/v1/korean-law/search`)
- `validators.py` — 새 유틸리티 모듈 추가 (`validate_nonempty`, `clean_business_number` 등)
- `runner.py` — 동기 래퍼 추가 (`run_npm_sync`, `run_script_sync`, `run_mcp_sync`, `run_pip_import_sync`)

### Fixed (3)
- `life/lunch` — `asyncio.run(safe_proxy_get(...))` 오류 수정 (동기 함수를 비동기로 감싸는 문제)
- `transit/flight-search` — 사용자 쿼리 인자 무시 오류 수정
- `transit/srt` — 사용자 쿼리 인자 무시 오류 수정

### Manifest Updates
- `finance/manifest.yaml` — 스킬 9개 → 13개 (국민연금, 금융위, 부정당, 체납 추가)
- `life/manifest.yaml` — 스킬 22개 → 23개 (인허가 조회 추가)
- `document/manifest.yaml` — 스킬 6개 → 7개 (AI 윤문 추가)
- `shopping/manifest.yaml` — `proxy: false` → `proxy: true` 수정
- `search/manifest.yaml` — `proxy: false` → `proxy: true` 수정

> **참고**: `market`, `other`, `sports` manifest의 proxy 플래그는 upstream sync 시 true로 변경되었으나, 동일 날짜 코드 리뷰에서 proxy 미사용 도메인으로 확인되어 false로 롤백되었습니다 (아래 "코드 리뷰 반영" 섹션 참조).

### Net change
- Skills: 89 → 95 (+6)
- Tests: 73 → 73 (동기화 완료)
- Updated: SKILL.md, README.md, BUGFIX_LOG.md

---

## 2026-06-07 — upstream sync (v2026.05.27.1 → v2026.06.07.1)

**Upstream**: NomaDamas/k-skill @ `1efef28` (2026-06-06)

### Removed (3 archived in upstream `legacy/unsupported-skills/`)
- `map/naver-directions` — proxy 404
- `map/naver-geocode` — proxy 404
- `life/blue-ribbon` — proxy 404

### Reimplemented (2)
- `transit/ktx` — switched from `run_pip_import('korail2', ...)` to `run_script('ktx_booking.py', ...)`. New options: `--date`, `--time`, `--train-type`, `--limit`, `--include-no-seats`, `--include-waiting-list`. Env: `KSKILL_KTX_ID`, `KSKILL_KTX_PASSWORD`.
- `travel/foresttrip` — switched from broken `run_pip_import('playwright', ...)` to `run_script('run_foresttrip_vacancy.py', ...)`. New options: `--dates`, `--all`, `--forest-id`, `--forest-name`, `--categories`, `--text`. Env: `KSKILL_FORESTTRIP_ID`, `KSKILL_FORESTTRIP_PASSWORD`.

### Added (2)
- `transit/seoul-bike` — 3 subcommands: `nearby` (좌표 주변 대여소), `info` (대여소 상세), `availability` (잔여 자전거 수). Proxy-based, no API key needed.
- `document/korean-middle-korean` — 중세 한국어 5가지 검색 (word/spelling/origin/example/translation). Node.js helper, no API key needed.

### Net change
- Skills: 90 → 89 (after -3 removals + 2 additions)
- Tests: 122 → 133 (+11 net: 12 new tests + 1 count update, minus 2 naver removals)
- Updated: SKILL.md, README.md

---

## 2026-06-13 — travel/foresttrip Playwright 전환

**변경 사유**: 숲나들e 공공데이터 API 미동작으로 인한 Playwright 기반 스크래핑 전환

### Changed (2)
- `cli_anything/k_skill/runner.py` — 환경변수 허용 목록에 `KSKILL_FORESTTRIP_ID`, `KSKILL_FORESTTRIP_PASSWORD`, `KSKILL_FORESTTRIP_API_KEY` 추가
- `cli_anything/k_skill/skills/travel/__init__.py` — `foresttrip` 명령어 `run_script('run_foresttrip_vacancy.py')` 호출 방식으로 변경, `script_dirs` 옵션 추가

### Added (1)
- `cli_anything/k_skill/scripts/run_foresttrip_vacancy.py` — Playwright 기반 숲나들e 자연휴양림 예약 가능 객실 조회 스크립트
  - 로그인 자동화 (`fn_goLogin()`)
  - 자연휴양림 검색 및 정보 파싱
  - 객실 상세 정보 조회 (신청하기 클릭 시)

### Env
- `KSKILL_FORESTTRIP_ID` — 숲나들e 로그인 아이디
- `KSKILL_FORESTTRIP_PASSWORD` — 숲나들e 로그인 비밀번호
- `KSKILL_FORESTTRIP_API_KEY` — 공공데이터 API 키 (선택)

### 주의사항
- `.env` 파일에 환경변수 저장 (`.gitignore`에 포함되어 깃 푸시 시 제외)
- Playwright chromium 브라우저 필요 (`playwright install chromium`)
- 타임아웃 기본 60초, 대량 조회 시 `-t 120` 권장

---

## 2026-07-20 · k-skill sync (110 skills) + 14 renames

### Upstream
- https://github.com/NomaDamas/k-skill (110 skills)

### Renamed (14)
- weather: fine-dust → fine-dust-location
- weather: han-river → han-river-water-level
- life: gas → cheap-gas-nearby
- life: waste → household-waste-info
- life: library → library-book-search
- life: lunch → k-schoollunch-menu
- life: holiday → korean-holiday-calendar
- life: nhis → nhis-care-checkup-search
- finance: korean-stock → korean-stock-search
- finance: nts-business → nts-business-registration
- search: naver-news → naver-news-search
- shopping: naver-shopping → naver-shopping-search
- realestate: real-estate → real-estate-search
- realestate: lh-notice → lh-notice-search
- transit: seoul-subway → seoul-subway-arrival
- recruiting: jobkorea-talent → jobkorea-talent-search

### Added (21) — k-cli에 없던 신규 스킬 전체
- life: assembly-bill-vote-search
- life: k-schoollunch-menu
- life: korean-holiday-calendar
- life: nhis-care-checkup-search
- life: library-book-search
- sports: kopis-performance-search
- other: kr-whois-lookup
- other: gov-overseas-trip-report
- other: naver-ad-performance
- weather: fine-dust-location
- weather: han-river-water-level
- finance: korean-stock-search
- finance: nts-business-registration
- search: naver-news-search
- shopping: naver-shopping-search
- realestate: real-estate-search
- realestate: lh-notice-search
- transit: seoul-subway-arrival
- life: cheap-gas-nearby
- life: household-waste-info
- recruiting: jobkorea-talent-search

### Reimplemented
- none

### Verification fixes (this session)
- `recruiting` 명령어 등록명 `jobkorea-talent` → `jobkorea-talent-search` 로 정정
- `search` 명령어 등록명 `naver-news` → `naver-news-search` 로 정정 (+ docstring 예시 갱신)
- `weather` docstring 예시 `han-river` → `han-river-water-level` 로 갱신
- `python -m cli_anything.k_skill` 동작을 위해 `cli_anything/k_skill/__main__.py` 추가
- 누락된 테스트 기대값 갱신: life 25→28, sports 8→9, other 4→7, stale 명령명 단언 4건 수정

---

## 2026-07-20 (추가) · CLI 명령어명을 upstream 키로 정렬 + 하위 호환 별칭 보존

### 배경
1차 sync에서 upstream 스킬 **키 매핑**(`safe_proxy_get` 1인자, manifest `name`)은 갱신됐으나, **사용자 노출 CLI 명령어명**은 구명 그대로 남아 있던 문제를 발견. upstream SKILL.md 예시를 그대로 타이핑할 수 있게 주 명령어명을 upstream 키로 통일하고, 구명은 별칭(alias)으로 보존해 기존 스크립트 호환성 유지.

### 정렬 대상 (primary 명령어명 ← 기존 별칭)
- weather: `fine-dust` ← `dust` / `han-river` ← `han_river`
- finance: `korean-stock` ← `stock` / `nts-business` ← `nts` (group)
- shopping: `naver-shopping` ← `naver-shop`
- realestate: `real-estate` ← `realestate` (group) / `lh-notice` ← `lh` (group)
- transit: `seoul-subway` ← `subway`
- life: `cheap-gas-nearby` ← `gas` / `household-waste-info` ← `waste` / `library-book-search` ← `library` / `k-schoollunch-menu` ← `lunch` / `korean-holiday-calendar` ← `holiday` / `nhis-care-checkup-search` ← `nhis` (group)
- (이미 일치: search `naver-news-search`, recruiting `jobkorea-talent-search`)

### 변경 방식
각 명령 함수에 primary `@cli.command(name='<upstream-key>')` 적용 후 `cli.add_command(func, name='<old>')` 로 별칭 등록. 프록시 키 문자열(`safe_proxy_get("fine-dust-location", ...)` 등)은 변경 없음.

### Code review nits
- `other/__init__.py` 중복 `error_response` 로컬 import 제거 (모듈 레벨 import로 통합)

### Verification
- 전 도메인 pytest 통과 (기존 180 + 신규 alias 테스트)
- 신/구 명령어명 모두 `--help` exit 0 확인

