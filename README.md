<p align="center">
  <strong>k-cli</strong><br>
  [NomaDamas/k-skill](https://github.com/NomaDamas/k-skill)의 CLI 래퍼<br>
  86개 한국 특화 스킬을 모든 AI 에이전트에서 단일 명령어로
</p>

<p align="center">
  <img src="https://img.shields.io/badge/skills-86-blue" alt="86 skills">
  <img src="https://img.shields.io/badge/domains-13-green" alt="13 domains">
  <img src="https://img.shields.io/badge/tests-92 passed-success" alt="92 tests">
  <img src="https://img.shields.io/badge/license-MIT-yellow" alt="MIT">
  <img src="https://img.shields.io/badge/python-3.10+-blue" alt="Python 3.10+">
</p>

---

## 왜 만들었는가

**[NomaDamas/k-skill](https://github.com/NomaDamas/k-skill)**은 한국인을 위한 86개 AI 에이전트 스킬 모음입니다. 날씨, 교통, 부동산, 당근마켓, 법령 검색까지 — 한국 생활에서 빼놓을 수 없는 도구들이죠. 이 프로젝트의 모든 스킬 커리큘럼과 프록시 인프라는 오직 **NomaDamas님 한 분의 열정**으로 만들어졌습니다.

하지만 에이전트 스킬이 많아지면서 몇 가지 문제가 생겼습니다:

- **컨텍스트 오염** — 스킬을 명시적으로 지정해야 하는 건 똑같은데, 스킬이 늘어날수록 사용하지 않는 스킬까지 에이전트에 로드되어 컨텍스트 윈도우를 잡아먹고 에이전트가 난잡해짐
- **다중 에이전트 설정의 고통** — Hermes, OpenCode, Claude Code, Codex 등 여러 에이전트를 쓰면 각각의 `settings.json`에 스킬을 지정하거나 심볼릭 링크를 만들어야 함
- **스킬명의 불필요한 컨텍스트 소비** — 86개의 스킬명이 프롬프트에 포함되는 것 자체가 비용

원작자님께 직접 CLI 래핑을 요청드렸으나 바쁘신 듯하여, Gemini Pro 4개월 무료 쿠폰을 받은 김에 직접 만들게 되었습니다.

---

> ## 🙏 NomaDamas님께 감사합니다
>
> 이 프로젝트는 **단 한 줄의 코드도 원래부터 존재하지 않았습니다.**
> 86개의 스킬 설계, 프록시 인프라 구축, API 연동, 그리고 한국 AI 커뮤니티에 기여해주신 모든 노력은 전적으로 [NomaDamas](https://github.com/NomaDamas)님의 것입니다.
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

```bash
pip install cli-anything-k-skill
```

의존성: Python 3.10+, curl

## 사용법

```bash
# 날씨/환경
k-skill weather forecast --lat 37.5665 --lon 126.9780 -j
k-skill weather fine-dust --region "서울 강남구" -j
k-skill weather han-river -j

# 교통
k-skill transit subway --station "강남" -j
k-skill transit bus --route "500" -j
k-skill transit srt-booking -j          # SRT 예약 (인증 필요)
k-skill transit ktx-booking -j          # KTX 예약 (인증 필요)

# 금융/공공
k-skill finance stock --query "삼성전자" -j
k-skill finance dart --corp "삼성전자" -j
k-skill finance nts-reg --bizno "123-45-67890" -j
k-skill finance kosis --stat-id "1061001" -j

# 부동산
k-skill realestate trade-price --region "서울 강남구" --type "아파트" -j
k-skill realestate gongsijiga --addr "서울 강남구 역삼동" -j
k-skill realestate lh-notice -j

# 쇼핑
k-skill shopping naver-shopping --query "에어팟" -j
k-skill shopping olive-young --query "선크림" -j
k-skill shopping daiso --query "수납함" -j
k-skill shopping coupang --query "키보드" -j

# 당근마켓/중고거래
k-skill market daangn-market --region "서울" --query "맥북" -j

# 스포츠/엔터
k-skill sports kbo --date 2026-05-21 --team "LG" -j
k-skill sports lotto -j
k-skill sports movie --region "강남" -j

# 검색/조사
k-skill search naver-news --query "AI" -j
k-skill search naver-blog --query "제주 여행" -j
k-skill search patent --query "반도체" -j

# 생활/편의
k-skill life gas-station --region "서울" -j
k-skill life waste --region "강남구" -j
k-skill life parking --region "강남역" -j
k-skill life hospital --region "서울" -j

# 문서
k-skill document hwp-read --file "문서.hwp" -j
k-skill document spell-check --text "안녕하세여" -j
k-skill document char-count --text "글자수를 셉니다" -j

# 배송
k-skill delivery track --carrier "CJ대한통운" --number "1234567890" -j

# 스킬 목록 확인
k-skill list --all
k-skill list --domain weather

# 의존성 체크
k-skill setup check
k-skill setup install-deps
```

모든 명령에 `-j` (`--json`) 플래그를 붙이면 구조화된 JSON 응답을 받을 수 있습니다.

---

## 스킬 목록 (13개 도메인, 86개 스킬)

| 도메인 | 스킬 수 | 설명 |
|--------|--------|------|
| weather | 3 | 날씨/환경 (기상청 예보, 미세먼지, 한강수위) |
| transit | 8 | 대중교통 (지하철, 버스, SRT, KTX, 항공편) |
| life | 23 | 생활/편의 (주유소, 쓰레기, 주차장, 맛집, 응급실 등) |
| finance | 9 | 금융/공공 (주식, DART, 코시스, 사업자등록, 법률) |
| realestate | 5 | 부동산 (실거래가, 공시지가, LH/SH 공고, 경매) |
| shopping | 7 | 쇼핑 (네이버, 올리브영, 다이소, 쿠팡) |
| market | 4 | 중고거래 (당근마켓, 번개장터, 중고차) |
| search | 6 | 검색 (네이버 뉴스/블로그, 특허, 실록, 장학금) |
| document | 5 | 문서 (HWP, 맞춤법, 글자수, 한국어 슬랭) |
| sports | 8 | 스포츠 (KBO, KBL, K리그, LCK, 로또, 영화관) |
| travel | 3 | 여행 (여행지, 숙소, 마이리얼트립) |
| delivery | 1 | 택배 송장 조회 |
| other | 4 | 기타 유틸리티 |

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

# 테스트 (92개)
pytest tests/ -v

# 의존성 스캐폴딩로 신규 스킬 추가
python scripts/add_skill.py --domain transit --name airport-lounge
```

---

## 라이선스

MIT License

버전 관리는 CalVer + patch 방식(`YYYY.MM.DD.P`)을 사용합니다. 버전 번호는 k-skill과 동기화한 날짜를 기준으로 합니다.

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
