# cli-anything-k-skill

한국인을 위한 CLI 스킬 모음 — NomaDamas/k-skill의 86개 스킬을 CLI-Anything 프레임워크로 래핑.

에이전트가 `pip install cli-anything-k-skill` 후 즉시 사용 가능합니다.

## 특징

- **86개 한국 특화 스킬** — 날씨, 교통, 금융, 부동산, 쇼핑, 스포츠, 생활 유틸리티
- **13개 도메인** — 직관적인 카테고리 분류
- **JSON 모드** — `-j` 플래그로 에이전트가 쉽게 파싱
- **프록시 기반** — 18개 핵심 스킬은 추가 설치 없이 즉시 사용 (k-skill-proxy)
- **동적 로딩** — manifest.yaml 추가만으로 자동 스킬 발견

## 설치

```bash
pip install cli-anything-k-skill
```

## 사용법

```bash
# 날씨
k-skill weather forecast "서울" -j
k-skill weather dust --region "강남구" -j

# 교통
k-skill transit subway "강남역" -j
k-skill transit srt -j

# 금융
k-skill finance nts status "1234567890" -j
k-skill finance stock "삼성전자" -j

# 쇼핑
k-skill shopping naver-shop "맥북" -j
k-skill shopping olive-young "선크림" -j

# 생활
k-skill life gas --lat 37.5 --lon 127.0 -j
k-skill life waste "강남구" -j
k-skill life emergency-room --region "서울" -j

# 스포츠
k-skill sports kbo --date 2025-06-01 -j
k-skill sports lotto --round 1100 -j

# 유틸리티
k-skill list --all -j           # 전체 스킬 목록
k-skill setup check -j           # 의존성 상태
k-skill setup proxy -j           # 프록시 연결
```

## 도메인별 스킬 수

| 도메인 | 스킬 수 | 설명 |
|--------|--------|------|
| weather | 3 | 날씨/환경 (기상청, 미세먼지, 한강수위) |
| transit | 8 | 교통 (지하철, 버스, 기차, 항공) |
| life | 23 | 생활/편의 (주유소, 쓰레기, 주차장 등) |
| finance | 9 | 금융/공공 (사업자등록, 주식, 법률) |
| realestate | 5 | 부동산 (실거래가, LH, 경매) |
| shopping | 7 | 쇼핑 (네이버, 올리브영, 다이소 등) |
| market | 4 | 중고거래 (당근, 번개장터, 중고차) |
| search | 6 | 검색 (뉴스, 블로그, 특허) |
| document | 5 | 문서 (HWP, 맞춤법, 글자수) |
| sports | 8 | 스포츠/엔터 (KBO, KBL, LCK, 로또) |
| travel | 3 | 여행 (마이리얼트립) |
| delivery | 1 | 배송 (택배 송장) |
| other | 4 | 기타 유틸리티 |

## JSON 응답 형식

```json
// 성공
{"skill": "weather/forecast", "status": "success", "data": {...}, "meta": {"source": "kma", "response_time_ms": 120}}

// 실패
{"skill": "weather/forecast", "status": "error", "error": {"code": "PROXY_DOWN", "message": "프록시 연결 실패", "fix": "k-skill setup proxy"}}
```

## 아키텍처

```
cli_anything/k_skill/
├── cli.py              # 메인 CLI 엔트리포인트
├── loader.py           # manifest 로더 + 자동 발견
├── proxy.py            # k-skill-proxy HTTP 클라이언트
├── dependency.py       # 의존성 체커
├── output.py           # JSON/Human 출력 포맷터
├── mcp_client.py       # Remote MCP 클라이언트
├── local_mcp_bridge.py # Local MCP 브릿지
├── runner.py           # 범용 스크립트 실행기 (npm/pip/script/mcp)
└── skills/             # 13개 도메인 디렉토리
    ├── weather/        # 날씨/환경
    ├── transit/        # 교통
    ├── life/           # 생활
    ├── finance/        # 금융
    ├── realestate/     # 부동산
    ├── shopping/       # 쇼핑
    ├── market/         # 중고거래
    ├── search/         # 검색
    ├── document/       # 문서
    ├── sports/         # 스포츠
    ├── travel/         # 여행
    ├── delivery/       # 배송
    └── other/          # 기타
```

## 개발

```bash
# 설치
pip install -e ".[dev]"

# 테스트 (venv 환경에서 실행)
.venv/bin/pytest tests/ -v

# 의존성 상태
k-skill setup check -j
```

## 라이선스

MIT
