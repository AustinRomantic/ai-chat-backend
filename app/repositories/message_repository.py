import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.message import Message


def list_messages(
    db: Session,
    conversation_id: uuid.UUID,
    page: int,
    page_size: int,
) -> tuple[list[Message], int]:
    count_statement = select(
        func.count(Message.id)
    ).where(
        Message.conversation_id == conversation_id
    )

    total = db.scalar(count_statement) or 0

    offset = (page - 1) * page_size

    list_statement = (
        select(Message)
        .where(
            Message.conversation_id == conversation_id
        )
        .order_by(
            Message.created_at.asc(),
            Message.id.asc(),
        )
        .offset(offset)
        .limit(page_size)
    )

    items = list(
        db.scalars(list_statement).all()
    )

    return items, total


def list_recent_messages(
    db: Session,
    conversation_id: uuid.UUID,
    limit: int = 10,
) -> list[Message]:
    statement = (
        select(Message)
        .where(
            Message.conversation_id == conversation_id
        )
        .order_by(
            Message.created_at.desc(),
            Message.id.desc(),
        )
        .limit(limit)
    )

    messages = list(
        db.scalars(statement).all()
    )

    messages.reverse()

    return messages


def create_message(
    db: Session,
    conversation_id: uuid.UUID,
    role: str,
    content: str,
) -> Message:
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
    )

    db.add(message)
    db.flush()
    db.refresh(message)

    return message


def list_messages_by_conversation(
    db: Session,
    conversation_id: uuid.UUID,
) -> list[Message]:
    statement = (
        select(Message)
        .where(
            Message.conversation_id == conversation_id
        )
        .order_by(
            Message.created_at.asc(),
            Message.id.asc(),
        )
    )

    return list(
        db.scalars(statement).all()
    )