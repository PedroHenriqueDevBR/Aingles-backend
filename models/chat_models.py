from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel
from sqlmodel import Relationship



class Chat(SQLModel, table=True):
    __tablename__ = "chat"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    title: str = Field()
    created_at: datetime = Field(default_factory=datetime.now())
    author_id: UUID | None = Field(foreign_key="user.id")
    
    messages: list["ChatMessage"] = Relationship(back_populates="chat")


class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_message"

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    DEVELOPER = "developer"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    role: str = Field()
    content: str = Field()
    created_at: datetime = Field(default_factory=datetime.now())
    chat_id: UUID = Field(foreign_key="chat.id")
    
    chat: Chat = Relationship(back_populates="messages")
