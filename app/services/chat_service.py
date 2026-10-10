import json
import logging
import uuid
from dataclasses import dataclass
from typing import Generator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import BizException
from app.models.conversation import Conversation
from app.models.message import Message
from app.repositories import (
    conversation_repository,
    message_repository,
)
from app.schemas.chat import ChatResponse
from app.services import conversation_service
from app.services.llm_service import llm_service


logger = logging.getLogger(__name__)

DEFAULT_SYSTEM_PROMPT = (
    "你是一个专业、耐心、表达清晰的 AI 助手。"
)

MAX_HISTORY_MESSAGES = 10


@dataclass
class PreparedChat:
    conversation: Conversation
    user_message_id: uuid.UUID
    llm_messages: list[dict[str, str]]


def validate_chat_message(message: str) -> None:
    if "违规" in message:
        raise BizException(
            message="输入内容不符合规范，请修改后重试",
            code=400,
            error_code="INVALID_CHAT_CONTENT",
        )

    if message == "系统异常":
        raise RuntimeError("模拟系统异常")


def build_chat_messages(
    system_prompt: str | None,
    history: list[Message],
    current_message: str,
) -> list[dict[str, str]]:
    final_system_prompt = (
        system_prompt or DEFAULT_SYSTEM_PROMPT
    )

    messages: list[dict[str, str]] = [
        {
            "role": "system",
            "content": final_system_prompt,
        }
    ]

    for history_message in history:
        messages.append(
            {
                "role": history_message.role,
                "content": history_message.content,
            }
        )

    messages.append(
        {
            "role": "user",
            "content": current_message,
        }
    )

    return messages


def prepare_chat(
    db: Session,
    conversation_id: uuid.UUID,
    message: str,
) -> PreparedChat:
    validate_chat_message(message)

    conversation = conversation_service.get_conversation(
        db=db,
        conversation_id=conversation_id,
    )

    if conversation.status != "active":
        raise BizException(
            message="已归档的会话不能继续聊天",
            code=409,
            error_code="CONVERSATION_ARCHIVED",
        )

    try:
        history = message_repository.list_recent_messages(
            db=db,
            conversation_id=conversation.id,
            limit=MAX_HISTORY_MESSAGES,
        )

        llm_messages = build_chat_messages(
            system_prompt=conversation.system_prompt,
            history=history,
            current_message=message,
        )

        user_message = message_repository.create_message(
            db=db,
            conversation_id=conversation.id,
            role="user",
            content=message,
        )

        conversation_repository.touch_conversation(
            db=db,
            conversation=conversation,
        )

        db.commit()

        logger.info(
            "User message persisted | "
            "conversation_id=%s | "
            "message_id=%s | "
            "history_count=%s",
            conversation.id,
            user_message.id,
            len(history),
        )

        return PreparedChat(
            conversation=conversation,
            user_message_id=user_message.id,
            llm_messages=llm_messages,
        )

    except SQLAlchemyError as exc:
        db.rollback()

        logger.exception(
            "Persist user message failed | "
            "conversation_id=%s | "
            "error_type=%s",
            conversation_id,
            exc.__class__.__name__,
        )

        raise BizException(
            message="保存用户消息失败，请稍后重试",
            code=500,
            error_code="USER_MESSAGE_SAVE_FAILED",
        ) from exc


def save_assistant_message(
    db: Session,
    prepared_chat: PreparedChat,
    content: str,
) -> Message:
    try:
        assistant_message = (
            message_repository.create_message(
                db=db,
                conversation_id=prepared_chat.conversation.id,
                role="assistant",
                content=content,
            )
        )

        conversation_repository.touch_conversation(
            db=db,
            conversation=prepared_chat.conversation,
        )

        db.commit()

        logger.info(
            "Assistant message persisted | "
            "conversation_id=%s | "
            "message_id=%s | "
            "content_length=%s",
            prepared_chat.conversation.id,
            assistant_message.id,
            len(content),
        )

        return assistant_message

    except SQLAlchemyError as exc:
        db.rollback()

        logger.exception(
            "Persist assistant message failed | "
            "conversation_id=%s | "
            "error_type=%s",
            prepared_chat.conversation.id,
            exc.__class__.__name__,
        )

        raise BizException(
            message="保存模型回答失败，请稍后重试",
            code=500,
            error_code="ASSISTANT_MESSAGE_SAVE_FAILED",
        ) from exc


def generate_reply(
    db: Session,
    conversation_id: uuid.UUID,
    message: str,
) -> ChatResponse:
    prepared_chat = prepare_chat(
        db=db,
        conversation_id=conversation_id,
        message=message,
    )

    reply = llm_service.chat_with_messages(
        prepared_chat.llm_messages
    )

    assistant_message = save_assistant_message(
        db=db,
        prepared_chat=prepared_chat,
        content=reply,
    )

    return ChatResponse(
        conversation_id=prepared_chat.conversation.id,
        user_message_id=prepared_chat.user_message_id,
        assistant_message_id=assistant_message.id,
        reply=reply,
    )


def format_sse_event(
    event: str,
    data: dict,
) -> str:
    return (
        f"event: {event}\n"
        f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
    )


def generate_reply_stream(
    db: Session,
    prepared_chat: PreparedChat,
) -> Generator[str, None, None]:
    content_parts: list[str] = []

    try:
        for content in (
            llm_service.chat_with_messages_stream(
                prepared_chat.llm_messages
            )
        ):
            content_parts.append(content)

            yield format_sse_event(
                event="message",
                data={
                    "content": content,
                },
            )

        complete_content = "".join(content_parts)

        if not complete_content.strip():
            raise BizException(
                message="模型返回内容为空",
                code=502,
                error_code="LLM_EMPTY_RESPONSE",
            )

        assistant_message = save_assistant_message(
            db=db,
            prepared_chat=prepared_chat,
            content=complete_content,
        )

        yield format_sse_event(
            event="done",
            data={
                "message": "[DONE]",
                "conversation_id": str(
                    prepared_chat.conversation.id
                ),
                "user_message_id": str(
                    prepared_chat.user_message_id
                ),
                "assistant_message_id": str(
                    assistant_message.id
                ),
            },
        )

    except BizException as exc:
        db.rollback()

        yield format_sse_event(
            event="error",
            data={
                "error_code": exc.error_code,
                "message": exc.message,
            },
        )

    except Exception as exc:
        db.rollback()

        logger.exception(
            "Unexpected stream error | "
            "conversation_id=%s | "
            "error_type=%s",
            prepared_chat.conversation.id,
            exc.__class__.__name__,
        )

        yield format_sse_event(
            event="error",
            data={
                "error_code": "INTERNAL_STREAM_ERROR",
                "message": "流式输出异常，请稍后重试",
            },
        )