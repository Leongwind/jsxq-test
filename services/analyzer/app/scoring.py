from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from .errors import ServiceError
from .models import (
    ExtractedRequirement,
    ExtractedSkill,
    MatchedSkill,
    MissingSkill,
    ScoreBreakdown,
)
from .text import evidence_in_source

ALIASES = {
    "js": "JavaScript",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "springboot": "Spring Boot",
    "spring boot": "Spring Boot",
    "vue.js": "Vue",
    "vuejs": "Vue",
    "vue": "Vue",
    "redis": "Redis",
    "java": "Java",
    "mysql": "MySQL",
    "docker": "Docker",
    "restful api": "REST API",
    "rest api": "REST API",
}
VERSIONED = re.compile(r"^(vue|react|angular|python|java|node(?:\.js)?)\s*(\d+(?:\.\d+)*)$", re.I)


def _key(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return "".join(
        character for character in normalized if character.isalnum() or character in "+#."
    )


def canonicalize(value: str) -> str:
    compact = " ".join(unicodedata.normalize("NFKC", value).strip().split())
    versioned = VERSIONED.match(compact)
    if versioned:
        base = ALIASES.get(versioned.group(1).casefold(), versioned.group(1).title())
        return f"{base} {versioned.group(2)}"
    folded = compact.casefold().replace("-", " ")
    return ALIASES.get(folded, compact)


def _versioned_family(value: str) -> str | None:
    versioned = VERSIONED.match(value)
    return canonicalize(versioned.group(1)) if versioned else None


def _skill_named_in_evidence(skill_name: str, evidence: str) -> bool:
    canonical = canonicalize(skill_name)
    candidates = {skill_name, canonical}
    for alias, target in ALIASES.items():
        if target == canonical:
            candidates.add(alias)
    normalized_evidence = unicodedata.normalize("NFKC", evidence).casefold()
    for candidate in candidates:
        normalized_candidate = unicodedata.normalize("NFKC", candidate).casefold().strip()
        if not normalized_candidate:
            continue
        parts = [re.escape(part) for part in re.split(r"[\s._-]+", normalized_candidate) if part]
        flexible_phrase = r"[\s._-]*".join(parts)
        if re.search(rf"(?<![a-z0-9]){flexible_phrase}(?![a-z0-9])", normalized_evidence):
            return True
    return False


@dataclass(frozen=True)
class ScoreResult:
    skills: list[ExtractedSkill]
    matched: list[MatchedSkill]
    missing: list[MissingSkill]
    score: int
    breakdown: ScoreBreakdown
    warnings: list[str]


def score_extraction(
    skills: list[ExtractedSkill],
    requirements: list[ExtractedRequirement],
    resume_text: str,
    job_text: str,
) -> ScoreResult:
    warnings: list[str] = []
    grounded_skills: dict[str, ExtractedSkill] = {}
    for skill in skills:
        canonical = canonicalize(skill.name)
        if evidence_in_source(skill.evidence, resume_text) and _skill_named_in_evidence(
            canonical, skill.evidence
        ):
            grounded_skills.setdefault(
                _key(canonical), ExtractedSkill(name=canonical, evidence=skill.evidence)
            )
        else:
            warnings.append(f"已忽略缺少原文技能证据的提取项：{canonical}")

    grounded_requirements: dict[str, ExtractedRequirement] = {}
    for requirement in requirements:
        canonical = canonicalize(requirement.name)
        if not evidence_in_source(requirement.evidence, job_text) or not _skill_named_in_evidence(
            canonical, requirement.evidence
        ):
            warnings.append(f"已忽略缺少岗位原文证据的要求：{canonical}")
            continue
        key = _key(canonical)
        candidate = ExtractedRequirement(
            name=canonical, priority=requirement.priority, evidence=requirement.evidence
        )
        existing = grounded_requirements.get(key)
        if existing is None or (
            existing.priority == "preferred" and candidate.priority == "required"
        ):
            grounded_requirements[key] = candidate

    if not grounded_requirements:
        raise ServiceError(
            422, "UNANALYZABLE_JD", "岗位文本中没有可验证的技能要求，请补充具体技术要求。"
        )

    matched: list[MatchedSkill] = []
    missing: list[MissingSkill] = []
    matched_weight = 0
    total_weight = 0
    for key, requirement in grounded_requirements.items():
        weight = 3 if requirement.priority == "required" else 1
        total_weight += weight
        resume_skill = grounded_skills.get(key)
        if resume_skill is None and _versioned_family(requirement.name) is None:
            resume_skill = next(
                (
                    skill
                    for skill in grounded_skills.values()
                    if (family := _versioned_family(skill.name)) is not None and _key(family) == key
                ),
                None,
            )
        if resume_skill:
            matched_weight += weight
            matched.append(
                MatchedSkill(
                    name=requirement.name,
                    weight=weight,
                    requirementEvidence=requirement.evidence,
                    resumeEvidence=resume_skill.evidence,
                )
            )
        else:
            missing.append(
                MissingSkill(
                    name=requirement.name,
                    weight=weight,
                    requirementEvidence=requirement.evidence,
                    suggestion=(
                        f"简历未体现 {requirement.name} 的证据；如有相关经历，请补充具体实践。"
                    ),
                )
            )
    matched.sort(key=lambda item: (-item.weight, item.name.casefold()))
    missing.sort(key=lambda item: (-item.weight, item.name.casefold()))
    score = round(100 * matched_weight / total_weight)
    return ScoreResult(
        skills=list(grounded_skills.values()),
        matched=matched,
        missing=missing,
        score=score,
        breakdown=ScoreBreakdown(matchedWeight=matched_weight, totalWeight=total_weight),
        warnings=warnings,
    )
