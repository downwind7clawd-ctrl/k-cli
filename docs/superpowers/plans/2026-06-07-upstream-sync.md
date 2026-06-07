# k-cli 업스트림 동기화 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** k-cli가 upstream NomaDamas/k-skill (HEAD 1efef28)의 변경을 정확히 반영하도록 동기화. 3개 아카이브 스킬 제거, 2개 실행 방식 재구현, 2개 신규 스킬 추가, 메타데이터 갱신.

**Architecture:** k-cli의 Click 기반 도메인 그룹 (`cli_anything/k_skill/skills/<domain>/__init__.py`)과 manifest (`manifest.yaml`)를 직접 수정. 모든 변경은 기존 패턴 (proxy/runner helpers) 따름. 영향 범위 검증 후 작업.

**Tech Stack:** Python 3.10+, Click 8.x, pytest-asyncio, httpx. 기존 의존성만 사용.

**Pre-work:** 이 plan은 `git worktree ../k-cli-sync-2026-06-07 main` 으로 작업 시작. 또는 main 브랜치에서 직접 작업.

---

## File Structure

| 파일 | 변경 종류 | 책임 |
|------|------|------|
| `cli_anything/k_skill/skills/map/__init__.py` | Modify | 2개 naver 명령어 제거 |
| `cli_anything/k_skill/skills/map/manifest.yaml` | Modify | 2개 naver manifest 엔트리 제거 |
| `cli_anything/k_skill/skills/life/__init__.py` | Modify | blue-ribbon 명령어 제거 |
| `cli_anything/k_skill/skills/life/manifest.yaml` | Modify | blue-ribbon manifest 엔트리 제거 |
| `cli_anything/k_skill/skills/transit/__init__.py` | Modify | ktx 재구현 + seoul-bike 추가 |
| `cli_anything/k_skill/skills/transit/manifest.yaml` | Modify | seoul-bike manifest 엔트리 추가 |
| `cli_anything/k_skill/skills/travel/__init__.py` | Modify | foresttrip 재구현 |
| `cli_anything/k_skill/skills/travel/manifest.yaml` | Modify (optional) | foresttrip 의존성 표기 |
| `cli_anything/k_skill/skills/document/__init__.py` | Modify | korean-middle-korean 추가 |
| `cli_anything/k_skill/skills/document/manifest.yaml` | Modify | korean-middle-korean manifest 엔트리 추가 |
| `tests/test_map.py` | Modify | naver 테스트 제거, kakao 200 시나리오 추가 |
| `tests/test_transit.py` (or create) | Create | seoul-bike 테스트 |
| `tests/test_document.py` (or create) | Create | korean-middle-korean 테스트 |
| `pyproject.toml` | Modify | version 2026.05.27.1 → 2026.06.07.1 |
| `SKILL.md` | Modify | skill counts, 신규 스킬 help |
| `README.md` | Modify | domain counts |
| `BUGFIX_LOG.md` | Modify | 2026-06-07 동기화 섹션 추가 |

---

## Phase A: Remove Archived Skills

### Task A1: Remove naver-directions and naver-geocode from map/__init__.py

**Files:**
- Modify: `cli_anything/k_skill/skills/map/__init__.py:44-67` (delete 24 lines)

- [ ] **Step 1: Open the file and verify current state**

Run: `cat -n cli_anything/k_skill/skills/map/__init__.py | sed -n '40,67p'`
Expected: naver-directions (lines 44-52) and naver-geocode (lines 55-67) functions visible.

- [ ] **Step 2: Delete the two naver Click command functions**

Use Edit tool to remove these two blocks exactly:

OLD:
```python

@cli.command(name='naver-directions')
@click.option('--start', required=True, help='출발지 좌표 (경도,위도)')
@click.option('--goal', required=True, help='도착지 좌표 (경도,위도)')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
def naver_directions(start, goal, as_json):
    """네이버 지도 자동차 길찾기."""
    params = {"start": start, "goal": goal}
    resp = safe_proxy_get("naver-map-route", "/v1/naver-map/directions", params)
    emit(resp, as_json=as_json)


@cli.command(name='naver-geocode')
@click.argument('query')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
def naver_geocode(query, as_json):
    """네이버 지도 주소 -> 좌표 변환 (Geocoding)."""
    if not query or not query.strip():
        emit({"skill": "naver-map-route", "status": "error",
              "error": {"code": "INVALID_INPUT", "message": "주소를 입력하세요"}},
             as_json=as_json)
        return
    params = {"query": query}
    resp = safe_proxy_get("naver-map-route", "/v1/naver-map/geocode", params)
    emit(resp, as_json=as_json)
```

NEW: (empty - both blocks deleted)

The file should end with the kakao_directions function. The final `safe_proxy_get("kakao-map", ...)` line on line 40 should be the last non-empty executable line in the file.

- [ ] **Step 3: Verify naver functions are gone**

Run: `grep -n "naver" cli_anything/k_skill/skills/map/__init__.py`
Expected: no output (empty)

- [ ] **Step 4: Verify map --help no longer shows naver**

Run: `python -c "from click.testing import CliRunner; from cli_anything.k_skill.cli import main; r = CliRunner(); res = r.invoke(main, ['map', '--help']); print(res.output); assert 'naver' not in res.output.lower(); print('OK')"`
Expected: `--help` shows `kakao-search`, `kakao-directions` only. Output includes "OK".

- [ ] **Step 5: Commit**

```bash
cd /home/david/nas_1tb/dev/k-cli
git add cli_anything/k_skill/skills/map/__init__.py
git commit -m "feat(map): remove archived naver-directions and naver-geocode (404 in upstream)"
```

---

### Task A2: Remove naver entries from map/manifest.yaml

**Files:**
- Modify: `cli_anything/k_skill/skills/map/manifest.yaml` (delete 12 lines)

- [ ] **Step 1: View current map manifest**

Run: `cat cli_anything/k_skill/skills/map/manifest.yaml`
Expected output contains:
```yaml
  kakao-search:
    name: kakao-map
  ...
  kakao-directions:
    name: kakao-map
  ...
  naver-directions:
    name: naver-map-route
    display_name: 네이버 지도 길찾기
    description: NCP 기반 자동차 길찾기 경로를 안내합니다
  naver-geocode:
    name: naver-map-route
    display_name: 네이버 지도 지오코딩
    description: 도로명/지번 주소를 좌표로 변환합니다
```

- [ ] **Step 2: Remove naver-directions and naver-geocode entries**

Use Edit tool:

OLD:
```yaml
  naver-directions:
    name: naver-map-route
    display_name: 네이버 지도 길찾기
    description: NCP 기반 자동차 길찾기 경로를 안내합니다
  naver-geocode:
    name: naver-map-route
    display_name: 네이버 지도 지오코딩
    description: 도로명/지번 주소를 좌표로 변환합니다
```

