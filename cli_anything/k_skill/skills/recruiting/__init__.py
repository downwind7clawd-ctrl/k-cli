"""채용 스킬 — 이력서 매칭, 인재검색."""

import asyncio
import click
import httpx

from cli_anything.k_skill.runner import run_npm
from cli_anything.k_skill.output import emit, error_response


@click.group(name='recruiting', help='채용: 이력서 매칭, 인재검색')
def cli():
    pass


# direct httpx-based: job-posting-match (구직자 관점 공고 매칭)
# upstream SKILL.md: 잡코리아 공개 검색 결과 페이지
#   https://www.jobkorea.co.kr/Search/?stext=<검색어>
@cli.command(name='job-posting-match', help='이력서 기반 채용공고 매칭')
@click.option('--json', '-j', 'as_json', is_flag=True)
@click.option('--timeout', '-t', default=30, type=int)
@click.option('--resume-file', help='이력서 파일 경로')
@click.option('--resume-text', help='이력서 텍스트')
@click.option('--keyword', help='검색 키워드 (이력서 대신 사용)')
@click.option('--location', help='희망 지역')
@click.option('--negative', help='제외 키워드 (쉼표 구분)')
@click.option('--limit', default=10, type=int)
def job_posting_match(resume_file, resume_text, keyword, location, negative, limit, as_json, timeout):
    stext = resume_text or keyword or ""
    params = {"stext": stext, "limit": limit}
    if resume_file:
        params["resumeFile"] = resume_file
    if location:
        params["loc"] = location
    if negative:
        params["exclude"] = negative
    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.get(
                "https://www.jobkorea.co.kr/Search/",
                params=params,
            )
            resp.raise_for_status()
            emit({"status": "success", "data": resp.json()}, as_json=as_json)
    except httpx.HTTPStatusError as e:
        emit(error_response("job-posting-match", "HTTP_ERROR", f"HTTP {e.response.status_code}"), as_json=as_json)
    except Exception as e:
        emit(error_response("job-posting-match", "UNKNOWN", str(e)), as_json=as_json)


# direct httpx-based: jobkorea-talent-search (기업회원 인재검색, no-login 공개 검색)
# upstream SKILL.md no-login fallback: 잡코리아 공개 검색 결과 페이지
#   https://www.jobkorea.co.kr/Search/?stext=<검색어>
@cli.command(name='jobkorea-talent', help='잡코리아 인재검색')
@click.option('--json', '-j', 'as_json', is_flag=True)
@click.option('--timeout', '-t', default=30, type=int)
@click.option('--keyword', help='검색 키워드')
@click.option('--work-area', help='근무지역')
@click.option('--career-min', default=0, type=int)
@click.option('--career-max', default=10, type=int)
@click.option('--limit', default=20, type=int)
def jobkorea_talent(keyword, work_area, career_min, career_max, limit, as_json, timeout):
    params = {
        "stext": keyword or "",
        "careerMin": career_min,
        "careerMax": career_max,
        "limit": limit,
    }
    if work_area:
        params["loc"] = work_area
    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.get(
                "https://www.jobkorea.co.kr/Search/",
                params=params,
            )
            resp.raise_for_status()
            emit({"status": "success", "data": resp.json()}, as_json=as_json)
    except httpx.HTTPStatusError as e:
        emit(error_response("jobkorea-talent-search", "HTTP_ERROR", f"HTTP {e.response.status_code}"), as_json=as_json)
    except Exception as e:
        emit(error_response("jobkorea-talent-search", "UNKNOWN", str(e)), as_json=as_json)


# npm-based: saramin-talent-search
@cli.command(name='saramin-talent', help='사람인 인재검색')
@click.option('--json', '-j', 'as_json', is_flag=True)
@click.option('--timeout', '-t', default=30, type=int)
@click.option('--keyword', help='검색 키워드')
@click.option('--location', help='지역')
@click.option('--career-min', default=0, type=int)
@click.option('--career-max', default=10, type=int)
@click.option('--limit', default=20, type=int)
def saramin_talent(keyword, location, career_min, career_max, limit, as_json, timeout):
    args = []
    if keyword:
        args += ['--keyword', keyword]
    if location:
        args += ['--location', location]
    args += ['--career-min', str(career_min), '--career-max', str(career_max), '--limit', str(limit)]
    result = asyncio.run(run_npm('saramin-talent-search', args, timeout=timeout))
    emit(result, as_json=as_json)
