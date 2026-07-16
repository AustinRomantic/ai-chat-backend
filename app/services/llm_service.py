import logging
import time
from typing import Callable, Dict, Generator, List, Optional, TypeVar

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    OpenAI,
    OpenAIError,
    RateLimitError,
)

from app.core.config import settings
from app.core.exceptions import BizException

logger = logging.getLogger(__name__)

T = TypeVar("T")


class LLMService:
    def __init__(self):
        if not settings.llm_api_key:
            raise BizException(
                message="LLM_API_KEY 未配置，请检查 .env 文件",
                code=500,
                error_code="LLM_API_KEY_NOT_CONFIGURED",
            )

        self.client = OpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
            timeout=settings.llm_timeout,
            # 关闭 SDK 默认重试，避免和我们自己的重试叠加。
            max_retries=0,
        )

    def chat(self, message: str, system_prompt: Optional[str] = None) -> str:
        messages: List[Dict[str, str]] = []

        if system_prompt:
            messages.append(
                {
                    "role": "system",
                    "content": system_prompt,
                }
            )

        messages.append(
            {
                "role": "user",
                "content": message,
            }
        )

        return self.chat_with_messages(messages)

    def chat_with_messages(self, messages: List[Dict[str, str]]) -> str:
        def call():
            return self.client.chat.completions.create(
                model=settings.llm_model,
                messages=messages,
                stream=False,
            )

        response = self._call_with_retry(
            call=call,
            operation="chat",
            messages_count=len(messages),
        )

        content = response.choices[0].message.content

        if not content:
            raise BizException(
                message="模型返回内容为空",
                code=502,
                error_code="LLM_EMPTY_RESPONSE",
            )

        return content

    def chat_with_messages_stream(
        self,
        messages: List[Dict[str, str]],
    ) -> Generator[str, None, None]:
        def call():
            return self.client.chat.completions.create(
                model=settings.llm_model,
                messages=messages,
                stream=True,
            )

        stream = self._call_with_retry(
            call=call,
            operation="chat_stream",
            messages_count=len(messages),
        )

        try:
            for chunk in stream:
                if not chunk.choices:
                    continue

                delta = chunk.choices[0].delta
                content = getattr(delta, "content", None)

                if content:
                    yield content

        except Exception as exc:
            logger.exception(
                "LLM stream iteration failed | provider=%s | model=%s | error_type=%s | error=%s",
                settings.llm_provider,
                settings.llm_model,
                exc.__class__.__name__,
                str(exc),
            )

            raise BizException(
                message="模型流式输出中断，请稍后重试",
                code=502,
                error_code="LLM_STREAM_INTERRUPTED",
            )

    def _call_with_retry(
        self,
        call: Callable[[], T],
        operation: str,
        messages_count: int,
    ) -> T:
        max_retries = max(settings.llm_max_retries, 0)
        total_attempts = max_retries + 1

        for attempt in range(1, total_attempts + 1):
            try:
                logger.info(
                    "LLM call start | provider=%s | model=%s | operation=%s | attempt=%s/%s | messages_count=%s",
                    settings.llm_provider,
                    settings.llm_model,
                    operation,
                    attempt,
                    total_attempts,
                    messages_count,
                )

                result = call()

                logger.info(
                    "LLM call success | provider=%s | model=%s | operation=%s | attempt=%s/%s",
                    settings.llm_provider,
                    settings.llm_model,
                    operation,
                    attempt,
                    total_attempts,
                )

                return result

            except Exception as exc:
                should_retry = self._should_retry(exc)

                logger.warning(
                    "LLM call failed | provider=%s | model=%s | operation=%s | attempt=%s/%s | retry=%s | error_type=%s | error=%s",
                    settings.llm_provider,
                    settings.llm_model,
                    operation,
                    attempt,
                    total_attempts,
                    should_retry,
                    exc.__class__.__name__,
                    str(exc),
                )

                if not should_retry or attempt >= total_attempts:
                    raise self._to_biz_exception(exc)

                time.sleep(settings.llm_retry_interval)

        raise BizException(
            message="模型服务调用失败，请稍后重试",
            code=502,
            error_code="LLM_CALL_FAILED",
        )

    def _should_retry(self, exc: Exception) -> bool:
        if isinstance(exc, (APITimeoutError, APIConnectionError, RateLimitError)):
            return True

        if isinstance(exc, APIStatusError):
            return exc.status_code in {408, 409, 429, 500, 502, 503, 504}

        return False

    def _to_biz_exception(self, exc: Exception) -> BizException:
        if isinstance(exc, AuthenticationError):
            return BizException(
                message="模型服务认证失败，请检查 API Key",
                code=502,
                error_code="LLM_AUTH_FAILED",
            )

        if isinstance(exc, BadRequestError):
            return BizException(
                message="模型请求参数错误，请检查模型名称或消息格式",
                code=400,
                error_code="LLM_BAD_REQUEST",
            )

        if isinstance(exc, RateLimitError):
            return BizException(
                message="模型服务请求过快，请稍后重试",
                code=429,
                error_code="LLM_RATE_LIMITED",
            )

        if isinstance(exc, APITimeoutError):
            return BizException(
                message="模型服务响应超时，请稍后重试",
                code=504,
                error_code="LLM_TIMEOUT",
            )

        if isinstance(exc, APIConnectionError):
            return BizException(
                message="模型服务网络连接失败，请检查网络或稍后重试",
                code=502,
                error_code="LLM_CONNECTION_FAILED",
            )

        if isinstance(exc, APIStatusError):
            status_code = exc.status_code

            if status_code >= 500:
                return BizException(
                    message="模型服务暂时不可用，请稍后重试",
                    code=502,
                    error_code="LLM_PROVIDER_SERVER_ERROR",
                )

            return BizException(
                message="模型服务返回异常，请检查请求配置",
                code=502,
                error_code=f"LLM_PROVIDER_STATUS_{status_code}",
            )

        if isinstance(exc, OpenAIError):
            return BizException(
                message="模型服务调用异常，请稍后重试",
                code=502,
                error_code="LLM_OPENAI_SDK_ERROR",
            )

        return BizException(
            message="模型服务调用失败，请稍后重试",
            code=502,
            error_code="LLM_CALL_FAILED",
        )


llm_service = LLMService()