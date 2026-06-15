# k-cli 전체 업데이트 및 리팩토링 계획

**날짜:** 2026-06-15
**목표:** 업스트림 NomaDamas/k-skill과 동기화 + 기술 부채 해소
**범위:** 10개 신규 스킬 + 기존 스킬 업데이트 + 전체 리팩토링

---

## Executive Summary

업스트림 NomaDamas/k-skill의 최신 변경 사항(2026-06-07 이후)을 k-cli에 동기화하고, 누적된 기술 부채를 해소하여 코드베이스의 일관성과 유지보수성을 향상시킵니다.

### 주요 변경 사항
- **신규 스킬 10개** 추가 (사업자 실사 6개, 윤문 1개, 선거 1개, 마라톤 1개, 증권 1개)
- **기존 스킬 업데이트** (SRT 좌석 탐색, 법령 검색 프록시 이동)
- **리팩토링** (조회 스텁 패턴 통합, 에러 응답 통일, 테스트 커버리지 확보)

---

## Phase 1: 기반 리팩토링 (3-4일)

> 신규 스킬 추가 전에 코드베이스의 기반을 다지는 단계

### 1.1 유틸리티 모듈 추가

**파일:** `cli_anything/k_skill/validators.py` (새 파일)

```python
"""입력 검증 유틸리티."""

def validate_nonempty(value, field_name="입력값"):
    """빈 문자열 검증, 에러 응답 반환."""
    if not value or not value.strip():
        return error_response("validator", "INVALID_INPUT", f"{field_name}을 입력하세요")
    return None

def clamp(value, min_val, max_val):
    """숫자 범위 클램핑."""
    return max(min_val, min(value, max_val))

def build_params(**kwargs):
    """None 값을 자동 제거한 파라미터 딕셔너리 반환."""
    return {k: v for k, v in kwargs.items() if v is not None}

def collect_env_vars(*keys):
    """환경변수를 안전하게 수집합니다."""
    import os
    return {k: os.environ[k] for k in keys if k in os.environ}

def clean_business_number(b_no):
    """사업자등록번호 정리 (하이픈 제거, 10자리 검증)."""
    import re
    digits = re.sub(r"[^0-9]", "", b_no)
    if len(digits) != 10:
        return None
    return digits
```

### 1.2 runner.py 동기 래퍼 추가

**파일:** `cli_anything/k_skill/runner.py`

```python
# 기존 async 함수들 아래에 추가

def run_npm_sync(package, args=None, **kwargs):
    """run_npm의 동기 래퍼."""
    return asyncio.run(run_npm(package, args, **kwargs))

def run_script_sync(script_name, args=None, **kwargs):
    """run_script의 동기 래퍼."""
    return asyncio.run(run_script(script_name, args, **kwargs))

def run_mcp_sync(skill_name, **kwargs):
    """run_mcp의 동기 래퍼."""
    return asyncio.run(run_mcp(skill_name, **kwargs))

def run_pip_import_sync(module_name, function_name, args=None, **kwargs):
    """run_pip_import의 동기 래퍼."""
    return asyncio.run(run_pip_import(module_name, function_name, args, **kwargs))
```

### 1.3 에러 응답 생성 통일

**영향 파일:** 12개 이상의 위치

기존 수동 에러 생성 패턴:
```python
# 변경 전 (12개 이상 위치)
emit({"skill": "fine-dust", "status": "error",
      "error": {"code": "INVALID_INPUT", "message": "지역명을 입력하세요"}},
     as_json=as_json)
```

변경 후:
```python
# 변경 후
from cli_anything.k_skill.output import error_response
emit(error_response("fine-dust", "INVALID_INPUT", "지역명을 입력하세요"),
     as_json=as_json)
```

**변경 대상 파일:**
- `skills/weather/__init__.py` (dust, han-river)
- `skills/transit/__init__.py` (subway)
- `skills/search/__init__.py` (naver-news)
- `skills/shopping/__init__.py` (naver-shop)
- `skills/life/__init__.py` (waste, library, drug, food)
- `skills/map/__init__.py` (kakao-search)
- `skills/realestate/__init__.py` (realestate/code)

### 1.4 manifest.yaml 일관성 정비

**변경 대상:**
- `skills/shopping/manifest.yaml`: `dependencies.proxy: true` 수정
- `skills/search/manifest.yaml`: `dependencies.proxy: true` 수정
- 모든 도메인에 `label` 필드 추가
- ktx, transit-route, foresttrip 스킬에 `env_keys` 추가

---

## Phase 2: 신규 스킬 추가 (5-6일)

