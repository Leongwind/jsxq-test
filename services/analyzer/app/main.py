import logging
import re
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .config import get_settings
from .errors import ServiceError
from .models import AnalyzeInput
from .service import analyze

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("careerlens.analyzer")
app = FastAPI(title="CareerLens Analyzer", version="1.0.0", docs_url=None, redoc_url=None)


def _request_id(request: Request) -> str:
    incoming = request.headers.get("x-request-id", "").strip()
    return incoming if re.fullmatch(r"[A-Za-z0-9._-]{1,128}", incoming) else str(uuid.uuid4())


def _error(status: int, code: str, message: str, request_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"code": code, "message": message, "requestId": request_id},
        headers={"X-Request-Id": request_id},
    )


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, _exc: RequestValidationError) -> JSONResponse:
    return _error(
        400, "INVALID_INPUT", "请求内容不完整或超出长度限制，请检查后重试。", _request_id(request)
    )


@app.exception_handler(ServiceError)
async def service_error(request: Request, exc: ServiceError) -> JSONResponse:
    return _error(exc.status_code, exc.code, exc.message, _request_id(request))


@app.exception_handler(Exception)
async def unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    request_id = _request_id(request)
    logger.error("requestId=%s analyzer failed type=%s", request_id, type(exc).__name__)
    return _error(503, "SERVICE_UNAVAILABLE", "分析服务暂时不可用，请稍后重试。", request_id)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/internal/analyze")
async def analyze_endpoint(payload: AnalyzeInput, request: Request) -> JSONResponse:
    request_id = _request_id(request)
    started = time.monotonic()
    try:
        result = await analyze(payload, request_id, get_settings())
    except TimeoutError as exc:
        raise ServiceError(504, "UPSTREAM_TIMEOUT", "分析请求超时，请稍后重试。") from exc
    logger.info(
        "requestId=%s analysis completed durationMs=%d",
        request_id,
        round((time.monotonic() - started) * 1000),
    )
    return JSONResponse(
        content=result.model_dump(by_alias=True), headers={"X-Request-Id": request_id}
    )
