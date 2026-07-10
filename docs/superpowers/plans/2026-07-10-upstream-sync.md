# k-cli ↔ k-skill Upstream 동기화 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** upstream `NomaDamas/k-skill`에 누락된 16개 신규 스킬을 로컬 `k-cli`(Python Click 래퍼)에 포팅하여 95 → 111 스킬로 현행화한다.

**Architecture:** 로컬 `k-cli`는 얇은 CLI 래퍼다. 무거운 로직(스크립트/npm 패키지)은 `K_SKILL_ROOT`(기본 `/home/david/nas_1tb/dev/k-skill`, upstream 클론)의 `scripts/`·`packages/`에 이미 존재한다. 따라서 포팅 = (1) `skills/<domain>/__init__.py`에 Click 명령어를 만들고, (2) 적절한 백엔드(`run_npm` / `run_script` / `safe_proxy_get` / 직접 httpx / 의존성 스텁)로 위임하며, (3) `manifest.yaml`을 작성한다. 신규 도메인은 `loader.discover_cli_groups()`가 자동 발견하므로 `cli.py` 수정은 헬프 텍스트뿐이다.

**Tech Stack:** Python 3.10+, Click 8, httpx, pytest, asyncio. 백엔드 위임 모듈: `cli_anything.k_skill.runner`(`run_npm`, `run_script`, `run_pip_import`), `cli_anything.k_skill.proxy`(`safe_proxy_get`/`safe_proxy_post`), `cli_anything.k_skill.dependency`(`SkillDependency`, `check_dependency`), `cli_anything.k_skill.output`(`emit`, `success_response`, `error_response`).

**핵심 참조 파일 (각 작업자 MUST READ):**
- 패턴 템플릿: `cli_anything/k_skill/skills/weather/__init__.py`, `.../skills/finance/__init__.py`
- 러너 시그니처: `cli_anything/k_skill/runner.py` (`run_npm` L135, `run_script` L205)
- 프록시: `cli_anything/k_skill/proxy.py` (`safe_proxy_get` L92)
- 의존성: `cli_anything/k_skill/dependency.py`
- 테스트 패턴: `tests/test_seoul_bike.py`, `tests/test_phase2_skills.py`
- upstream 소스(클론됨): `/tmp/opencode/k-skill-upstream` — 각 스킬의 `SKILL.md`와 `packages/<name>/package.json`(bin 확인)를 읽어 정확한 인자/엔드포인트/파라미터를 추출할 것.

---

## File Structure

**Create (신규 도메인/스킬):**
- `cli_anything/k_skill/skills/fortune/__init__.py` + `manifest.yaml`  (saju-fortune, naming-house)
- `cli_anything/k_skill/skills/business/__init__.py` + `manifest.yaml`  (biz-health-check, court-payment-order-assistant, d2b-notice-search, g2b-order-plan-search, localdata-business-status, popbill, s2b-notice-search)
- `cli_anything/k_skill/skills/recruiting/__init__.py` + `manifest.yaml`  (job-posting-match, jobkorea-talent-search, saramin-talent-search)
- `cli_anything/k_skill/skills/messaging/__init__.py` + `manifest.yaml`  (kakaotalk-mac)
- `cli_anything/k_skill/skills/life/__init__.py` (EXTEND: kakao-bar-nearby, lovebug-report, yebigun-training 추가) + `manifest.yaml` (EXTEND)
- `tests/test_fortune.py`, `tests/test_business.py`, `tests/test_recruiting.py`, `tests/test_messaging.py`, `tests/test_life_ext.py`

**Modify:**
- `cli_anything/k_skill/cli.py` (헬프 텍스트: Commands 목록, 스킬 카운트, 에이전트 빠른 실행 가이드)
- `pyproject.toml` (버전 CalVer bump)
- `tests/test_phase2_skills.py` (DOMAINS 리스트 + `test_total_skill_count` 기대값)

**백엔드 분류 (16개):**
| 도메인 | 스킬 | 백엔드 | 비고 |
|---|---|---|---|
| fortune | saju-fortune | `run_npm('saju-fortune')` | npm 패키지 필요 |
| fortune | naming-house | `run_npm('naming-house')` | npm 패키지 필요 |
| business | biz-health-check | `safe_proxy_get` 집계 | 기존 finance 라우트 재사용, 키 불필요 |
| business | court-payment-order-assistant | `run_npm('court-payment-order-assistant')` | npm 패키지 |
| business | d2b-notice-search | `run_npm('d2b-notice-search')` | npm 패키지 |
| business | g2b-order-plan-search | `safe_proxy_get('/v1/g2b/order-plans')` | 프록시(서버측 DATA_GO_KR_API_KEY) |
| business | localdata-business-status | 직접 httpx (inline) | localdata.go.kr 공공 API |
| business | popbill | 의존성 스텁 + `run_script` | pip `popbill` SDK + env 키 필요 |
| business | s2b-notice-search | `run_npm('s2b-notice-search')` | npm 패키지 |
| recruiting | job-posting-match | 직접 httpx (inline) | 공개 채용 API |
| recruiting | jobkorea-talent-search | 직접 httpx (inline) | 공개 채용 API |
| recruiting | saramin-talent-search | `run_npm('saramin-talent-search')` | npm 패키지 |
| messaging | kakaotalk-mac | `run_script('kakaotalk_mac.py')` | macOS 전용 |
| life+ | kakao-bar-nearby | `run_npm('kakao-bar-nearby')` | npm 패키지 |
| life+ | lovebug-report | `run_npm('lovebug-report')` | npm 패키지 |
| life+ | yebigun-training | `run_npm('yebigun-training')` | npm 패키지(playwright-core) |