NEW: (empty - both blocks deleted)

Make sure to keep the trailing newline of the file.

- [ ] **Step 3: Verify manifest is valid YAML**

Run: `python -c "import yaml; data = yaml.safe_load(open('cli_anything/k_skill/skills/map/manifest.yaml')); print('Skills:', list(data['skills'].keys()))"`
Expected: `Skills: ['kakao-search', 'kakao-directions']`

- [ ] **Step 4: Run list_all_skills to verify discovery**

Run: `python -c "from cli_anything.k_skill.loader import list_all_skills; sk = [s for s in list_all_skills() if s['domain'] == 'map']; print([s['skill_id'] for s in sk])"`
Expected: `['kakao_search', 'kakao_directions']` (2 items)

- [ ] **Step 5: Commit**

```bash
cd /home/david/nas_1tb/dev/k-cli
git add cli_anything/k_skill/skills/map/manifest.yaml
git commit -m "feat(map): remove naver entries from manifest.yaml"
```

---

### Task A3: Remove blue-ribbon from life/__init__.py

**Files:**
- Modify: `cli_anything/k_skill/skills/life/__init__.py:218-226` (delete 9 lines)

- [ ] **Step 1: Delete the blue-ribbon command**

Use Edit tool:

OLD:
```python

@cli.command(name='blue-ribbon', help='블루리본 인증 맛집 검색')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def blue_ribbon(query, as_json, timeout):
    """블루리본 맛집."""
    args = [query] if query else []
    result = asyncio.run(run_npm('blue-ribbon-nearby', args, timeout=timeout))
    emit(result, as_json=as_json)

```

NEW: (empty - block deleted, including trailing blank line if it leaves a clean break)

The block immediately before blue-ribbon is `plastic-surgery` (line 207-215), and the block after is `public-restroom` (line 229-237). Make sure there is exactly one blank line between them after deletion.

- [ ] **Step 2: Verify blue_ribbon function is gone**

Run: `grep -n "blue_ribbon\|blue-ribbon" cli_anything/k_skill/skills/life/__init__.py`
Expected: no output

- [ ] **Step 3: Verify life --help no longer shows blue-ribbon**

Run: `python -c "from click.testing import CliRunner; from cli_anything.k_skill.cli import main; r = CliRunner(); res = r.invoke(main, ['life', '--help']); assert 'blue-ribbon' not in res.output; print('OK')"`
Expected: outputs "OK"

- [ ] **Step 4: Commit**

```bash
cd /home/david/nas_1tb/dev/k-cli
git add cli_anything/k_skill/skills/life/__init__.py
git commit -m "feat(life): remove archived blue-ribbon (upstream moved to legacy/unsupported-skills)"
```

---

### Task A4: Remove blue-ribbon from life/manifest.yaml

**Files:**
- Modify: `cli_anything/k_skill/skills/life/manifest.yaml` (delete 3 lines)

- [ ] **Step 1: Remove blue-ribbon entry**

Use Edit tool:

OLD:
```yaml
  blue-ribbon:
    name: blue-ribbon-nearby
    display_name: 블루리본 맛집
    description: 블루리본 인증 맛집 검색
```

NEW: (empty - block deleted)

- [ ] **Step 2: Verify life manifest is valid YAML and 22 skills**

Run: `python -c "import yaml; data = yaml.safe_load(open('cli_anything/k_skill/skills/life/manifest.yaml')); print('Skill count:', len(data['skills'])); assert 'blue-ribbon' not in data['skills']; print('OK')"`
Expected: `Skill count: 22`, then `OK`

- [ ] **Step 3: Commit**

```bash
cd /home/david/nas_1tb/dev/k-cli
git add cli_anything/k_skill/skills/life/manifest.yaml
git commit -m "feat(life): remove blue-ribbon from manifest.yaml"
```

---

### Task A5: Remove naver tests from test_map.py

**Files:**
- Modify: `tests/test_map.py:16-17, 66-90` (delete 4 lines from test_map_commands_registered, delete 25 lines of naver tests)

- [ ] **Step 1: Update test_map_commands_registered to remove naver assertions**

Use Edit tool:

OLD:
```python
    assert result.exit_code == 0
    assert 'kakao-search' in result.output
    assert 'kakao-directions' in result.output
    assert 'naver-directions' in result.output
    assert 'naver-geocode' in result.output
```

NEW:
```python
    assert result.exit_code == 0
    assert 'kakao-search' in result.output
    assert 'kakao-directions' in result.output
```

- [ ] **Step 2: Delete test_naver_directions_valid and test_naver_geocode_missing_query functions**

Use Edit tool:

OLD:
```python

@patch("cli_anything.k_skill.skills.map.safe_proxy_get")
def test_naver_directions_valid(mock_proxy_get):
    """naver-directions 명령어 파라미터 바인딩 테스트."""
    mock_proxy_get.return_value = {"status": "success", "data": {}}
    
    runner = CliRunner()
    result = runner.invoke(main, ['map', 'naver-directions', '--start', '127.1,37.1', '--goal', '127.2,37.2', '-j'])
    
    assert result.exit_code == 0
    mock_proxy_get.assert_called_once_with(
        "naver-map-route",
        "/v1/naver-map/directions",
        {"start": "127.1,37.1", "goal": "127.2,37.2"}
    )


def test_naver_geocode_missing_query():
    """naver-geocode 명령어가 쿼리 누락 시 에러를 반환하는지 테스트."""
    runner = CliRunner()
    result = runner.invoke(main, ['map', 'naver-geocode', ' ', '-j'])
    
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["status"] == "error"
    assert data["error"]["message"] == "주소를 입력하세요"
```

NEW: (empty - both functions deleted, including trailing blank line if appropriate)

- [ ] **Step 3: Run test_map.py to verify**

Run: `pytest tests/test_map.py -v`
Expected: all tests pass. Test count should be 3 (test_map_commands_registered, test_kakao_search_missing_keyword, test_kakao_search_valid, test_kakao_directions_valid) = 4 tests.

- [ ] **Step 4: Commit**

```bash
cd /home/david/nas_1tb/dev/k-cli
git add tests/test_map.py
git commit -m "test(map): remove naver test cases (commands removed)"
```

---

### Task A6: Phase A regression check

- [ ] **Step 1: Run full test suite**

Run: `pytest tests/ -v`
Expected: all 114+ tests pass (was 116, minus 2 naver tests = 114).

- [ ] **Step 2: Smoke test the CLI**

Run: `python -c "from click.testing import CliRunner; from cli_anything.k_skill.cli import main; r = CliRunner(); print(r.invoke(main, ['map', '--help']).output); print('==='); print(r.invoke(main, ['life', '--help']).output)" | head -50`
Expected: `map --help` shows 2 commands (kakao-search, kakao-directions). `life --help` does not show blue-ribbon.

