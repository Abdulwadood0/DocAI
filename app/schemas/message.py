from datetime import datetime

from pydantic import BaseModel


class MessagePublic(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime