# k-cli 업스트림 동기화 — 설계 문서

- **날짜**: 2026-06-07
- **버전**: 2026.05.27.1 → 2026.06.07.1
- **상위 변경**: upstream NomaDamas/k-skill HEAD `1efef28` (2026-06-06)
- **승인자**: 다비드
- **저자**: 맥거핀

## 1. 배경

k-cli는 upstream NomaDamas/k-skill을 Click 기반 CLI 래퍼로 재구성한 프로젝트입니다. upstream이 2026-05-28부터 2026-06-06 사이에 약 40개 커밋을 진행하며 일부 스킬을 아카이브하고, 일부 엔드포인트 라우트를 변경했습니다. 본 작업은 k-cli가 이 변경을 정확히 반영하도록 동기화합니다.

## 2. 동기화로 인한 영향 (검증 완료)

| 엔드포인트/스킬 | upstream 상태 | k-cli 영향 |
|------|------|------|
| `/v1/naver-map/directions` | 404 (route archived) | `map/naver-directions` 깨짐 |
| `/v1/naver-map/geocode` | 404 (route archived) | `map/naver-geocode` 깨짐 |
| `blue-ribbon-nearby` (npm) | upstream SKILL.md는 `legacy/unsupported-skills/`로 이동 | `life/blue-ribbon` 더 이상 권장되지 않음 |
| `/v1/kakao-map/search/keyword` | 200 ✅ (이미 k-cli 코드가 이 라우트 사용 중) | 변경 불필요 |
| `/v1/kakao-mobility/directions` | 200 ✅ (이미 k-cli 코드가 이 라우트 사용 중) | 변경 불필요 |
| `/v1/seoul-bike/realtime` / `stations` / `nearby` | 200 ✅ | 신규 추가 가능 |
| `ktx-booking` (proxy 미사용, 직접 실행) | `scripts/ktx_booking.py` helper 추가 | `transit/ktx` 재구현 필요 (현재 `run_pip_import('korail2', ...)`는 부적절) |
| `foresttrip-vacancy` (proxy 미사용) | helper `run_foresttrip_vacancy.py` 사용 | `travel/foresttrip` 재구현 필요 (현재 `run_pip_import('playwright', ...)`는 버그) |
| `korean-middle-korean` (Node 스크립트) | upstream 신규 | 신규 추가 |
| `startup-support` | upstream에서 완전 제거 (k-cli엔 없었음) | 무영향 |

## 3. 작업 범위

### 3.1. 제거 (3개 명령어 + 2개 manifest 항목)

1. `cli_anything/k_skill/skills/map/__init__.py`
   - `naver-directions` 명령어 제거 (라인 44-52)
   - `naver-geocode` 명령어 제거 (라인 55-67)
2. `cli_anything/k_skill/skills/map/manifest.yaml`
   - `naver-directions`, `naver-geocode` 항목 제거
3. `cli_anything/k_skill/skills/life/__init__.py`
   - `blue-ribbon` 명령어 제거 (라인 218-226)
4. `cli_anything/k_skill/skills/life/manifest.yaml`
   - `blue-ribbon` 항목 제거

### 3.2. 재구현 (2개 명령어 — upstream helper 스크립트로 교체)

1. `cli_anything/k_skill/skills/transit/__init__.py`
   - `ktx` 명령어: `run_pip_import('korail2', ...)` → `run_script('ktx_booking.py', ...)`로 변경
   - 환경변수 `KSKILL_KTX_ID`, `KSKILL_KTX_PASSWORD`를 `env_vars`로 전달
   - Click 옵션: `--date`, `--from`, `--to`, `--time`, `--train-type`, `--limit`, `--include-no-seats`, `--include-waiting-list`, `--json`, `--timeout`
2. `cli_anything/k_skill/skills/travel/__init__.py`
   - `foresttrip` 명령어: `run_pip_import('playwright', ...)` → `run_script('run_foresttrip_vacancy.py', ...)`로 변경
   - 환경변수 `KSKILL_FORESTTRIP_ID`, `KSKILL_FORESTTRIP_PASSWORD`를 `env_vars`로 전달
   - Click 옵션: `--dates`, `--all`, `--forest-id`, `--forest-name`, `--categories`, `--text/--json`, `--timeout`

### 3.3. 신규 추가 (2개 명령어 + 2개 manifest 항목)

1. **`cli_anything/k_skill/skills/transit/__init__.py`** — `seoul-bike` 추가
   - 3개 서브커맨드 구조는 단일 Click group + options 패턴 사용 (다른 도메인과 일관성)
   - `--lat`, `--lon` (required) / `--station-name` (mutually exclusive) / `--start-index`, `--end-index`, `--radius-m`, `--limit`
   - 3개 프록시 라우트 사용:
     - `--mode nearby` → `/v1/seoul-bike/nearby`
     - `--mode search` → `/v1/seoul-bike/stations?stationName=...`
     - `--mode realtime` → `/v1/seoul-bike/realtime?startIndex=...&endIndex=...`

