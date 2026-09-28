from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    limit: int = 5


class Source(BaseModel):
    chunk_id: int
    document_id: int
    chunk_index: int
    content: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]