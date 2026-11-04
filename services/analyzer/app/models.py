from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class JobInput(StrictModel):
    id: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=12000)

    @field_validator("id", "title", "description")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value


class AnalyzeInput(StrictModel):
    resume_text: str = Field(alias="resumeText", min_length=1, max_length=20000)
    job: JobInput

    @field_validator("resume_text")
    @classmethod
    def resume_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value


class ExtractedSkill(StrictModel):
    name: str = Field(min_length=1, max_length=100)
    evidence: str = Field(min_length=1, max_length=500)


class ExtractedRequirement(StrictModel):
    name: str = Field(min_length=1, max_length=100)
    priority: Literal["required", "preferred"]
    evidence: str = Field(min_length=1, max_length=500)


class ResumeIssue(StrictModel):
    type: str = Field(min_length=1, max_length=60)
    severity: Literal["info", "warning"]
    evidence: str = Field(max_length=500)
    suggestion: str = Field(min_length=1, max_length=500)


class LlmExtraction(StrictModel):
    summary: str = Field(max_length=1000)
    education: list[str]
    experience: list[str]
    projects: list[str]
    skills: list[ExtractedSkill]
    requirements: list[ExtractedRequirement]
    issues: list[ResumeIssue]


class ResponseJob(StrictModel):
    id: str
    title: str


class ResumeResult(StrictModel):
    summary: str
    education: list[str]
    experience: list[str]
    projects: list[str]
    skills: list[ExtractedSkill]


class MatchedSkill(StrictModel):
    name: str
    weight: int
    requirement_evidence: str = Field(alias="requirementEvidence")
    resume_evidence: str = Field(alias="resumeEvidence")


class MissingSkill(StrictModel):
    name: str
    weight: int
    requirement_evidence: str = Field(alias="requirementEvidence")
    suggestion: str


class ScoreBreakdown(StrictModel):
    matched_weight: int = Field(alias="matchedWeight")
    total_weight: int = Field(alias="totalWeight")
    formula: str = "round(100 × matchedWeight / totalWeight)"


class AnalysisMeta(StrictModel):
    mode: Literal["live", "test"]
    model: str
    duration_ms: int = Field(alias="durationMs")


class AnalyzeResponse(StrictModel):
    request_id: str = Field(alias="requestId")
    job: ResponseJob
    resume: ResumeResult
    issues: list[ResumeIssue]
    matched_skills: list[MatchedSkill] = Field(alias="matchedSkills")
    missing_skills: list[MissingSkill] = Field(alias="missingSkills")
    score: int
    score_breakdown: ScoreBreakdown = Field(alias="scoreBreakdown")
    warnings: list[str]
    meta: AnalysisMeta


class ApiError(StrictModel):
    code: str
    message: str
    request_id: str = Field(alias="requestId")
