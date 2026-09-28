import asyncio
import json
from typing import Annotated

from api.deps import get_current_user
from db.database import SessionDep
from db.models.conversation import Conversation
from db.models.message import Message
from db.models.user import User
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from schemas.chat import ChatRequest
from services.llm import generate_answer_stream, rewrite_query
from services.retrieval import search_similar_chunks
from sqlmodel import select

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


def sse_event(event: str, data):
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@router.post("/{conversation_id}")
def chat(
    conversation_id: int,
    data: ChatRequest,
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

    messages = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    ).all()

    history = [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in messages
    ]

    search_query = rewrite_query(
        question=data.question,
        history=history,
    )

    results = search_similar_chunks(
        session=session,
        user_id=current_user.id,
        query=search_query,
        limit=data.limit,
    )

    context = "\n\n".join(result[0].content for result in results)

    sources = [result[0] for result in results]

    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=data.question,
    )

    session.add(user_message)
    session.commit()

    async def generate():
        full_answer = ""

        try:
            stream = generate_answer_stream(
                question=data.question,
                context=context,
                history=history,
            )

            async for chunk in stream:
                full_answer += chunk

                yield sse_event(
                    "token",
                    {"text": chunk},
                )

            # Send sources only after the answer is complete
            yield sse_event(
                "sources",
                [
                    {
                        "chunk_id": source.id,
                        "document_id": source.document_id,
                        "chunk_index": source.chunk_index,
                        "content": source.content,
                    }
                    for source in sources
                ],
            )

            # Save assistant message only after successful completion
            assistant_message = Message(
                conversation_id=conversation_id,
                role="assistant",
                content=full_answer,
            )

            session.add(assistant_message)
            session.commit()

            yield sse_event(
                "done",
                {"message": "completed"},
            )

        except asyncio.CancelledError:
            print("Client disconnected. Streaming cancelled.")
            raise

        except Exception as e:
            print(f"Streaming error: {e}")

            yield sse_event(
                "error",
                {"message": "Something went wrong while generating the answer."},
            )

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
    )