---

## Task 1: Scaffold — cli.py 헬프 + pyproject 버전

**Files:**
- Modify: `cli_anything/k_skill/cli.py:11-26` (Commands 목록), `cli.py:57` (카운트), `cli.py:68-144` (에이전트 빠른 실행 가이드)
- Modify: `pyproject.toml` (version)

- [ ] **Step1: cli.py Commands 목록에 신규 도메인 추가**

`cli.py` 라인 11-26 블록 끝(`delivery ...` / `life ...` / `travel ...` 행 뒤)에 다음 4행 삽입:
```python
    fortune     사주/작명 (사주 운세, 작명소)
    business    비즈니스/법무/조달 (사업체건강, 법원진행, 나라장터, 사업자등록)
    recruiting  채용 (이력서 매칭, 잡코리아/사람인 인재검색)
    messaging   메시징 (카카오톡 macOS 아카이브)
```

- [ ] **Step2: cli.py 카운트 텍스트 갱신**

`cli.py:57` 의 `k-skill — 한국인을 위한 CLI 스킬 모음 (95개 스킬)` → `(111개 스킬)` 로 변경.

- [ ] **Step3: 에이전트 빠른 실행 가이드에 신규 섹션 추가**

`cli.py` 라인 144(`k-skill setup proxy -j`) 뒤, 라인 146(`───...`) 앞에 삽입:
```python
    사주/작명:
      k-skill fortune saju-fortune "1990-05-15 14:30" --sex M -j
      k-skill fortune naming-house "김철수" --birth "1990-05-15" -j

    비즈니스/법무/조달:
      k-skill business biz-health-check --b-no 1248100998 --name "삼성전자" -j
      k-skill business court-payment --case-no "2024가단12345" -j
      k-skill business d2b-notice --keyword "소프트웨어" --limit 10 -j
      k-skill business g2b-order-plan --instNm "조달청" --limit 10 -j
      k-skill business localdata-status --biz-name "커피월드" -j
      k-skill business popbill config-check -j
      k-skill business s2b-notice --keyword "AI" --limit 10 -j

    채용:
      k-skill recruiting job-posting-match --resume-file resume.txt --location 서울 -j
      k-skill recruiting jobkorea-talent --keyword "퍼포먼스 마케터" --work-area 서울 -j
      k-skill recruiting saramin-talent --keyword "백엔드" --location 서울 -j

    메시징:
      k-skill messaging kakaotalk-mac index --query "회의록" -j

    생활(추가):
      k-skill life kakao-bar --query "강남" -j
      k-skill life lovebug-report search --query "중랑" -j
      k-skill life yebigun-training training-info -j
```

- [ ] **Step4: pyproject.toml 버전 bump**

`version = "2026.06.15.1"` → `version = "2026.07.10.1"`.

- [ ] **Step5: import smoke 테스트**

Run: `cd /home/david/nas_1tb/dev/k-cli && python -c "import cli_anything.k_skill.cli; print('ok')"`
Expected: `ok`

- [ ] **Step6: Commit**

```bash
git add cli_anything/k_skill/cli.py pyproject.toml
git commit -m "chore: scaffold upstream-sync help text + version bump to 111 skills"
```

---

## Task 2: fortune 도메인 (saju-fortune, naming-house)

**Files:**
- Create: `cli_anything/k_skill/skills/fortune/__init__.py`
- Create: `cli_anything/k_skill/skills/fortune/manifest.yaml`
- Test: `tests/test_fortune.py`

- [ ] **Step1: upstream SKILL.md 분석**

Run:
```bash
sed -n '1,80p' /tmp/opencode/k-skill-upstream/saju-fortune/SKILL.md
cat /tmp/opencode/k-skill-upstream/packages/saju-fortune/package.json | grep -A3 '"bin"'
```
`bin` 이름과 CLI 인자(생년월일/성별/음력 등)를 확인한다. naming-house도 동일하게 분석.

- [ ] **Step2: 실패 테스트 작성 (TDD)**

