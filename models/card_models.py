import uuid
from datetime import datetime, timedelta

from sqlmodel import Field, Relationship, SQLModel

EASY = 1
MEDIUM = 2
HARD = 3
IMPOSSIBLE = 4

LEVELS: dict[int, str] = {
    EASY: "Easy",
    MEDIUM: "Medium",
    HARD: "Hard",
    IMPOSSIBLE: "Impossible",
}


class Card(SQLModel, table=True):
    __tablename__ = "card"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    front: str | None = Field(default="", index=True)
    back: str | None = Field(default="")
    appearsCount: int | None = Field(default=0)
    createdAt: datetime | None = Field(default=datetime.now())
    nextReviewAt: datetime | None = Field(default=datetime.now() + timedelta(days=1))
    author_id: str | None = Field(default=None, index=True)

    reviews: list["CardReviewLog"] = Relationship(back_populates="card")


class CardReviewLog(SQLModel, table=True):
    __tablename__ = "card_review_log"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    card_id: uuid.UUID = Field(foreign_key="card.id")
    user_id: uuid.UUID = Field(foreign_key="user.id")
    review_at: datetime | None = Field(default_factory=datetime.now)
    next_review_at: datetime | None = Field(
        default_factory=lambda: datetime.now() + timedelta(days=1),
    )
    difficult: int = Field(default=EASY)

    card: Card = Relationship(back_populates="reviews")
