from uuid import UUID, uuid4
from datetime import datetime

from sqlmodel import Field, SQLModel


class Article(SQLModel, table=True):
    __tablename__ = "article"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    content_url: str | None = Field(default="", unique=True, index=True)
    title: str = Field(default="", index=True)
    content: str = Field(default="")
    created_at: datetime | None = Field(default=datetime.now())
    author_id: UUID | None = Field(
        foreign_key="user.id",
    )


class ArticleReaded(SQLModel, table=True):
    __tablename__ = "article_readed"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    readed_at: datetime | None = Field(default=datetime.now())
    article_id: UUID = Field(foreign_key="article.id")
    user_id: UUID = Field(foreign_key="user.id")
