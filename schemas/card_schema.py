from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

from sqlmodel import SQLModel


class CardReviewLogResponse(SQLModel):
    id: UUID
    review_at: datetime
    next_review_at: datetime
    difficult: int


class CardResponse(SQLModel):
    id: UUID
    front: Optional[str]
    back: Optional[str]
    appearsCount: Optional[int]
    createdAt: Optional[datetime]
    nextReviewAt: Optional[datetime]
    reviews: List[CardReviewLogResponse] = []

    class Config:
        orm_mode = True


class CardReviewUpdate(BaseModel):
    reviewAt: datetime
    nextReviewAt: datetime
    difficult: int
    appearsCount: int

    class Config:
        json_schema_extra = {
            "example": {
                "reviewAt": "2024-07-01T12:00:00Z",
                "nextReviewAt": "2024-07-02T12:00:00Z",
                "difficult": 1, # 1 - EASY, 2 - MEDIUM, 3 - HARD, 4 - IMPOSSIBLE
                "appearsCount": 5,
            }
        }