`tests/test_fortune.py`:
```python
from unittest.mock import patch
from click.testing import CliRunner
from cli_anything.k_skill.cli import main

class TestFortune:
    @patch("cli_anything.k_skill.skills.fortune.run_npm")
    def test_saju_calls_npm(self, mock_run):
        import asyncio
        mock_run.return_value = {"status": "success", "data": {}}
        runner = CliRunner()
        result = runner.invoke(main, ["fortune", "saju-fortune", "1990-05-15 14:30", "--sex", "M", "-j"])
        assert result.exit_code == 0
        mock_run.assert_called_once()
        # 첫 인자(package)가 saju-fortune 임을 확인
        assert mock_run.call_args[0][0] == "saju-fortune"

    @patch("cli_anything.k_skill.skills.fortune.run_npm")
    def test_naming_calls_npm(self, mock_run):
        import asyncio
        mock_run.return_value = {"status": "success", "data": {}}
        runner = CliRunner()
        result = runner.invoke(main, ["fortune", "naming-house", "김철수", "--birth", "1990-05-15", "-j"])
        assert result.exit_code == 0
        assert mock_run.call_args[0][0] == "naming-house"
```

- [ ] **Step3: 테스트 실패 확인**

Run: `cd /home/david/nas_1tb/dev/k-cli && python -m pytest tests/test_fortune.py -q`
Expected: FAIL (module `fortune` 없음)

- [ ] **Step4: __init__.py 구현**

`cli_anything/k_skill/skills/fortune/__init__.py`:
```python
"""사주/작명 스킬 — 사주 운세, 이름 짓기."""

import asyncio
import click

from cli_anything.k_skill.runner import run_npm
from cli_anything.k_skill.output import emit


@click.group(name='fortune', help='사주/작명: 사주 운세, 작명소')
def cli():
    pass


@cli.command(name='saju-fortune', help='사주 운세 (생년월일시/성별)')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.option('--sex', help='성별 (M/F)')
@click.argument('query', required=False)
def saju_fortune(query, sex, as_json, timeout):
    """사주 운세 조회."""
    args = [query] if query else []
    if sex:
        args += ['--sex', sex]
    result = asyncio.run(run_npm('saju-fortune', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='naming-house', help='작명소 (이름 짓기)')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.option('--birth', help='생년월일 (YYYY-MM-DD)')
@click.argument('query', required=False)
def naming_house(query, birth, as_json, timeout):
    """작명소 (이름 추천)."""
    args = [query] if query else []
    if birth:
        args += ['--birth', birth]
    result = asyncio.run(run_npm('naming-house', args, timeout=timeout))
    emit(result, as_json=as_json)
```
> NOTE: upstream SKILL.md에서 확인한 실제 인자명(--sex, --birth 등)으로 옵션을 조정한다. 누락 인자는 upstream `bin` CLI에 맞춰 추가한다.

- [ ] **Step5: manifest.yaml 작성**

`cli_anything/k_skill/skills/fortune/manifest.yaml`:
```yaml
domain: fortune
description: 사주/작명 (사주 운세, 작명소)
dependencies:
  proxy: false
  npm: ["saju-fortune", "naming-house"]
  python: []
  env_keys: []
skills:
  saju_fortune:
    name: saju-fortune
    display_name: 사주 운세
    description: 사주 기반 운세 조회 (npm saju-fortune)
    category: fortune
  naming_house:
    name: naming-house
    display_name: 작명소
    description: 성명학 기반 이름 추천 (npm naming-house)
    category: fortune
```

- [ ] **Step6: 테스트 통과 확인**

Run: `python -m pytest tests/test_fortune.py -q`
Expected: PASS

- [ ] **Step7: Commit**

```bash
git add cli_anything/k_skill/skills/fortune tests/test_fortune.py
git commit -m "feat: add fortune domain (saju-fortune, naming-house)"
```

---

## Task 3: business 도메인 (7개, 혼합 백엔드)

**Files:**
- Create: `cli_anything/k_skill/skills/business/__init__.py`
- Create: `cli_anything/k_skill/skills/business/manifest.yaml`
- Test: `tests/test_business.py`

이 도메인은 7개 스킬이 각기 다른 백엔드를 쓴다. 공통 패턴은 Task 2의 `run_npm` 래퍼다. 아래는 스킬별 차이점만 명시한다.

- [ ] **Step1: upstream SKILL.md 일괄 분석**

```bash
for d in biz-health-check court-payment-order-assistant d2b-notice-search g2b-order-plan-search localdata-business-status popbill s2b-notice-search; do
  echo "=== $d ==="
  sed -n '1,60p' /tmp/opencode/k-skill-upstream/$d/SKILL.md
  [ -f /tmp/opencode/k-skill-upstream/packages/$d/package.json ] && grep -A3 '"bin"' /tmp/opencode/k-skill-upstream/packages/$d/package.json
done
```

- [ ] **Step2: 실패 테스트 작성**

