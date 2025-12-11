from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from sqlmodel import SQLModel

from models.chat_models import ChatMessage


class CreateChatRequest(BaseModel):
    title: str

    class Config:
        json_schema_extra = {
            "example": {
                "title": "My New Chat",
            }
        }


class ChatMessageRequest(BaseModel):
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Hello, how are you?",
            }
        }


class MessageResponse(SQLModel):
    id: UUID
    role: str
    content: str
    created_at: datetime

    class Config:
        orm_mode = True


class ChatMessageResponse(BaseModel):
    user_message: ChatMessage
    assistant_message: ChatMessage


class ChatWithMessagesResponse(SQLModel):
    id: UUID
    title: str
    created_at: datetime
    messages: list[MessageResponse] = []

    class Config:
        orm_mode = True