### 2.1 프록시 기반 스킬 (4개) — 가장 쉬운 순서대로

#### 2.1.1 national-pension-workplace (국민연금 가입 사업장)
- **타입:** 프록시 기반 Python 스킬
- **스크립트:** `cli_anything/k_skill/scripts/national_pension_workplace.py`
- **프록시 라우트:** `GET /v1/national-pension/workplace`
- **변경:**
  - `skills/finance/__init__.py`에 새 명령어 추가
  - `skills/finance/manifest.yaml`에 스킬 엔트리 추가
  - upstream 스크립트를 `scripts/`로 복사

#### 2.1.2 fsc-corporate-info (금융위 법인 개요)
- **타입:** 프록시 기반 Python 스킬
- **스크립트:** `cli_anything/k_skill/scripts/fsc_corporate_info.py`
- **프록시 라우트:** `GET /v1/fsc/corp-outline`
- **변경:** finance 도메인에 추가

#### 2.1.3 g2b-sanctioned-supplier (부정당제재업체)
- **타입:** 프록시 기반 Python 스킬
- **스크립트:** `cli_anything/k_skill/scripts/g2b_sanctioned_supplier.py`
- **프록시 라우트:** `GET /v1/g2b/sanctioned-supplier`
- **변경:** finance 도메인에 추가

#### 2.1.4 korean-law-search 프록시 이동
- **변경:** `skills/finance/__init__.py`의 `korean_law` 명령어 수정
- **이전:** 로컬 MCP 호출 (`local://korean-law-mcp`)
- **이후:** 프록시 호출 (`/v1/korean-law/search`, `/v1/korean-law/detail`)
- **스크립트:** `cli_anything/k_skill/scripts/korean_law.py` (upstream에서 복사)

### 2.2 직접 호출 스킬 (3개)

#### 2.2.1 nts-tax-delinquency (국세 체납 명단)
- **타입:** 직접 호출 (무인증 공개 검색)
- **스크립트:** `cli_anything/k_skill/scripts/nts_tax_delinquency.py`
- **프록시 불필요:** nts.go.kr 직접 스크래핑
- **변경:** finance 도메인에 추가

#### 2.2.2 localdata-business-status (인허가 영업상태)
- **타입:** 직접 호출 (무인증 CSV 다운로드)
- **스크립트:** `cli_anything/k_skill/scripts/localdata_business_status.py`
- **데이터 파일:** `cli_anything/k_skill/data/localdata_industries.json`, `localdata_orgcodes.json`
- **변경:** life 도메인에 추가

#### 2.2.3 biz-health-check (사업자 실사 복합)
- **타입:** 복합 스킬 (6개 단품 조합)
- **스크립트:** `cli_anything/k_skill/scripts/biz_health_check.py`
- **의존성:** 위 6개 스킬의 스크립트가 같은 디렉토리 구조에 있어야 함
- **변경:** life 도메인에 추가 (복합이므로 life가 적합)

### 2.3 하이브리드 스킬 (3개)

#### 2.3.1 korean-humanizer (AI 윤문) — Python 프롬프트 기반
- **타입:** 프롬프트/지식 기반 (스크립트 없음)
- **구현:** `skills/document/__init__.py`에 새 명령어 추가
- **참조:** upstream `korean-humanizer/SKILL.md`의 403줄 지식 베이스
- **변경:**
  - `skills/document/__init__.py`에 `humanizer` 명령어 추가
  - `skills/document/manifest.yaml`에 스킬 엔트리 추가
  - SKILL.md의 지식을 docstring에 포함

#### 2.3.2 local-election-candidate-search (지방선거) — Python 스크래핑
- **타입:** 직접 스크래핑 (Python)
- **스크립트:** `cli_anything/k_skill/scripts/local_election_candidate_search.py`
- **타겟:** `https://info.nec.go.kr/search/searchCandidate.xhtml`
- **변경:** life 도메인의 기존 `election` 명령어 수정 (upstream 스크립트로 교체)

#### 2.3.3 korean-marathon-schedule (마라톤) — Python 스크래핑
- **타입:** 직접 스크래핑 (Python)
- **스크립트:** `cli_anything/k_skill/scripts/korean_marathon_schedule.py`
- **타겟:** `https://gorunning.kr/races/`
- **변경:** sports 도메인에 추가

### 2.4 npm 패키지 스킬 (1개)

#### 2.4.1 toss-securities (토스증권)
- **타입:** npm 패키지 (OAuth2 인증)
- **패키지:** `toss-securities` (upstream npm 패키지)
- **환경변수:** `TOSSINVEST_CLIENT_ID`, `TOSSINVEST_CLIENT_SECRET`, `TOSSINVEST_ACCOUNT`
- **변경:** finance 도메인에 추가
- **주의:** 사용자 인증 필요