`tests/test_business.py` (각 백엔드 mock):
```python
import asyncio
from unittest.mock import patch
from click.testing import CliRunner
from cli_anything.k_skill.cli import main

class TestBusiness:
    @patch("cli_anything.k_skill.skills.business.run_npm")
    def test_court_calls_npm(self, mock_run):
        mock_run.return_value = {"status": "success", "data": {}}
        r = CliRunner()
        res = r.invoke(main, ["business", "court-payment", "--case-no", "2024가단12345", "-j"])
        assert res.exit_code == 0 and mock_run.call_args[0][0] == "court-payment-order-assistant"

    @patch("cli_anything.k_skill.skills.business.run_npm")
    def test_d2b_calls_npm(self, mock_run):
        mock_run.return_value = {"status": "success", "data": {}}
        r = CliRunner()
        res = r.invoke(main, ["business", "d2b-notice", "--keyword", "AI", "-j"])
        assert res.exit_code == 0 and mock_run.call_args[0][0] == "d2b-notice-search"

    @patch("cli_anything.k_skill.skills.business.run_npm")
    def test_s2b_calls_npm(self, mock_run):
        mock_run.return_value = {"status": "success", "data": {}}
        r = CliRunner()
        res = r.invoke(main, ["business", "s2b-notice", "--keyword", "AI", "-j"])
        assert res.exit_code == 0 and mock_run.call_args[0][0] == "s2b-notice-search"

    @patch("cli_anything.k_skill.skills.business.safe_proxy_get")
    def test_g2b_calls_proxy(self, mock_get):
        mock_get.return_value = {"status": "success", "data": {}}
        r = CliRunner()
        res = r.invoke(main, ["business", "g2b-order-plan", "--instNm", "조달청", "-j"])
        assert res.exit_code == 0
        assert mock_get.call_args[0][1] == "/v1/g2b/order-plans"

    @patch("cli_anything.k_skill.skills.business.httpx.Client")
    def test_localdata_direct_http(self, mock_client):
        import cli_anything.k_skill.skills.business as b
        resp = type("R", (), {"raise_for_status": lambda self: None, "json": lambda self: {"status":"success","data":{}}})()
        mock_client.return_value.__enter__.return_value.get.return_value = resp
        r = CliRunner()
        res = r.invoke(main, ["business", "localdata-status", "--biz-name", "커피월드", "-j"])
        assert res.exit_code == 0
```

- [ ] **Step3: 테스트 실패 확인** → `python -m pytest tests/test_business.py -q` → FAIL

- [ ] **Step4: __init__.py 구현**

