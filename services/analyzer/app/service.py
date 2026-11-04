import asyncio
import time

from .config import Settings
from .llm import extract_with_llm
from .models import (
    AnalysisMeta,
    AnalyzeInput,
    AnalyzeResponse,
    ResponseJob,
    ResumeResult,
)
from .scoring import score_extraction
from .text import clean_text, evidence_in_source


async def analyze(payload: AnalyzeInput, request_id: str, settings: Settings) -> AnalyzeResponse:
    started = time.monotonic()
    resume_text = clean_text(payload.resume_text)
    job_text = clean_text(payload.job.description)
    extraction = await asyncio.wait_for(
        extract_with_llm(resume_text, job_text, settings, request_id),
        timeout=settings.service_timeout_seconds,
    )
    score = score_extraction(extraction.skills, extraction.requirements, resume_text, job_text)
    grounded_issues = []
    issue_warnings = []
    for issue in extraction.issues:
        if not issue.evidence or evidence_in_source(issue.evidence, resume_text):
            grounded_issues.append(issue)
        else:
            issue_warnings.append(f"已忽略缺少简历原文证据的问题项：{issue.type}")
    return AnalyzeResponse(
        requestId=request_id,
        job=ResponseJob(id=payload.job.id, title=payload.job.title),
        resume=ResumeResult(
            summary=extraction.summary,
            education=extraction.education,
            experience=extraction.experience,
            projects=extraction.projects,
            skills=score.skills,
        ),
        issues=grounded_issues,
        matchedSkills=score.matched,
        missingSkills=score.missing,
        score=score.score,
        scoreBreakdown=score.breakdown,
        warnings=[*score.warnings, *issue_warnings],
        meta=AnalysisMeta(
            mode=settings.llm_mode,
            model=settings.llm_model,
            durationMs=round((time.monotonic() - started) * 1000),
        ),
    )
