import asyncio
import json
from urllib.parse import urlparse

import httpx
from pydantic import ValidationError

from .config import Settings
from .errors import ServiceError
from .models import LlmExtraction

ASYNCIO_TIMEOUT = getattr(asyncio, "TimeoutError", TimeoutError)

SYSTEM_PROMPT = """你是简历事实提取器。只根据提供的简历与岗位原文输出 JSON，不评分，不猜测。
必须输出且仅输出这个 JSON 对象：
{"summary":"", "education":["教育经历文本"], "experience":["工作经历文本"],
 "projects":["项目经历文本"],
 "skills":[{"name":"技能名","evidence":"含该技能名的简历原文连续片段"}],
 "requirements":[{"name":"技能名","priority":"required或preferred","evidence":"含该技能名的岗位原文连续片段"}],
 "issues":[{"type":"structure或impact或clarity","severity":"info或warning","evidence":"简历原文连续片段；缺失类问题可为空","suggestion":"具体建议"}]}
规则：数组不可省略。education、experience、projects 的每个元素必须是字符串，禁止输出对象或嵌套数组。
技能证据和岗位证据必须是对应原文的连续片段，并明确包含技能名称或常用别名。
必备要求标为 required，明确写明优先/加分的要求标为 preferred。不得把职责、软技能或学历当作技术技能。
不得输出简历或岗位中没有的事实，不得输出 Markdown。"""


def _chat_url(base_url: str) -> str:
    return f"{base_url.rstrip('/')}/chat/completions"


def _provider_options(base_url: str) -> dict[str, object]:
    host = (urlparse(base_url).hostname or "").casefold()
    if host == "api.deepseek.com" or host.endswith(".api.deepseek.com"):
        return {"thinking": {"type": "disabled"}}
    return {}


async def extract_with_llm(
    resume_text: str, job_text: str, settings: Settings, request_id: str
) -> LlmExtraction:
    if not settings.llm_api_key.strip() or not settings.llm_model.strip():
        raise ServiceError(503, "LLM_NOT_CONFIGURED", "分析模型尚未配置，请联系服务管理员。")

    payload: dict[str, object] = {
        "model": settings.llm_model,
        "temperature": 0,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"<resume>\n{resume_text}\n</resume>\n<job>\n{job_text}\n</job>",
            },
        ],
        **_provider_options(settings.llm_base_url),
    }
    headers = {
        "Authorization": f"Bearer {settings.llm_api_key}",
        "Content-Type": "application/json",
        "X-Request-Id": request_id,
    }
    try:
        async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
            response = await asyncio.wait_for(
                client.post(_chat_url(settings.llm_base_url), json=payload, headers=headers),
                timeout=settings.llm_timeout_seconds,
            )
    except (TimeoutError, ASYNCIO_TIMEOUT, httpx.TimeoutException) as exc:
        raise ServiceError(504, "UPSTREAM_TIMEOUT", "模型分析超时，请稍后重试。") from exc
    except httpx.HTTPError as exc:
        raise ServiceError(502, "LLM_UPSTREAM_ERROR", "模型服务暂时不可用，请稍后重试。") from exc

    if response.status_code == 429:
        raise ServiceError(429, "RATE_LIMITED", "模型请求过于频繁，请稍后重试。")
    if response.status_code in {401, 403}:
        raise ServiceError(503, "LLM_NOT_CONFIGURED", "模型鉴权失败，请联系服务管理员。")
    if response.status_code >= 400:
        raise ServiceError(502, "LLM_UPSTREAM_ERROR", "模型服务返回异常，请稍后重试。")

    try:
        envelope = response.json()
        content = envelope["choices"][0]["message"]["content"]
        if not isinstance(content, str):
            raise TypeError("message content is not a string")
        return LlmExtraction.model_validate(json.loads(content))
    except (KeyError, IndexError, TypeError, ValueError, ValidationError) as exc:
        raise ServiceError(
            502, "LLM_INVALID_RESPONSE", "模型返回内容无法验证，请重新分析。"
        ) from exc
