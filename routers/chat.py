from uuid import UUID
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import selectinload
from sqlmodel import select

from models.chat_models import Chat, ChatMessage
from schemas.chat_schema import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatWithMessagesResponse,
    CreateChatRequest,
    MessageResponse,
)
from services import sqlite_service, ai_service

from utils.dependencies import CurrentUser

router = APIRouter()


@router.get("/")
def get_my_chats(
    current_user: CurrentUser,
    session: sqlite_service.SessionDep,
) -> list[Chat]:
    if not current_user.has_ai_access:
        raise HTTPException(
            status_code=403, detail="AI access is required to view chats."
        )

    chats = session.exec(
        select(Chat).filter(Chat.author_id == current_user.uuid).offset(0).limit(100)
    ).all()
    return chats


@router.get("/{chat_id}/messages")
def chat_messages(
    chat_id: str,
    current_user: CurrentUser,
    session: sqlite_service.SessionDep,
) -> ChatWithMessagesResponse:
    if not current_user.has_ai_access:
        raise HTTPException(
            status_code=403, detail="AI access is required to view chats."
        )

    chat = session.exec(
        select(Chat)
        .options(selectinload(Chat.messages))
        .filter(Chat.id == UUID(chat_id))
        .filter(Chat.author_id == current_user.uuid)
    ).first()

    return chat


@router.post("/")
def create_chat(
    current_user: CurrentUser,
    session: sqlite_service.SessionDep,
    chat_data: CreateChatRequest,
) -> Chat:
    if not current_user.has_ai_access:
        raise HTTPException(
            status_code=403, detail="AI access is required to view chats."
        )

    chat = ai_service.AIService().initialize_chat(current_user.uuid, chat_data)
    session.add(chat)
    session.commit()
    session.refresh(chat)

    return chat


@router.delete("/{chat_id}")
def delete_chat(
    chat_id: str,
    current_user: CurrentUser,
    session: sqlite_service.SessionDep,
) -> dict:
    if not current_user.has_ai_access:
        raise HTTPException(
            status_code=403, detail="AI access is required to view chats."
        )

    chat = session.exec(
        select(Chat)
        .filter(Chat.id == UUID(chat_id))
        .filter(Chat.author_id == current_user.uuid)
    ).first()

    messages = session.exec(
        select(ChatMessage).filter(ChatMessage.chat_id == UUID(chat_id))
    ).all()

    for message in messages:
        session.delete(message)

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    session.delete(chat)
    session.commit()

    return Response(
        content='{"detail": "Chat deleted successfully"}',
        status_code=204,
        media_type="application/json",
    )


@router.post("/{chat_id}/message/")
def send_message(
    chat_id: str,
    content: ChatMessageRequest,
    current_user: CurrentUser,
    session: sqlite_service.SessionDep,
) -> ChatMessageResponse:
    if not current_user.has_ai_access:
        raise HTTPException(
            status_code=403, detail="AI access is required to view chats."
        )

    chat = session.exec(
        select(Chat)
        .filter(Chat.id == UUID(chat_id))
        .filter(Chat.author_id == current_user.uuid)
    ).first()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    message_response = ai_service.AIService().send_message(
        chat,
        content.message,
    )

    session.add(chat)
    session.commit()
    session.refresh(message_response.assistant_message)
    session.refresh(message_response.user_message)

    return message_response


@router.post("/{chat_id}/message/stream")
def send_message_stream(
    chat_id: str,
    current_user: CurrentUser,
    session: sqlite_service.SessionDep,
    content: ChatMessageRequest,
) -> MessageResponse:
    if not current_user.has_ai_access:
        raise HTTPException(
            status_code=403, detail="AI access is required to view chats."
        )

    chat = session.exec(
        select(Chat)
        .options(selectinload(Chat.messages))
        .filter(Chat.id == UUID(chat_id))
        .filter(Chat.author_id == current_user.uuid)
    ).first()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    def generate():
        for chunk in ai_service.AIService().send_message_stream(
            chat,
            content.message,
        ):
            yield chunk

        session.add(chat)
        session.commit()

    return StreamingResponse(generate(), media_type="text/plain")
