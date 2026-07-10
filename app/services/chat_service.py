import logging
from typing import Dict, List, Optional

from app.core.exceptions import BizException
from app.schemas.chat import ChatMessage
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

DEFAULT_SYSTEM_PROMPT = "你是一个专业、耐心、表达清晰的 AI 助手。"


def build_chat_messages(
    message: str,
    system_prompt: Optional[str],
    history: List[ChatMessage],
) -> List[Dict[str, str]]:
    final_system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT

    messages: List[Dict[str, str]] = [
        {
            "role": "system",
            "content": final_system_prompt,
        }
    ]

    # 只取最后 10 条历史，防止上下文过长
    recent_history = history[-10:]

    for item in recent_history:
        messages.append(
            {
                "role": item.role,
                "content": item.content,
            }
        )

    messages.append(
        {
            "role": "user",
            "content": message,
        }
    )

    return messages


def generate_reply(
    message: str,
    system_prompt: Optional[str] = None,
    history: Optional[List[ChatMessage]] = None,
) -> str:
    if "违规" in message:
        raise BizException(
            message="输入内容不符合规范，请修改后重试",
            code=400,
            error_code="INVALID_CHAT_CONTENT",
        )

    if message == "系统异常":
        raise RuntimeError("模拟系统异常")
    
    safe_history = history or []

    messages = build_chat_messages(
        message=message,
        system_prompt=system_prompt,
        history=safe_history,
    )

    logger.info(
        "Chat request received | message_length=%s | history_count=%s | final_messages_count=%s",
        len(message),
        len(safe_history),
        len(messages),
    )

    return llm_service.chat_with_messages(messages)
