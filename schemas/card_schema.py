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
    appears_count: Optional[int]
    created_at: Optional[datetime]
    next_review_at: Optional[datetime]
    reviews: List[CardReviewLogResponse] = []

    class Config:
        orm_mode = True


class CardUpdateRequest(BaseModel):
    front: Optional[str] = None
    back: Optional[str] = None
    appears_count: Optional[int] = None
    next_review_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "front": "What is the capital of France?",
                "back": "Paris",
                "appears_count": 3,
                "next_review_at": "2024-07-01T12:00:00Z",
            }
        }


class CardReviewUpdate(BaseModel):
    reviewAt: datetime
    next_review_at: datetime
    difficult: int
    appears_count: int

    class Config:
        json_schema_extra = {
            "example": {
                "reviewAt": "2024-07-01T12:00:00Z",
                "next_review_at": "2024-07-02T12:00:00Z",
                "difficult": 1, # 1 - EASY, 2 - MEDIUM, 3 - HARD, 4 - IMPOSSIBLE
                "appears_count": 5,
            }
        }
