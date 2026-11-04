import asyncio
import json

import httpx
import pytest

from app.config import Settings
from app.errors import ServiceError
from app.llm import _chat_url, _provider_options, extract_with_llm


def test_chat_url_accepts_base_with_or_without_v1() -> None:
    assert _chat_url("https://api.deepseek.com") == "https://api.deepseek.com/chat/completions"
    assert _chat_url("https://example.test/v1/") == "https://example.test/v1/chat/completions"


def test_thinking_is_disabled_only_for_deepseek_provider() -> None:
    assert _provider_options("https://api.deepseek.com") == {"thinking": {"type": "disabled"}}
    assert _provider_options("https://compatible.example/v1") == {}


@pytest.mark.asyncio
async def test_missing_model_configuration_fails_without_network() -> None:
    with pytest.raises(ServiceError) as captured:
        await extract_with_llm("Java", "Java", Settings(llm_api_key="", llm_model=""), "req")
    assert captured.value.code == "LLM_NOT_CONFIGURED"


@pytest.mark.asyncio
async def test_invalid_provider_json_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": json.dumps({"summary": "missing arrays"})}}]},
        )

    original_init = httpx.AsyncClient.__init__

    def fake_init(self: httpx.AsyncClient, *args: object, **kwargs: object) -> None:
        kwargs["transport"] = httpx.MockTransport(handler)
        original_init(self, *args, **kwargs)

    monkeypatch.setattr(httpx.AsyncClient, "__init__", fake_init)
    with pytest.raises(ServiceError) as captured:
        await extract_with_llm(
            "Java", "Java", Settings(llm_api_key="secret", llm_model="model"), "req"
        )
    assert captured.value.code == "LLM_INVALID_RESPONSE"


@pytest.mark.asyncio
async def test_llm_timeout_is_a_strict_total_budget(monkeypatch: pytest.MonkeyPatch) -> None:
    async def slow_post(*_args: object, **_kwargs: object) -> httpx.Response:
        await asyncio.sleep(0.05)
        return httpx.Response(200, json={})

    monkeypatch.setattr(httpx.AsyncClient, "post", slow_post)
    with pytest.raises(ServiceError) as captured:
        await extract_with_llm(
            "Java",
            "Java",
            Settings(
                llm_api_key="secret",
                llm_model="model",
                llm_timeout_seconds=0.01,
            ),
            "req",
        )
    assert captured.value.status_code == 504
    assert captured.value.code == "UPSTREAM_TIMEOUT"
