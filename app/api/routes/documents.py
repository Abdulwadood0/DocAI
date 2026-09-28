from pathlib import Path
from uuid import uuid4
from pypdf import PdfReader

from fastapi import APIRouter, HTTPException, UploadFile, status

from api.deps import get_current_user
from db.database import SessionDep
from db.models.document import Document
from db.models.user import User
from db.models.document_chunk import DocumentChunk
from services.embeddings import create_embeddings
from services.chunking import chunk_text
from typing import Annotated
from fastapi import Depends

from schemas.documents import (
    DocumentSearchRequest,
    DocumentSearchResult,
)
from services.retrieval import search_similar_chunks



router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported",
        )

    file_id = uuid4()
    file_path = UPLOAD_DIR / f"{file_id}.pdf"

    contents = await file.read()

    file_path.write_bytes(contents)

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    document = Document(
        user_id=current_user.id,
        filename=file.filename or "unknown.pdf",
        file_path=str(file_path),
    )

    session.add(document)
    session.commit()
    session.refresh(document)

    # Split text into chunks
    chunks = chunk_text(text)

    # Generate embeddings for all chunks
    embeddings = create_embeddings(chunks)

    # Save chunks + embeddings
    for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        document_chunk = DocumentChunk(
        document_id=document.id,
        content=chunk,
        chunk_index=index,
        embedding=embedding,
        )
        session.add(document_chunk)

    session.commit()

    return {
        "id": document.id,
        "filename": document.filename,
        "pages": len(reader.pages),
        "chunks": len(chunks),
    }



@router.post(
    "/search",
    response_model=list[DocumentSearchResult],
)
def search_documents(
    data: DocumentSearchRequest,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    chunks = search_similar_chunks(
    session=session,
    user_id=current_user.id,
    query=data.query,
    limit=data.limit,
    )

    return [
        DocumentSearchResult(
            chunk_id=chunk.id,
            document_id=chunk.document_id,
            content=chunk.content,
            chunk_index=chunk.chunk_index,
        )
        for chunk in chunks
    ]