`cli_anything/k_skill/skills/business/__init__.py`:
```python
"""비즈니스/법무/조달 스킬 — 사업체건강, 법원진행, 나라장터, 사업자등록."""

import asyncio
import click
import httpx

from cli_anything.k_skill.proxy import safe_proxy_get
from cli_anything.k_skill.runner import run_npm, run_script
from cli_anything.k_skill.output import emit, error_response
from cli_anything.k_skill.dependency import SkillDependency, check_dependency


@click.group(name='business', help='비즈니스/법무/조달')
def cli():
    pass


# npm 기반 (court-payment, d2b, s2b)
@cli.command(name='court-payment', help='법원 경매/지급명령 진행조회')
@click.option('--json', '-j', 'as_json', is_flag=True)
@click.option('--timeout', '-t', default=30, type=int)
@click.argument('query', required=False)
def court_payment(query, as_json, timeout):
    args = [query] if query else []
    result = asyncio.run(run_npm('court-payment-order-assistant', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='d2b-notice', help='D2B 나라장터 입찰공고 검색')
@click.option('--json', '-j', 'as_json', is_flag=True)
@click.option('--timeout', '-t', default=30, type=int)
@click.option('--keyword', help='검색어')
@click.option('--limit', default=10, type=int)
@click.argument('query', required=False)
def d2b_notice(query, keyword, limit, as_json, timeout):
    args = [query] if query else []
    if keyword: args += ['--keyword', keyword]
    args += ['--limit', str(limit)]
    result = asyncio.run(run_npm('d2b-notice-search', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='s2b-notice', help='S2B 나라장터 판로/사업 검색')
@click.option('--json', '-j', 'as_json', is_flag=True)
@click.option('--timeout', '-t', default=30, type=int)
@click.option('--keyword', help='검색어')
@click.option('--limit', default=10, type=int)
@click.argument('query', required=False)
def s2b_notice(query, keyword, limit, as_json, timeout):
    args = [query] if query else []
    if keyword: args += ['--keyword', keyword]
    args += ['--limit', str(limit)]
    result = asyncio.run(run_npm('s2b-notice-search', args, timeout=timeout))
    emit(result, as_json=as_json)


# 프록시 기반 (g2b-order-plan)
@cli.command(name='g2b-order-plan', help='조달청 나라장터 발주계획 조회')
@click.option('--json', '-j', 'as_json', is_flag=True)
@click.option('--instNm', help='발주기관명')
@click.option('--limit', default=10, type=int)
@click.argument('query', required=False)
def g2b_order_plan(query, instnm, limit, as_json):
    params = {"numOfRows": min(max(limit, 1), 100)}
    if query: params["q"] = query
    if instnm: params["instNm"] = instnm
    resp = safe_proxy_get("g2b-order-plan", "/v1/g2b/order-plans", params)
    emit(resp, as_json=as_json)


# 직접 httpx 기반 (localdata-business-status)
@cli.command(name='localdata-status', help='통합데이터지도 지역사업체 영업상태 조회')
@click.option('--json', '-j', 'as_json', is_flag=True)
@click.option('--biz-name', required=True, help='사업체명')
@click.option('--biz-type', help='업종명')
def localdata_status(biz_name, biz_type, as_json):
    params = {"bizNm": biz_name}
    if biz_type: params["bizType"] = biz_type
    try:
        with httpx.Client(timeout=15) as client:
            resp = client.get(
                "https://localdata.go.kr/platform/rest/congruentBussEnlarge/getBBBList.json",
                params=params,
            )
            resp.raise_for_status()
            emit({"status": "success", "data": resp.json()}, as_json=as_json)
    except httpx.HTTPStatusError as e:
        emit(error_response("localdata-business-status", "HTTP_ERROR", f"HTTP {e.response.status_code}"), as_json=as_json)
    except Exception as e:
        emit(error_response("localdata-business-status", "UNKNOWN", str(e)), as_json=as_json)


# 프록시 집계 기반 (biz-health-check)
@cli.command(name='biz-health-check', help='사업체 건강진단 (국세청/국민연금/금융위/부정당 집계)')
@click.option('--json', '-j', 'as_json', is_flag=True)
@click.option('--b-no', required=True, help='사업자등록번호(10자리)')
@click.option('--name', help='상호명')
def biz_health_check(b_no, name, as_json):
    # 기존 finance 프록시 라우트 재사용 (키 불필요)
    results = {}
    base = {"bizno": b_no}
    for tag, path in [
        ("nts", "/v1/nts-business/status"),
        ("national_pension", "/v1/national-pension/workplace"),
        ("fsc", "/v1/fsc/corp-outline"),
        ("g2b_sanction", "/v1/g2b/sanctioned-supplier"),
    ]:
        r = safe_proxy_get(tag, path, base)
        results[tag] = r
    emit({"status": "success", "data": results}, as_json=as_json)


# 의존성 스텁 기반 (popbill)
@cli.command(name='popbill', help='팝빌 전자세금계산서/문서 조회 (API 키 필요)')
@click.option('--json', '-j', 'as_json', is_flag=True)
@click.option('--timeout', '-t', default=30, type=int)
@click.argument('query', required=False)
def popbill(query, as_json, timeout):
    import os
    dep = SkillDependency(
        name="popbill",
        python=["popbill"],
        env_keys=["POPBILL_LinkID", "POPBILL_SECRET_KEY", "POPBILL_CORP_NUM"],
    )
    report = asyncio.run(check_dependency(dep))
    if not report.ready:
        emit(error_response(
            "popbill", "MISSING_DEPENDENCY",
            "팝빌 SDK 또는 API 키가 없습니다.",
            fix="pip install popbill && 환경변수 설정: " + ", ".join(report.missing_env or []),
        ), as_json=as_json)
        return
    args = [query] if query else []
    result = asyncio.run(run_script("popbill_cli.py", args, timeout=timeout))
    emit(result, as_json=as_json)
```
> NOTE: `court-payment`/`d2b`/`s2b`의 실제 인자명은 upstream SKILL.md + `packages/<name>/package.json`의 `bin` CLI에 맞춰 조정. `localdata-status`의 정확한 엔드포인트/파라미터는 upstream SKILL.md에서 추출. `biz-health-check`는 finance에 이미 존재하는 4개 라우트를 재사용.

- [ ] **Step5: manifest.yaml 작성**

`cli_anything/k_skill/skills/business/manifest.yaml`:
```yaml
domain: business
description: 비즈니스/법무/조달 (사업체건강, 법원진행, 나라장터, 사업자등록)
dependencies:
  proxy: true
  npm:
    - court-payment-order-assistant
    - d2b-notice-search
    - s2b-notice-search
  python: []
  env_keys:
    - POPBILL_LinkID
    - POPBILL_SECRET_KEY
    - POPBILL_CORP_NUM
skills:
  biz_health_check:
    name: biz-health-check
    display_name: 사업체 건강진단
    description: 국세청/국민연금/금융위/부정당 집계 조회
    category: business
  court_payment:
    name: court-payment-order-assistant
    display_name: 법원 진행조회
    description: 법원 경매/지급명령 진행내역 조회
    category: business
  d2b_notice:
    name: d2b-notice-search
    display_name: D2B 공고검색
    description: 나라장터 D2B 입찰공고 검색
    category: business
  g2b_order_plan:
    name: g2b-order-plan-search
    display_name: 조달 발주계획
    description: 조달청 나라장터 발주계획현황 조회
    category: business
  localdata_status:
    name: localdata-business-status
    display_name: 지역사업체 상태
    description: 통합데이터지도 지역사업체 영업상태 조회
    category: business
  popbill:
    name: popbill
    display_name: 팝빌
    description: 팝빌 전자세금계산서/문서 조회 (API 키 필요)
    category: business
  s2b_notice:
    name: s2b-notice-search
    display_name: S2B 검색
    description: 나라장터 S2B 판로/사업 검색
    category: business
```

