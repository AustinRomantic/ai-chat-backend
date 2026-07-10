from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import generate_reply

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest):
    reply = generate_reply(
        message=request.message,
        system_prompt=request.system_prompt,
        history=request.history,
    )
    return ChatResponse(reply=reply)