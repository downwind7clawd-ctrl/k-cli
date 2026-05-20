---
title: "k-skill CLI 래핑 아키텍처 설계"
created: 2026-05-21
tags: [k-skill, cli-anything, agent, architecture, korea]
status: draft
---

# k-skill CLI 래핑 아키텍처 설계

> **목표:** NomaDamas/k-skill(86개 한국 특화 스킬)을 CLI-Anything 프레임워크로 래핑하여, 모든 AI 에이전트(Hermes, Hubris/Gemini, OpenCode, Codex 등)가 상시 설치 없이 즉시 사용할 수 있는 단일 CLI 패키지로 제공

## 1. 배경

### 1.1 현재 문제

- **에이전트 종속성:** k-skill은 `~/.gemini/skills/`에 symlink 설치 → Hubris 전용. Hermes, OpenCode 등은 사용 불가
- **ductor 동기화 문제:** Gemini CLI 기반 ductor가 자동으로 symlink를 다른 경로(OpenCode 등)에 복제하여 통제 불능 상태
- **설치 복잡성:** `npx skills add --all` + npm 글로벌 패키지 N개 + Python 패키지 + API key 설정 + 프록시 서버 운영
- **확장성 부족:** 신규 스킬 추가 시 매번 symlink + 패키지 설치 + 설정 업데이트 반복

### 1.2 CLI-Anything이 해결할 수 있는 것

CLI-Anything은 HKUDS(홍콩대)에서 만든 에이전트 네이티브 CLI 래핑 프레임워크:

- **에이전트 독립:** Claude Code, OpenCode, Codex, OpenClaw, Gemini CLI 등 모든 코딩 에이전트 지원
- **SKILL.md 자동 생성:** 에이전트가 자동으로 CLI를 발견하고 사용 가능
- **CLI-Hub 배포:** `pip install` 한 번으로 설치 완료
- **JSON 출력 표준:** 모든 명령이 `--json` 플래그로 구조화된 응답 반환
- **standalone repo 지원:** 별도 저장소에서 개발 → registry.json에 등록만으로 허브에 등록

---

## 2. k-skill 스킬 분석

### 2.1 규모

- **총 스킬 수:** 86개 (2026-05-21 기준)
- **지속 증가 중:** 신규 스킬이 정기적으로 추가됨

### 2.2 의존성 분류

k-skill 스킬은 4가지 의존성 패턴으로 분류됨:

| 타입 | 수량 | 설명 | CLI 래핑 난이도 |
|------|------|------|----------------|
| **순수 프록시** | ~33개 | `k-skill-proxy.nomadamas.org` HTTP 호출만으로 동작 | ★☆☆ (최저) |
| **로컬 스크립트** | ~38개 | `scripts/` 폴더 내 Python/Node 헬퍼 실행 | ★★☆ (보통) |
| **npm 글로벌 패키지** | ~15개 | `kordoc`, `kbo-game`, `daiso` 등 npm 패키지 필요 | ★★☆ (보통) |
| **Python 패키지** | ~5개 | `SRTrain`, `korail2` 등 pip 패키지 필요 | ★★☆ (보통) |

### 2.3 순수 프록시 스킬 (래핑이 가장 쉬운 33개)

```
korean-stock-search, korea-weather, fine-dust-location, real-estate-search,
k-dart, kosis-stats, household-waste-info, library-book-search, naver-news-search,
naver-shopping-search, korean-law-search(법망 폴백), nts-business-registration,
kstartup-search, daangn-used-goods-search, daangn-realty-search, daangn-cars-search,
daangn-jobs-search, seoul-subway-arrival, seoul-density, sh-notice-search,
lh-notice-search, court-auction-notice-search, subway-lost-property,
k-schoollunch-menu, mfds-drug-safety, mfds-food-safety, korean-transit-route,
korean-character-count, korean-slang-writing, naver-blog-research, korean-scholarship-search,
korean-jangbu-for, korean-privacy-terms ...
```