- [ ] **Step6: 테스트 통과 + import 확인**

Run:
```bash
python -m pytest tests/test_business.py -q
python -c "from cli_anything.k_skill.skills.business import cli; print('ok')"
```
Expected: PASS, ok

- [ ] **Step7: Commit**

```bash
git add cli_anything/k_skill/skills/business tests/test_business.py
git commit -m "feat: add business domain (7 skills, mixed backends)"
```

---

## Task 4: recruiting 도메인 (job-posting-match, jobkorea-talent-search, saramin-talent-search)

**Files:**
- Create: `cli_anything/k_skill/skills/recruiting/__init__.py`
- Create: `cli_anything/k_skill/skills/recruiting/manifest.yaml`
- Test: `tests/test_recruiting.py`

- [ ] **Step1: upstream SKILL.md 분석** (job-posting-match, jobkorea-talent-search, saramin-talent-search) — 인자/엔드포인트 추출. `saramin-talent-search`는 `packages/saramin-talent-search` 존재 시 `run_npm`, 아니면 직접 httpx.

- [ ] **Step2: 실패 테스트 작성** (`tests/test_recruiting.py`) — run_npm(inline) 또는 httpx.Client mock로 각 명령이 올바른 백엔드를 호출하는지 assert. 패턴은 Task 3 테스트 참조.

- [ ] **Step3: 테스트 실패 확인** → FAIL

- [ ] **Step4: __init__.py 구현**

`job-posting-match`와 `jobkorea-talent-search`는 공개 채용 API를 직접 호출(공개 키 불필요):
```python
"""채용 스킬 — 이력서 매칭, 인재검색."""

import asyncio
import click

from cli_anything.k_skill.runner import run_npm
from cli_anything.k_skill.output import emit


@click.group(name='recruiting', help='채용: 이력서 매칭, 인재검색')
def cli():
    pass


@cli.command(name='job-posting-match', help='이력서 기반 채용공고 매칭')
@click.option('--json', '-j', 'as_json', is_flag=True)
@click.option('--timeout', '-t', default=30, type=int)
@click.option('--resume-file', help='이력서 파일 경로')
@click.option('--resume-text', help='이력서 텍스트')
@click.option('--location', help='희망 지역')
@click.option('--limit', default=10, type=int)
def job_posting_match(resume_file, resume_text, location, limit, as_json, timeout):
    args = []
    if resume_file: args += ['--resume-file', resume_file]
    if resume_text: args += ['--resume-text', resume_text]
    if location: args += ['--location', location]
    args += ['--limit', str(limit)]
    # 공개 채용 API 직접 호출 백엔드 (upstream SKILL.md의 엔드포인트 사용)
    result = asyncio.run(run_npm('job-posting-match', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='jobkorea-talent', help='잡코리아 인재검색')
@click.option('--json', '-j', 'as_json', is_flag=True)
@click.option('--timeout', '-t', default=30, type=int)
@click.option('--keyword', help='검색 키워드')
@click.option('--work-area', help='근무지역')
@click.option('--career-min', default=0, type=int)
@click.option('--career-max', default=10, type=int)
@click.option('--limit', default=20, type=int)
def jobkorea_talent(keyword, work_area, career_min, career_max, limit, as_json, timeout):
    args = []
    if keyword: args += ['--keyword', keyword]
    if work_area: args += ['--work-area', work_area]
    args += ['--career-min', str(career_min), '--career-max', str(career_max), '--limit', str(limit)]
    result = asyncio.run(run_npm('jobkorea-talent-search', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='saramin-talent', help='사람인 인재검색')
@click.option('--json', '-j', 'as_json', is_flag=True)
@click.option('--timeout', '-t', default=30, type=int)
@click.option('--keyword', help='검색 키워드')
@click.option('--location', help='지역')
@click.option('--limit', default=20, type=int)
def saramin_talent(keyword, location, limit, as_json, timeout):
    args = []
    if keyword: args += ['--keyword', keyword]
    if location: args += ['--location', location]
    args += ['--limit', str(limit)]
    result = asyncio.run(run_npm('saramin-talent-search', args, timeout=timeout))
    emit(result, as_json=as_json)
```
> NOTE: `job-posting-match`/`jobkorea-talent-search`는 upstream에 전용 스크립트가 없으므로 직접 호출 백엔드로 구현한다. upstream SKILL.md의 실제 엔드포인트/파라미터로 `run_npm` 대신 직접 httpx 호출로 교체할 것(필요 시). `saramin-talent-search`는 `packages/saramin-talent-search` 존재 시 `run_npm`.

