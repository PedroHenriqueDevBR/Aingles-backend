from uuid import UUID
from fastapi import APIRouter, HTTPException, Response
from sqlmodel import select

from models.card_models import Card, CardReviewLog
from schemas.card_schema import CardResponse, CardReviewUpdate, CardUpdateRequest
from services import sqlite_service
from utils.dependencies import CurrentUser
from sqlalchemy.orm import selectinload

router = APIRouter()


@router.get("/")
def get_all_cards(
    current_user: CurrentUser,
    session: sqlite_service.SessionDep,
) -> list[Card]:
    cards = session.exec(
        select(Card)
        .filter(Card.author_id == current_user.id)
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
    
    if card.author_id != current_user.id:
        raise HTTPException(status_code=404, detail="Card not found!")

    return card


@router.post("/")
def create_card(
    current_user: CurrentUser,
    card: Card,
    session: sqlite_service.SessionDep,
) -> CardResponse:
    card.author_id = current_user.id
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
    for card in cards:
        card.author_id = current_user.id

    session.add_all(cards)
    session.commit()
    for card in cards:
        session.refresh(card)

    return cards


@router.put("/{card_id}/update")
def update_card(
    current_user: CurrentUser,
    card_id: str,
    card_arg: CardUpdateRequest,
    session: sqlite_service.SessionDep,
) -> CardResponse:
    card = session.get(Card, UUID(card_id))
    if not card or card.author_id != current_user.id:
        raise HTTPException(status_code=404, detail="Card not found")
    if card_arg.front:
        card.front = card_arg.front
    if card_arg.back:
        card.back = card_arg.back
    if card_arg.appearsCount:
        card.appearsCount = card_arg.appearsCount
    if card_arg.nextReviewAt:
        card.nextReviewAt = card_arg.nextReviewAt

    session.commit()
    session.refresh(card)
    return card


@router.patch("/{card_id}/review")
def review_card(
    current_user: CurrentUser,
    card_id: str,
    card_arg: CardReviewUpdate,
    session: sqlite_service.SessionDep,
) -> CardResponse:
    card = session.get(Card, UUID(card_id))
    if not card or card.author_id != current_user.id:
        raise HTTPException(status_code=404, detail="Card not found")

    card.nextReviewAt = max(card.nextReviewAt.date(), card_arg.nextReviewAt.date())
    card.appearsCount = max(card.appearsCount, card_arg.appearsCount)
    card_review_log = CardReviewLog(
        card_id=card.id,
        user_id=current_user.id,
        review_at=card_arg.reviewAt,
        next_review_at=card_arg.nextReviewAt,
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
    if not card or card.author_id != current_user.id:
        raise HTTPException(status_code=404, detail="Card not found")
    
    for review in card.reviews:
        session.delete(review)

    session.delete(card)
    session.commit()

    return Response(status_code=204)
