import uuid

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    conversation_id: uuid.UUID

    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
    )


class ChatResponse(BaseModel):
    conversation_id: uuid.UUID
    user_message_id: uuid.UUID
    assistant_message_id: uuid.UUID
    reply: str