이들 스킬은 **curl 한 줄**로 동작하므로 CLI-Anything의 Click 그룹에 HTTP 래퍼만 추가하면 됨.

### 2.4 도메인별 그룹핑 (CLI 커맨드 구조 기준)

```
k-skill (루트 CLI)
├── weather          # 날씨/환경 (korea-weather, fine-dust-location, han-river-water-level, seoul-density)
├── transit          # 교통/이동 (srt-booking, ktx-booking, express-bus, subway, parking, flight)
├── shopping         # 쇼핑 (coupang, daiso, olive-young, market-kurly, danawa, naver-shopping)
├── realestate       # 부동산 (real-estate, daangn-realty, gongsijiga, SH/LH 공고, 법원 경매)
├── sports           # 스포츠/엔터 (KBO, KBL, K리그, LCK, 영화관, 로또, 공연)
├── finance          # 법률/금융 (법령, 주식, DART, 코시스, 사업자등록, 토스증권)
├── market           # 중고거래 (당근, 번개장터, 중고차, 중고차가격)
├── search           # 검색 (네이버 뉴스, 블로그, 긱뉴스, 특허, 실록, 장학금)
├── document         # 문서 (HWP 읽기/편집, 맞춤법, 글자수)
├── delivery         # 배송 (택배송장)
├── life             # 생활 (생활쓰레기, 응급실, 주유소, 공중화장실, 기부처)
└── setup            # 설정 (k-skill-setup, k-skill-cleaner)
```

---

## 3. 아키텍처 설계

### 3.1 핵심 설계 원칙

> **"레포 클론 → CLI 설치 → 즉시 사용"**
> 신규 k-skill이 추가되면 최소한의 보일러플레이트만으로 자동 통합되어야 함

#### P1: Plug-in Skill Registry (자동 스킬 발견)
- `skills/` 디렉토리에 SKILL.md 파일만 놓으면 자동으로 CLI 서브커맨드로 등록
- manifest 파일 하나로 스킬 메타데이터 관리 (`skill.yaml` 또는 SKILL.md frontmatter)

#### P2: 의존성 자동 해결 (Prerequisite Chain)
- CLI 진입 시 의존성 체크 → 부족하면 자동 설치 또는 명확한 에러 메시지
- 3단계: ① 시스템 의존 (Node, Python) → ② 패키지 의존 (npm/pip) → ③ 런타임 의존 (API key, 프록시)

#### P3: 프록시 투명성
- `KSKILL_PROXY_BASE_URL` 환경변수로 프록시 전환
- 기본값: `https://k-skill-proxy.nomadamas.org`
- self-host 시: 로컬 프록시 주소로 오버라이드

#### P4: 확장 용이성
- 신규 스킬 추가 시 수정해야 할 파일 = **최대 2개** (스킬 디렉토리 + manifest)

### 3.2 전체 구조 (Standalone Repo)

```
cli-anything-k-skill/
├── pyproject.toml                    # 메타 패키지 (pip install cli-anything-k-skill)
├── SKILL.md                          # 루트 SKILL.md (에이전트 자동 발견용)
├── README.md
├── registry.json                     # 내부 스킬 레지스트리 (자동 생성 가능)
│
├── cli_anything/
│   └── k_skill/
│       ├── __init__.py
│       ├── cli.py                    # Click 진입점 (동적 서브커맨드 로딩)
│       ├── loader.py                 # 스킬 자동 발견 & 등록
│       ├── dependency.py             # 의존성 체크 & 설치
│       ├── proxy.py                  # 프록시 라우팅
│       ├── output.py                 # JSON/휴먼 출력 포맷터
│       └── skills/                   # ★ 스킬 구현 디렉토리 (확장 포인트)
│           ├── weather/
│           │   ├── __init__.py
│           │   ├── fine_dust.py      # Click 그룹 + 명령
│           │   └── weather.py
│           ├── transit/
│           │   ├── __init__.py
│           │   ├── srt.py
│           │   ├── ktx.py
│           │   └── subway.py
│           ├── shopping/
│           │   ├── __init__.py
│           │   ├── coupang.py
│           │   └── daiso.py
│           ├── ...                   # 도메인별 그룹
│           └── _templates/           # ★ 신규 스킬 보일러플레이트
│               └── new_skill.py.tpl
│
├── skills/                           # SKILL.md 파일들 (CLI-Anything 표준)
│   └── cli-anything-k-skill/
│       └── SKILL.md
│
├── tests/
│   ├── test_loader.py                # 스킬 자동 로딩 테스트
│   ├── test_dependency.py            # 의존성 체크 테스트
│   ├── test_proxy.py                 # 프록시 라우팅 테스트
│   └── test_skills/                  # 스킬별 단위 테스트 (mock)
│       ├── test_weather.py
│       └── test_transit.py
│
└── scripts/
    ├── generate_manifest.py          # SKILL.md → manifest 자동 생성
    └── add_skill.py                  # 신규 스킬 스캐폴딩
```

