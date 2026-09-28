from openai import OpenAI

from core.config import settings


client = OpenAI(
    api_key=settings.OPENAI_API_KEY
)


def create_embeddings(texts: list[str]) -> list[list[float]]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
    )

    return [item.embedding for item in response.data]