from sqlmodel import SQLModel, Field
from datetime import datetime


class Card(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    front: str | None = Field(default="", index=True)
    back: str | None = Field(default="")
    appearsCount: int | None = Field(default=0)
    createdAt: datetime | None = Field()
    nextReviewAt: datetime | None = Field()
