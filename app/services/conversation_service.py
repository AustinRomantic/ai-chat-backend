import logging
import uuid

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import BizException
from app.models.conversation import Conversation
from app.repositories import (
    conversation_repository,
    message_repository,
    user_repository,
)
from app.schemas.conversation import (
    ConversationCreate,
    ConversationUpdate,
)


logger = logging.getLogger(__name__)


def _get_development_user(db: Session):
    user = user_repository.get_user_by_email(
        db,
        settings.dev_user_email,
    )

    if user is None:
        raise BizException(
            message="开发用户不存在，请先执行 seed_dev_user 脚本",
            code=500,
            error_code="DEVELOPMENT_USER_NOT_FOUND",
        )

    return user


def _get_owned_conversation_or_raise(
    db: Session,
    user_id: uuid.UUID,
    conversation_id: uuid.UUID,
) -> Conversation:
    conversation = conversation_repository.get_conversation(
        db=db,
        user_id=user_id,
        conversation_id=conversation_id,
    )

    if conversation is None:
        raise BizException(
            message="会话不存在",
            code=404,
            error_code="CONVERSATION_NOT_FOUND",
        )

    return conversation

def create_conversation(
    db: Session,
    payload: ConversationCreate,
) -> Conversation:
    user = _get_development_user(db)

    try:
        conversation = conversation_repository.create_conversation(
            db=db,
            user_id=user.id,
            title=payload.title,
            system_prompt=payload.system_prompt,
        )
        db.commit()
        db.refresh(conversation)
        return conversation

    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Create conversation failed")
        raise BizException(
            message="创建会话失败，请稍后重试",
            code=500,
            error_code="CONVERSATION_CREATE_FAILED",
        ) from exc


def list_conversations(
    db: Session,
    page: int,
    page_size: int,
    status: str | None,
) -> dict:
    user = _get_development_user(db)

    items, total = conversation_repository.list_conversations(
        db=db,
        user_id=user.id,
        page=page,
        page_size=page_size,
        status=status,
    )

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def get_conversation(
    db: Session,
    conversation_id: uuid.UUID,
) -> Conversation:
    user = _get_development_user(db)
    return _get_owned_conversation_or_raise(
        db=db,
        user_id=user.id,
        conversation_id=conversation_id,
    )


def update_conversation(
    db: Session,
    conversation_id: uuid.UUID,
    payload: ConversationUpdate,
) -> Conversation:
    user = _get_development_user(db)
    conversation = _get_owned_conversation_or_raise(
        db=db,
        user_id=user.id,
        conversation_id=conversation_id,
    )

    changes = payload.model_dump(exclude_unset=True)

    try:
        conversation_repository.update_conversation(
            db=db,
            conversation=conversation,
            changes=changes,
        )
        db.commit()
        db.refresh(conversation)
        return conversation

    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Update conversation failed")
        raise BizException(
            message="更新会话失败，请稍后重试",
            code=500,
            error_code="CONVERSATION_UPDATE_FAILED",
        ) from exc


def delete_conversation(
    db: Session,
    conversation_id: uuid.UUID,
) -> None:
    user = _get_development_user(db)
    conversation = _get_owned_conversation_or_raise(
        db=db,
        user_id=user.id,
        conversation_id=conversation_id,
    )

    try:
        conversation_repository.delete_conversation(
            db=db,
            conversation=conversation,
        )
        db.commit()

    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Delete conversation failed")
        raise BizException(
            message="删除会话失败，请稍后重试",
            code=500,
            error_code="CONVERSATION_DELETE_FAILED",
        ) from exc


def list_conversation_messages(
    db: Session,
    conversation_id: uuid.UUID,
    page: int,
    page_size: int,
) -> dict:
    user = _get_development_user(db)
    conversation = _get_owned_conversation_or_raise(
        db=db,
        user_id=user.id,
        conversation_id=conversation_id,
    )

    items, total = message_repository.list_messages(
        db=db,
        conversation_id=conversation.id,
        page=page,
        page_size=page_size,
    )

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
