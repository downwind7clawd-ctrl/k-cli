# k-skill 최신 동기화 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** k-skill(upstream NomaDamas/k-skill) 최신 114개 스킬에 맞춰 k-cli 래퍼를 동기화한다 — 신규 21개 스킬 래핑 + 기존 구키명 14개를 신규 키로 갱신 + orphan 2개(data4library, neis-school-meal) 정리.

**Architecture:** k-cli는 각 도메인 디렉토리(`cli_anything/k_skill/skills/<domain>/__init__.py` + `manifest.yaml`)에 Click 명령어로 스킬을 래핑한다. 프록시 기반 스킬은 `safe_proxy_get(skill_name, "/v1/...", params)`를, 로컬 스크립트 기반 스킬은 `run_script("x.py", args, script_dirs=[K_SKILL_ROOT / "skill-name"])`를 호출한다. `loader.py`의 `discover_cli_groups()`가 `skills/` 하위를 자동 스캔하므로 신규 도메인 외엔 `cli.py` 수정 불필요. 도메인 매핑 표는 `docs/upstream-sync-guide.md` §도메인 매핑 규칙 참조.

**Tech Stack:** Python 3.11+, Click, httpx, PyYAML. 테스트: pytest. venv: `/home/david/nas_1tb/dev/k-cli/.venv`. 작업 위치: worktree `.worktrees/sync-2026-07-20` (브랜치 `sync-2026-07-20`). K_SKILL_ROOT 기본값 = `../k-skill` (project memory #389: `/home/david/nas_1tb/dev/k-skill`).

**사전 파악 결과:**
- k-skill은 이미 origin/main 최신 (behind 커밋 0). `git pull --ff-only` 완료.
- k-cli 현재 매핑 107개, k-skill 실제 스킬 114개 → 신규/누락 21개, 리네임/orphan 14개 확인.
- 프록시 라우트는 `packages/k-skill-proxy/src/server.js`에서 확인: `/v1/{assembly,fine-dust,han-river,household-waste,kopis,korean-holiday,korean-stock,kr-whois,lh-notice,data4library,naver-news,naver-shopping,nhis,nts-business,real-estate,seoul-subway,opinet,neis}/...`
- `gov-overseas-trip-report`, `naver-ad-performance`는 로컬 Python 스크립트 기반(프록시 아님) → `run_script` 패턴.

---

## 파일 구조 (변경 대상)

기존 도메인 `__init__.py` / `manifest.yaml` 수정 + 신규 도메인 1개(`civic` 또는 기존 `life`/`other` 활용). 도메인 매핑:

| k-skill 스킬 | k-cli 도메인 | 처리 |
|---|---|---|
| assembly-bill-vote-search | life (civic) | 신규 |
| cheap-gas-nearby | life | 기존 cheap-gas 리네임 |
| fine-dust-location | weather | 기존 fine-dust 리네임 |
| gov-overseas-trip-report | other | 신규(스크립트) |
| han-river-water-level | weather | 기존 han-river 리네임 |
| household-waste-info | life | 기존 household-waste 리네임 |
| jobkorea-talent-search | recruiting | 기존 jobkorea-talent 리네임 |
| k-schoollunch-menu | life | 신규 (neis-school-meal 대체) |
| kopis-performance-search | sports | 신규 |
| korean-holiday-calendar | life | 신규 |
| korean-stock-search | finance | 기존 korean-stock 리네임 |
| kr-whois-lookup | other | 신규 |
| lh-notice-search | realestate | 기존 lh-notice 리네임 |
| library-book-search | life | 신규 (data4library 대체) |
| naver-ad-performance | other | 신규(스크립트) |
| naver-news-search | search | 기존 naver-news 리네임 |
| naver-shopping-search | shopping | 기존 naver-shopping 리네임 |
| nhis-care-checkup-search | life | 신규 |
| nts-business-registration | finance | 기존 nts-business 리네임 |
| real-estate-search | realestate | 기존 real-estate 리네임 |
| seoul-subway-arrival | transit | 기존 seoul-subway 리네임 |

orphan 정리: `data4library`→`library-book-search`로 흡수, `neis-school-meal`→`k-schoollunch-menu`로 흡수(기존 명령 별칭 유지 권장).

---

## Task 1: weather 도메인 — fine-dust / han-river 리네임

**Files:**
- Modify: `cli_anything/k_skill/skills/weather/__init__.py`
- Modify: `cli_anything/k_skill/skills/weather/manifest.yaml`
- Test: `tests/skills/test_weather_sync.py` (신규)

- [ ] **Step 1: 실패 테스트 작성**

```python
# tests/skills/test_weather_sync.py
import pytest
from click.testing import CliRunner
from cli_anything.k_skill.skills.weather import cli as weather_cli
from cli_anything.k_skill.proxy import safe_proxy_get


def test_fine_dust_command_registered(monkeypatch):
    captured = {}
    def fake_get(name, path, params=None, timeout=None):
        captured["name"] = name
        captured["path"] = path
        return {"status": "success", "data": {}}
    monkeypatch.setattr("cli_anything.k_skill.skills.weather.safe_proxy_get", fake_get)
    runner = CliRunner()
    res = runner.invoke(weather_cli, ["dust", "서울 강남구", "-j"])
    assert res.exit_code == 0, res.output
    assert captured["name"] == "fine-dust-location"
    assert captured["path"] == "/v1/fine-dust/report"


def test_han_river_command_registered(monkeypatch):
    captured = {}
    def fake_get(name, path, params=None, timeout=None):
        captured["name"] = name
        captured["path"] = path
        return {"status": "success", "data": {}}
    monkeypatch.setattr("cli_anything.k_skill.skills.weather.safe_proxy_get", fake_get)
    runner = CliRunner()
    res = runner.invoke(weather_cli, ["han-river", "한강대교", "-j"])
    assert res.exit_code == 0, res.output
    assert captured["name"] == "han-river-water-level"
    assert captured["path"] == "/v1/han-river/water-level"
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `.venv/bin/pytest tests/skills/test_weather_sync.py -v`
Expected: FAIL (`fine-dust-location`/`han-river-water-level` 라우트가 아직 아님)

- [ ] **Step 3: 구현 — `__init__.py`의 `safe_proxy_get` 첫 인자/경로 갱신**

`weather/__init__.py`에서:
- `dust` 명령: `safe_proxy_get("fine-dust", "/v1/fine-dust/report", params)` → `safe_proxy_get("fine-dust-location", "/v1/fine-dust/report", params)`
- `han_river` 명령: `safe_proxy_get("han-river", "/v1/han-river/water-level", params)` (기존 경로가 `han-river/water-level`이 맞는지 확인 후 name만 `han-river-water-level`로)
- `error_response`의 첫 인자도 동일하게 갱신

- [ ] **Step 4: manifest.yaml 갱신**

```yaml
  dust:
    name: fine-dust-location
    display_name: 미세먼지 조회
    description: 에어코리아 기반 PM10/PM2.5 미세먼지 지역별 조회.
    category: utility
  han_river:
    name: han-river-water-level
    display_name: 한강 수위
    description: 한강홍수통제소 기반 관측소별 수위/유량 조회.
    category: utility
```

- [ ] **Step 5: 테스트 통과 확인**

Run: `.venv/bin/pytest tests/skills/test_weather_sync.py -v`
Expected: PASS

- [ ] **Step 6: 커밋**

```bash
git add cli_anything/k_skill/skills/weather/ tests/skills/test_weather_sync.py
git commit -m "sync(weather): fine-dust→fine-dust-location, han-river→han-river-water-level"
```

---

## Task 2: life 도메인 — household-waste / cheap-gas 리네임 + 신규 4개

**Files:**
- Modify: `cli_anything/k_skill/skills/life/__init__.py`
- Modify: `cli_anything/k_skill/skills/life/manifest.yaml`
- Test: `tests/skills/test_life_sync.py` (신규)

- [ ] **Step 1: 실패 테스트 작성**

```python
# tests/skills/test_life_sync.py
import pytest
from click.testing import CliRunner
from cli_anything.k_skill.skills.life import cli as life_cli


def _monk(monkeypatch, target):
    cap = {}
    def fake(name, path, params=None, timeout=None):
        cap["name"], cap["path"] = name, path
        return {"status": "success", "data": {}}
    monkeypatch.setattr(target, fake)
    return cap


def test_household_waste_renamed(monkeypatch):
    cap = _monk(monkeypatch, "cli_anything.k_skill.skills.life.safe_proxy_get")
    r = CliRunner().invoke(life_cli, ["waste", "강남구", "-j"])
    assert r.exit_code == 0, r.output
    assert cap["name"] == "household-waste-info"


def test_cheap_gas_renamed(monkeypatch):
    cap = _monk(monkeypatch, "cli_anything.k_skill.skills.life.safe_proxy_get")
    r = CliRunner().invoke(life_cli, ["gas", "--lat", "37.5", "--lon", "127.0", "-j"])
    assert r.exit_code == 0, r.output
    assert cap["name"] == "cheap-gas-nearby"


def test_korean_holiday_new(monkeypatch):
    cap = _monk(monkeypatch, "cli_anything.k_skill.skills.life.safe_proxy_get")
    r = CliRunner().invoke(life_cli, ["holiday", "--year", "2026", "-j"])
    assert r.exit_code == 0, r.output
    assert cap["name"] == "korean-holiday-calendar"
    assert cap["path"] == "/v1/korean-holiday/calendar"


def test_nhis_checkup_new(monkeypatch):
    cap = _monk(monkeypatch, "cli_anything.k_skill.skills.life.safe_proxy_get")
    r = CliRunner().invoke(life_cli, ["nhis", "checkup", "--operation", "list", "-j"])
    assert r.exit_code == 0, r.output
    assert cap["name"] == "nhis-care-checkup-search"
```

- [ ] **Step 2: 테스트 실패 확인** → `.venv/bin/pytest tests/skills/test_life_sync.py -v` (FAIL)

- [ ] **Step 3: 구현**

`life/__init__.py`:
- `waste` 명령: `safe_proxy_get("household-waste", ...)` → `safe_proxy_get("household-waste-info", "/v1/household-waste/info", params)`
- `gas` 명령: `safe_proxy_get("cheap-gas", "/v1/opinet/around", params)` → `safe_proxy_get("cheap-gas-nearby", "/v1/opinet/around", params)`
- 신규 `holiday` 명령 추가:
```python
@cli.command(name="holiday")
@click.option("--year", required=True, help="연도(YYYY)")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def holiday(year, as_json):
    """한국 공휴일 조회 (korean-holiday-calendar)."""
    resp = safe_proxy_get("korean-holiday-calendar", "/v1/korean-holiday/calendar", {"year": year})
    emit(resp, as_json=as_json)
```
- 신규 `nhis` 그룹 추가 (checkup / long-term-care):
```python
@cli.group(name="nhis")
def nhis():
    """국민건강보험 조회 (nhis-care-checkup-search)."""
    pass

@nhis.command(name="checkup")
@click.option("--operation", required=True, help="조회 작업")
@click.option("--json", "-j", "as_json", is_flag=True)
def nhis_checkup(operation, as_json):
    resp = safe_proxy_get("nhis-care-checkup-search", "/v1/nhis/checkup/%s" % operation, {})
    emit(resp, as_json=as_json)

@nhis.command(name="long-term-care")
@click.option("--json", "-j", "as_json", is_flag=True)
def nhis_ltc(as_json):
    resp = safe_proxy_get("nhis-care-checkup-search", "/v1/nhis/long-term-care", {})
    emit(resp, as_json=as_json)
```
- `library` 명령이 `data4library` 경유였다면 `library-book-search`로 갱신: `safe_proxy_get("library-book", "/v1/data4library/book-search", ...)` → `safe_proxy_get("library-book-search", "/v1/data4library/book-search", ...)` (name만 갱신, 경로 동일)
- 신규 `school-lunch` 명령 추가 (neis-school-meal 대체):
```python
@cli.group(name="school-lunch")
def school_lunch():
    """학교 급식 식단 조회 (k-schoollunch-menu)."""
    pass

@school_lunch.command(name="search")
@click.option("--name", required=True, help="학교명")
@click.option("--office", help="교육청명")
@click.option("--json", "-j", "as_json", is_flag=True)
def sl_search(name, office, as_json):
    params = {"schoolName": name}
    if office: params["officeName"] = office
    resp = safe_proxy_get("k-schoollunch-menu", "/v1/neis/school-meal", params)
    emit(resp, as_json=as_json)
```

- [ ] **Step 4: manifest.yaml 갱신** — `household-waste`, `cheap-gas` name 갱신 + `korean-holiday-calendar`, `nhis-care-checkup-search`, `library-book-search`, `k-schoollunch-menu` 엔트리 추가.

- [ ] **Step 5: 테스트 통과** → `.venv/bin/pytest tests/skills/test_life_sync.py -v` (PASS)

- [ ] **Step 6: 커밋** `git commit -m "sync(life): waste/gas rename + holiday/nhis/library/lunch new"`

---

## Task 3: finance 도메인 — korean-stock / nts-business 리네임

**Files:** Modify `cli_anything/k_skill/skills/finance/__init__.py`, `finance/manifest.yaml`, Test `tests/skills/test_finance_sync.py`

- [ ] **Step 1: 실패 테스트** — `stock` 명령이 `safe_proxy_get("korean-stock-search", ...)` 호출, `nts` 명령이 `safe_proxy_get("nts-business-registration", ...)` 호출 확인.
- [ ] **Step 2: 실패 확인** (FAIL)
- [ ] **Step 3: 구현** — `finance/__init__.py`:
  - stock: `safe_proxy_get("korean-stock", "/v1/korean-stock/search", ...)` → name=`korean-stock-search` (경로 `/v1/korean-stock/search`, `/v1/korean-stock/base-info`, `/v1/korean-stock/trade-info` 유지)
  - nts: `safe_proxy_get("nts-business", "/v1/nts-business/status", ...)` → name=`nts-business-registration` (경로 동일)
  - `error_response` 첫 인자도 동일 갱신
- [ ] **Step 4: manifest 갱신** — `korean-stock`→`korean-stock-search`, `nts-business`→`nts-business-registration`
- [ ] **Step 5: 통과 확인** `.venv/bin/pytest tests/skills/test_finance_sync.py -v`
- [ ] **Step 6: 커밋** `git commit -m "sync(finance): korean-stock/nts-business rename"`

---

## Task 4: search / shopping 도메인 — naver 뉴스/쇼핑 리네임

**Files:** Modify `search/__init__.py`, `search/manifest.yaml`, `shopping/__init__.py`, `shopping/manifest.yaml`, Test `tests/skills/test_search_shop_sync.py`

- [ ] **Step 1: 실패 테스트** — `search naver-news` → name `naver-news-search`; `shopping naver-shop` → name `naver-shopping-search`
- [ ] **Step 2: 실패 확인**
- [ ] **Step 3: 구현** — name만 갱신(`naver-news`→`naver-news-search`, `naver-shopping`→`naver-shopping-search`), 경로 `/v1/naver-news/search`, `/v1/naver-shopping/search` 유지. error_response 인자 동일 갱신.
- [ ] **Step 4: manifest 갱신**
- [ ] **Step 5: 통과** `.venv/bin/pytest tests/skills/test_search_shop_sync.py -v`
- [ ] **Step 6: 커밋**

---

## Task 5: realestate 도메인 — real-estate / lh-notice 리네임

**Files:** Modify `realestate/__init__.py`, `realestate/manifest.yaml`, Test `tests/skills/test_realestate_sync.py`

- [ ] **Step 1: 실패 테스트** — `realestate realestate` → name `real-estate-search`; `realestate lh` → name `lh-notice-search`
- [ ] **Step 2: 실패 확인**
- [ ] **Step 3: 구현** — name 갱신(`real-estate`→`real-estate-search`, `lh-notice`→`lh-notice-search`), 경로 `/v1/real-estate/region-code`, `/v1/real-estate/:assetType/:dealType`, `/v1/lh-notice/search`, `/v1/lh-notice/detail` 유지.
- [ ] **Step 4: manifest 갱신**
- [ ] **Step 5: 통과**
- [ ] **Step 6: 커밋**

---

## Task 6: transit 도메인 — seoul-subway 리네임

**Files:** Modify `transit/__init__.py`, `transit/manifest.yaml`, Test `tests/skills/test_transit_sync.py`

- [ ] **Step 1: 실패 테스트** — `transit subway` → name `seoul-subway-arrival`
- [ ] **Step 2: 실패 확인**
- [ ] **Step 3: 구현** — name `seoul-subway`→`seoul-subway-arrival`, 경로 `/v1/seoul-subway/arrival` 유지.
- [ ] **Step 4: manifest 갱신**
- [ ] **Step 5: 통과**
- [ ] **Step 6: 커밋**

---

## Task 7: recruiting 도메인 — jobkorea-talent 리네임

**Files:** Modify `recruiting/__init__.py`, `recruiting/manifest.yaml`, Test `tests/skills/test_recruiting_sync.py`

- [ ] **Step 1: 실패 테스트** — `recruiting jobkorea-talent` 호출 시 error_response/식별자 `jobkorea-talent-search` 사용 확인 (직접 HTTP 방식 유지, name만 갱신)
- [ ] **Step 2: 실패 확인**
- [ ] **Step 3: 구현** — `jobkorea-talent` 명령 내 `error_response("jobkorea-talent", ...)` → `error_response("jobkorea-talent-search", ...)`, help 텍스트의 upstream 명칭 갱신.
- [ ] **Step 4: manifest 갱신** — `jobkorea-talent`→`jobkorea-talent-search`
- [ ] **Step 5: 통과**
- [ ] **Step 6: 커밋**

---

## Task 8: sports 도메인 — kopis-performance-search 신규

**Files:** Modify `sports/__init__.py`, `sports/manifest.yaml`, Test `tests/skills/test_sports_sync.py`

- [ ] **Step 1: 실패 테스트** — `sports kopis performances` → name `kopis-performance-search`, path `/v1/kopis/performances`; `sports kopis facilities` → path `/v1/kopis/facilities`
- [ ] **Step 2: 실패 확인**
- [ ] **Step 3: 구현** — `kopis` 그룹 + `performances`/`facilities`/`detail` 명령 추가:
```python
@cli.group(name="kopis")
def kopis():
    """KOPIS 공연예술 조회 (kopis-performance-search)."""
    pass

@kopis.command(name="performances")
@click.option("--keyword", help="공연명")
@click.option("--json", "-j", "as_json", is_flag=True)
def kopis_perf(keyword, as_json):
    params = {"keyword": keyword} if keyword else {}
    resp = safe_proxy_get("kopis-performance-search", "/v1/kopis/performances", params)
    emit(resp, as_json=as_json)

@kopis.command(name="facilities")
@click.option("--json", "-j", "as_json", is_flag=True)
def kopis_fac(as_json):
    resp = safe_proxy_get("kopis-performance-search", "/v1/kopis/facilities", {})
    emit(resp, as_json=as_json)
```
- [ ] **Step 4: manifest 갱신** — `kopis-performance-search` 엔트리 추가
- [ ] **Step 5: 통과**
- [ ] **Step 6: 커밋**

---

## Task 9: other 도메인 — kr-whois + 스크립트 기반 2개 신규

**Files:** Modify `other/__init__.py`, `other/manifest.yaml`, Test `tests/skills/test_other_sync.py`

- [ ] **Step 1: 실패 테스트** — `other whois domain --q x.com` → name `kr-whois-lookup` path `/v1/kr-whois/domain`; `other gov-overseas providers` → run_script('gov_overseas_trip_report.py', ..., script_dirs=[K_SKILL_ROOT/"gov-overseas-trip-report"]); `other naver-ad doctor` → run_script('naver_ad_performance.py', ..., script_dirs=[K_SKILL_ROOT/"naver-ad-performance"])
- [ ] **Step 2: 실패 확인**
- [ ] **Step 3: 구현**
  - `whois` 그룹: `domain`/`as`/`ip` 서브커맨드, `safe_proxy_get("kr-whois-lookup", "/v1/kr-whois/{kind}", {"query": q})`
  - `gov-overseas` 그룹: `providers`/`list`/`detail`/`search`/`discover` 서브커맨드 → `asyncio.run(run_script("gov_overseas_trip_report.py", args, timeout=timeout, script_dirs=[K_SKILL_ROOT / "gov-overseas-trip-report"]))` + `emit`
  - `naver-ad` 그룹: `doctor`/`campaigns`/`adgroups`/`keywords`/`stats`/`keywordtool` → `asyncio.run(run_script("naver_ad_performance.py", args, timeout=timeout, script_dirs=[K_SKILL_ROOT / "naver-ad-performance"]))` + `emit`
  - import: `from cli_anything.k_skill.runner import run_script, K_SKILL_ROOT`
- [ ] **Step 4: manifest 갱신** — `kr-whois-lookup`, `gov-overseas-trip-report`(requires script), `naver-ad-performance`(requires script) 엔트리 추가
- [ ] **Step 5: 통과**
- [ ] **Step 6: 커밋**

---

## Task 10: assembly-bill-vote-search 신규 (life 도메인 civic)

**Files:** Modify `life/__init__.py`, `life/manifest.yaml`, Test `tests/skills/test_life_sync.py`(확장)

- [ ] **Step 1: 실패 테스트** — `life assembly bills --query x` → name `assembly-bill-vote-search` path `/v1/assembly/bills`; `life assembly votes --bill-id y` → path `/v1/assembly/votes`
- [ ] **Step 2: 실패 확인**
- [ ] **Step 3: 구현** — `assembly` 그룹 + `bills`/`votes`/`bill-detail` 서브커맨드:
```python
@cli.group(name="assembly")
def assembly():
    """열린국회 의안/표결 조회 (assembly-bill-vote-search)."""
    pass

@assembly.command(name="bills")
@click.option("--query", help="의안 검색어")
@click.option("--json", "-j", "as_json", is_flag=True)
def asm_bills(query, as_json):
    params = {"query": query} if query else {}
    resp = safe_proxy_get("assembly-bill-vote-search", "/v1/assembly/bills", params)
    emit(resp, as_json=as_json)

@assembly.command(name="votes")
@click.option("--bill-id", required=True, help="의안 ID")
@click.option("--json", "-j", "as_json", is_flag=True)
def asm_votes(bill_id, as_json):
    resp = safe_proxy_get("assembly-bill-vote-search", "/v1/assembly/votes", {"billId": bill_id})
    emit(resp, as_json=as_json)
```
- [ ] **Step 4: manifest 갱신** — `assembly-bill-vote-search` 엔트리 추가
- [ ] **Step 5: 통과**
- [ ] **Step 6: 커밋**

---

## Task 11: 통합 검증

- [ ] **Step 1: 전체 pytest** → `.venv/bin/pytest tests/ -q` (100% PASS)
- [ ] **Step 2: CLI 스모크** → `k-skill --help` (신규 도메인/명령 노출 확인), `k-skill list --all` 스킬 수 110→121 증가 확인
- [ ] **Step 3: 스킬 카운트 교차 검증** → k-cli manifest name 집합이 k-skill 114개와 일치(리네임/신규 반영)하는지 rtk grep으로 확인
- [ ] **Step 4: orphan 재확인** → `data4library`, `neis-school-meal`이 새 키로 흡수되었는지 확인
- [ ] **Step 5: BUGFIX_LOG.md 작성** → 날짜 헤더 + upstream 참조 + Removed/Added/Reimplemented 섹션 (워크플로우 #376)
- [ ] **Step 6: README 카운트 갱신** (110→121 스킬, 도메인 수 변동 시)

---

## Self-Review (작성자 체크)

1. **Spec coverage:** 신규 21개 전부 태스크에 매핑됨 (weather 2, life 6, finance 2, search/shop 2, realestate 2, transit 1, recruiting 1, sports 1, other 3, assembly 1 = 21). 리네임 14개: cheap-gas, fine-dust, han-river, household-waste, jobkorea-talent, korean-stock, lh-notice, naver-news, naver-shopping, nts-business, real-estate, seoul-subway (=12) + orphan data4library→library-book-search, neis-school-meal→k-schoollunch-menu (=2) = 14. ✓
2. **Placeholder scan:** 모든 step에 실제 코드/명령 포함. TBD 없음.
3. **Type consistency:** `safe_proxy_get(name, path, params)` 시그니처 일관. `run_script(name, args, script_dirs=[])` 시그니처 일관. `emit`/`error_response` 사용 일관.

**실행 전 주의:** 각 Task의 `safe_proxy_get` 경로는 `server.js` 실제 라우트와 정확히 대조할 것. `:operation`, `:assetType` 등 파라미터화 경로는 실제 upstream 호출 규격 확인 후 인자 매핑.
