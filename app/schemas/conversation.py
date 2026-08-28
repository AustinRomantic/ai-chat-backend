import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


ConversationStatus = Literal["active", "archived"]


class ConversationCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(..., min_length=1, max_length=200)
    system_prompt: str | None = Field(default=None, max_length=2000)


class ConversationUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(default=None, min_length=1, max_length=200)
    system_prompt: str | None = Field(default=None, max_length=2000)
    status: ConversationStatus | None = None

    @model_validator(mode="after")
    def validate_update_fields(self):
        if not self.model_fields_set:
            raise ValueError("至少需要提供一个要更新的字段")

        if "title" in self.model_fields_set and self.title is None:
            raise ValueError("title 不能为 null")

        if "status" in self.model_fields_set and self.status is None:
            raise ValueError("status 不能为 null")

        return self


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    system_prompt: str | None
    status: ConversationStatus
    created_at: datetime
    updated_at: datetime


class ConversationListResponse(BaseModel):
    items: list[ConversationResponse]
    total: int
    page: int
    page_size: int
