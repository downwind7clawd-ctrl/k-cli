---
name: k-skill
display_name: K-Skill CLI
description: 한국인을 위한 CLI 스킬 모음 90개 — 날씨, 교통, 금융, 부동산, 쇼핑, 스포츠, 생활 유틸리티를 단일 명령어로
version: 2026.05.27.1
dependencies: []
---

# K-Skill CLI — 한국인을 위한 CLI 스킬 모음

에이전트가 `pip install cli-anything-k-skill` 후 즉시 사용 가능한 90개 한국 특화 CLI 스킬.
모든 명령에 `-j` (`--json`) 플래그로 구조화된 JSON 응답을 받을 수 있습니다.

## 설치

```bash
pip install cli-anything-k-skill
```

## 빠른 시작

```bash
k-skill weather forecast --lat 37.5665 --lon 126.9780 -j
k-skill transit subway "강남" -j
k-skill finance stock "삼성전자" -j
k-skill sports kbo --date 2025-06-01 -j
k-skill life waste "강남구" -j
k-skill market daangn-market --region "서울" -j
k-skill search naver-news "AI" -j
k-skill setup check -j
```

## 도메인 목록 (14개 도메인, 90개 스킬)

| 도메인 | 스킬 수 | 설명 |
|--------|--------|------|
| weather | 3 | 날씨/환경 조회 (기상청, 미세먼지, 한강수위) |
| map | 4 | 지도/길찾기 (카카오맵 장소/길찾기, 네이버 길찾기/지오코딩) |
| transit | 8 | 대중교통 (지하철, 버스, 기차, 항공편) |
| life | 23 | 생활/편의 (주유소, 쓰레기, 주차장, 맛집 등) |
| finance | 9 | 금융/공공 (사업자등록, 주식, 법률, 통계) |
| realestate | 5 | 부동산 (실거래가, LH, 경매) |
| shopping | 7 | 쇼핑 검색 (네이버, 올리브영, 다이소 등) |
| market | 4 | 당근마켓, 번개장터 등 |
| search | 6 | 검색/조사 (뉴스, 블로그, 특허, 실록) |
| document | 5 | HWP, 맞춤법, 글자수 |
| sports | 8 | 스포츠 경기, 로또, 영화관 |
| travel | 3 | 여행지, 숙소 검색 |
| delivery | 1 | 택배 송장 조회 |
| other | 4 | 기타 유틸리티 |
| **합계** | **90** | |

## JSON 응답 형식

```json
// 성공: {"skill": "weather/forecast", "status": "success", "data": {...}, "meta": {"source": "...", "response_time_ms": N}}
// 실패: {"skill": "weather/forecast", "status": "error", "error": {"code": "PROXY_DOWN", "message": "...", "fix": "..."}}
```

## 에러 코드

| 코드 | 의미 | 해결 |
|------|------|------|
| PROXY_DOWN | 프록시 서버 연결 실패 | `k-skill setup proxy` |
| PROXY_HTTP_ERROR | 프록시 HTTP 에러 | 파라미터 확인 |
| TIMEOUT | 응답 시간 초과 | `--timeout` 증가 |
| MISSING_DEPENDENCY | 필수 패키지 미설치 | `k-skill setup install` |
| INVALID_INPUT | 입력값 오류 | `--help` 확인 |
| MCP_ERROR | MCP 통신 오류 | MCP 서버 상태 확인 |
| UNKNOWN | 알 수 없는 오류 | 이슈 등록 |

## 환경변수

| 변수 | 설명 | 기본값 |
|------|------|--------|
| KSKILL_PROXY_BASE_URL | 프록시 URL | https://k-skill-proxy.nomadamas.org |
| K_SKILL_ROOT | k-skill 스크립트/패키지 루트 경로 | 패키지 기준 상대경로 자동 계산 |

* **보안 서브프로세스 환경변수 상속:** 로컬 스크립트 실행에 필요한 주요 API 키 및 프록시 설정 변수(`KSKILL_PROXY_BASE_URL`, `ODSAY_API_KEY`, `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET`, `COUPANG_ACCESS_KEY`, `COUPANG_SECRET_KEY`, `DART_API_KEY`, `KOSIS_API_KEY`)는 하위 실행 환경으로 안전하게 자동 상속되도록 설계되어 있습니다.

## 유틸리티

```bash
k-skill list                   # 도메인별 요약
k-skill -j list --all          # 전체 스킬 JSON (전역 -j 사용)
k-skill list -d weather        # 도메인별
k-skill -j setup check         # 의존성 상태 (JSON)
k-skill -j setup proxy         # 프록시 연결 (JSON)
k-skill setup install          # 설치 가이드
```