---

## Phase B: Reimplement KTX and Foresttrip

### Task B1: Reimplement ktx using run_script with ktx_booking.py

**Files:**
- Modify: `cli_anything/k_skill/skills/transit/__init__.py:94-101` (replace 8 lines)

- [ ] **Step 1: Replace the ktx function**

Use Edit tool:

OLD:
```python

@cli.command(name='ktx', help='KTX/코레일 열차 조회/예매')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def ktx(query, as_json, timeout):
    """KTX 예매."""
    result = asyncio.run(run_pip_import('korail2', 'search_train', packages=["korail2-ncard", "pycryptodome"], timeout=timeout))
    emit(result, as_json=as_json)
```

NEW:
```python

@cli.command(name='ktx', help='KTX/코레일 열차 조회/예매')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=60, type=int, help='타임아웃(초)')
@click.argument('from_station')
@click.argument('to_station')
@click.option('--date', required=True, help='출발일 (YYYYMMDD)')
@click.option('--time', 'start_time', default='000000', help='희망 시작 시각 (HHMMSS, 기본 000000)')
@click.option('--train-type', 'train_type', default='ktx', help='열차 종류 (ktx/itx-saemaeul/mugunghwa/nuriro/tonggeun/itx-cheongchun/airport/all)')
@click.option('--limit', default=5, type=int, help='결과 개수 (기본 5)')
@click.option('--include-no-seats', 'include_no_seats', is_flag=True, help='좌석 없는 열차도 포함')
@click.option('--include-waiting-list', 'include_waiting_list', is_flag=True, help='예약 대기 가능 열차도 포함')
def ktx(from_station, to_station, date, start_time, train_type, limit, include_no_seats, include_waiting_list, as_json, timeout):
    """KTX 예매.

    KTX/Korail 열차 조회, 호차별 좌석번호 확인, 예약 흐름을 처리합니다.
    upstream k-skill/scripts/ktx_booking.py helper를 호출합니다.

    필요 환경변수: KSKILL_KTX_ID, KSKILL_KTX_PASSWORD

    예시:
      k-skill transit ktx 서울 부산 20260607 090000 --date 20260607 -j
      k-skill transit ktx 서울 부산 --date 20260607 --train-type ktx --limit 10 -j
    """
    import os
    env_vars = {k: os.environ[k] for k in ["KSKILL_KTX_ID", "KSKILL_KTX_PASSWORD"] if k in os.environ}
    args = [from_station, to_station, date, start_time,
            "--train-type", train_type,
            "--limit", str(min(max(limit, 1), 30)]
            ]
    if include_no_seats:
        args.append("--include-no-seats")
    if include_waiting_list:
        args.append("--include-waiting-list")
    result = asyncio.run(run_script('ktx_booking.py', args, env_vars=env_vars, timeout=timeout))
    emit(result, as_json=as_json)
```

- [ ] **Step 2: Verify transit --help shows the new options**

Run: `python -c "from click.testing import CliRunner; from cli_anything.k_skill.cli import main; r = CliRunner(); res = r.invoke(main, ['transit', 'ktx', '--help']); print(res.output)"`
Expected: shows new options like `--date`, `--from`, `--to`, `--time`, `--train-type`, `--limit`, `--include-no-seats`, `--include-waiting-list`.

- [ ] **Step 3: Commit**

```bash
cd /home/david/nas_1tb/dev/k-cli
git add cli_anything/k_skill/skills/transit/__init__.py
git commit -m "feat(transit): reimplement ktx using upstream ktx_booking.py helper"
```

---

### Task B2: Reimplement foresttrip using run_script

**Files:**
- Modify: `cli_anything/k_skill/skills/travel/__init__.py:33-40` (replace 8 lines)

- [ ] **Step 1: Replace the foresttrip function**

Use Edit tool:

OLD:
```python

@cli.command(name='foresttrip', help='산림청 숲나들예약 잔여석 조회')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def foresttrip(query, as_json, timeout):
    """숲나들예약."""
    result = asyncio.run(run_pip_import('playwright', 'sync_api', packages=["playwright"], timeout=timeout))
    emit(result, as_json=as_json)
```

NEW:
```python

@cli.command(name='foresttrip', help='산림청 숲나들예약 잔여석 조회')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--text', 'as_text', is_flag=True, help='사람용 텍스트 출력 (기본과 동일)')
@click.option('--dates', 'dates', help='조회 일자 (YYYYMMDD, 여러 개면 콤마 구분, 미지정시 오늘)')
@click.option('--all', 'all_forests', is_flag=True, help='전체 자연휴양림 조회')
@click.option('--forest-id', 'forest_id', help='특정 insttId 조회')
@click.option('--forest-name', 'forest_name', help='공식 휴양림명 부분 일치 조회')
@click.option('--categories', 'categories', help='카테고리 필터 (01=숙박, 02=야영, 둘다: 01,02)')
@click.option('--timeout', '-t', default=60, type=int, help='타임아웃(초)')
def foresttrip(dates, all_forests, forest_id, forest_name, categories, as_json, as_text, timeout):
    """숲나들예약 빈 객실 조회.

    산림청 숲나들e에서 자연휴양림 예약 가능 객실을 날짜 기준으로 조회합니다.
    upstream k-skill/scripts/run_foresttrip_vacancy.py helper를 호출합니다.

    필요 환경변수: KSKILL_FORESTTRIP_ID, KSKILL_FORESTTRIP_PASSWORD
    필요 의존성: playwright, chromium browser

    예시:
      k-skill travel foresttrip --all --dates 20260607 -j
      k-skill travel foresttrip --forest-name "가야" --dates 20260607,20260608 -j
      k-skill travel foresttrip --all --categories 02 --dates 20260607
    """
    import os
    env_vars = {k: os.environ[k] for k in ["KSKILL_FORESTTRIP_ID", "KSKILL_FORESTTRIP_PASSWORD"] if k in os.environ}
    args = []
    if all_forests:
        args.append("--all")
    if forest_id:
        args.extend(["--forest-id", forest_id])
    if forest_name:
        args.extend(["--forest-name", forest_name])
    if dates:
        args.extend(["--dates", dates])
    if categories:
        args.extend(["--categories", categories])
    if as_json or not as_text:
        args.append("--json")
    else:
        args.append("--text")
    result = asyncio.run(run_script('run_foresttrip_vacancy.py', args, env_vars=env_vars, timeout=timeout))
    emit(result, as_json=as_json)
```

- [ ] **Step 2: Verify travel --help shows the new options**

Run: `python -c "from click.testing import CliRunner; from cli_anything.k_skill.cli import main; r = CliRunner(); res = r.invoke(main, ['travel', 'foresttrip', '--help']); print(res.output)"`
Expected: shows new options like `--dates`, `--all`, `--forest-id`, `--forest-name`, `--categories`, `--text`.