### 3.3 동적 스킬 로딩 메커니즘 (핵심)

```python
# cli_anything/k_skill/loader.py
"""
SKILL.md frontmatter 또는 manifest에서 스킬을 자동 발견하여
Click 서브커맨드로 동적 등록하는 로더.
"""
import importlib
from pathlib import Path

SKILLS_DIR = Path(__file__).parent / "skills"

def discover_skills():
    """skills/ 하위 도메인 디렉토리에서 모든 Click 그룹을 자동 발견"""
    groups = {}
    for domain_dir in sorted(SKILLS_DIR.iterdir()):
        if domain_dir.is_dir() and not domain_dir.name.startswith("_"):
            for py_file in domain_dir.glob("*.py"):
                module_name = f"cli_anything.k_skill.skills.{domain_dir.name}.{py_file.stem}"
                mod = importlib.import_module(module_name)
                if hasattr(mod, "cli"):
                    groups[domain_dir.name] = mod.cli
    return groups

def register_commands(main_cli):
    """메인 CLI에 발견된 도메인 그룹을 서브커맨드로 등록"""
    for name, group in discover_skills().items():
        main_cli.add_command(group, name=name)
```

### 3.4 의존성 관리 아키텍처

```
┌─────────────────────────────────────────────────┐
│              cli-anything-k-skill               │
│                                                 │
│  ┌─────────────────────────────────────────┐    │
│  │  Layer 1: 런타임 의존성 체크            │    │
│  │  - Node.js 18+ 존재 여부                │    │
│  │  - Python 3.10+ 존재 여부               │    │
│  │  - 필수 시스템 도구 (curl, jq)           │    │
│  └────────────────┬────────────────────────┘    │
│                   │                             │
│  ┌────────────────▼────────────────────────┐    │
│  │  Layer 2: 패키지 의존성 해결            │    │
│  │  - npm 글로벌 패키지 자동 체크/설치     │    │
│  │  - pip 패키지 자동 체크/설치             │    │
│  │  - 패키지별 버전 호환성 검증             │    │
│  └────────────────┬────────────────────────┘    │
│                   │                             │
│  ┌────────────────▼────────────────────────┐    │
│  │  Layer 3: 런타임 설정                   │    │
│  │  - API key 확인 (환경변수 / .env)        │    │
│  │  - 프록시 연결성 테스트                   │    │
│  │  - self-host 모드 감지                   │    │
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

의존성은 **스킬 manifest**에 선언적으로 정의:

```yaml
# skills/weather/manifest.yaml
domain: weather
skills:
  fine_dust:
    name: fine-dust
    display_name: 미세먼지 조회
    description: 지역 기준 PM10/PM2.5 미세먼지 조회
    requires:
      system: [curl]
      proxy: true
    category: utility
  weather:
    name: korea-weather
    display_name: 한국 날씨
    requires:
      proxy: true
    category: utility
```

```yaml
# skills/transit/manifest.yaml
domain: transit
skills:
  srt:
    name: srt-booking
    requires:
      python: [SRTrain, pycryptodome]
      auth: true  # 사용자 로그인 필요
  ktx:
    name: ktx-booking
    requires:
      python: [korail2, pycryptodome]
      auth: true
