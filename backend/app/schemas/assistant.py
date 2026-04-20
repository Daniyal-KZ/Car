from pydantic import BaseModel, Field


class AssistantMessageIn(BaseModel):
    role: str
    content: str


class AssistantChatRequest(BaseModel):
    message: str = Field(min_length=1)
    history: list[AssistantMessageIn] = Field(default_factory=list)


class AssistantChatResponse(BaseModel):
    answer: str
    provider: str = "gemini"
    model: str = "gemini-1.5-flash"
