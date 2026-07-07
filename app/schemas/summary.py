from pydantic import BaseModel, Field

class SummaryRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)

class SummaryResponse(BaseModel):
    summary: str