```

### 3.5 프록시 투명 라우팅

```python
# cli_anything/k_skill/proxy.py
import os
import httpx

DEFAULT_PROXY = "https://k-skill-proxy.nomadamas.org"

def get_proxy_base():
    return os.environ.get("KSKILL_PROXY_BASE_URL", DEFAULT_PROXY)

async def proxy_get(path: str, params: dict = None) -> dict:
    """프록시 또는 self-host 엔드포인트에 GET 요청"""
    base = get_proxy_base()
    url = f"{base}{path}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
```

### 3.6 신규 스킬 추가 플로우 (확장 용이성)

신규 스킬 추가는 **3단계**로 완료:

```
1. 스캐폴딩
   $ python scripts/add_skill.py --domain transit --name airport-lounge

   → skills/transit/airport_lounge.py 자동 생성 (보일러플레이트)
   → skills/transit/manifest.yaml 자동 업데이트
   → test_skills/test_transit.py에 빈 테스트 케이스 추가

2. 구현
   → airport_lounge.py에 비즈니스 로직 작성
   → 프록시 경로면 proxy_get() 호출만, 로컬이면 별도 로직

3. 검증
   $ pytest tests/ -v
   $ cli-anything-k-skill transit airport-lounge --help
```

**manifest.yaml만 업데이트하면 로더가 자동 발견**하므로, 레지스트리나 루트 CLI 코드를 수정할 필요 없음.

---

## 4. CLI-Anything 통합 방안

### 4.1 Standalone Repo 방식 (권장)

CLI-Anything의 **Option 2: Standalone repository** 패턴 사용:

- 독립 repo `downwind7clawd/cli-anything-k-skill` (또는 `NomaDamas/cli-anything-k-skill`)
- `pip install cli-anything-k-skill` 로 설치
- CLI-Anything의 `registry.json`에 PR 제출하여 CLI-Hub 등록

**registry.json 엔트리:**

```json
{
  "name": "k-skill",
  "display_name": "K-Skill (한국인을 위한 스킬 모음)",
  "version": "1.0.0",
  "description": "86+ Korean utility skills — weather, transit, shopping, real estate, sports, finance, and more. Zero-config with hosted proxy.",
  "requires": "curl, Python 3.10+",
  "homepage": "https://github.com/NomaDamas/k-skill",
  "source_url": "https://github.com/NomaDamas/cli-anything-k-skill",
  "install_cmd": "pip install cli-anything-k-skill",
  "entry_point": "cli-anything-k-skill",
  "skill_md": "https://github.com/NomaDamas/cli-anything-k-skill/blob/main/skills/cli-anything-k-skill/SKILL.md",
  "category": "search",
  "contributors": [
    {"name": "NomaDamas", "url": "https://github.com/NomaDamas"}
  ]
}
```

### 4.2 Monorepo 방식 (대안)

CLI-Anything monorepo 내 `k-skill/agent-harness/` 로 통합:

- 장점: CLI-Anything CI/CD 직접 활용
- 단점: 86개 스킬 규모가 monorepo에 부담, k-skill 독립 릴리스 주기와 충돌 가능

**→ standalone 방식 권장**

### 4.3 In-repo Harness vs Standalone 비교

| 측면 | In-repo | Standalone (권장) |
|------|---------|-------------------|
| 버전 관리 | monorepo 릴리스에 종속 | 독립 버전 관리 가능 |
| CI/CD | CLI-Anything 파이프라인 사용 | 자체 GitHub Actions |
| PR 프로세스 | CLI-Anything 리뷰어 필요 | 자체 리뷰 + registry PR만 |
| 패키지 배포 | `pip install git+...#subdirectory=k-skill` | `pip install cli-anything-k-skill` |
| 업데이트 주기 | CLI-Anything 머지 타이밍 | 자유로운 릴리스 |
| 스킬 규모 대응 | 86개 스킬은 무거움 | 독립적 가벼운 패키지 |

---

## 5. 기술 스펙

### 5.1 엔트리포인트

