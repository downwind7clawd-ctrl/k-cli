# 메인테이너용 배포 가이드 (Publishing)

이 문서는 **메인테이너 전용**입니다. 일반 사용자는 `pip install k-skill-cli` 만으로 설치되므로 이 절차가 필요 없습니다.

## 버전 규칙

버전은 **CalVer + patch** 방식을 사용합니다: `YYYY.MM.DD.P`

- `YYYY.MM.DD` — k-skill과 동기화한 날짜 (예: 2026-07-20 → `2026.07.20`)
- `P` — 해당 날짜 내 패치 번호 (첫 배포는 `.1`, 재배포는 `.2`, ...)
- 예: `2026.07.10.2`

> PyPI는 동일 버전 재업로드를 허용하지 않으므로, 배포 실패로 재업로드할 때는 patch 번호를 올려야 합니다.

버전은 `pyproject.toml`의 `version` 필드를 수정합니다. 문서(SKILL.md, README, BUGFIX_LOG)의 버전 명시도 함께 갱신하세요.

## 배포 절차

### 1. 패키지 빌드 (sdist + wheel)

```bash
python -m build
```

### 2. 업로드 (twine)

```bash
pip install twine
TWINE_USERNAME=__token__ TWINE_PASSWORD="$PYPI_API_TOKEN" twine upload dist/*
```

### 2-대안. uv publish (twine 불필요)

```bash
UV_PUBLISH_TOKEN="$PYPI_API_TOKEN" uv publish dist/*
```

### 3. (선택) TestPyPI에서 먼저 검증

```bash
TWINE_USERNAME=__token__ TWINE_PASSWORD="$TEST_PYPI_API_TOKEN" twine upload --repository testpypi dist/*
```

## 보안 주의

- PyPI API 토큰은 **절대 하드코딩하지 마세요**.
- `.env` 파일 또는 셸 환경변수로 주입하세요: `PYPI_API_TOKEN`, `TEST_PYPI_API_TOKEN`.
- `.env`는 `.gitignore`에 포함되어 있어 깃 푸시 시 제외됩니다.

## 배포 전 체크리스트

- [ ] `pyproject.toml` 버전 갱신
- [ ] `pytest tests/ -q` 전부 통과
- [ ] `python -m cli_anything.k_skill --help` 정상 동작
- [ ] `manifest.yaml`가 wheel에 포함되었는지 확인 (패키지 데이터)
- [ ] 문서(SKILL.md, README, BUGFIX_LOG) 버전/스킬 수 갱신
- [ ] `dist/` 이전 빌드 잔여물 정리 후 재빌드