2. **`cli_anything/k_skill/skills/document/__init__.py`** — `korean-middle-korean` 추가
   - `run_script('korean_middle_korean.js', ...)` 사용 (Node 스크립트, K_SKILL_ROOT 기준)
   - Click 옵션: `--text TEXT` (mutually exclusive) / `--file FILE` / `--stdin`, `--format` (text/json), `--json`, `--timeout`

### 3.4. Manifest 추가/제거 항목

1. `cli_anything/k_skill/skills/transit/manifest.yaml`
   - `seoul-bike` 항목 추가
2. `cli_anything/k_skill/skills/document/manifest.yaml`
   - `korean-middle-korean` 항목 추가
3. (제거 항목은 3.1과 일치)

### 3.5. 메타데이터 갱신

1. `pyproject.toml` — `version = "2026.05.27.1"` → `"2026.06.07.1"`
2. `SKILL.md` — 스킬 수 변경 (90 → 89 + seoul-bike 1개 = 90), 새 스킬 help 텍스트 추가
3. `README.md` — 스킬 수 동일 유지 (90), 도메인별 카운트만 일부 변경
4. `BUGFIX_LOG.md` — 새 섹션 추가 ("2026-06-07 업스트림 동기화")

### 3.6. 테스트

1. `tests/test_loader.py`에 신규 스킬 2개가 manifest에서 자동 발견되는지 확인하는 케이스 추가 (선택)
2. `tests/test_map.py`의 `naver-directions`, `naver-geocode` 케이스 제거
3. `tests/test_phase2_skills.py`의 `blue-ribbon` 케이스 제거 (있는 경우)
4. `pytest tests/ -v` 전체 회귀 확인

## 4. 성공 기준 (Acceptance Criteria)

- [ ] `k-skill map --help`에 더 이상 `naver-directions`, `naver-geocode` 없음
- [ ] `k-skill life --help`에 더 이상 `blue-ribbon` 없음
- [ ] `k-skill transit --help`에 `seoul-bike` 포함
- [ ] `k-skill document --help`에 `korean-middle-korean` 포함
- [ ] `k-skill map kakao-search "강남역" -j` 정상 응답 (200)
- [ ] `k-skill map kakao-directions --origin ... --destination ... -j` 정상 응답 (200)
- [ ] `k-skill transit seoul-bike --lat 37.5665 --lon 126.9780 -j` 200 응답
- [ ] `k-skill list --all -j | jq 'length'` == 89 (90 - 3 제거 + 2 추가 = 89)
- [ ] `pytest tests/ -v` 모든 테스트 통과
- [ ] `pyproject.toml` 버전이 `2026.06.07.1`
- [ ] git 커밋은 작은 단위로 7~8개 (제거 1, 재구현 2, 신규 2, 메타 1, 테스트 1)

## 5. 위험 및 완화

| 위험 | 완화 |
|------|------|
| KTX/foresttrip은 credential 필요 → 통합 테스트 어려움 | manifest의 `requires.python: [playwright]` 같은 메타데이터만 검증, 실제 호출은 스킵 |
| `run_script`로 k-skill helper를 호출하려면 `K_SKILL_ROOT` 환경변수 필요 | 테스트에서는 `K_SKILL_ROOT`가 없을 때 적절한 에러 응답을 반환하는지 unit test |
| 의존성 누락 (korail2, playwright, korean-middle-korean) | `k-skill setup check`에 의존성 추가 (또는 기존 dependency.py로 자동 감지) |

## 6. 비목표 (Out of Scope)

- k-skill-proxy 자체 라우트 추가/수정 (서버는 upstream에서 관리)
- 다른 도메인 (weather, finance 등) 검토 (이번 동기화 대상 외)
- README 영문화/i18n
- PyPI 자동 배포 (CI 파이프라인은 기존 시스템 그대로)
- `ktx-booking`의 `--seats-detail`, `--reserve` 등 깊은 워크플로우 (upstream helper를 그대로 호출하는 래퍼만 구현)
- npm 패키지 매니페스트 동기화 (`package.json`은 k-cli가 직접 관리)

## 7. 단계 (Implementation Phases)

writing-plans skill로 별도 implementation plan 작성 예정. 각 phase는 독립적으로 테스트 가능.

- Phase A: 제거 (naver, blue-ribbon) + manifest + 테스트
- Phase B: 재구현 (ktx, foresttrip) + manifest
- Phase C: 신규 추가 (seoul-bike, korean-middle-korean) + manifest + 테스트
- Phase D: 메타데이터 (버전, SKILL.md, README.md, BUGFIX_LOG.md)
- Phase E: 최종 검증 (`pytest`, 수동 smoke test, `k-skill list`)
