from datetime import datetime, timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column
from sqlmodel import Field, SQLModel


class DocumentChunk(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    document_id: int = Field(
        foreign_key="document.id",
        index=True,
    )

    content: str

    chunk_index: int

    embedding: list[float] | None = Field(
        default=None,
        sa_column=Column(Vector(1536)),
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )