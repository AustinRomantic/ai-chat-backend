from fastapi import APIRouter

from fastapi.responses import StreamingResponse

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import generate_mock_stream, generate_reply, generate_reply_stream

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest):
    reply = generate_reply(
        message=request.message,
        system_prompt=request.system_prompt,
        history=request.history,
    )
    return ChatResponse(reply=reply)

@router.post("/stream-mock")
async def chat_stream(request: ChatRequest):
    stream = generate_mock_stream(
        message=request.message,
        system_prompt=request.system_prompt,
        history=request.history,
    )

    return StreamingResponse(
        stream,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )

@router.post("/stream")
def chat_stream(request: ChatRequest):
    stream = generate_reply_stream(
        message=request.message,
        system_prompt=request.system_prompt,
        history=request.history,
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