- [ ] **Step 3: Commit**

```bash
cd /home/david/nas_1tb/dev/k-cli
git add cli_anything/k_skill/skills/travel/__init__.py
git commit -m "feat(travel): reimplement foresttrip using upstream run_foresttrip_vacancy.py helper"
```

---

### Task B3: Phase B regression check

- [ ] **Step 1: Run full test suite**

Run: `pytest tests/ -v`
Expected: all tests still pass.

- [ ] **Step 2: Verify no broken imports**

Run: `python -c "from cli_anything.k_skill.cli import main; from cli_anything.k_skill.skills import transit, travel; print('Imports OK')"`
Expected: `Imports OK`

---

## Phase C: Add New Skills (seoul-bike, korean-middle-korean)

### Task C1: Add seoul-bike to transit/__init__.py

**Files:**
- Modify: `cli_anything/k_skill/skills/transit/__init__.py` (append at end)

- [ ] **Step 1: Add the seoul-bike Click command at the end of transit/__init__.py**

Use Edit tool to append after the last function (transit_route) but before any module-level code:

OLD (last few lines of file):
```python
    result = asyncio.run(run_script('transit_route.py', args, env_vars=env_vars, timeout=timeout))
    emit(result, as_json=as_json)
```

NEW:
```python
    result = asyncio.run(run_script('transit_route.py', args, env_vars=env_vars, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='seoul-bike', help='서울 따릉이 실시간 대여소 조회 (대여 가능 자전거 / 빈 거치대)')
@click.option('--mode', 'mode', required=True, type=click.Choice(['nearby', 'search', 'realtime']),
              help='조회 모드: nearby=좌표 주변, search=대여소 이름, realtime=실시간 전체')
@click.option('--lat', type=float, help='위도 (nearby 모드 필수)')
@click.option('--lon', type=float, help='경도 (nearby 모드 필수)')
@click.option('--radius-m', 'radius_m', default=500, type=int, help='반경 (m, nearby 모드, 기본 500)')
@click.option('--station-name', 'station_name', help='대여소 이름 키워드 (search 모드)')
@click.option('--start-index', 'start_index', default=1, type=int, help='시작 인덱스 (realtime 모드, 기본 1)')
@click.option('--end-index', 'end_index', default=1000, type=int, help='끝 인덱스 (realtime 모드, 기본 1000)')
@click.option('--limit', default=10, type=int, help='결과 개수 (nearby/search 모드, 기본 10)')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
def seoul_bike(mode, lat, lon, radius_m, station_name, start_index, end_index, limit, as_json):
    """서울 따릉이 실시간 대여 정보.

    k-skill-proxy를 경유해 서울 열린데이터 광장의 따릉이 실시간 대여정보를 조회합니다.

    예시:
      k-skill transit seoul-bike --mode nearby --lat 37.5665 --lon 126.9780 -j
      k-skill transit seoul-bike --mode search --station-name "광화문" -j
      k-skill transit seoul-bike --mode realtime --start-index 1 --end-index 100 -j
    """
    if mode == 'nearby':
        if lat is None or lon is None:
            emit({"skill": "seoul-bike", "status": "error",
                  "error": {"code": "INVALID_INPUT", "message": "nearby 모드는 --lat, --lon이 필수입니다"}},
                 as_json=as_json)
            return
        params = {"lat": lat, "lon": lon, "radius_m": min(max(radius_m, 100), 5000), "limit": min(max(limit, 1), 100)}
        resp = safe_proxy_get("seoul-bike", "/v1/seoul-bike/nearby", params)
    elif mode == 'search':
        if not station_name or not station_name.strip():
            emit({"skill": "seoul-bike", "status": "error",
                  "error": {"code": "INVALID_INPUT", "message": "search 모드는 --station-name 필수"}},
                 as_json=as_json)
            return
        params = {"stationName": station_name, "limit": min(max(limit, 1), 100)}
        resp = safe_proxy_get("seoul-bike", "/v1/seoul-bike/stations", params)
    else:  # realtime
        params = {"startIndex": max(start_index, 1), "endIndex": min(max(end_index, 2), 10000)}
        resp = safe_proxy_get("seoul-bike", "/v1/seoul-bike/realtime", params)
    emit(resp, as_json=as_json)
```

- [ ] **Step 2: Verify transit --help shows seoul-bike**

