import logging
from typing import Optional

from app.core.exceptions import BizException
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

DEFAULT_SYSTEM_PROMPT = "你是一个专业、耐心、表达清晰的 AI 助手。"

def generate_reply(message: str, system_prompt: Optional[str] = None) -> str:
    if "违规" in message:
       raise BizException(
            message="输入内容不符合规范，请修改后重试",
            code=400,
            error_code="INVALID_CHAT_CONTENT"
       )
    
    if message == "系统异常":
        raise RuntimeError("模拟系统异常")

    final_system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT

    logger.info(
        "Chat request received | message_length=%s | has_system_prompt=%s",
        len(message),
        bool(system_prompt),
    )

    return llm_service.chat(
        message=message,
        system_prompt=final_system_prompt,
    )