from fastapi import APIRouter, HTTPException, Response
from sqlmodel import select

from models.card_models import Card
from services import sqlite_service

router = APIRouter()


@router.get("/")
def get_all_cards(session: sqlite_service.SessionDep) -> list[Card]:
    cards = session.exec(select(Card).offset(0).limit(100)).all()
    return cards


@router.get("/{card_id}")
def get_card(card_id: int, session: sqlite_service.SessionDep) -> Card:
    card = session.get(Card, card_id)
    if not card:
        return HTTPException(status_code=404, detail="Card not found!")
    return card


@router.post("/")
def create_card(card: Card, session: sqlite_service.SessionDep) -> Card:
    session.add(card)
    session.commit()
    session.refresh(card)
    return card


@router.post("/createall")
def create_all_cards(
    cards: list[Card], session: sqlite_service.SessionDep
) -> list[Card]:
    session.add_all(cards)
    session.commit()
    for card in cards:
        session.refresh(card)

    return cards


@router.put("/{card_id}/update")
def update_card(
    card_id: int, card_arg: Card, session: sqlite_service.SessionDep
) -> Card:
    card = session.get(Card, card_id)
    if not Card:
        raise HTTPException(status_code=404, detail="Card not found")

    card.front = card_arg.front
    card.back = card.back
    card.appearsCount = card_arg.appearsCount
    card.createdAt = card_arg.createdAt
    card.nextReviewAt = card_arg.nextReviewAt

    session.commit()
    session.refresh(card)
    return card


@router.delete("/{card_id}/delete")
def delete_card(card_id: int, session: sqlite_service.SessionDep):
    card = session.get(Card, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    session.delete(card)
    session.commit()

    return Response(status_code=204)