```toml
# pyproject.toml
[project]
name = "cli-anything-k-skill"
version = "1.0.0"
description = "CLI-Anything harness for k-skill: 86+ Korean utility skills"
requires-python = ">=3.10"
dependencies = [
    "click>=8.0",
    "httpx>=0.25",
    "pyyaml>=6.0",
]

[project.scripts]
cli-anything-k-skill = "cli_anything.k_skill.cli:main"
```

### 5.2 기본 사용 예시

```bash
# 설치
pip install cli-anything-k-skill

# 프록시 기반 스킬 (의존성 없이 즉시 사용)
cli-anything-k-skill weather fine-dust --region "서울 강남구" --json
cli-anything-k-skill finance stock-search --query "삼성전자" --json
cli-anything-k-skill transit subway --station "강남" --json
cli-anything-k-skill sports kbo --date 2026-05-21 --team "LG" --json

# 의존성 체크
cli-anything-k-skill setup check
cli-anything-k-skill setup install-deps  # 누락된 의존성 자동 설치

# Self-host 프록시
KSKILL_PROXY_BASE_URL=http://localhost:3456 cli-anything-k-skill weather fine-dust --region "부산"

# 목록
cli-anything-k-skill list --all
cli-anything-k-skill list --domain weather
cli-anything-k-skill list --category utility
```

### 5.3 JSON 출력 표준 (CLI-Anything 규격)

```json
{
  "skill": "fine-dust",
  "status": "success",
  "data": {
    "station": "강남구",
    "timestamp": "2026-05-21T14:00:00+09:00",
    "pm10": {"value": 35, "grade": "보통"},
    "pm25": {"value": 18, "grade": "좋음"},
    "overall_grade": "보통"
  },
  "meta": {
    "source": "k-skill-proxy",
    "response_time_ms": 142
  }
}
```

### 5.4 에러 처리

```json
{
  "skill": "srt-booking",
  "status": "error",
  "error": {
    "code": "MISSING_DEPENDENCY",
    "message": "SRTrain 패키지가 설치되어 있지 않습니다",
    "fix": "pip install SRTrain 또는 cli-anything-k-skill setup install-deps"
  }
}
```

---

## 6. 마이그레이션 로드맵

### Phase 1: 코어 인프라 (MVP)

- [ ] standalone repo 생성 & 프로젝트 스캐폴딩
- [ ] `cli.py` Click 라우터 + `loader.py` 동적 로딩
- [ ] `proxy.py` 프록시 라우팅
- [ ] `dependency.py` 3계층 의존성 체크
- [ ] `output.py` JSON/휴먼 출력 포맷터

### Phase 2: 순수 프록시 스킬 래핑 (33개)

- [ ] `add_skill.py` 스캐폴딩 스크립트
- [ ] weather 도메인 (4개 스킬)
- [ ] finance 도메인 (주식, DART, 코시스)
- [ ] transit 도메인 (지하철, 혼잡도)
- [ ] realestate 도메인 (실거래가, 공시지가, 공고문)
- [ ] life 도메인 (응급실, 주유소, 공중화장실)
- [ ] 단위 테스트 (mock 기반)

### Phase 3: 패키지 의존 스킬 래핑 (~53개)

- [ ] 로컬 스크립트 스킬 (38개)
- [ ] npm 글로벌 패키지 스킬 (15개)
- [ ] Python 패키지 스킬 (5개)
- [ ] 인증 필요 스킬 (SRT, KTX 등) — credential safe 패턴

### Phase 4: 배포 & 통합

- [ ] PyPI 배포 (`pip install cli-anything-k-skill`)
- [ ] CLI-Anything `registry.json` PR 제출
- [ ] CLI-Hub 등록
- [ ] SKILL.md 자동 생성 (에이전트 discoverable)
- [ ] GitHub Actions CI/CD

### Phase 5: k-skill 동기화

- [ ] k-skill 업스트림 변경 감지 스크립트
- [ ] 신규 스킬 자동 스캐폴딩 PR 생성 (옵션)
- [ ] 버전 관리 자동화

