# BUGFIX LOG — k-cli / k-skill CLI

이 문서는 동기화, 버그 수정, 대규모 리팩토링 작업의 변경 이력을 누적 기록합니다.

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