---

# 상세 도움말

<details><summary>weather --help</summary>

```
Usage: python -m cli_anything.k_skill.cli weather [OPTIONS] COMMAND [ARGS]...

  날씨/환경 조회 (기상청, 미세먼지, 한강수위).

  모든 명령은 k-skill-proxy를 경유하며 별도 API 키 불필요.

Options:
  --help  Show this message and exit.

Commands:
  dust       미세먼지/초미세먼지 조회.
  han-river  한강 수위/유량 조회.
  weather    한국 날씨 (기상청 단기예보).
```

</details>

<details><summary>transit --help</summary>

```
Usage: python -m cli_anything.k_skill.cli transit [OPTIONS] COMMAND [ARGS]...

  대중교통 (서울 지하철 실시간 도착정보).

  서울 열린데이터 광장 Open API를 k-skill-proxy로 경유 조회.

Options:
  --help  Show this message and exit.

Commands:
  express-bus    KOBUS 고속버스 시간표/잔여석 조회
  flight-search  Google Flights 항공권 가격/일정 검색
  intercity-bus  Tmoney 시외버스 시간표/잔여석 조회
  ktx            KTX/코레일 열차 조회/예매
  srt            SRT 열차 조회/예매
  subway         서울 지하철 실시간 도착정보.
  subway-lost    서울교통공사 지하철 분실물 검색
  transit-route  ODSay 대중교통 길찾기
```

</details>

<details><summary>life --help</summary>

```
Usage: python -m cli_anything.k_skill.cli life [OPTIONS] COMMAND [ARGS]...

  생활/편의 (주유소, 쓰레기, 주차장, 도서관, 급식, 의약품, 식품안전).

  모든 명령은 k-skill-proxy를 경유하며 별도 API 키 불필요.

Options:
  --help  Show this message and exit.

Commands:
  blue-ribbon        블루리본 인증 맛집 검색
  catchtable         캐치테이블 예약 자동 캡처
  cleaner            k-skill 사용량 정리
  corp-registration  법인설립 서류 작성 자동화
  daangn-jobs        당근마켓 알바 구인 검색
  donation           기부처 검색
  drug               의약품 안전 조회.
  election           지방선거 후보자 검색
  emergency-room     근처 응급실 실시간 병상 조회
  food               식품 안전 조회.
  gas                근처 주유소 가격 조회.
  hipass             하이패스 통행료 영수증 조회
  kakao-bar          카카오맵 근처 술집 검색
  kakaotalk          카카오톡 macOS 자동화
  library            도서관 도서 검색.
  lunch              학교 급식 식단.
  parking            공영주차장 검색.
  plastic-surgery    강남유니 성형외과 정보 검색
  public-restroom    근처 공중화장실 검색
  seoul-density      서울 실시간 인구밀도 조회
  slang              신조어/유행어 생성 및 검색
  waste              쓰레기 분리수거 정보.
  zipcode            우편번호 검색
```

</details>

<details><summary>finance --help</summary>

```
Usage: python -m cli_anything.k_skill.cli finance [OPTIONS] COMMAND [ARGS]...

  금융/공부 (사업자등록, 주식, 창업공고).

  모든 명령은 k-skill-proxy를 경유하며 별도 API 키 불필요.

Options:
  --help  Show this message and exit.

Commands:
  daishin-report  대신증권 리서치 리포트 검색
  dart            금융감독원 DART 전자공시 조회
  gongsijiga      개별공시지가(토지가격) 조회
  korean-law      대한민국 법령/판례/유권해석 검색
  kosis           KOSIS 국가통계포털 통계 조회
  kstartup        K-Startup 창업공고 검색.
  nts             국세청 사업자등록 진위확인.
  stock           한국 주식 조회 (KRX).
  toss-stock      토스증권 주식 시세/정보 조회
```

</details>

<details><summary>realestate --help</summary>

```
Usage: python -m cli_anything.k_skill.cli realestate [OPTIONS] COMMAND
                                                     [ARGS]...

  부동산 (실거래가/전월세, LH 청약공고).

  국토교통부 실거래가 데이터와 LH 공고를 k-skill-proxy로 경유 조회.

Options:
  --help  Show this message and exit.

Commands:
  court-auction  법원 경매 공고문 검색
  daangn-realty  당근부동산 매물 검색
  lh             LH 청약 공고문 조회.
  realestate     부동산 실거래가/전월세 조회.
  sh-notice      서울주택도시공사 분양/입주 공고 검색
```

</details>

<details><summary>shopping --help</summary>

