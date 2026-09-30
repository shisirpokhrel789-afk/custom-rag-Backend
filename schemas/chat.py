from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(
        ...,
        min_length=1,
        description="Unique ID for the conversation",
    )

    message: str = Field(
        ...,
        min_length=1,
        description="User's message",
    )


class ChatResponse(BaseModel):
    session_id: str
    answer: str