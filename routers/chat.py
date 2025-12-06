from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import selectinload
from sqlmodel import select

from models.chat_models import Chat, ChatMessage
from schemas.chat_schema import CreateChatRequest
from services import sqlite_service, ai_service

from utils.dependencies import CurrentUser

router = APIRouter()


@router.get("/")
def get_my_chats(
    current_user: CurrentUser,
    session: sqlite_service.SessionDep,
) -> list[Chat]:
    chats = session.exec(
        select(Chat).filter(Chat.author_id == current_user.id).offset(0).limit(100)
    ).all()
    return chats


@router.post("/")
def create_chat(
    current_user: CurrentUser,
    session: sqlite_service.SessionDep,
    chat_data: CreateChatRequest,
) -> Chat:
    chat = ai_service.AIService().initialize_chat(current_user.id, chat_data)
    session.add(chat)
    session.commit()
    session.refresh(chat)

    return chat


@router.post("/{chat_id}/message/")
def send_message(
    chat_id: str,
    current_user: CurrentUser,
    session: sqlite_service.SessionDep,
    message_content: str,
) -> ChatMessage:
    chat = session.exec(
        select(Chat)
        .options(selectinload(Chat.messages))
        .filter(Chat.id == chat_id)
        .filter(Chat.author_id == current_user.id)
    ).first()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    assistant_message = ai_service.AIService().send_message(chat, message_content)

    session.add(chat)
    session.commit()
    session.refresh(assistant_message)

    return assistant_message


@router.post("/{chat_id}/message/stream")
def send_message_stream(
    chat_id: str,
    current_user: CurrentUser,
    session: sqlite_service.SessionDep,
    message_content: str,
):
    chat = session.exec(
        select(Chat)
        .options(selectinload(Chat.messages))
        .filter(Chat.id == chat_id)
        .filter(Chat.author_id == current_user.id)
    ).first()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    def generate():
        for chunk in ai_service.AIService().send_message_stream(chat, message_content):
            yield chunk

        session.add(chat)
        session.commit()

    return StreamingResponse(generate(), media_type="text/plain")
