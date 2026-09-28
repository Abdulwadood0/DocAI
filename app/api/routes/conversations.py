from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from api.deps import get_current_user
from db.database import SessionDep
from db.models.conversation import Conversation
from db.models.message import Message
from db.models.user import User
from schemas.conversation import (
    ConversationCreate,
    ConversationPublic,
)
from schemas.message import MessagePublic


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


@router.post(
    "/",
    response_model=ConversationPublic,
)
def create_conversation(
    data: ConversationCreate,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    conversation = Conversation(
        user_id=current_user.id,
        title=data.title,
    )

    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    return conversation


@router.get(
    "/",
    response_model=list[ConversationPublic],
)
def get_conversations(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    statement = (
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.created_at.desc())
    )

    return list(session.exec(statement))


@router.get(
    "/{conversation_id}/messages",
    response_model=list[MessagePublic],
)
def get_messages(
    conversation_id: int,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    conversation = session.exec(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    ).first()

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )

    return list(session.exec(statement))