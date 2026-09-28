from openai import OpenAI
from sqlmodel import Session, select

from core.config import settings
from db.models.document_chunk import DocumentChunk
from db.models.document import Document

client = OpenAI(
    api_key=settings.OPENAI_API_KEY
)


def search_similar_chunks(
    session: Session,
    user_id: int,
    query: str,
    limit: int = 5,
    max_distance: float = 0.5,
):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query,
    )

    query_embedding = response.data[0].embedding

    distance = DocumentChunk.embedding.cosine_distance(
        query_embedding
    )

    statement = (
        select(
            DocumentChunk,
            distance.label("distance"),
        )
        .join(Document)
        .where(
            Document.user_id == user_id,
            distance <= max_distance,
        )
        .order_by(distance)
        .limit(limit)
    )

    return session.exec(statement).all()