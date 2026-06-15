"""문서 도메인 스킬."""

import asyncio
import click

from cli_anything.k_skill.runner import run_npm, run_script
from cli_anything.k_skill.output import emit, error_response


@click.group(name='document', help='문서: HWP, 맞춤법, 글자수, 윤문')
def cli():
    pass

@cli.command(name='hwp-convert', help='HWP/HWPX 문서를 PDF 등으로 변환')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def hwp_convert(query, as_json, timeout):
    """HWP 변환."""
    args = [query] if query else []
    result = asyncio.run(run_npm('kordoc', args, timeout=timeout))
    emit(result, as_json=as_json)

@cli.command(name='rhwp-debug', help='rhwp Rust CLI로 HWP 레이아웃 디버깅')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def rhwp_debug(query, as_json, timeout):
    """HWP 레이아웃 디버그."""
    args = [query] if query else []
    result = asyncio.run(run_script('rhwp', args, timeout=timeout))
    emit(result, as_json=as_json)

@cli.command(name='rhwp-edit', help='HWP 문서 편집 (k-skill-rhwp)')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def rhwp_edit(query, as_json, timeout):
    """HWP 편집."""
    args = [query] if query else []
    result = asyncio.run(run_npm('k-skill-rhwp', args, timeout=timeout))
    emit(result, as_json=as_json)

@cli.command(name='spell-check', help='한국어 맞춤법/문법 검사')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def spell_check(query, as_json, timeout):
    """맞춤법 검사."""
    args = [query] if query else []
    result = asyncio.run(run_script('korean_spell_check.py', args, timeout=timeout))
    emit(result, as_json=as_json)

@cli.command(name='char-count', help='한국어 글자/어절/문단 수 카운트')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=30, type=int, help='타임아웃(초)')
@click.argument('query', required=False)
def char_count(query, as_json, timeout):
    """글자 수 세기."""
    args = [query] if query else []
    result = asyncio.run(run_npm('korean-character-count', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='korean-middle-korean', help='중세 한국어 형태/원형/예문/번역 검색')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.option('--timeout', '-t', default=60, type=int, help='타임아웃(초)')
@click.option('--limit', '-l', default=10, type=int, help='결과 개수 (1~50, 기본 10)')
@click.argument('search_type', type=click.Choice(['word', 'spelling', 'origin', 'example', 'translation']))
@click.argument('query')
def korean_middle_korean(search_type, query, limit, as_json, timeout):
    """중세 한국어 형태/원형/예문/번역 검색.

    upstream NomaDamas/k-skill의 korean-middle-korean 스킬을 래핑합니다.
    scripts/korean_middle_korean_search.js를 호출합니다.

    필요 의존성: node, npm (prebuild된 node_modules 필요)

    예시:
      k-skill document korean-middle-korean word '가다' -j
      k-skill document korean-middle-korean origin '나아가다' -j
      k-skill document korean-middle-korean example '사랑' -j
      k-skill document korean-middle-korean translation 'mountains' -j
    """
    limit = max(1, min(limit, 50))
    args = [search_type, query, "--limit", str(limit), "--json"]
    result = asyncio.run(run_script('korean_middle_korean_search.js', args, timeout=timeout))
    emit(result, as_json=as_json)


@cli.command(name='humanizer', help='AI 한국어 글 윤문 (번역체/AI 상투어 제거)')
@click.option('--length', type=int, help='목표 글자수')
@click.option('--json', '-j', 'as_json', is_flag=True, help='JSON 출력')
@click.argument('text', required=False)
def humanizer(length, as_json, text):
    """AI 한국어 글 윤문.

    AI가 쓴 티가 나는 한국어 글을 자연스러운 사람 글로 고칩니다.
    프롬프트 기반 스킬로, 에이전트가 SKILL.md를 읽고 작업을 수행합니다.

    예시:
      k-skill document humanizer "AI가 작성한 글을 자연스럽게 고쳐주세요"
      k-skill document humanizer --length 1000 "수정할 텍스트"
    """
    result = {
        "skill": "korean-humanizer",
        "status": "success",
        "data": {
            "type": "prompt-based",
            "description": "AI 한국어 글 윤문 스킬입니다.",
            "usage": "이 스킬은 프롬프트 기반으로, 에이전트가 SKILL.md를 읽고 번역체/AI 상투어를 감지하여 수정합니다.",
            "input_text": text,
            "target_length": length,
            "instructions": [
                "1. 입력 텍스트에서 AI 흔적(A~J 카테고리)을 감지합니다",
                "2. 심각도(S1/S2/S3)로 분류합니다",
                "3. 의미를 보존하면서 다시 씁니다",
                "4. 목표 글자수가 있으면 그에 맞춰 조절합니다"
            ],
            "detection_categories": {
                "A": "번역체",
                "B": "영어 인용",
                "C": "구조적",
                "D": "관용구",
                "E": "리듬",
                "F": "수식",
                "G": "hedging",
                "H": "접속사",
                "I": "형식명사",
                "J": "시각 장식"
            }
        }
    }
    emit(result, as_json=as_json)
