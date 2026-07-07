from fastapi import APIRouter

from app.schemas.summary import SummaryRequest, SummaryResponse
from app.services.summary_service import generate_mock_reply

router = APIRouter(prefix="/summary", tags=["Summary"])

@router.post("", response_model=SummaryResponse)

def chat(request: SummaryRequest):
    summary = generate_mock_reply(request.text)
    return SummaryResponse(summary=summary)