# k-cli ↔ k-skill upstream 동기화 설계 (2026-07-10)

## 1. 목적

로컬 `k-cli`(Python Click 래퍼, 95 스킬 / 14 도메인)가 upstream
`NomaDamas/k-skill`(108+ 스킬 모노레포)에 뒤처진 기능을 따라잡는다.
upstream의 누락 신규 스킬을 로컬 패턴(`docs/upstream-sync-guide.md`)대로
**100% 포팅**하여 최대한 현행화한다.

## 2. 대상 스킬 (16개 신규)

로컬 manifest와 upstream 폴더를 정규화 대조한 결과, 이름만 다른 기존
포팅(data4library↔library-book-search, neis-school-meal↔k-schoollunch-menu,
k-skill-cleaner/set, korean-stock, lh-notice, seoul-subway, fine-dust 등)은
**이미 존재**하므로 제외. 실제 누락은 다음 16개.

| 신규 도메인 | 스킬 | upstream 호출 방식(예상) |
|---|---|---|
| `fortune` (신규) | saju-fortune, naming-house | npm 패키지 / 프록시 |
| `business` (신규) | biz-health-check, court-payment-order-assistant, d2b-notice-search, g2b-order-plan-search, localdata-business-status, popbill, s2b-notice-search | 프록시(일부 API 키 필요) |
| `recruiting` (신규) | job-posting-match, jobkorea-talent-search, saramin-talent-search | 프록시 / 스크립트 |
| `messaging` (신규) | kakaotalk-mac | 로컬(macOS 아카이브) |
| 기존 `life` 확장 | kakao-bar-nearby, lovebug-report, yebigun-training | 프록시 / 스크립트 |

## 3. 호출 방식 매핑 규칙

upstream `SKILL.md` + `k-skill-proxy/server.js` 라우트를 분석해 결정.

- **프록시 기반(키 불필요, 다수):** 기존 `safe_proxy_get()`/`emit()` 패턴 재사용.
- **API 키 필요:** `dependency.py`의 `SkillDependency` 패턴으로 키 존재 여부 체크.
  없으면 친절한 안내 + 설치 가이드 반환(스텁). 대상: popbill, g2b/d2b/s2b(조달청),
  localdata-business-status 등.
- **npm 패키지 기반:** `runner.run_npm()` 사용. 패키지 미설치 시 dependency 체크로 안내.
  대상: saju-fortune, naming-house.
- **로컬 전용:** kakaotalk-mac — 프록시 없이 로컬 파일/실행. macOS 전용임을 manifest에 명시.

## 4. 파일 구조 (기존 패턴 준수)

```
cli_anything/k_skill/skills/<domain>/__init__.py   # Click group + 명령어
cli_anything/k_skill/skills/<domain>/manifest.yaml # 메타데이터
tests/test_<domain>.py                             # 등록/파라미터/목(mock) 테스트
```

- `loader.discover_cli_groups()`가 `skills/` 하위 디렉터리를 자동 스캔하므로
  `cli.py`의 `register_skill_commands()` 수정 불필요(신규 도메인도 자동 발견).
- 신규 도메인은 `manifest.yaml`의 `domain` 필드와 `__init__.py`의 Click `cli` 그룹만
  있으면 등록됨.

## 5. 테스트 / 검증

- 도메인별 `tests/test_<domain>.py` 추가:
  - manifest 로드/필수 필드 존재
  - 명령어 등록 확인(`k-skill <domain> --help`)
  - 프록시 호출은 `httpx` MockTransport로 목 테스트(기존 패턴)
  - 키 필요 스킬은 dependency 체크 경로 테스트
- `tests/test_phase2_skills.py`의 `test_total_skill_count` 기대값 **95 → 111** 갱신.
- 검증 절차:
  1. `pytest tests/ -q` 전체 통과
  2. `k-skill list --all -j`로 16개 신규 스킬 등록 확인
  3. `k-skill <domain> <skill> --help` 동작 확인
  4. 라이브 호출은 네트워크/키 필요 → 수동(자동 테스트 제외, 목 처리)

## 6. 부수 수정

- `cli_anything/k_skill/cli.py` 상단 도움말의 "에이전트 빠른 실행 가이드"에
  신규 도메인(fortune/business/recruiting/messaging) 노출.
- `pyproject.toml` 버전 CalVer bump (예: 2026.06.15.1 → 2026.07.10.1).
- `tests/test_loader.py` 등 도메인 수 기대값 있는 경우 갱신.

## 7. 실행 접근 (병렬 서브에이전트)

16개 스킬을 도메인 배치로 나누어 병렬 포팅:
- 배치1: `fortune`(2) / `messaging`(1)
- 배치2: `business`(7)
- 배치3: `recruiting`(3) + `life` 확장(3)
각 서브에이전트는 엄격한 템플릿 + 기존 패턴을 따라 작성 후,
해당 도메인 단위 테스트 통과까지 검증. 최종 통합에서 전체 테스트 스위트
+ `list --all` 등록 확인.

## 8. 범위 밖 (Out of Scope)

- upstream의 `packages/` npm 워크스페이스 자체 이식(해당 npm 패키지는
  PyPI/registry에서 설치해 사용).
- `.changeset`/CI/release-please 파이프라인 이식(로컬은 PyPI setuptools 배포).
- 이미 포팅된 95개 스킬의 리팩터링(이번 작업은 누락 스킬 추가에 한정).
- 라이브 API 키 발급/실제 외부 호출 검증(목 기반 테스트로 대체).