---

## 7. 위험 분석 및 대응

| 위험 | 확률 | 영향 | 대응 |
|------|------|------|------|
| k-skill 프록시 다운 | 보통 | 33개 스킬 장애 | self-host fallback + direct API fallback |
| 업스트림 스킬 API 변경 | 높음 | 개별 스킬 장애 | 버전별 핀 + 실패 시 명확한 에러 |
| npm/pip 패키지 의존성 충돌 | 보통 | 설치 실패 | 가상환경 권장 + 버전 핀 |
| 86개 스킬 테스트 커버리지 | 높음 | 품질 저하 | mock 기반 통합 테스트 + smoke test |
| CLI-Anything API 변경 | 낮음 | 빌드 실패 | 핀된 버전 사용 + 업데이트 추적 |

---

## 8. MCP 의존 스킬 처리 전략

k-skill의 MCP 의존 스킬은 **3가지 패턴**으로 분류됨. 각 패턴마다 CLI 래핑 전략이 다름.

### 8.1 패턴 분류

#### Pattern A: Remote MCP (HTTP/SSE) — 2개

MCP 서버가 원격에 호스팅되어 있고, Streamable HTTP 또는 SSE로 통신.

| 스킬 | 엔드포인트 | 프로토콜 |
|------|-----------|----------|
| `myrealtrip-search` | `https://mcp-servers.myrealtrip.com/mcp` | Streamable HTTP MCP |
| `hola-poke-yeoksam` | `https://hola-poke-yeoksam-skill.onrender.com/mcp` | Remote MCP |

**래핑 전략: CLI 내부 MCP HTTP 클라이언트**

```python
# cli_anything/k_skill/mcp_client.py
"""
Remote MCP 서버와 Streamable HTTP로 통신하는 클라이언트.
Python mcp SDK를 사용하지 않고 httpx로 직접 MCP 프로토콜을 구현.
"""
import httpx
import json

class RemoteMCPClient:
    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        self._request_id = 0

    async def initialize(self) -> dict:
        """MCP handshake - 프로토콜 버전 협상"""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                self.endpoint,
                json={"jsonrpc": "2.0", "method": "initialize",
                       "params": {"protocolVersion": "2025-03-26",
                                  "clientInfo": {"name": "cli-anything-k-skill", "version": "1.0.0"},
                                  "capabilities": {}},
                       "id": self._next_id()},
                headers={"Content-Type": "application/json"}
            )
            return resp.json()

    async def list_tools(self) -> list:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                self.endpoint,
                json={"jsonrpc": "2.0", "method": "tools/list",
                       "params": {}, "id": self._next_id()},
                headers={"Content-Type": "application/json"}
            )
            return resp.json().get("result", {}).get("tools", [])

    async def call_tool(self, tool_name: str, arguments: dict = None) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                self.endpoint,
                json={"jsonrpc": "2.0", "method": "tools/call",
                       "params": {"name": tool_name,
                                  "arguments": arguments or {}},
                       "id": self._next_id()},
                headers={"Content-Type": "application/json"}
            )
            return resp.json()

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id
```

**장점:**
- 추가 패키지 없이 `httpx`만으로 구현 (이미 의존성에 포함)
- MCP 프로토콜은 단순 JSON-RPC over HTTP
- 세션 관리 불필요 (stateless)

---

#### Pattern B: Local MCP Server (subprocess + stdio) — 2개

로컬에서 MCP 서버 프로세스를 띄우고 stdio로 JSON-RPC 통신.

| 스킬 | MCP 서버 | 방식 |
|------|---------|------|
| `coupang-product-search` | `retention-corp/coupang_partners/bin/coupang_mcp.py` | 로컬 클론 → subprocess |
| `catchtable-sniper` | Chrome MCP | 브라우저 자동화 (래핑 한계) |

**래핑 전략: Subprocess MCP 브릿지**

