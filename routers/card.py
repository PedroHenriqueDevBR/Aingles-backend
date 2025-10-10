from fastapi import APIRouter, HTTPException
from models.card_models import Card
from sqlmodel import select
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


@router.put("/{card_id}/update")
def update_card(card_id: int, card_arg: Card, session: sqlite_service.SessionDep) -> Card:
    card = session.get(Card, card_id)
    if not Card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    card = card_arg
    session.commit(card)
    return card