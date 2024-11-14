import tiktoken
from typing import Any


def get_openai_embeddings(text: str, openai_client: Any) -> list[float]:
    response = openai_client._openai_client.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding  # Devolver la lista de floats


def document_to_vectors(content: str, openai_client: Any) -> list[list[float]]:
    chunks = chunk_text(content, max_tokens=2048)
    content_vectors = [get_openai_embeddings(chunk, openai_client) for chunk in chunks]
    return content_vectors


def chunk_text(text: str, max_tokens: int) -> list[str]:
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(text)

    chunks = [tokens[i:i + max_tokens] for i in range(0, len(tokens), max_tokens)]
    chunk_texts = [tokenizer.decode(chunk) for chunk in chunks]
    return chunk_texts
