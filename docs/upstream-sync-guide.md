# k-skill 업스트림 동기화 가이드

k-skill (upstream: `NomaDamas/k-skill`)에 신규 스킬이 추가되면, k-cli에서도 **별도 래핑 개발**이 필요합니다. `git pull`만으로는 반영되지 않습니다.

본 가이드는 **모든 신규 k-skill에 공통으로 적용**되는 표준 절차를 정의합니다.

---

## 왜 별도 개발이 필요한가?

k-cli는 각 스킬을 **Click CLI 명령어 + `safe_proxy_get()`/`emit()` 래핑 코드**로 Python에서 직접 구현합니다. k-skill의 `SKILL.md`는 프롬프트 기반이지만, k-cli는 실제 API 호출을 수행하는 실행 가능한 CLI입니다.

```
k-skill (upstream)          k-cli (우리)
├── <skill-name>/          ├── skills/<domain>/__init__.py   ← Click 명령어 구현
│   └── SKILL.md           ├── skills/<domain>/manifest.yaml  ← 메타데이터
│   (프롬프트 정의)         └── proxy.py → /v1/<skill>/endpoint
```

---

## 1. 업스트림 변경 감지

### 1-1. 크론/수동 점검

```bash
cd ~/nas_1tb/dev/k-skill
git fetch origin
git log --oneline HEAD..origin/main   # 뒤처진 커밋 확인
```

### 1-2. 신규 스킬 감지

k-skill에 있는 스킬 vs k-cli에 래핑된 스킬을 비교:

```bash
# k-skill에 있는 모든 스킬 디렉토리 vs k-cli에 래핑된 스킬 비교
diff <(cd ~/nas_1tb/dev/k-skill && find . -maxdepth 1 -mindepth 1 -type d ! -name '.*' | sort | sed 's|./||') \
     <(cd ~/nas_1tb/dev/k-cli && grep -rh 'name:' cli_anything/k_skill/skills/*/manifest.yaml | awk '{print $2}' | sort)
```

### 1-3. 감지 자동화 (선택)

크론잡으로 정기 실행하면 신규 스킬 추가 시 알림을 받을 수 있습니다.

---

## 2. 신규 스킬 래핑 절차

### Step 1: k-skill SKILL.md 분석

upstream의 `SKILL.md`에서 다음 정보를 추출:

| 항목 | 확인 포인트 |
|------|-----------|
| **스킬명** | YAML frontmatter `name` 필드 |
| **카테고리** | `metadata.category` → k-cli 도메인 매핑 |
| **호출 방식** | `k-skill-proxy` 경유 or 직접 HTTP or MCP |
| **엔드포인트** | 프록시 라우트(`/v1/...`) or 공개 API URL |
| **필수 파라미터** | 필수/선택 입력값 |
| **응답 형식** | 반환 데이터 구조 |

### Step 2: 호출 방식별 래핑

#### A. 프록시 기반 (k-skill-proxy 라우트 있음)

가장 간단한 패턴. `safe_proxy_get()` 사용.

```python
"""도메인 설명 스킬."""

import click
from cli_anything.k_skill.proxy import safe_proxy_get
from cli_anything.k_skill.output import emit


@click.group()
def cli():
    """도메인 설명."""
    pass


@cli.command()
@click.option("--param1", required=True, help="설명")
@click.option("--param2", required=False, help="설명")
@click.option("--json", "-j", "as_json", is_flag=True, help="JSON 출력")
def skill_name(param1, param2, as_json):
    """스킬 설명.

    예시:
      k-cli domain skill-name --param1 "값" -j
    """
    params = {"param1": param1}
    if param2:
        params["param2"] = param2
    resp = safe_proxy_get("skill-name", "/v1/skill-name/endpoint", params)
    emit(resp, as_json=as_json)
```

**프록시 라우트 확인:** `k-skill-proxy` 서버의 `server.js`에서 `app.get("/v1/...")` 패턴 확인.

#### B. 직접 HTTP 호출 (공개 API, 프록시 없음)

`proxy.py`의 `proxy_get()`을 쓰지 않고 직접 `httpx`로 호출. 프라이빗 API 키가 필요한 경우 `dependency.py` 패턴 참고.

#### C. MCP 기반

`mcp_client.py` 또는 `local_mcp_bridge.py` 패턴 참고. MCP 서버 설치 + 로컬 실행 필요.

### Step 3: 도메인 매핑 및 파일 생성

#### 도메인 매핑 규칙

k-skill의 `metadata.category`를 k-cli 도메인 디렉토리에 매핑:

