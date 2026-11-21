"""Adapter for an OpenAI-compatible chat-completions endpoint."""

import json
import logging
import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlsplit

import httpx

from app.core.config import settings
from app.core.errors import AppError

logger = logging.getLogger(__name__)


@dataclass
class AICompletionResult:
    """Parsed AI output without exposing the source prompt to the caller."""

    data: dict[str, Any]


def _safe_endpoint_label(url: str) -> str:
    """Return endpoint context without credentials, query, fragment, or secret path segments."""
    try:
        parsed = urlsplit(url)
        host = parsed.hostname
        port = parsed.port
    except ValueError:
        return "<invalid-endpoint>"

    if not host:
        return "<invalid-endpoint>"

    port_label = f":{port}" if port else ""
    segments = [part for part in parsed.path.split("/") if part]
    versions = [part for part in segments[:-2] if re.fullmatch(r"v\d+", part)]
    path_label = f"/{versions[-1]}/chat/completions" if versions else "/<base-path>/chat/completions"
    return f"{parsed.scheme}://{host}{port_label}{path_label}"


class AIService:
    async def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: dict[str, Any] | None = None,
    ) -> AICompletionResult:
        missing_settings = [
            name
            for name, value in (
                ("AI_BASE_URL", settings.ai_base_url),
                ("AI_MODEL", settings.ai_model),
                ("AI_API_KEY", settings.ai_api_key),
            )
            if not value
        ]
        if missing_settings:
            logger.error(
                "AI configuration missing fields=%s", ",".join(missing_settings)
            )
            raise AppError(
                "AI_CONFIGURATION_MISSING",
                "AI 분석 서비스가 설정되지 않았습니다.",
                "AI_BASE_URL, AI_MODEL, AI_API_KEY를 서버 환경 변수에 설정해 주세요.",
                status_code=503,
            )

        base_url = settings.ai_base_url.rstrip("/")
        scheme = ""
        try:
            parsed_base_url = urlsplit(base_url)
            scheme = parsed_base_url.scheme
            host = parsed_base_url.hostname
            parsed_base_url.port  # Validate a malformed port before making a request.
        except ValueError:
            host = None

        if scheme not in {"https", "http"} or not host:
            logger.error(
                "AI endpoint configuration invalid scheme=%s host_present=%s",
                scheme or "<missing>",
                bool(host),
            )
            raise AppError(
                "AI_CONFIGURATION_INVALID",
                "AI_BASE_URL 설정이 올바르지 않습니다.",
                "http:// 또는 https://로 시작하는 호환 API 주소를 설정해 주세요.",
                status_code=503,
            )

        url = f"{base_url}/chat/completions"
        safe_endpoint = _safe_endpoint_label(url)
        headers = {
            "Authorization": f"Bearer {settings.ai_api_key}",
            "Content-Type": "application/json",
        }
        response_format: dict[str, Any] = {"type": "json_object"}
        if response_schema:
            response_format = {
                "type": "json_schema",
                "json_schema": response_schema,
            }

        body = {
            "model": settings.ai_model,
            "reasoning_effort": settings.ai_reasoning_effort,
            "response_format": response_format,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        try:
            async with httpx.AsyncClient(timeout=settings.ai_timeout_seconds) as client:
                response = await client.post(url, headers=headers, json=body)
        except httpx.InvalidURL as exc:
            logger.error(
                "AI endpoint invalid after URL construction endpoint=%s",
                safe_endpoint,
            )
            raise AppError(
                "AI_ENDPOINT_INVALID",
                "AI endpoint 주소 형식이 올바르지 않습니다.",
                "AI_BASE_URL의 scheme, host, port, 경로를 확인해 주세요.",
                status_code=503,
            ) from exc
        except httpx.TimeoutException as exc:
            logger.warning("AI transport category=timeout endpoint=%s", safe_endpoint)
            raise AppError(
                "AI_TIMEOUT",
                "AI 분석 요청 시간이 초과되었습니다.",
                "잠시 후 다시 시도해 주세요.",
                status_code=502,
                retryable=True,
            ) from exc
        except httpx.RequestError as exc:
            logger.warning(
                "AI transport category=network_error exception=%s endpoint=%s",
                type(exc).__name__,
                safe_endpoint,
            )
            raise AppError(
                "AI_CONNECTION_FAILED",
                "AI 분석 서비스에 연결할 수 없습니다.",
                "AI 주소와 네트워크 상태를 확인한 뒤 다시 시도해 주세요.",
                status_code=502,
                retryable=True,
            ) from exc

        if response.status_code == 429 or response.status_code >= 500:
            logger.warning(
                "AI provider category=%s status=%s endpoint=%s",
                "rate_limited_or_quota" if response.status_code == 429 else "server_error",
                response.status_code,
                safe_endpoint,
            )
            raise AppError(
                "AI_PROVIDER_TEMPORARY_ERROR",
                "AI 분석 서비스가 일시적으로 응답하지 않습니다.",
                "잠시 후 다시 시도해 주세요.",
                status_code=502,
                retryable=True,
            )
        if response.is_error:
            if response.status_code in {401, 403}:
                error_code = "AI_AUTH_OR_PERMISSION_REJECTED"
                category = "authentication_or_permission"
                message = "AI 서비스가 인증 또는 모델 권한을 거부했습니다."
                action = "인증 설정과 선택한 모델의 사용 권한을 확인해 주세요. 키 값은 로그에 기록되지 않습니다."
            elif response.status_code in {404, 405}:
                error_code = "AI_ENDPOINT_OR_MODEL_NOT_FOUND"
                category = "endpoint_or_model_not_found"
                message = "AI endpoint 또는 모델을 찾을 수 없습니다."
                action = "AI_BASE_URL 경로와 모델 식별자가 해당 서비스 사양과 일치하는지 확인해 주세요."
            elif response.status_code in {400, 422}:
                error_code = "AI_REQUEST_FORMAT_REJECTED"
                category = "request_or_model_parameters_rejected"
                message = "AI 서비스가 요청 형식 또는 모델 설정을 거부했습니다."
                action = "선택한 모델의 Chat Completions 지원 여부와 요청 설정 호환성을 확인해 주세요."
            else:
                error_code = "AI_PROVIDER_REJECTED_REQUEST"
                category = "provider_rejected_request"
                message = "AI 분석 서비스가 요청을 처리하지 못했습니다."
                action = "AI endpoint 주소와 모델 설정이 선택한 서비스 사양과 일치하는지 확인해 주세요."

            logger.warning(
                "AI provider category=%s status=%s endpoint=%s",
                category,
                response.status_code,
                safe_endpoint,
            )
            raise AppError(
                error_code,
                message,
                action,
                status_code=502,
            )

        try:
            response_body = response.json()
            content = response_body["choices"][0]["message"]["content"]
            if isinstance(content, list):
                content = "".join(
                    part.get("text", "") for part in content if isinstance(part, dict)
                )
            if not isinstance(content, str):
                raise ValueError("Expected text content")
            return AICompletionResult(
                data=self._parse_json(content),
            )
        except (ValueError, KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            logger.warning(
                "AI response category=parse_error exception=%s endpoint=%s",
                type(exc).__name__,
                safe_endpoint,
            )
            raise AppError(
                "AI_INVALID_RESPONSE",
                "AI가 결과를 읽을 수 있는 형식으로 반환하지 않았습니다.",
                "다시 분석해 주세요. 문제가 반복되면 AI 모델의 JSON 출력 지원 여부를 확인해 주세요.",
                status_code=502,
                retryable=True,
            ) from exc

    @staticmethod
    def _parse_json(content: str) -> dict[str, Any]:
        cleaned = content.strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            start, end = cleaned.find("{"), cleaned.rfind("}")
            if start < 0 or end <= start:
                raise
            parsed = json.loads(cleaned[start : end + 1])
        if not isinstance(parsed, dict):
            raise ValueError("AI output must be a JSON object")
        return parsed
