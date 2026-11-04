from app.text import clean_text, evidence_in_source


def test_clean_text_removes_controls_and_collapses_layout() -> None:
    assert clean_text("  Java\x00  开发\r\n\r\n\r\n 项目  ") == "Java 开发\n\n项目"


def test_evidence_match_normalizes_spacing_and_case() -> None:
    assert evidence_in_source("SPRING   BOOT", "使用 Spring Boot 开发接口")
    assert not evidence_in_source("Redis", "只使用了 MySQL")
