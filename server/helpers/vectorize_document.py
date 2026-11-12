import tiktoken
from typing import Any


def get_openai_embeddings(text: str, openai_client: Any) -> list[float]:
    if hasattr(openai_client, "get_embedding"):
        return openai_client.get_embedding(text)

    # Compatibilidad con el adaptador utilizado por versiones anteriores.
    response = openai_client._openai_client.embeddings.create(
        input=text,
        model="text-embedding-3-small",
    )
    return response.data[0].embedding


def document_to_vectors(content: str, openai_client: Any) -> list[list[float]]:
    chunks = chunk_text(content, max_tokens=2048)
    if not chunks:
        raise ValueError("The document does not contain extractable text")
    content_vectors = [get_openai_embeddings(chunk, openai_client) for chunk in chunks]
    return content_vectors


def chunk_text(text: str, max_tokens: int) -> list[str]:
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(text)

    chunks = [tokens[i:i + max_tokens] for i in range(0, len(tokens), max_tokens)]
    chunk_texts = [tokenizer.decode(chunk) for chunk in chunks if chunk]
    return chunk_texts