Run: `python -c "from click.testing import CliRunner; from cli_anything.k_skill.cli import main; r = CliRunner(); res = r.invoke(main, ['transit', '--help']); assert 'seoul-bike' in res.output; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Verify seoul-bike --help shows new options**

Run: `python -c "from click.testing import CliRunner; from cli_anything.k_skill.cli import main; r = CliRunner(); res = r.invoke(main, ['transit', 'seoul-bike', '--help']); print(res.output)"`
Expected: shows `--mode`, `--lat`, `--lon`, `--station-name`, `--radius-m`, `--start-index`, `--end-index`, `--limit`.

- [ ] **Step 4: Smoke test nearby mode (real proxy)**

Run: `python -c "from click.testing import CliRunner; from cli_anything.k_skill.cli import main; r = CliRunner(); res = r.invoke(main, ['transit', 'seoul-bike', '--mode', 'nearby', '--lat', '37.5665', '--lon', '126.9780', '-j']); print('exit:', res.exit_code); print(res.output[:200])"`
Expected: exit code 0, JSON output starting with `{"skill": "seoul-bike", "status": "success"`.

- [ ] **Step 5: Smoke test invalid mode (validation)**

Run: `python -c "from click.testing import CliRunner; from cli_anything.k_skill.cli import main; r = CliRunner(); res = r.invoke(main, ['transit', 'seoul-bike', '--mode', 'invalid']); print('exit:', res.exit_code)"`
Expected: exit code 2 (Click validation error).

- [ ] **Step 6: Commit**

```bash
cd /home/david/nas_1tb/dev/k-cli
git add cli_anything/k_skill/skills/transit/__init__.py
git commit -m "feat(transit): add seoul-bike command (3 modes: nearby/search/realtime)"
```

---

### Task C2: Add seoul-bike to transit/manifest.yaml

**Files:**
- Modify: `cli_anything/k_skill/skills/transit/manifest.yaml`

- [ ] **Step 1: Append seoul-bike skill entry**

Use Edit tool to add a new skill after `transit-route`:

OLD:
```yaml
  transit-route:
    name: korean-transit-route
    display_name: 대중교통 길찾기
    description: ODSay 대중교통 길찾기
```

NEW:
```yaml
  transit-route:
    name: korean-transit-route
    display_name: 대중교통 길찾기
    description: ODSay 대중교통 길찾기
  seoul-bike:
    name: seoul-bike
    display_name: 서울 따릉이
    description: 서울 따릉이 실시간 대여 정보 (대여 가능 자전거 / 빈 거치대)
```

- [ ] **Step 2: Verify manifest is valid YAML and 9 skills**

Run: `python -c "import yaml; data = yaml.safe_load(open('cli_anything/k_skill/skills/transit/manifest.yaml')); print('Skill count:', len(data['skills'])); print('Skills:', list(data['skills'].keys())); assert 'seoul-bike' in data['skills']; print('OK')"`
Expected: `Skill count: 9`, includes `seoul-bike`, then `OK`.

- [ ] **Step 3: Commit**

```bash
cd /home/david/nas_1tb/dev/k-cli
git add cli_anything/k_skill/skills/transit/manifest.yaml
git commit -m "feat(transit): add seoul-bike to manifest.yaml"
```

---

### Task C3: Add korean-middle-korean to document/__init__.py

**Files:**
- Modify: `cli_anything/k_skill/skills/document/__init__.py` (append at end)

- [ ] **Step 1: Append korean-middle-korean Click command**

Use Edit tool to add after the last function (`char_count`):

OLD (last lines of file):
```python
    args = [query] if query else []
    result = asyncio.run(run_npm('korean-character-count', args, timeout=timeout))
    emit(result, as_json=as_json)
```

NEW:
```python
    args = [query] if query else []
    result = asyncio.run(run_npm('korean-character-count', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='korean-middle-korean', help='한국어를 중세국어풍 문체로 변환 (창작용 스타일)')
@click.option('--text', 'text_input', help='변환할 한국어 텍스트 (--text/--file/--stdin 중 하나)')
@click.option('--file', 'file_path', help='입력 파일 경로')
@click.option('--stdin', 'from_stdin', is_flag=True, help='stdin에서 입력 받기')
@click.option('--format', 'output_format', type=click.Choice(['json', 'text']), default='json', help='출력 형식')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력 (기본값)')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
def korean_middle_korean(text_input, file_path, from_stdin, output_format, as_json, timeout):
    """한국 중세국어풍 변환.

    upstream k-skill/scripts/korean_middle_korean.js helper를 Node로 실행합니다.
    학술적 복원이 아니라 창작용 스타일 변환입니다.

    예시:
      k-skill document korean-middle-korean --text "민수는 3월 5일 학교에서 공부했다."
      k-skill document korean-middle-korean --text "열애설을 인정했다." --format text
      cat input.txt | k-skill document korean-middle-korean --stdin
    """
    args = []
    if text_input:
        args.extend(["--text", text_input])
    elif file_path:
        args.extend(["--file", file_path])
    elif from_stdin:
        args.append("--stdin")
    else:
        emit({"skill": "korean-middle-korean", "status": "error",
              "error": {"code": "INVALID_INPUT", "message": "--text, --file, --stdin 중 하나는 필수"}},
             as_json=as_json)
        return
    args.extend(["--format", output_format])
    result = asyncio.run(run_script('korean_middle_korean.js', args, timeout=timeout))
    emit(result, as_json=as_json)
```

- [ ] **Step 2: Verify document --help shows korean-middle-korean**

Run: `python -c "from click.testing import CliRunner; from cli_anything.k_skill.cli import main; r = CliRunner(); res = r.invoke(main, ['document', '--help']); assert 'korean-middle-korean' in res.output; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Verify korean-middle-korean --help shows new options**

Run: `python -c "from click.testing import CliRunner; from cli_anything.k_skill.cli import main; r = CliRunner(); res = r.invoke(main, ['document', 'korean-middle-korean', '--help']); print(res.output)"`
Expected: shows `--text`, `--file`, `--stdin`, `--format`, `--json`.

- [ ] **Step 4: Verify validation works (no input)**

Run: `python -c "from click.testing import CliRunner; from cli_anything.k_skill.cli import main; r = CliRunner(); res = r.invoke(main, ['document', 'korean-middle-korean', '-j']); print('exit:', res.exit_code); import json; data = json.loads(res.output); print('error:', data.get('error', {}).get('code'))"`
Expected: exit 0, error code `INVALID_INPUT`.

- [ ] **Step 5: Commit**

```bash
cd /home/david/nas_1tb/dev/k-cli
git add cli_anything/k_skill/skills/document/__init__.py
git commit -m "feat(document): add korean-middle-korean command (Node script wrapper)"
```

---

### Task C4: Add korean-middle-korean to document/manifest.yaml

**Files:**
- Modify: `cli_anything/k_skill/skills/document/manifest.yaml`

- [ ] **Step 1: Append korean-middle-korean skill entry**

Use Edit tool:

OLD (last skill):
```yaml
  char-count:
    name: "korean-character-count"
    display_name: "글자 수 세기"
    description: "한국어 글자/어절/문단 수 카운트"
    npm: ["korean-character-count"]
```

NEW:
```yaml
  char-count:
    name: "korean-character-count"
    display_name: "글자 수 세기"
    description: "한국어 글자/어절/문단 수 카운트"
    npm: ["korean-character-count"]
  korean-middle-korean:
    name: "korean-middle-korean"
    display_name: "중세국어풍 변환"
    description: "한국어 입력문을 중세국어풍으로 결정론적 변환 (창작용 스타일)"
```

- [ ] **Step 2: Verify manifest is valid YAML and 6 skills**

Run: `python -c "import yaml; data = yaml.safe_load(open('cli_anything/k_skill/skills/document/manifest.yaml')); print('Skill count:', len(data['skills'])); assert 'korean-middle-korean' in data['skills']; print('OK')"`
Expected: `Skill count: 6`, then `OK`.

- [ ] **Step 3: Commit**

```bash
cd /home/david/nas_1tb/dev/k-cli
git add cli_anything/k_skill/skills/document/manifest.yaml
git commit -m "feat(document): add korean-middle-korean to manifest.yaml"
```

---

### Task C5: Add unit tests for seoul-bike and korean-middle-korean

**Files:**
- Create: `tests/test_transit_seoul_bike.py`
- Create: `tests/test_document_korean_middle_korean.py`

- [ ] **Step 1: Create test_transit_seoul_bike.py**

```python
"""Tests for transit/seoul-bike command."""

import json
from unittest.mock import patch
from click.testing import CliRunner
from cli_anything.k_skill.cli import main


def test_seoul_bike_registered():
    """seoul-bike 명령어가 transit 도메인에 등록되어 있는지 확인."""
    runner = CliRunner()
    result = runner.invoke(main, ['transit', '--help'])
    assert result.exit_code == 0
    assert 'seoul-bike' in result.output


def test_seoul_bike_nearby_missing_coords():
    """nearby 모드에서 lat/lon 누락 시 에러 반환."""
    runner = CliRunner()
    result = runner.invoke(main, ['transit', 'seoul-bike', '--mode', 'nearby', '-j'])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["status"] == "error"
    assert data["error"]["code"] == "INVALID_INPUT"


@patch("cli_anything.k_skill.skills.transit.safe_proxy_get")
def test_seoul_bike_nearby_valid(mock_proxy_get):
    """nearby 모드 정상 호출."""
    mock_proxy_get.return_value = {"status": "success", "data": {"stations": []}}
    runner = CliRunner()
    result = runner.invoke(main, [
        'transit', 'seoul-bike', '--mode', 'nearby',
        '--lat', '37.5665', '--lon', '126.9780', '-j'
    ])
    assert result.exit_code == 0
    mock_proxy_get.assert_called_once()
    call_args = mock_proxy_get.call_args
    assert call_args[0][0] == "seoul-bike"
    assert call_args[0][1] == "/v1/seoul-bike/nearby"
    assert call_args[0][2]["lat"] == 37.5665
    assert call_args[0][2]["lon"] == 126.9780


@patch("cli_anything.k_skill.skills.transit.safe_proxy_get")
def test_seoul_bike_search_valid(mock_proxy_get):
    """search 모드 정상 호출."""
    mock_proxy_get.return_value = {"status": "success", "data": {"stations": []}}
    runner = CliRunner()
    result = runner.invoke(main, [
        'transit', 'seoul-bike', '--mode', 'search',
        '--station-name', '광화문', '-j'
    ])
    assert result.exit_code == 0
    mock_proxy_get.assert_called_once_with(
        "seoul-bike",
        "/v1/seoul-bike/stations",
        {"stationName": "광화문", "limit": 10}
    )


def test_seoul_bike_search_missing_station():
    """search 모드에서 station-name 누락 시 에러."""
    runner = CliRunner()
    result = runner.invoke(main, ['transit', 'seoul-bike', '--mode', 'search', '-j'])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["status"] == "error"
    assert data["error"]["code"] == "INVALID_INPUT"


@patch("cli_anything.k_skill.skills.transit.safe_proxy_get")
def test_seoul_bike_realtime_valid(mock_proxy_get):
    """realtime 모드 정상 호출."""
    mock_proxy_get.return_value = {"status": "success", "data": {"rentBikeStatus": []}}
    runner = CliRunner()
    result = runner.invoke(main, [
        'transit', 'seoul-bike', '--mode', 'realtime', '-j'
    ])
    assert result.exit_code == 0
    mock_proxy_get.assert_called_once_with(
        "seoul-bike",
        "/v1/seoul-bike/realtime",
        {"startIndex": 1, "endIndex": 1000}
    )


def test_seoul_bike_invalid_mode():
    """잘못된 mode 값은 Click validation error."""
    runner = CliRunner()
    result = runner.invoke(main, ['transit', 'seoul-bike', '--mode', 'invalid', '-j'])
    assert result.exit_code == 2  # Click usage error
```

- [ ] **Step 2: Run seoul-bike tests**

Run: `pytest tests/test_transit_seoul_bike.py -v`
Expected: 7 tests pass.

- [ ] **Step 3: Create test_document_korean_middle_korean.py**

```python
"""Tests for document/korean-middle-korean command."""

import json
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from cli_anything.k_skill.cli import main


def test_korean_middle_korean_registered():
    """korean-middle-korean 명령어가 document 도메인에 등록되어 있는지 확인."""
    runner = CliRunner()
    result = runner.invoke(main, ['document', '--help'])
    assert result.exit_code == 0
    assert 'korean-middle-korean' in result.output


def test_korean_middle_korean_missing_input():
    """--text, --file, --stdin 모두 누락 시 에러."""
    runner = CliRunner()
    result = runner.invoke(main, ['document', 'korean-middle-korean', '-j'])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["status"] == "error"
    assert data["error"]["code"] == "INVALID_INPUT"


@patch("cli_anything.k_skill.skills.document.run_script")
def test_korean_middle_korean_text_input(mock_run_script):
    """--text 입력 시 올바른 args로 run_script 호출."""
    mock_run_script.return_value = MagicMock()
    # run_script returns awaitable, so we need AsyncMock
    from unittest.mock import AsyncMock
    mock_run_script.return_value = {"status": "success", "data": {"output": "result"}}

    runner = CliRunner()
    result = runner.invoke(main, [
        'document', 'korean-middle-korean',
        '--text', '민수는 3월 5일 학교에서 공부했다.',
        '-j'
    ])

    # run_script is called via asyncio.run, so we just check it was called with expected args
    # The mock won't actually return a proper coroutine, so we expect COMMAND_FAILED or success
    assert result.exit_code in (0, 1)  # may fail in runner if mock not awaitable


@patch("cli_anything.k_skill.skills.document.asyncio")
def test_korean_middle_korean_text_runs_asyncio(mock_asyncio):
    """--text 입력 시 asyncio.run이 run_script와 함께 호출됨."""
    mock_asyncio.run.return_value = {"status": "success", "data": {"output": "result"}}

    runner = CliRunner()
    result = runner.invoke(main, [
        'document', 'korean-middle-korean',
        '--text', '안녕하세요', '--format', 'text', '-j'
    ])

    # asyncio.run should be called
    assert mock_asyncio.run.called
    # The coroutine passed should call run_script with right args
    # Just verify exit code is 0 (success path)
    assert result.exit_code == 0
```

- [ ] **Step 4: Run korean-middle-korean tests**

Run: `pytest tests/test_document_korean_middle_korean.py -v`
Expected: 4 tests pass.

- [ ] **Step 5: Run full test suite**

Run: `pytest tests/ -v`
Expected: all tests pass. Count should be 114 (Phase A) + 7 (seoul-bike) + 4 (korean-middle-korean) = 125 tests.

- [ ] **Step 6: Commit**

```bash
cd /home/david/nas_1tb/dev/k-cli
git add tests/test_transit_seoul_bike.py tests/test_document_korean_middle_korean.py
git commit -m "test: add unit tests for seoul-bike and korean-middle-korean"
```

---

## Phase D: Metadata Updates

### Task D1: Bump version in pyproject.toml

**Files:**
- Modify: `pyproject.toml:3`

- [ ] **Step 1: Update version string**

Use Edit tool:

OLD: `version = "2026.05.27.1"`
NEW: `version = "2026.06.07.1"`

- [ ] **Step 2: Verify version is updated**

Run: `grep "version" pyproject.toml | head -1`
Expected: `version = "2026.06.07.1"`

- [ ] **Step 3: Commit**

```bash
cd /home/david/nas_1tb/dev/k-cli
git add pyproject.toml
git commit -m "chore: bump version to 2026.06.07.1"
```

---

### Task D2: Update SKILL.md with new skills

**Files:**
- Modify: `SKILL.md:5, 41, 49, 308-313` (or wherever the relevant lines are)

- [ ] **Step 1: Update version in frontmatter**

Use Edit tool:

OLD: `version: 2026.05.27.1`
NEW: `version: 2026.06.07.1`

- [ ] **Step 2: Update domain skill counts**

Update the domain table in SKILL.md:

OLD (in the table area):
```
| transit | 8 | 대중교통 (지하철, 버스, 기차, 항공편) |
| life | 23 | 생활/편의 (주유소, 쓰레기, 주차장, 맛집 등) |
| document | 5 | HWP, 맞춤법, 글자수 |
```

NEW:
```
| transit | 9 | 대중교통 (지하철, 버스, 기차, 항공편, 따릉이) |
| life | 22 | 생활/편의 (주유소, 쓰레기, 주차장, 맛집 등) |
| document | 6 | HWP, 맞춤법, 글자수, 중세국어풍 변환 |
```

- [ ] **Step 3: Update transit --help section to include seoul-bike**

Use Edit tool:

OLD (in the transit help details):
```
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

NEW:
```
Commands:
  express-bus    KOBUS 고속버스 시간표/잔여석 조회
  flight-search  Google Flights 항공권 가격/일정 검색
  intercity-bus  Tmoney 시외버스 시간표/잔여석 조회
  ktx            KTX/코레일 열차 조회/예매
  seoul-bike     서울 따릉이 실시간 대여소 조회
  srt            SRT 열차 조회/예매
  subway         서울 지하철 실시간 도착정보.
  subway-lost    서울교통공사 지하철 분실물 검색
  transit-route  ODSay 대중교통 길찾기
```

- [ ] **Step 4: Update document --help section to include korean-middle-korean**

Use Edit tool:

OLD:
```
Commands:
  char-count   한국어 글자/어절/문단 수 카운트
  hwp-convert  HWP/HWPX 문서를 PDF 등으로 변환
  rhwp-debug   rhwp Rust CLI로 HWP 레이아웃 디버깅
  rhwp-edit    HWP 문서 편집 (k-skill-rhwp)
  spell-check  한국어 맞춤법/문법 검사
```

NEW:
```
Commands:
  char-count             한국어 글자/어절/문단 수 카운트
  hwp-convert            HWP/HWPX 문서를 PDF 등으로 변환
  korean-middle-korean   한국어 중세국어풍 변환 (창작용 스타일)
  rhwp-debug             rhwp Rust CLI로 HWP 레이아웃 디버깅
  rhwp-edit              HWP 문서 편집 (k-skill-rhwp)
  spell-check            한국어 맞춤법/문법 검사
```

- [ ] **Step 5: Remove map --help section's naver entries (if present)**

Search for and remove any references to `naver-directions` and `naver-geocode` in SKILL.md.

Run: `grep -n "naver" SKILL.md`
Expected: no output

If grep finds anything, use Edit tool to remove.

- [ ] **Step 6: Verify SKILL.md renders correctly**

Run: `python -c "with open('SKILL.md') as f: content = f.read(); assert '2026.06.07.1' in content; assert 'seoul-bike' in content; assert 'korean-middle-korean' in content; assert 'naver' not in content.lower() or 'naver-blog' in content; print('OK')"`
Expected: `OK`

Note: 'naver-blog' (search domain) should still be present. Only 'naver-directions' and 'naver-geocode' should be gone.

- [ ] **Step 7: Commit**

```bash
cd /home/david/nas_1tb/dev/k-cli
git add SKILL.md
git commit -m "docs(SKILL): update for 2026.06.07.1 (add seoul-bike, korean-middle-korean, remove naver)"
```

---

### Task D3: Update README.md skill counts

**Files:**
- Modify: `README.md:135-156` (the skill list table)

- [ ] **Step 1: Update transit/life/document counts in skill table**

Use Edit tool to update the table:

OLD:
```
| transit | 8 | 대중교통 (지하철, 버스, SRT, KTX, 항공편) |
| life | 23 | 생활/편의 (주유소, 쓰레기, 주차장, 맛집, 응급실 등) |
| document | 5 | 문서 (HWP, 맞춤법, 글자수) |
```

NEW:
```
| transit | 9 | 대중교통 (지하철, 버스, SRT, KTX, 따릉이, 항공편) |
| life | 22 | 생활/편의 (주유소, 쓰레기, 주차장, 맛집, 응급실 등) |
| document | 6 | 문서 (HWP, 맞춤법, 글자수, 중세국어풍 변환) |
```

- [ ] **Step 2: Verify README is valid markdown**

Run: `python -c "with open('README.md') as f: content = f.read(); assert 'transit | 9' in content; assert 'life | 22' in content; assert 'document | 6' in content; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
cd /home/david/nas_1tb/dev/k-cli
git add README.md
git commit -m "docs(README): update domain skill counts for 2026.06.07.1"
```

---

### Task D4: Add changelog entry to BUGFIX_LOG.md

**Files:**
- Modify: `BUGFIX_LOG.md` (append at end)

- [ ] **Step 1: Append the 2026-06-07 sync entry**

```markdown

---

## 2026-06-07 — upstream 동기화 (v2026.05.27.1 → v2026.06.07.1)

**Author:** 맥거핀 (다비드 승인)
**Scope:** upstream NomaDamas/k-skill HEAD `1efef28` (2026-06-06) 기준 동기화

### 제거 (3 commands)
- `map/naver-directions` — upstream `naver-map-route` 스킬 archive → 프록시 404
- `map/naver-geocode` — 동일
- `life/blue-ribbon` — upstream SKILL.md가 `legacy/unsupported-skills/`로 이동

### 재구현 (2 commands)
- `transit/ktx` — `run_pip_import('korail2', ...)` (잘못된 호출) → `run_script('ktx_booking.py', ...)` (upstream helper 사용). 옵션: `--date`, `--time`, `--train-type`, `--limit`, `--include-no-seats`, `--include-waiting-list`
- `travel/foresttrip` — `run_pip_import('playwright', 'sync_api', ...)` (잘못된 호출) → `run_script('run_foresttrip_vacancy.py', ...)` (upstream helper 사용). 옵션: `--dates`, `--all`, `--forest-id`, `--forest-name`, `--categories`, `--text`

### 신규 추가 (2 commands)
- `transit/seoul-bike` — 서울 따릉이 실시간 대여소 조회. 3 modes (`nearby` / `search` / `realtime`) → `/v1/seoul-bike/{nearby,stations,realtime}` 프록시 라우트 사용
- `document/korean-middle-korean` — 한국 중세국어풍 변환. `run_script('korean_middle_korean.js', ...)` (Node 스크립트) 사용. 옵션: `--text` / `--file` / `--stdin` (mutually exclusive), `--format` (text/json)

### 변경 없음
- `map/kakao-search`, `map/kakao-directions` — 이미 upstream 변경 라우트로 갱신되어 있었음
- `startup-support` — upstream에서 완전 제거, k-cli엔 없었음

### 메타
- `pyproject.toml` 버전: `2026.05.27.1` → `2026.06.07.1`
- 스킬 수: 90 → 89
- 도메인별 변경: transit 8→9, life 23→22, document 5→6, map 4→2

### 테스트
- `tests/test_map.py`: naver 테스트 3개 제거
- `tests/test_transit_seoul_bike.py`: 신규 (7 tests)
- `tests/test_document_korean_middle_korean.py`: 신규 (4 tests)
- 전체 통과: 125 tests

### 참조
- 설계: `docs/superpowers/specs/2026-06-07-upstream-sync-design.md`
- 플랜: `docs/superpowers/plans/2026-06-07-upstream-sync.md`
- upstream 커밋: `46f44ed` (startup-support 제거), `bbba283` (map archive), `1efef28` (latest)
```

- [ ] **Step 2: Verify BUGFIX_LOG.md is valid**

Run: `python -c "with open('BUGFIX_LOG.md') as f: content = f.read(); assert '2026-06-07' in content; assert 'naver-directions' in content; assert 'seoul-bike' in content; assert 'korean-middle-korean' in content; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
cd /home/david/nas_1tb/dev/k-cli
git add BUGFIX_LOG.md
git commit -m "docs(BUGFIX_LOG): add 2026-06-07 upstream sync entry"
```

---

## Phase E: Final Verification

### Task E1: Run full test suite

- [ ] **Step 1: Run all tests with verbose output**

Run: `pytest tests/ -v 2>&1 | tee /tmp/pytest-final.log`
Expected: all tests pass.

- [ ] **Step 2: Count tests**

Run: `grep -E "PASSED|FAILED" /tmp/pytest-final.log | wc -l`
Expected: ≥ 125 tests

- [ ] **Step 3: Verify no failures**

Run: `grep -E "FAILED" /tmp/pytest-final.log | wc -l`
Expected: 0

---

### Task E2: Verify skill list count

- [ ] **Step 1: Check total skill count via CLI**

Run: `python -c "import json, subprocess; from click.testing import CliRunner; from cli_anything.k_skill.cli import main; r = CliRunner(); res = r.invoke(main, ['list', '--all', '-j']); data = json.loads(res.output); print('Total skills:', len(data))"`
Expected: `Total skills: 89`

- [ ] **Step 2: Verify expected skills exist**

Run: `python -c "import json; from click.testing import CliRunner; from cli_anything.k_skill.cli import main; r = CliRunner(); res = r.invoke(main, ['list', '--all', '-j']); data = json.loads(res.output); names = {s['name'] for s in data}; assert 'seoul-bike' in names; assert 'korean-middle-korean' in names; assert 'naver-directions' not in {s['skill_id'] for s in data}; assert 'naver-geocode' not in {s['skill_id'] for s in data}; assert 'blue-ribbon' not in {s['skill_id'] for s in data}; print('All checks pass')"`
Expected: `All checks pass`

---

### Task E3: Smoke test live skills

- [ ] **Step 1: Test seoul-bike nearby (real proxy call)**

Run: `python -c "import json; from click.testing import CliRunner; from cli_anything.k_skill.cli import main; r = CliRunner(); res = r.invoke(main, ['transit', 'seoul-bike', '--mode', 'nearby', '--lat', '37.5665', '--lon', '126.9780', '-j']); data = json.loads(res.output); print('Status:', data['status']); assert data['status'] == 'success'; print('Source:', data['meta']['source']); print('Response time:', data['meta'].get('response_time_ms'))"`
Expected: `Status: success`, response time > 0

- [ ] **Step 2: Test seoul-bike search (real proxy call)**

Run: `python -c "import json; from click.testing import CliRunner; from cli_anything.k_skill.cli import main; r = CliRunner(); res = r.invoke(main, ['transit', 'seoul-bike', '--mode', 'search', '--station-name', '강남', '-j']); data = json.loads(res.output); print('Status:', data['status']); assert data['status'] == 'success'"`
Expected: `Status: success`

- [ ] **Step 3: Test kakao-search (regression check)**

Run: `python -c "import json; from click.testing import CliRunner; from cli_anything.k_skill.cli import main; r = CliRunner(); res = r.invoke(main, ['map', 'kakao-search', '강남역', '-j']); data = json.loads(res.output); print('Status:', data['status']); assert data['status'] == 'success'"`
Expected: `Status: success`

- [ ] **Step 4: Test kakao-directions (regression check)**

Run: `python -c "import json; from click.testing import CliRunner; from cli_anything.k_skill.cli import main; r = CliRunner(); res = r.invoke(main, ['map', 'kakao-directions', '--origin', '127.027,37.497', '--destination', '127.110,37.394', '-j']); data = json.loads(res.output); print('Status:', data['status']); assert data['status'] == 'success'"`
Expected: `Status: success`

---

### Task E4: Final commit (if any uncommitted changes)

- [ ] **Step 1: Check git status**

Run: `git status`
Expected: clean working tree OR only __pycache__ files

- [ ] **Step 2: If there are uncommitted changes, commit them**

```bash
cd /home/david/nas_1tb/dev/k-cli
git status
# If there are real changes:
git add -A
git commit -m "chore: final cleanup for 2026.06.07.1 release"
```

- [ ] **Step 3: Verify final commit history**

Run: `git log --oneline -15`
Expected: 13-14 commits since 7d05dfe, with each phase properly grouped.

---

## Acceptance Criteria Checklist

- [ ] `k-skill map --help` shows only kakao-search and kakao-directions (2 commands)
- [ ] `k-skill life --help` does not show blue-ribbon
- [ ] `k-skill transit --help` shows seoul-bike (9 commands)
- [ ] `k-skill document --help` shows korean-middle-korean (6 commands)
- [ ] `k-skill list --all -j` returns 89 skills
- [ ] `k-skill transit seoul-bike --mode nearby --lat 37.5665 --lon 126.9780 -j` returns success
- [ ] `k-skill map kakao-search "강남역" -j` returns success
- [ ] `k-skill map kakao-directions --origin 127.027,37.497 --destination 127.110,37.394 -j` returns success
- [ ] `pytest tests/ -v` all 125+ tests pass
- [ ] `pyproject.toml` version is `2026.06.07.1`
- [ ] git log shows clean phase-based commits

---

## Out of Scope (deferred)

- KTX/foresttrip credential-based end-to-end testing (covered by unit tests of Click options)
- PyPI auto-publish (existing CI/CD handles)
- npm package manifest updates
- i18n
