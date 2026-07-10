from typing import Optional

from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    system_prompt: Optional[str] = Field(default=None, max_length=2000)


class ChatResponse(BaseModel):
    reply: str