- [ ] **Step5: manifest.yaml 작성** (3개 스킬, category: recruiting, npm 의존성 명시)

- [ ] **Step6: 테스트 통과** → `python -m pytest tests/test_recruiting.py -q` → PASS

- [ ] **Step7: Commit**

```bash
git add cli_anything/k_skill/skills/recruiting tests/test_recruiting.py
git commit -m "feat: add recruiting domain (job-posting-match, jobkorea/saramin talent)"
```

---

## Task 5: messaging 도메인 (kakaotalk-mac)

**Files:**
- Create: `cli_anything/k_skill/skills/messaging/__init__.py`
- Create: `cli_anything/k_skill/skills/messaging/manifest.yaml`
- Test: `tests/test_messaging.py`

- [ ] **Step1: upstream SKILL.md 분석** — `kakaotalk-mac`는 `scripts/kakaotalk_mac.py`(이미 `K_SKILL_ROOT/scripts`에 존재)를 `run_script`로 호출. CLI 인자(index/search 등) 확인.

- [ ] **Step2: 실패 테스트 작성** (`tests/test_messaging.py`) — `run_script` mock, `kakaotalk_mac.py` 호출 assert.

- [ ] **Step3: 테스트 실패** → FAIL

- [ ] **Step4: __init__.py 구현**
```python
"""메시징 스킬 — 카카오톡 macOS 아카이브 검색."""

import asyncio
import click

from cli_anything.k_skill.runner import run_script
from cli_anything.k_skill.output import emit


@click.group(name='messaging', help='메시징: 카카오톡 macOS 아카이브')
def cli():
    pass


@cli.command(name='kakaotalk-mac', help='카카오톡 macOS 대화 아카이브 검색 (macOS 전용)')
@click.option('--json', '-j', 'as_json', is_flag=True)
@click.option('--timeout', '-t', default=60, type=int)
@click.argument('query', required=False)
def kakaotalk_mac(query, as_json, timeout):
    """카카오톡 macOS 아카이브 검색."""
    args = [query] if query else []
    result = asyncio.run(run_script('kakaotalk_mac.py', args, timeout=timeout))
    emit(result, as_json=as_json)
```

- [ ] **Step5: manifest.yaml 작성** (category: messaging, macOS 전용 명시, `skills.kakaotalk_mac` 엔트리)

- [ ] **Step6: 테스트 통과** → `python -m pytest tests/test_messaging.py -q` → PASS

- [ ] **Step7: Commit**

```bash
git add cli_anything/k_skill/skills/messaging tests/test_messaging.py
git commit -m "feat: add messaging domain (kakaotalk-mac)"
```

---

## Task 6: life 도메인 확장 (kakao-bar-nearby, lovebug-report, yebigun-training)

**Files:**
- Modify: `cli_anything/k_skill/skills/life/__init__.py` (3개 명령 추가)
- Modify: `cli_anything/k_skill/skills/life/manifest.yaml` (3개 엔트리 추가)
- Test: `tests/test_life_ext.py`

> 주의: `life` 도메인에 이미 동일 스킬이 있는지 먼저 확인한다(`grep -n "kakao-bar\|lovebug\|yebigun" cli_anything/k_skill/skills/life/manifest.yaml`). 없을 때만 추가.

- [ ] **Step1: upstream SKILL.md 분석** — `kakao-bar-nearby`(packages/kakao-bar-nearby), `lovebug-report`(packages/lovebug-report), `yebigun-training`(packages/yebigun-training, playwright-core 의존)의 인자/CLI 확인.

- [ ] **Step2: 실패 테스트 작성** (`tests/test_life_ext.py`) — `run_npm` mock, 3개 명령 각각 패키지명 assert.

- [ ] **Step3: 테스트 실패** → FAIL

- [ ] **Step4: life/__init__.py에 3개 명령 추가** (기존 코드 끝에 append):
```python
@cli.command(name='kakao-bar', help='주변 카카오 맥주/술집 검색')
@click.option('--json', '-j', 'as_json', is_flag=True)
@click.option('--timeout', '-t', default=30, type=int)
@click.option('--query', help='지역명/키워드')
def kakao_bar(query, as_json, timeout):
    args = [query] if query else []
    result = asyncio.run(run_npm('kakao-bar-nearby', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='lovebug-report', help='lovebug.com 모기 지수/제보 검색')
@click.option('--json', '-j', 'as_json', is_flag=True)
@click.option('--timeout', '-t', default=30, type=int)
@click.argument('query', required=False)
def lovebug_report(query, as_json, timeout):
    args = [query] if query else []
    result = asyncio.run(run_npm('lovebug-report', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='yebigun-training', help='예비군 훈련일정/메뉴 조회 (playwright 필요)')
@click.option('--json', '-j', 'as_json', is_flag=True)
@click.option('--timeout', '-t', default=60, type=int)
@click.argument('query', required=False)
def yebigun_training(query, as_json, timeout):
    args = [query] if query else []
    result = asyncio.run(run_npm('yebigun-training', args, timeout=timeout))
    emit(result, as_json=as_json)
```

