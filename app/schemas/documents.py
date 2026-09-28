from pydantic import BaseModel


class DocumentSearchRequest(BaseModel):
    query: str
    limit: int = 5


class DocumentSearchResult(BaseModel):
    chunk_id: int
    document_id: int
    content: str
    chunk_index: int