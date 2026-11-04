import pytest

from app.errors import ServiceError
from app.models import ExtractedRequirement, ExtractedSkill
from app.scoring import canonicalize, score_extraction


def test_aliases_and_versions_are_canonicalized() -> None:
    assert canonicalize("SpringBoot") == "Spring Boot"
    assert canonicalize("JS") == "JavaScript"
    assert canonicalize("Vue 3") == "Vue 3"
    assert canonicalize("Vue 2") != canonicalize("Vue 3")


def test_required_overrides_duplicate_preferred_and_score_is_deterministic() -> None:
    result = score_extraction(
        [
            ExtractedSkill(name="SpringBoot", evidence="使用 SpringBoot 开发接口"),
            ExtractedSkill(name="JS", evidence="掌握 JS 与浏览器开发"),
        ],
        [
            ExtractedRequirement(
                name="Spring Boot", priority="preferred", evidence="Spring Boot 经验优先"
            ),
            ExtractedRequirement(
                name="springboot", priority="required", evidence="必须熟悉 SpringBoot"
            ),
            ExtractedRequirement(
                name="JavaScript", priority="preferred", evidence="了解 JavaScript 加分"
            ),
            ExtractedRequirement(name="Redis", priority="preferred", evidence="了解 Redis 加分"),
        ],
        "使用 SpringBoot 开发接口\n掌握 JS 与浏览器开发",
        "Spring Boot 经验优先\n必须熟悉 SpringBoot\n了解 JavaScript 加分\n了解 Redis 加分",
    )
    assert result.breakdown.matched_weight == 4
    assert result.breakdown.total_weight == 5
    assert result.score == 80
    assert [item.name for item in result.missing] == ["Redis"]


def test_unrelated_evidence_cannot_support_a_skill() -> None:
    result = score_extraction(
        [ExtractedSkill(name="Redis", evidence="负责缓存模块开发")],
        [ExtractedRequirement(name="Redis", priority="required", evidence="要求熟悉 Redis")],
        "负责缓存模块开发",
        "要求熟悉 Redis",
    )
    assert result.score == 0
    assert result.matched == []
    assert result.missing[0].name == "Redis"
    assert result.warnings == ["已忽略缺少原文技能证据的提取项：Redis"]


def test_java_is_not_inferred_from_javascript_token() -> None:
    result = score_extraction(
        [ExtractedSkill(name="Java", evidence="使用 JavaScript 开发页面")],
        [ExtractedRequirement(name="Java", priority="required", evidence="要求熟悉 Java")],
        "使用 JavaScript 开发页面",
        "要求熟悉 Java",
    )
    assert result.score == 0
    assert result.matched == []


def test_distinct_chinese_skills_do_not_share_an_empty_key() -> None:
    result = score_extraction(
        [
            ExtractedSkill(name="微服务", evidence="具备微服务开发经验"),
            ExtractedSkill(name="消息队列", evidence="使用消息队列处理异步任务"),
        ],
        [
            ExtractedRequirement(name="微服务", priority="required", evidence="要求微服务经验"),
            ExtractedRequirement(name="消息队列", priority="required", evidence="要求消息队列经验"),
        ],
        "具备微服务开发经验\n使用消息队列处理异步任务",
        "要求微服务经验\n要求消息队列经验",
    )
    assert result.score == 100
    assert {item.name for item in result.matched} == {"微服务", "消息队列"}
    assert result.breakdown.total_weight == 6


@pytest.mark.parametrize("family,version", [("Vue", "Vue 3"), ("Java", "Java 17")])
def test_versioned_resume_skill_satisfies_generic_requirement(family: str, version: str) -> None:
    result = score_extraction(
        [ExtractedSkill(name=version, evidence=f"使用 {version} 开发")],
        [ExtractedRequirement(name=family, priority="required", evidence=f"要求熟悉 {family}")],
        f"使用 {version} 开发",
        f"要求熟悉 {family}",
    )
    assert result.score == 100
    assert result.matched[0].resume_evidence == f"使用 {version} 开发"


def test_different_explicit_versions_do_not_match() -> None:
    result = score_extraction(
        [ExtractedSkill(name="Vue 2", evidence="使用 Vue 2 开发")],
        [ExtractedRequirement(name="Vue 3", priority="required", evidence="要求熟悉 Vue 3")],
        "使用 Vue 2 开发",
        "要求熟悉 Vue 3",
    )
    assert result.score == 0
    assert result.matched == []


def test_generic_resume_skill_does_not_claim_a_version() -> None:
    result = score_extraction(
        [ExtractedSkill(name="Vue", evidence="使用 Vue 开发")],
        [ExtractedRequirement(name="Vue 3", priority="required", evidence="要求熟悉 Vue 3")],
        "使用 Vue 开发",
        "要求熟悉 Vue 3",
    )
    assert result.score == 0
    assert result.matched == []


def test_unverifiable_requirements_never_produce_a_score() -> None:
    with pytest.raises(ServiceError) as captured:
        score_extraction(
            [],
            [ExtractedRequirement(name="Java", priority="required", evidence="后端经验")],
            "无技能",
            "需要后端经验",
        )
    assert captured.value.status_code == 422
    assert captured.value.code == "UNANALYZABLE_JD"
