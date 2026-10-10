from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import (
    generate_reply,
    generate_reply_stream,
    prepare_chat,
)


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post(
    "",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    return generate_reply(
        db=db,
        conversation_id=request.conversation_id,
        message=request.message,
    )


@router.post("/stream")
def chat_stream(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    prepared_chat = prepare_chat(
        db=db,
        conversation_id=request.conversation_id,
        message=request.message,
    )

    stream = generate_reply_stream(
        db=db,
        prepared_chat=prepared_chat,
    )

    return StreamingResponse(
        stream,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )