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
    count_statement = select(func.count(Message.id)).where(
        Message.conversation_id == conversation_id
    )
    total = db.scalar(count_statement) or 0

    offset = (page - 1) * page_size

    list_statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(
            Message.created_at.asc(),
            Message.id.asc(),
        )
        .offset(offset)
        .limit(page_size)
    )

    items = list(db.scalars(list_statement).all())
    return items, total