```
Usage: python -m cli_anything.k_skill.cli shopping [OPTIONS] COMMAND [ARGS]...

  쇼핑 검색 (네이버 쇼핑).

  네이버 쇼핑 검색 API를 경유해 상품 후보, 가격, 판매처를 조회.

Options:
  --help  Show this message and exit.

Commands:
  coupang       쿠팡 파트너스 API 상품 검색
  daiso         다이소몰 상품 재고 조회
  danawa        다나와 최저가 검색/비교
  market-kurly  마켓컬리 상품 검색
  naver-shop    네이버 쇼핑 검색.
  ohou-deal     오늘의집 데일리특가 조회
  olive-young   올리브영 상품 검색 및 재고 확인
```

</details>

<details><summary>market --help</summary>

```
Usage: python -m cli_anything.k_skill.cli market [OPTIONS] COMMAND [ARGS]...

  중고거래: 당근마켓, 번개장터 등

Options:
  --help  Show this message and exit.

Commands:
  bunjang         번개장터 중고상품 검색
  daangn-cars     당근마켓 중고차 매물 검색
  daangn-market   당근마켓 중고거래 검색
  used-car-price  SK렌터카 중고차 가격 조회
```

</details>

<details><summary>search --help</summary>

```
Usage: python -m cli_anything.k_skill.cli search [OPTIONS] COMMAND [ARGS]...

  검색 (네이버 뉴스).

  네이버 뉴스 검색 API를 경유해 최신 뉴스 기사를 조회.

Options:
  --help  Show this message and exit.

Commands:
  geeknews     긱뉴스 테크 뉴스 조회
  naver-blog   네이버 블로그 검색 및 요약
  naver-news   네이버 뉴스 검색.
  patent       KIPIRIS 한국 특허 검색
  scholarship  한국 장학금 검색
  sillok       조선왕조실록 검색
```

</details>

<details><summary>document --help</summary>

```
Usage: python -m cli_anything.k_skill.cli document [OPTIONS] COMMAND [ARGS]...

  문서: HWP, 맞춤법, 글자수

Options:
  --help  Show this message and exit.

Commands:
  char-count   한국어 글자/어절/문단 수 카운트
  hwp-convert  HWP/HWPX 문서를 PDF 등으로 변환
  rhwp-debug   rhwp Rust CLI로 HWP 레이아웃 디버깅
  rhwp-edit    HWP 문서 편집 (k-skill-rhwp)
  spell-check  한국어 맞춤법/문법 검사
```

</details>

<details><summary>sports --help</summary>

```
Usage: python -m cli_anything.k_skill.cli sports [OPTIONS] COMMAND [ARGS]...

  스포츠/레저: 스포츠 경기, 로또, 영화관

Options:
  --help  Show this message and exit.

Commands:
  cinema    CGV/메가박스/롯데시네마 영화관/상영작 검색
  kbl       KBL 프로농구 경기 결과 조회
  kbo       KBO 한국야구 경기 결과 조회
  kleague   K리그 축구 경기 결과 조회
  lck       LCK 리그오브레전드 경기/분석
  lotto     로또 당첨번호 조회
  marathon  한국 마라톤 대회 일정 검색
  ticket    공연/전시 티켓 잔여석 조회
```

</details>

<details><summary>travel --help</summary>

```
Usage: python -m cli_anything.k_skill.cli travel [OPTIONS] COMMAND [ARGS]...

  여행: 여행지, 숙소 검색

Options:
  --help  Show this message and exit.

Commands:
  foresttrip  산림청 숲나들예약 잔여석 조회
  hola-poke   올라포케 역삼점 메뉴/영업시간
  myrealtrip  마이리얼트립 숙소/패키지 검색
```

</details>

<details><summary>delivery --help</summary>

```
Usage: python -m cli_anything.k_skill.cli delivery [OPTIONS] COMMAND [ARGS]...

  배송: 택배 송장 조회

Options:
  --help  Show this message and exit.

Commands:
  delivery  택배 송장번호로 배송 조회
```

</details>

<details><summary>other --help</summary>

```
Usage: python -m cli_anything.k_skill.cli other [OPTIONS] COMMAND [ARGS]...

  기타: 기타 유틸리티

Options:
  --help  Show this message and exit.

Commands:
  iros           지식재산권 등록 자동화
  jangbu         한국식 장부/가계부
  privacy-terms  개인정보처리방침 생성
  setup          k-skill 초기 설정 마법사
```

</details>

<details><summary>nts --help</summary>

```
Usage: k-skill finance nts [OPTIONS] COMMAND [ARGS]...

  국세청 사업자등록 진위확인.

Options:
  --help  Show this message and exit.

Commands:
  status    사업자등록 상태조회.
  validate  사업자등록 진위확인.
```

</details>
