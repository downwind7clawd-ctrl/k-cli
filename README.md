<p align="center">
  <strong>k-skill</strong><br>
  <a href="https://github.com/NomaDamas/k-skill">NomaDamas/k-skill</a>의 CLI 래퍼<br>
  114개 한국 특화 스킬을 모든 AI 에이전트에서 단일 명령어로
</p>

<p align="center">
  <img src="https://img.shields.io/badge/skills-114-blue" alt="114 skills">
  <img src="https://img.shields.io/badge/domains-18-green" alt="18 domains">
  <img src="https://img.shields.io/badge/tests-143 passed-success" alt="143 tests">
  <img src="https://img.shields.io/badge/license-MIT-yellow" alt="MIT">
  <img src="https://img.shields.io/badge/python-3.10+-blue" alt="Python 3.10+">
</p>

---

## 왜 만들었는가

**[NomaDamas/k-skill](https://github.com/NomaDamas/k-skill)**은 한국인을 위한 114개 AI 에이전트 스킬 모음입니다. 날씨, 교통, 부동산, 당근마켓, 법령 검색까지 — 한국 생활에서 빼놓을 수 없는 도구들이죠. 이 프로젝트의 모든 스킬 커리큘럼과 프록시 인프라는 오직 **NomaDamas님 한 분의 열정**으로 만들어졌습니다.

하지만 에이전트 스킬이 많아지면서 몇 가지 문제가 생겼습니다:

- **컨텍스트 오염** — 스킬을 명시적으로 지정해야 하는 건 똑같은데, 스킬이 늘어날수록 사용하지 않는 스킬까지 에이전트에 로드되어 컨텍스트 윈도우를 잡아먹고 에이전트가 난잡해짐
- **다중 에이전트 설정의 고통** — Hermes, OpenCode, Claude Code, Codex 등 여러 에이전트를 쓰면 각각의 `settings.json`에 스킬을 지정하거나 심볼릭 링크를 만들어야 함
- **스킬명의 불필요한 컨텍스트 소비** — 114개의 스킬명이 프롬프트에 포함되는 것 자체가 비용

원작자님께 직접 CLI 래핑을 요청드렸으나 바쁘신 듯하여, Gemini Pro 4개월 무료 쿠폰을 받은 김에 직접 만들게 되었습니다.

---

> ## 🙏 NomaDamas님께 감사합니다
>
> 이 프로젝트는 **단 한 줄의 코드도 원래부터 존재하지 않았습니다.**
> 114개의 스킬 설계, 프록시 인프라 구축, API 연동, 그리고 한국 AI 커뮤니티에 기여해주신 모든 노력은 전적으로 [NomaDamas](https://github.com/NomaDamas)님의 것입니다.
>
> 저는 단지 그 위에 CLI 래퍼를 얹었을 뿐입니다.
>
> **본 프로젝트를 사용해주신다면, 원작자님께 스타를 눌러주세요.** ⭐
>
> 👉 [github.com/NomaDamas/k-skill](https://github.com/NomaDamas/k-skill)

## 아키텍처

[HKUDS/CLI-Anything](https://github.com/HKUDS/CLI-Anything) (홍콩대학) 프레임워크 기반으로 구현되었습니다. 에이전트 네이티브 CLI 래핑을 통해 `pip install` 한 번으로 모든 AI 에이전트가 스킬을 발견하고 사용할 수 있습니다.

---

## 설치

`k-skill-cli`는 **PyPI에 배포**되어 있어 한 줄로 설치됩니다:

```bash
pip install k-skill-cli
```

설치 후 `k-skill --help` 로 CLI 진입점이 생성되는지 확인하세요.

의존성: Python 3.10+, curl

## 사용법

```bash
# 날씨/환경
k-skill weather fine-dust "서울 강남구" -j
k-skill weather forecast --lat 37.5665 --lon 126.9780 -j
k-skill weather han-river-water-level -j

# 지도/길찾기
k-skill map kakao-search "강남역" -j
k-skill map kakao-directions --origin "127.1101,37.3947" --destination "127.1082,37.4020" -j

# 교통
k-skill transit seoul-subway-arrival "강남" -j
k-skill transit ktx "서울" "부산" --date 20260523 -j
k-skill transit srt "수서" "부산" --date 20260523 -j
k-skill transit express-bus "서울경부" "부산" --date 20260523 -j
k-skill transit seoul-bike nearby --lat 37.5665 --lon 126.9780 -j
k-skill transit seoul-bike availability --lat 37.5665 --lon 126.9780 -j

# 금융/공공
k-skill finance korean-stock "삼성전자" -j
k-skill finance nts status --b-no 1234567890 -j
k-skill finance kosis "통계명" -j
k-skill finance kstartup announcements --keyword "청년" --open Y -j
k-skill finance korean-law "검색어" -j
k-skill finance gongsijiga "지역명" -j
k-skill finance national-pension --name "삼성전자(주)" -j
k-skill finance fsc-corp --name "삼성전자" -j
k-skill finance g2b-sanction --bizno 124-81-00998 -j
k-skill finance nts-delinquency --name "OO건설" -j

# 부동산
k-skill realestate real-estate-search search --lawd-cd 11680 --date 202403 -j
k-skill realestate lh-notice-search search --status "공고중" -j
k-skill realestate sh-notice "행복주택" --category 임대 -j

# 쇼핑
k-skill shopping naver-shopping-search "에어팟" -j
k-skill shopping ohou-deal --min-discount 30 -j
k-skill shopping olive-young "선크림" -j
k-skill shopping coupang "키보드" -j

# 당근마켓/중고거래
k-skill market daangn-market --region "서울" -j
k-skill market bunjang "아이폰" -j

# 스포츠/엔터
k-skill sports kbo --date 2026-05-23 -j
k-skill sports cinema theaters --chain cgv --keyword "강남" -j
k-skill sports lotto -j

# 검색/조사
k-skill search naver-news-search "AI" -j
k-skill search naver-blog "제주 여행" -j
k-skill search patent "반도체" -j
k-skill search sillok "검색어" -j

# 생활/편의
k-skill life election "오세훈" --election 시도지사 -j
k-skill life emergency-room "광화문" --limit 5 -j
k-skill life cheap-gas-nearby --lat 37.5665 --lon 126.9780 -j
k-skill life household-waste-info "강남구" -j
k-skill life drug "타이레놀" -j
k-skill life localdata-biz --name "카페" --region "서울종로구" -j

# 문서
k-skill document hwp-convert "문서.hwp" -j
k-skill document spell-check "안녕하세여" -j
k-skill document char-count "글자수를 셉니다" -j
k-skill document korean-middle-korean word "가다" -j
k-skill document humanizer "AI가 작성한 글" -j

# 배송
k-skill delivery delivery "1234567890" -j

# 스킬 목록 확인
k-skill list --all -j
k-skill list -d weather -j

# 의존성 체크
k-skill setup check -j
```

모든 명령에 `-j` (`--json`) 플래그를 붙이면 구조화된 JSON 응답을 받을 수 있습니다.

---

## 스킬 목록 (18개 도메인, 114개 스킬)

| 도메인 | 스킬 수 | 설명 |
|--------|--------|------|
| weather | 3 | 날씨/환경 (기상청 예보, 미세먼지, 한강수위) |
| map | 2 | 지도/길찾기 (카카오맵 장소/길찾기) |
| transit | 9 | 대중교통 (지하철, 버스, SRT, KTX, 항공편, 따릉이) |
| life | 23 | 생활/편의 (주유소, 쓰레기, 주차장, 맛집, 응급실, 인허가 조회 등) |
| finance | 13 | 금융/공공 (주식, DART, 코시스, 사업자등록, 법률, 국민연금, 금융위, 부정당, 체납) |
| realestate | 5 | 부동산 (실거래가, 공시지가, LH/SH 공고, 경매) |
| shopping | 7 | 쇼핑 (네이버, 올리브영, 다이소, 쿠팡) |
| market | 4 | 중고거래 (당근마켓, 번개장터, 중고차) |
| search | 6 | 검색 (네이버 뉴스/블로그, 특허, 실록, 장학금) |
| document | 7 | 문서 (HWP, 맞춤법, 글자수, 중세 한국어, AI 윤문) |
| sports | 8 | 스포츠 (KBO, KBL, K리그, LCK, 로또, 영화관) |
| travel | 3 | 여행 (여행지, 숙소, 마이리얼트립) |
| delivery | 1 | 택배 송장 조회 |
| other | 4 | 기타 유틸리티 |
| fortune | 2 | 사주/작명 (사주풀이, 집이름 작명) |
| business | 7 | 비즈니스/법무/조달 (사업체건강, 법원진행, 나라장터, 사업자등록) |
| recruiting | 3 | 채용 (이력서 매칭, 잡코리아/사람인 인재검색) |
| messaging | 1 | 메시징 (카카오톡 Mac) |

## Self-host 프록시

기본값은 공개 프록시(`k-skill-proxy.nomadamas.org`)를 사용합니다. 직접 호스팅하려면:

```bash
KSKILL_PROXY_BASE_URL=http://localhost:3456 k-skill weather forecast --lat 37.5 --lon 127.0 -j
```

## 개발

```bash
# 클론
git clone https://github.com/NomaDamas/cli-anything-k-skill.git
cd cli-anything-k-skill

# 설치 (dev)
pip install -e ".[dev]"

# 테스트 (143개 통과 / 155개 수행)
pytest tests/ -v

# 스킬 추가 방법
# 1. skills/<domain>/__init__.py에 Click 명령어 구현
# 2. skills/<domain>/manifest.yaml에 스킬 엔트리 추가
# ※ loader.py가 manifest.yaml을 자동 발견하므로 cli.py 수정 불필요
```

---

## 설치

```bash
pip install k-skill-cli
```

PyPI 최신 버전(현재 **2026.07.10.2**)이 설치됩니다. 별도 빌드/업로드 불필요합니다.

> 메인테이너용 배포 절차(`build`/`twine`/`uv publish`, 버전 규칙 등)는 [docs/publishing.md](docs/publishing.md)를 참고하세요.

---

## Recently Removed (2026-06-07 sync)

Upstream NomaDamas/k-skill이 3개 스킬을 `legacy/unsupported-skills/`로 이동하여 프록시 호출 시 404가 반환됩니다. 후속 동기화에서 제외했습니다.

| 도메인 | 스킬 | 사유 |
|--------|------|------|
| map | `naver-directions` | 프록시 404 (upstream `legacy/unsupported-skills/`) |
| map | `naver-geocode` | 프록시 404 (upstream `legacy/unsupported-skills/`) |
| life | `blue-ribbon` | 프록시 404 (upstream `legacy/unsupported-skills/`) |

---

## 라이선스

MIT License


이 프로젝트는 [NomaDamas/k-skill](https://github.com/NomaDamas/k-skill)의 스킬 커리큘럼과 [HKUDS/CLI-Anything](https://github.com/HKUDS/CLI-Anything) 프레임워크를 기반으로 만들어졌습니다. 두 원작 프로젝트의 라이선스를 존중합니다.

```
MIT License

Copyright (c) 2026 cli-anything-k-skill contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
