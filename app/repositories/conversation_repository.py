import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.conversation import Conversation


def create_conversation(
    db: Session,
    user_id: uuid.UUID,
    title: str,
    system_prompt: str | None,
) -> Conversation:
    conversation = Conversation(
        user_id=user_id,
        title=title,
        system_prompt=system_prompt,
    )
    db.add(conversation)
    db.flush()
    return conversation


def list_conversations(
    db: Session,
    user_id: uuid.UUID,
    page: int,
    page_size: int,
    status: str | None,
) -> tuple[list[Conversation], int]:
    filters = [Conversation.user_id == user_id]

    if status is not None:
        filters.append(Conversation.status == status)

    count_statement = (
        select(func.count(Conversation.id))
        .where(*filters)
    )
    total = db.scalar(count_statement) or 0

    offset = (page - 1) * page_size

    list_statement = (
        select(Conversation)
        .where(*filters)
        .order_by(
            Conversation.updated_at.desc(),
            Conversation.id.desc(),
        )
        .offset(offset)
        .limit(page_size)
    )

    items = list(db.scalars(list_statement).all())
    return items, total


def get_conversation(
    db: Session,
    user_id: uuid.UUID,
    conversation_id: uuid.UUID,
) -> Conversation | None:
    statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id,
    )
    return db.scalar(statement)


def update_conversation(
    db: Session,
    conversation: Conversation,
    changes: dict[str, Any],
) -> Conversation:
    for field_name, value in changes.items():
        setattr(conversation, field_name, value)

    db.flush()
    return conversation


def delete_conversation(
    db: Session,
    conversation: Conversation,
) -> None:
    db.delete(conversation)
    db.flush()