| k-skill category | k-cli 도메인 |
|-----------------|-------------|
| weather, environment | `skills/weather/` |
| map, location | `skills/map/` |
| sports, entertainment | `skills/sports/` |
| finance, law, business | `skills/finance/` |
| transit, transportation | `skills/transit/` |
| shopping, retail | `skills/shopping/` |
| realestate, housing | `skills/realestate/` |
| market, secondhand | `skills/market/` |
| search | `skills/search/` |
| document, utility | `skills/document/` |
| delivery | `skills/delivery/` |
| life, health, civic | `skills/life/` |
| travel | `skills/travel/` |
| other, utility, meta | `skills/other/` |

> **새 카테고리가 필요하면:** 새 도메인 디렉토리 생성 + `manifest.yaml` 작성.

#### 파일 생성 체크리스트

```
skills/<domain>/
├── __init__.py        # ← Click 명령어 구현 (필수)
└── manifest.yaml      # ← 스킬 메타데이터 (필수)
```

### Step 4: manifest.yaml 작성

```yaml
domain: <domain-name>
description: <도메인 설명>
skills:
  <skill_key>:
    name: <k-skill 스킬명>
    display_name: <표시명>
    description: <스킬 설명>
    category: <카테고리>
    requires:
      proxy: true    # 프록시 기반인 경우
      # mcp: "server-name"  # MCP 기반인 경우
```

### Step 5: 기존 도메인에 추가 vs 새 도메인

**기존 도메인에 추가** (예: `life/`에 새 스킬 추가):
1. `skills/life/__init__.py`에 `@cli.command()` 추가
2. `skills/life/manifest.yaml`에 스킬 엔트리 추가

**새 도메인 생성** (카테고리가 기존에 없는 경우):
1. `skills/<new-domain>/__init__.py` 생성 (Click group + 명령어)
2. `skills/<new-domain>/manifest.yaml` 생성
3. `cli.py` 상단 도움말의 에이전트 빠른 실행 가이드에 추가

> **참고:** `loader.py`의 `discover_cli_groups()`가 `skills/` 하위 디렉토리를 자동 스캔하므로, `cli.py`의 `register_skill_commands()`는 수정 불필요. manifest.yaml만 있으면 자동 발견됨.

### Step 6: 테스트

```bash
cd ~/nas_1tb/dev/k-cli
pip install -e ".[dev]"                    # editable 설치 (필요시)
k-cli <domain> <skill> --param "값"        # 수동 테스트
k-cli <domain> <skill> --param "값" -j     # JSON 출력 테스트
k-cli list --all -j                        # 스킬 목록에 나타나는지 확인
```

---

## 3. 배포

```bash
# pyproject.toml CalVer 업데이트
# 예: 2026.5.23 → 2026.5.24
vim pyproject.toml

# PyPI 배포
git add -A && git commit -m "feat: add <skill-name> to <domain>"
git push
# CI/CD 파이프라인이 자동 배포하거나 수동 배포
```

---

## 4. 래핑 결정 템플릿

신규 스킬 감지 시 아래 템플릿을 복사해서 사용:

```markdown
## 스킬: <skill-name>

- **호출 방식:** [ ] 프록시 / [ ] 직접 HTTP / [ ] MCP
- **프록시 라우트:** `/v1/...` (있으면 기입)
- **할당 도메인:** `skills/<domain>/`
  - [ ] 기존 도메인에 추가
  - [ ] 신규 도메인 생성 필요
- **필수 파라미터:** (목록 기입)
- **응답 형식:** (JSON 구조 요약)
- **특이사항:** (API 키 필요, 인증 방식, 속도 제한 등)
```

---

## 5. 체크리스트 요약

- [ ] k-skill `git log`로 신규 스킬 목록 확인
- [ ] 각 스킬 `SKILL.md`에서 호출 방식/엔드포인트/파라미터 분석
- [ ] `k-skill-proxy/server.js`에서 프록시 라우트 존재 여부 확인
- [ ] 도메인 매핑 결정 (기존 or 신규)
- [ ] `__init__.py`에 Click 명령어 구현
- [ ] `manifest.yaml`에 스킬 엔트리 추가
- [ ] `cli.py` 도움말 업데이트 (에이전트 빠른 실행 가이드, 신규 도메인인 경우만)
- [ ] `k-cli list --all`로 등록 확인
- [ ] 실제 호출 테스트
- [ ] 버전 배포 (`pyproject.toml` CalVer 업데이트 → PyPI 배포)
