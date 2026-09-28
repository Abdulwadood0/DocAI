from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    email: str = Field(
        index=True,
        unique=True,
    )

    hashed_password: str | None = None

    google_id: str | None = Field(
        default=None,
        unique=True,
        index=True,
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )