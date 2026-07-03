from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import generate_mock_reply

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("", response_model=ChatResponse)

def chat(request: ChatRequest):
    reply = generate_mock_reply(request.message)
    return ChatResponse(reply=reply)