from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.api.auth import get_current_user
from app.dependencies import get_db
from app.models import User, AssistantChat
from app.schemas import (
    AssistantChatCreate,
    AssistantChatOut,
    AssistantChatSendIn,
    AssistantChatSendOut,
    AssistantChatSummaryOut,
    AssistantChatUpdate,
)
from app.services.assistant_service import create_chat, delete_chat, get_chat, list_chats, send_message, update_chat

router = APIRouter(prefix="/assistant", tags=["assistant"])


def _chat_to_out(chat: AssistantChat) -> AssistantChatOut:
    return AssistantChatOut(
        id=chat.id,
        title=chat.title,
        provider=chat.provider,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
        messages_count=len(chat.messages),
        messages=[
            {
                "id": message.id,
                "role": message.role,
                "content": message.content,
                "intent": message.intent,
                "action_json": message.action_json,
                "created_at": message.created_at,
            }
            for message in chat.messages
        ],
    )


@router.get("/chats", response_model=list[AssistantChatSummaryOut])
def get_chats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chats = list_chats(db, current_user)
    return [
        AssistantChatSummaryOut(
            id=chat.id,
            title=chat.title,
            provider=chat.provider,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            messages_count=len(chat.messages),
        )
        for chat in chats
    ]


@router.post("/chats", response_model=AssistantChatOut, status_code=201)
def create_new_chat(
    payload: AssistantChatCreate | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chat = create_chat(db, current_user, title=payload.title if payload else None)
    chat = (
        db.query(AssistantChat)
        .options(joinedload(AssistantChat.messages))
        .filter(AssistantChat.id == chat.id)
        .first()
    )
    return _chat_to_out(chat)


@router.get("/chats/{chat_id}", response_model=AssistantChatOut)
def get_chat_detail(
    chat_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chat = get_chat(db, current_user, chat_id)
    chat = (
        db.query(AssistantChat)
        .options(joinedload(AssistantChat.messages))
        .filter(AssistantChat.id == chat.id)
        .first()
    )
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return _chat_to_out(chat)


@router.post("/chats/{chat_id}/messages", response_model=AssistantChatSendOut)
def post_chat_message(
    chat_id: str,
    payload: AssistantChatSendIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = send_message(db, current_user, chat_id, payload.message)
    chat = result["chat"]
    chat = (
        db.query(AssistantChat)
        .options(joinedload(AssistantChat.messages))
        .filter(AssistantChat.id == chat.id)
        .first()
    )
    return AssistantChatSendOut(
        chat=_chat_to_out(chat),
        answer=result["answer"],
        intent=result.get("intent"),
        action_json=result.get("action_json"),
        provider=result.get("provider", "gemini"),
        model=result.get("model", "gemini"),
    )


@router.patch("/chats/{chat_id}", response_model=AssistantChatOut)
def rename_chat(
    chat_id: str,
    payload: AssistantChatUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chat = update_chat(db, current_user, chat_id, title=payload.title)
    chat = (
        db.query(AssistantChat)
        .options(joinedload(AssistantChat.messages))
        .filter(AssistantChat.id == chat.id)
        .first()
    )
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return _chat_to_out(chat)


@router.delete("/chats/{chat_id}", status_code=204)
def remove_chat(
    chat_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_chat(db, current_user, chat_id)