---

## Phase 3: 기존 스킬 업데이트 (2-3일)

### 3.1 SRT 예매 개선
- **파일:** `cli_anything/k_skill/scripts/srt_booking.py`, `scripts/srt_seats.py`
- **변경 내용:**
  - 좌석 탐색 우선순위 개선
  - `--car-no`, `--available-only`, `--seat` 옵션 추가
  - `--car-priority`, `--seat-priority` 옵션 추가
- **변경:** `skills/transit/__init__.py`의 `srt` 명령어 업데이트

### 3.2 korean-law-search 프록시 이동
- **이전:** 로컬 MCP (`local://korean-law-mcp`)
- **이후:** 프록시 (`/v1/korean-law/search`)
- **변경:** `skills/finance/__init__.py`의 `korean_law` 명령어 수정

---

## Phase 4: 테스트 및 검증 (2-3일)

### 4.1 기반 리팩토링 테스트
- `tests/test_validators.py` (새 파일)
- 기존 테스트 파일 업데이트 (에러 응답 패턴 변경 반영)

### 4.2 신규 스킬 테스트
- `tests/test_national_pension.py`
- `tests/test_fsc_corporate.py`
- `tests/test_g2b_sanction.py`
- `tests/test_nts_tax_delinquency.py`
- `tests/test_localdata_business.py`
- `tests/test_biz_health_check.py`
- `tests/test_korean_humanizer.py`
- `tests/test_local_election.py`
- `tests/test_korean_marathon.py`
- `tests/test_toss_securities.py`

### 4.3 통합 테스트
- `tests/test_phase2_skills.py` 업데이트 (스킬 수 87 → 97+)
- `k-skill list --all -j`로 전체 스킬 수 확인
- `k-skill setup check -j`로 의존성 상태 확인

### 4.4 문서 업데이트
- `SKILL.md` 업데이트 (스킬 수 89 → 97+)
- `README.md` 업데이트
- `BUGFIX_LOG.md`에 변경 이력 기록

---

## 구현 순서 및 의존성

```
Phase 1 (기반 리팩토링)
    │
    ├─ 1.1 유틸리티 모듈
    ├─ 1.2 runner 동기 래퍼
    ├─ 1.3 에러 응답 통일
    └─ 1.4 manifest 정비
    │
    ▼
Phase 2 (신규 스킬)
    │
    ├─ 2.1 프록시 기반 (4개) — 독립적
    ├─ 2.2 직접 호출 (3개) — 독립적
    ├─ 2.3 하이브리드 (3개) — 독립적
    └─ 2.4 npm 패키지 (1개) — 독립적
    │
    ▼
Phase 3 (기존 업데이트)
    │
    ├─ 3.1 SRT 개선
    └─ 3.2 법령 검색 프록시 이동
    │
    ▼
Phase 4 (테스트/검증)
    │
    ├─ 4.1-4.3 테스트
    └─ 4.4 문서
```

---

## 리스크 및 대응

| 리스크 | 확률 | 영향 | 대응 |
|--------|------|------|------|
| 업스트림 스크립트와 k-cli 구조 불일치 | 높음 | 중간 | 스크립트 커스터마이징 필요 시 주석으로 명시 |
| 프록시 라우트 미반영 | 중간 | 높음 | 프록시 서버 배포 확인 후 테스트 |
| 테스트 커버리지 부족 | 중간 | 중간 | 스모크 테스트 + 통합 테스트로 커버 |
| 의존성 충돌 | 낮음 | 높음 | 가상환경 격리 + 버전 핀 |

---

## 성공 기준

1. **스킬 수:** 87개 → 97개 이상 (10개 신규 추가)
2. **테스트 커버리지:** 6.7% → 50% 이상
3. **에러 응답 일관성:** 수동 생성 12개 → 0개
4. **코드 중복:** 조회 스텁 30+개 → 유틸리티 함수 사용
5. **manifest 일관성:** label, proxy, env_keys 전부 정비

---

## 참고 자료

- 업스트림 레포: `/tmp/k-skill-upstream/`
- 현재 k-cli: `/home/david/nas_1tb/dev/k-cli/`
- BUGFIX_LOG: `/home/david/nas_1tb/dev/k-cli/BUGFIX_LOG.md`
- AGENTS.md: `/home/david/nas_1tb/dev/k-cli/AGENTS.md` (맥거핀 프로젝트)
