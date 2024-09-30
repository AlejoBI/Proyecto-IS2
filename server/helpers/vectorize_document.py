import tiktoken # Importar la librería tiktoken para tokenizar el texto y dividirlo en chunks de tamaño máximo
import asyncio  # Para operaciones asíncronas

def get_openai_embeddings(text: str, openai_client) -> list[float]:
    response = openai_client._openai_client.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding  # Devolver la lista de floats

# Función para convertir el contenido de un documento en vectores
async def document_to_vectors(content: str, openai_client) -> list[list[float]]:
    chunks = chunk_text(content, max_tokens=2048)
    tasks = [get_openai_embeddings(chunk, openai_client) for chunk in chunks]
    content_vectors = await asyncio.gather(*tasks)
    return content_vectors


# Función para dividir texto en fragmentos, respetando un máximo de tokens
def chunk_text(text: str, max_tokens: int) -> list[str]:
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(text)

    # Divide el texto en chunks de tamaño max_tokens
    chunks = [tokens[i:i + max_tokens] for i in range(0, len(tokens), max_tokens)]
    chunk_texts = [tokenizer.decode(chunk) for chunk in chunks]
    return chunk_texts