- [ ] **Step5: life/manifest.yaml에 3개 엔트리 추가** (category: life, npm 의존성 `kakao-bar-nearby`/`lovebug-report`/`yebigun-training` 를 `dependencies.npm`에 추가)

- [ ] **Step6: 테스트 통과** → `python -m pytest tests/test_life_ext.py -q` → PASS

- [ ] **Step7: Commit**

```bash
git add cli_anything/k_skill/skills/life tests/test_life_ext.py
git commit -m "feat: extend life domain (kakao-bar, lovebug-report, yebigun-training)"
```

---

## Task 7: 통합 테스트 + 기존 테스트 갱신

**Files:**
- Modify: `tests/test_phase2_skills.py` (DOMAINS 리스트 + `test_total_skill_count`)

- [ ] **Step1: test_phase2_skills.py DOMAINS 리스트 갱신**

라인 12-26 `DOMAINS`에 신규 도메인 추가 + life 카운트 23→26:
```python
    ("fortune", 2),
    ("business", 7),
    ("recruiting", 3),
    ("messaging", 1),
    ("life", 26),   # 기존 23 + 3 (kakao-bar, lovebug-report, yebigun-training)
```
나머지 기존 항목(weather 3, transit 9, finance 13, realestate 5, shopping 7, search 6, market 4, document 7, sports 8, travel 3, delivery 1, other 4)는 그대로.

- [ ] **Step2: test_total_skill_count 갱신**

라인 258-262 `test_total_skill_count`:
```python
    def test_total_skill_count(self):
        all_skills = list_all_skills()
        # 95 (기존) + 16 (신규) = 111
        assert len(all_skills) >= 111
```

- [ ] **Step3: 전체 테스트 스위트 실행**

Run: `cd /home/david/nas_1tb/dev/k-cli && python -m pytest tests/ -q`
Expected: 모두 PASS (133 → 약 150+)

- [ ] **Step4: CLI 등록/도움말 확인**

Run:
```bash
k-skill list --all -j | python -c "import sys,json; d=json.load(sys.stdin); print(len(d['data']))"
k-skill fortune --help
k-skill business --help
k-skill recruiting --help
k-skill messaging --help
k-skill life --help
```
Expected: list --all JSON `data` 배열 길이 ≥ 111; 각 `--help`에 신규 명령 표시.

- [ ] **Step5: Commit**

```bash
git add tests/test_phase2_skills.py
git commit -m "test: update skill count to 111 and register new domains"
```

---

## Task 8: 최종 검증 + 통합 커밋

- [ ] **Step1: lint/타입 점검**

Run: `cd /home/david/nas_1tb/dev/k-cli && python -m pyflakes cli_anything/k_skill/skills/fortune cli_anything/k_skill/skills/business cli_anything/k_skill/skills/recruiting cli_anything/k_skill/skills/messaging cli_anything/k_skill/skills/life 2>/dev/null || python -m py_compile cli_anything/k_skill/skills/*/__init__.py && echo COMPILE_OK`
Expected: COMPILE_OK (문법 오류 없음)

- [ ] **Step2: 전체 회귀 테스트 최종 실행**

Run: `python -m pytest tests/ -q`
Expected: PASS

- [ ] **Step3: BUGFIX_LOG 기록**

`BUGFIX_LOG.md` 상단에 날짜 헤더(`## 2026-07-10`)와 Added 섹션에 16개 신규 스킬 + 4 신규 도메인 기록.

- [ ] **Step4: 최종 커밋 (이미 Task별 커밋 완료 시 생략 가능)**

```bash
git status --short   # 미커밋 파일 없음 확인
git log --oneline -8
```

---

## 검증 체크리스트 (완료 기준)

- [ ] `fortune`(2) / `business`(7) / `recruiting`(3) / `messaging`(1) 도메인 자동 발견되어 `k-skill list --all`에 노출
- [ ] `life` 도메인에 `kakao-bar` / `lovebug-report` / `yebigun-training` 추가 (23→26)
- [ ] 전체 스킬 수 95 → 111
- [ ] `pytest tests/ -q` 전체 PASS
- [ ] npm/직접호출 스킬은 `K_SKILL_ROOT`의 패키지·스크립트가 없으면 `run_npm`/`run_script`가 친절한 `MISSING_DEPENDENCY` 오류 반환
- [ ] `popbill`은 키/SDK 미설치 시 `MISSING_DEPENDENCY` + 설치 안내 반환 (스텁)
- [ ] `cli.py` 헬프에 신규 도메인 4개 + life 3개 추가, 카운트 111로 갱신
- [ ] `pyproject.toml` 버전 `2026.07.10.1`
