from datetime import datetime

from pydantic import BaseModel


class ConversationCreate(BaseModel):
    title: str = "New conversation"


class ConversationPublic(BaseModel):
    id: int
    title: str
    created_at: datetime