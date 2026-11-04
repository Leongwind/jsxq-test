import logging
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.main import app
from app.models import LlmExtraction


def test_health_does_not_require_llm() -> None:
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_validation_is_mapped_to_contract_error() -> None:
    response = TestClient(app).post(
        "/internal/analyze",
        json={"resumeText": "   ", "job": {"id": "j", "title": "t", "description": "Java"}},
        headers={"X-Request-Id": "known-id"},
    )
    assert response.status_code == 400
    assert response.json() == {
        "code": "INVALID_INPUT",
        "message": "请求内容不完整或超出长度限制，请检查后重试。",
        "requestId": "known-id",
    }


def test_success_preserves_request_id_and_computes_score(monkeypatch) -> None:
    extraction = LlmExtraction.model_validate(
        {
            "summary": "后端开发候选人",
            "education": [],
            "experience": ["使用 Java 开发接口"],
            "projects": [],
            "skills": [{"name": "Java", "evidence": "使用 Java 开发接口"}],
            "requirements": [
                {"name": "Java", "priority": "required", "evidence": "要求熟悉 Java"},
                {"name": "Redis", "priority": "preferred", "evidence": "了解 Redis 优先"},
            ],
            "issues": [],
        }
    )
    monkeypatch.setattr("app.service.extract_with_llm", AsyncMock(return_value=extraction))
    response = TestClient(app).post(
        "/internal/analyze",
        json={
            "resumeText": "使用 Java 开发接口",
            "job": {
                "id": "java",
                "title": "Java 开发",
                "description": "要求熟悉 Java\n了解 Redis 优先",
            },
        },
        headers={"X-Request-Id": "known-id"},
    )
    assert response.status_code == 200
    body = response.json()
    assert response.headers["x-request-id"] == "known-id"
    assert body["requestId"] == "known-id"
    assert body["score"] == 75
    assert body["scoreBreakdown"] == {
        "matchedWeight": 3,
        "totalWeight": 4,
        "formula": "round(100 × matchedWeight / totalWeight)",
    }
    assert body["missingSkills"][0]["name"] == "Redis"


def test_invalid_request_id_is_replaced() -> None:
    response = TestClient(app).post(
        "/internal/analyze",
        json={"resumeText": ""},
        headers={"X-Request-Id": "not safe!"},
    )
    assert response.status_code == 400
    assert response.json()["requestId"] != "not safe!"


def test_unexpected_error_does_not_log_or_return_sensitive_content(monkeypatch, caplog) -> None:
    sensitive = "secret resume and provider credential"
    monkeypatch.setattr("app.main.analyze", AsyncMock(side_effect=RuntimeError(sensitive)))
    with caplog.at_level(logging.ERROR, logger="careerlens.analyzer"):
        response = TestClient(app, raise_server_exceptions=False).post(
            "/internal/analyze",
            json={
                "resumeText": "Java project",
                "job": {"id": "java", "title": "Java", "description": "Java required"},
            },
            headers={"X-Request-Id": "safe-id"},
        )
    assert response.status_code == 503
    assert response.json()["code"] == "SERVICE_UNAVAILABLE"
    assert sensitive not in response.text
    assert sensitive not in caplog.text
    assert "RuntimeError" in caplog.text
