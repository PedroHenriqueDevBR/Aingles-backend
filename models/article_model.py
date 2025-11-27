import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class Article(SQLModel, table=True):
    __tablename__ = "article"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    content_url: str | None = Field(default="", unique=True, index=True)
    title: str = Field(default="", index=True)
    content: str = Field(default="")
    created_at: datetime | None = Field(default=datetime.now())
    author_id: uuid.UUID | None = Field(
        default_factory=uuid.uuid4,
        foreign_key="user.id",
    )


class ArticleReaded(SQLModel, table=True):
    __tablename__ = "article_readed"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    readed_at: datetime | None = Field(default=datetime.now())
    article_id: uuid.UUID = Field(foreign_key="article.id")
    user_id: uuid.UUID = Field(foreign_key="user.id")