```python
# cli_anything/k_skill/local_mcp_bridge.py
"""
로컬 MCP 서버를 subprocess로 실행하고 stdio JSON-RPC로 통신.
MCP 프로토콜 = stdin/stdout 기반 JSON-RPC.
"""
import asyncio
import json
from typing import Optional

class LocalMCPBridge:
    def __init__(self, command: list, cwd: Optional[str] = None):
        self.command = command
        self.cwd = cwd
        self._process = None
        self._request_id = 0

    async def start(self):
        self._process = await asyncio.create_subprocess_exec(
            *self.command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.cwd
        )
        # initialize handshake
        await self._send({"jsonrpc": "2.0", "method": "initialize",
                          "params": {"protocolVersion": "2025-03-26",
                                     "clientInfo": {"name": "cli-anything-k-skill", "version": "1.0.0"},
                                     "capabilities": {}},
                          "id": self._next_id()})
        await self._read_response()

    async def call_tool(self, tool_name: str, arguments: dict = None) -> dict:
        await self._send({"jsonrpc": "2.0", "method": "tools/call",
                          "params": {"name": tool_name, "arguments": arguments or {}},
                          "id": self._next_id()})
        return await self._read_response()

    async def _send(self, payload: dict):
        self._process.stdin.write((json.dumps(payload) + "\n").encode())
        await self._process.stdin.drain()

    async def _read_response(self) -> dict:
        line = await self._process.stdout.readline()
        return json.loads(line.decode())

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id

    async def stop(self):
        if self._process:
            self._process.terminate()
            await self._process.wait()
```

**catchtable-sniper 한계:**
- Chrome MCP는 브라우저 프로세스 + DOM 조작 필요
- CLI 래핑으로 제어 가능하나, **설정 복잡도가 높고 에이전트 실행 환경에 GUI 의존**
- Phase 3 이후 optional 스킬로 분류 권장

---

#### Pattern C: MCP-originated but already replaced — 5개

원래 MCP 서버 기반이었으나, k-skill에서 이미 프록시 또는 CLI로 대체한 스킬들.

| 스킬 | 원래 MCP | 현재 대체 경로 | CLI 래핑 |
|------|---------|--------------|----------|
| `korean-stock-search` | `jjlabsio/korea-stock-mcp` | `k-skill-proxy` 프록시 | HTTP GET (프록시) |
| `real-estate-search` | `tae0y/real-estate-mcp` | `k-skill-proxy` 프록시 | HTTP GET (프록시) |
| `korean-cinema-search` | `hmmhmmhm/daiso-mcp` | `daiso` npm CLI | subprocess |
| `olive-young-search` | `hmmhmmhm/daiso-mcp` | `daiso` npm CLI | subprocess |
| `korean-law-search` | `korean-law-mcp` | CLI + 법망 fallback | subprocess + HTTP 폴백 |

**래핑 전략: 기존 대체 경로 그대로 사용 (MCP 코드 전혀 불필요)**

```python
# korean-law-search: CLI + HTTP fallback 체인
@click.command()
@click.argument("query")
def law_search(query):
    """한국 법령 검색"""
    import subprocess, shutil, httpx

    # 1차: 로컬 korean-law-mcp CLI
    if shutil.which("korean-law"):
        result = subprocess.run(
            ["korean-law", "search", query], capture_output=True, text=True
        )
        if result.returncode == 0:
            click.echo(result.stdout)
            return

    # 2차: 법망 HTTP fallback
    resp = httpx.get("https://api.beopmang.org/api/v4/law",
                     params={"action": "search", "query": query})
    click.echo(resp.json())
```

---

### 8.2 MCP 처리 아키텍처 요약

