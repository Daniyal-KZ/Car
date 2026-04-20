from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AssistantChatCreate(BaseModel):
    title: Optional[str] = None


class AssistantChatUpdate(BaseModel):
    title: Optional[str] = None


class AssistantChatMessageIn(BaseModel):
    role: str
    content: str


class AssistantChatSendIn(BaseModel):
    message: str = Field(min_length=1)


class AssistantMessageOut(BaseModel):
    id: int
    role: str
    content: str
    intent: Optional[str] = None
    action_json: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AssistantChatSummaryOut(BaseModel):
    id: str
    title: str
    provider: str
    created_at: datetime
    updated_at: datetime
    messages_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class AssistantChatOut(AssistantChatSummaryOut):
    messages: list[AssistantMessageOut] = Field(default_factory=list)


class AssistantChatSendOut(BaseModel):
    chat: AssistantChatOut
    answer: str
    intent: Optional[str] = None
    action_json: Optional[str] = None
    provider: str = "gemini"
    model: str = "gemini"
