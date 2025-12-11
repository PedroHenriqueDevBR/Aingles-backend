from uuid import UUID
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Response
from sqlalchemy.orm import selectinload
from sqlmodel import select

from models.card_models import Card, CardReviewLog
from schemas.card_schema import (
    CardResponse,
    CardReviewLogResponse,
    CardReviewUpdate,
    CardUpdateRequest,
)
from services import sqlite_service
from utils.dependencies import CurrentUser

router = APIRouter()


@router.get("/")
def get_all_cards(
    current_user: CurrentUser,
    session: sqlite_service.SessionDep,
) -> list[Card]:
    cards = session.exec(
        select(Card)
        .filter(Card.author_id == current_user.uuid)
        .options(selectinload(Card.reviews))
        .offset(0)
        .limit(100)
    ).all()
    return cards


@router.get("/{card_id}")
def get_card(
    current_user: CurrentUser,
    card_id: str,
    session: sqlite_service.SessionDep,
) -> CardResponse:
    card = session.get(Card, UUID(card_id))
    if not card:
        raise HTTPException(status_code=404, detail="Card not found!")

    if card.author_id != current_user.uuid:
        raise HTTPException(status_code=404, detail="Card not found!")

    return card


@router.post("/")
def create_card(
    current_user: CurrentUser,
    card: Card,
    session: sqlite_service.SessionDep,
) -> CardResponse:
    card.author_id = current_user.uuid
    card.id = UUID(str(card.id)) if card.id is not None else None
    card.created_at = (
        datetime.fromisoformat(card.created_at)
        if type(card.created_at) is str
        else datetime.now()
    )
    card.next_review_at = (
        datetime.fromisoformat(card.next_review_at)
        if type(card.next_review_at) is str
        else datetime.now() + timedelta(minutes=10)
    )

    session.add(card)
    session.commit()
    session.refresh(card)
    return card


@router.post("/createall")
def create_all_cards(
    current_user: CurrentUser,
    cards: list[Card],
    session: sqlite_service.SessionDep,
) -> list[Card]:
    newCards = []
    for card in cards:
        card.id = UUID(str(card.id)) if card.id is not None else None
        card.author_id = current_user.uuid
        card.created_at = (
            datetime.fromisoformat(card.created_at)
            if type(card.created_at) is str
            else datetime.now()
        )
        card.next_review_at = (
            datetime.fromisoformat(card.next_review_at)
            if type(card.next_review_at) is str
            else datetime.now() + timedelta(minutes=10)
        )
        
        if session.get(Card, card.id):
            continue

        newCards.append(card)

    session.add_all(newCards)
    session.commit()
    for card in newCards:
        session.refresh(card)

    return newCards


@router.put("/{card_id}/update")
def update_card(
    current_user: CurrentUser,
    card_id: str,
    card_arg: CardUpdateRequest,
    session: sqlite_service.SessionDep,
) -> CardResponse:
    card = session.get(Card, UUID(card_id))
    if not card or card.author_id != current_user.uuid:
        raise HTTPException(status_code=404, detail="Card not found")
    if card_arg.front:
        card.front = card_arg.front
    if card_arg.back:
        card.back = card_arg.back
    if card_arg.appears_count:
        card.appears_count = card_arg.appears_count
    if card_arg.next_review_at:
        card.next_review_at = card_arg.next_review_at

    session.commit()
    session.refresh(card)
    return card


@router.patch(
    "/{card_id}/review",
    description="Review a card and log the review details",
)
def review_card(
    current_user: CurrentUser,
    card_id: str,
    card_arg: CardReviewUpdate,
    session: sqlite_service.SessionDep,
) -> CardResponse:
    card = session.get(Card, UUID(card_id))
    if not card or card.author_id != current_user.uuid:
        raise HTTPException(status_code=404, detail="Card not found")

    card.next_review_at = max(
        card.next_review_at.date(), card_arg.next_review_at.date()
    )
    card.appears_count = max(card.appears_count, card_arg.appears_count)
    card_review_log = CardReviewLog(
        card_id=card.id,
        user_id=current_user.uuid,
        review_at=card_arg.reviewAt,
        next_review_at=card_arg.next_review_at,
        difficult=card_arg.difficult,
    )

    session.add(card_review_log)
    session.commit()
    session.refresh(card)
    return card


@router.delete("/{card_id}/delete")
def delete_card(
    current_user: CurrentUser,
    card_id: str,
    session: sqlite_service.SessionDep,
):
    card = session.get(Card, UUID(card_id))
    if not card or card.author_id != current_user.uuid:
        raise HTTPException(status_code=404, detail="Card not found")

    for review in card.reviews:
        session.delete(review)

    session.delete(card)
    session.commit()

    return Response(status_code=204)