```
┌────────────────────────────────────────────────────────────┐
│                  cli-anything-k-skill                      │
│                                                            │
│  ┌──────────────────────────────────────────────────┐     │
│  │  mcp_client.py (Remote HTTP MCP)                 │     │
│  │  - httpx 기반 Streamable HTTP JSON-RPC           │     │
│  │  - myrealtrip-search, hola-poke-yeoksam          │     │
│  │  - 추가 패키지 불필요 (httpx만 사용)              │     │
│  └──────────────────────────────────────────────────┘     │
│                                                            │
│  ┌──────────────────────────────────────────────────┐     │
│  │  local_mcp_bridge.py (Subprocess stdio MCP)      │     │
│  │  - subprocess + asyncio stdin/stdout JSON-RPC     │     │
│  │  - coupang-product-search                        │     │
│  │  - git clone 자동화 + Python subprocess          │     │
│  └──────────────────────────────────────────────────┘     │
│                                                            │
│  ┌──────────────────────────────────────────────────┐     │
│  │  proxy.py (HTTP 프록시 — 기존 대체 경로)          │     │
│  │  - korean-stock-search, real-estate-search       │     │
│  │  - 프록시/CLI/Fallback 체인                       │     │
│  │  - MCP 코드 전혀 불필요                           │     │
│  └──────────────────────────────────────────────────┘     │
│                                                            │
│  ★ catchtable-sniper = Phase 3 이후 optional (GUI 필요)    │
└────────────────────────────────────────────────────────────┘
```

### 8.3 의존성 테이블 (최종)

| 타입 | 수량 | 처리 방식 | 추가 패키지 |
|------|------|----------|------------|
| 순수 프록시 (curl) | ~33개 | `proxy.py` HTTP GET | 없음 |
| Remote MCP (HTTP) | 2개 | `mcp_client.py` | 없음 (httpx 내장) |
| Local MCP (subprocess) | 1개* | `local_mcp_bridge.py` | 없음 (asyncio 내장) |
| npm CLI 래핑 | ~8개 | subprocess + JSON 파싱 | 해당 npm 패키지 |
| Python 스크립트 | ~5개 | subprocess 또는 임포트 | 해당 pip 패키지 |
| 인증 필요 | ~8개 | credential safe 패턴 | 사용자 환경변수 |
| CLI + HTTP 폴백 | ~5개 | 체인 호출 | 경우에 따라 |
| GUI/브라우저 필요 | 1개* | optional (Phase 3+) | playwright |

*catchtable-sniper은 브라우저 자동화 기반이므로 Phase 3 이후 optional로 분류

### 8.4 확장 시 신규 MCP 스킬 추가

앞으로 새로운 MCP 서버 기반 스킬이 k-skill에 추가되면:

```
1. Remote MCP → mcp_client.py 인스턴스 + manifest에 엔드포인트 선언
2. Local MCP → local_mcp_bridge.py 인스턴스 + manifest에 command 선언
3. 레지스트리/로더 코드 수정 불필요 (manifest 기반 자동 발견)
```

manifest.yaml 예시 (Remote MCP):

```yaml
# skills/travel/manifest.yaml
domain: travel
skills:
  myrealtrip:
    name: myrealtrip-search
    display_name: 마이리얼트립 검색
    description: 항공권, 숙소, 투어 검색
    mcp:
      type: remote_http
      endpoint: https://mcp-servers.myrealtrip.com/mcp
      protocol_version: "2025-03-26"
    category: travel
```

manifest.yaml 예시 (Local MCP):

```yaml
# skills/shopping/manifest.yaml
domain: shopping
skills:
  coupang:
    name: coupang-product-search
    display_name: 쿠팡 상품 검색
    mcp:
      type: local_stdio
      command: ["python3", "bin/coupang_mcp.py"]
      repo_url: https://github.com/retention-corp/coupang_partners.git
      cache_dir: ~/.cache/cli-anything-k-skill/coupang_partners
    category: retail
```

---

## 9. 참고 자료

- [[concepts/agent-webboard-idea]] | 이전 에이전트 웹보드 아이디어 (관련 배경)
- NomaDamas/k-skill: https://github.com/NomaDamas/k-skill
- HKUDS/CLI-Anything: https://github.com/HKUDS/CLI-Anything
- CLI-Hub: https://hkuds.github.io/CLI-Anything/hub/
- CLI-Anything CONTRIBUTING.md: Option 2 (Standalone Repository) 섹션
- MCP 프로토콜 사양: https://modelcontextprotocol.io/specification
