from core.config import settings

from openai import AsyncOpenAI, OpenAI

client_Async = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
client = OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_answer(
    question: str,
    context: str,
    history: list[dict[str, str]],
) -> str:

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant answering questions "
                "about the user's documents. "
                "Use the provided document context to answer. "
                "If the answer cannot be found in the documents, "
                "say you could not find the answer. "
                "Do not make up information."
            ),
        }
    ]

    messages.extend(history)

    messages.append(
        {
            "role": "user",
            "content": f"""
Document context:

{context}

Question:

{question}
""",
        }
    )

    response = client.responses.create(
        model="gpt-5.6-luna",
        input=messages,
    )

    return response.output_text




async def generate_answer_stream(
    question: str,
    context: str,
    history: list[dict[str, str]],
):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant answering questions "
                "about the user's documents. "
                "Use the provided document context to answer. "
                "If the answer cannot be found in the documents, "
                "say you could not find the answer. "
                "Do not make up information."
            ),
        }
    ]

    messages.extend(history)

    messages.append(
        {
            "role": "user",
            "content": f"""
Document context:

{context}

Question:

{question}
""",
        }
    )

    stream = await client_Async.responses.create(
        model="gpt-5.6-luna",
        input=messages,
        stream=True,
    )

    async for event in stream:
        if event.type == "response.output_text.delta":
            yield event.delta


def rewrite_query(
    question: str,
    history: list[dict[str, str]],
) -> str:

    if not history:
        return question

    messages = [
        {
            "role": "system",
            "content": (
                "Rewrite the user's latest question into a standalone "
                "search query that can be understood without conversation "
                "history. Preserve the user's intent and important terms. "
                "Do not answer the question."
            ),
        }
    ]

    messages.extend(history)

    messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    response = client.responses.create(
        model="gpt-5.6-luna",
        input=messages,
    )

    return response.output_text