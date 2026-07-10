import logging

from openai import OpenAI

from app.core.config import settings
from app.core.exceptions import BizException

logger = logging.getLogger(__name__)

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
        )
    def chat(self, message: str, system_prompt: str | None = None) -> str:
        messages = []

        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt,
            })

        messages.append({
            "role": "user",
            "content": message,
        })
        print(messages)

        try:
            response = self.client.chat.completions.create(
                model=settings.llm_model,
                messages=messages,
                stream=False,
            )

            content = response.choices[0].message.content

            if not content:
                raise BizException(
                    message="模型返回内容为空",
                    code=502,
                    error_code="LLM_EMPTY_RESPONSE",
                )

            return content

        except BizException:
            raise

        except Exception as exc:
            logger.exception("LLM call failed | error=%s", str(exc))
            raise BizException(
                message="模型服务调用失败，请稍后重试",
                code=502,
                error_code="LLM_CALL_FAILED",
            )


llm_service = LLMService()