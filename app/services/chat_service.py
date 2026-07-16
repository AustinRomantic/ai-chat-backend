import asyncio
import json
import logging
from typing import AsyncGenerator, Generator, Dict, List, Optional

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


def validate_chat_message(message: str) -> None:
    if "违规" in message:
        raise BizException(
            message="输入内容不符合规范，请修改后重试",
            code=400,
            error_code="INVALID_CHAT_CONTENT",
        )

    if message == "系统异常":
        raise RuntimeError("模拟系统异常")


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


async def generate_mock_stream(
    message: str,
    system_prompt: Optional[str] = None,
    history: Optional[List[ChatMessage]] = None,
) -> AsyncGenerator[str, None]:
    if "违规" in message:
        raise BizException(
            message="输入内容不符合规范，请修改后重试",
            code=400,
            error_code="INVALID_CHAT_CONTENT",
        )

    if message == "系统异常":
        raise RuntimeError("模拟系统异常")

    safe_history = history or []

    logger.info(
        "Mock stream request received | message_length=%s | history_count=%s | has_system_prompt=%s",
        len(message),
        len(safe_history),
        bool(system_prompt),
    )

    mock_reply = f"这是一个 Mock 流式回答。你刚才说的是：{message}"

    for char in mock_reply:
        yield f"data: {char}\n\n"
        await asyncio.sleep(0.05)

    yield "event: done\ndata: [DONE]\n\n"


def format_sse_event(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def generate_reply_stream(
    message: str,
    system_prompt: Optional[str] = None,
    history: Optional[List[ChatMessage]] = None,
) -> Generator[str, None, None]:
    """
    真实 LLM 流式输出。

    注意：
    - 开始 yield 之前，可以通过 raise 走全局异常处理。
    - 一旦已经开始 yield，后续错误就应该通过 event: error 返回给前端。
    """
    validate_chat_message(message)

    safe_history = history or []

    messages = build_chat_messages(
        message=message,
        system_prompt=system_prompt,
        history=safe_history,
    )

    logger.info(
        "LLM stream request received | message_length=%s | history_count=%s | final_messages_count=%s",
        len(message),
        len(safe_history),
        len(messages),
    )

    try:
        for content in llm_service.chat_with_messages_stream(messages):
            yield format_sse_event(
                event="message",
                data={
                    "content": content,
                },
            )

        yield format_sse_event(
            event="done",
            data={
                "message": "[DONE]",
            },
        )

    except BizException as exc:
        yield format_sse_event(
            event="error",
            data={
                "error_code": exc.error_code,
                "message": exc.message,
            },
        )

    except Exception as exc:
        logger.exception("Unexpected stream error | error=%s", str(exc))
        yield format_sse_event(
            event="error",
            data={
                "error_code": "INTERNAL_STREAM_ERROR",
                "message": "流式输出异常，请稍后重试",
            },
        )
