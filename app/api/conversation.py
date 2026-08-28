import uuid

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.conversation import (
    ConversationCreate,
    ConversationListResponse,
    ConversationResponse,
    ConversationStatus,
    ConversationUpdate,
)
from app.schemas.message import MessageListResponse
from app.services import conversation_service


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


@router.post(
    "",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_conversation(
    payload: ConversationCreate,
    db: Session = Depends(get_db),
):
    return conversation_service.create_conversation(
        db=db,
        payload=payload,
    )


@router.get(
    "",
    response_model=ConversationListResponse,
)
def list_conversations(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status_filter: ConversationStatus | None = Query(
        default=None,
        alias="status",
    ),
    db: Session = Depends(get_db),
):
    return conversation_service.list_conversations(
        db=db,
        page=page,
        page_size=page_size,
        status=status_filter,
    )


@router.get(
    "/{conversation_id}/messages",
    response_model=MessageListResponse,
)
def list_conversation_messages(
    conversation_id: uuid.UUID,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return conversation_service.list_conversation_messages(
        db=db,
        conversation_id=conversation_id,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse,
)
def get_conversation(
    conversation_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    return conversation_service.get_conversation(
        db=db,
        conversation_id=conversation_id,
    )


@router.patch(
    "/{conversation_id}",
    response_model=ConversationResponse,
)
def update_conversation(
    conversation_id: uuid.UUID,
    payload: ConversationUpdate,
    db: Session = Depends(get_db),
):
    return conversation_service.update_conversation(
        db=db,
        conversation_id=conversation_id,
        payload=payload,
    )


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_conversation(
    conversation_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> Response:
    conversation_service.delete_conversation(
        db=db,
        conversation_id=conversation_id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)