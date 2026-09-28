from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class Message(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    conversation_id: int = Field(
        foreign_key="conversation.id",
        index=True,
    )

    role: str

    content: str

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )