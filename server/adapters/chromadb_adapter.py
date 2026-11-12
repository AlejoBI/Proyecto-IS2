from abc import ABC
import chromadb
from typing import List, Optional, Any
from server.core import ports
from server.core import models
from server.helpers.vectorize_document import chunk_text, get_openai_embeddings
from server.adapters.openai_adapter import ProviderError


class NoDocumentsIndexedError(Exception):
    """No hay documentos disponibles para la sesión y proveedor solicitados."""


class ChromaDBAdapter(ports.DocumentRepositoryPort, ABC):
    def __init__(self, number_of_vectorial_results: int, path: str = "./chroma_data",
                 chunk_size_tokens: int = 2048) -> None:
        self.client = chromadb.PersistentClient(path=path)
        self.collection = self.client.get_or_create_collection("documents")
        self._collections = {"openai": self.collection}
        self._number_of_vectorial_results = number_of_vectorial_results
        self._chunk_size_tokens = chunk_size_tokens

    def _get_collection(self, provider: str):
        if provider not in self._collections:
            self._collections[provider] = self.client.get_or_create_collection(
                f"documents_{provider}"
            )
        return self._collections[provider]

    def save_document(self, document: models.Document, content: str, openai_client: Any,
                      provider: str = "openai") -> None:
        chunks = chunk_text(content, max_tokens=self._chunk_size_tokens)
        if not chunks:
            raise ValueError("The document does not contain extractable text")
        embeddings = [get_openai_embeddings(chunk, openai_client) for chunk in chunks]
        if not embeddings or any(not embedding for embedding in embeddings):
            raise ProviderError(
                f"{provider.capitalize()} returned an empty embedding"
            )
        ids = [f"{document.id}:{index}" for index in range(len(chunks))]

        self._get_collection(provider).upsert(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=[{"document_id": document.id, "title": document.title or "",
                        "session_id": document.session_id or "",
                        "owner_email": document.owner_email or "",
                        "provider": provider,
                        "expires_at": document.expires_at or "",
                        "checksum": document.checksum or ""}
                       for _ in chunks],
        )

    def get_documents(self, query: str, openai_client: Any, n_results: Optional[int] = None,
                      session_id: Optional[str] = None,
                      owner_email: Optional[str] = None,
                      provider: str = "openai") -> List[models.Document]:
        if not n_results:
            n_results = self._number_of_vectorial_results

        kwargs = {
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"],
        }
        if owner_email:
            kwargs["where"] = {"owner_email": owner_email}
        elif session_id:
            kwargs["where"] = {"session_id": session_id}
        collection = self._get_collection(provider)
        indexed = collection.get(
            where=kwargs.get("where"), include=["metadatas"]
        ) if kwargs.get("where") else collection.get(include=["metadatas"])
        if not indexed.get("ids", []):
            raise NoDocumentsIndexedError(
                "No documents are indexed for this session and provider"
            )

        query_embedding = get_openai_embeddings(query, openai_client)
        if not query_embedding:
            raise ProviderError(f"{provider.capitalize()} returned an empty embedding")
        kwargs["query_embeddings"] = [query_embedding]
        results = collection.query(**kwargs)

        documents = []
        ids = results.get("ids", [[]])[0]
        retrieved_documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0] or []
        for index, (chunk_id, chunk) in enumerate(zip(ids, retrieved_documents)):
            metadata = metadatas[index] if index < len(metadatas) and metadatas[index] else {}
            documents.append(models.Document(
                id=metadata.get("document_id", chunk_id),
                title=metadata.get("title"),
                content=chunk,
                session_id=metadata.get("session_id"),
                owner_email=metadata.get("owner_email"),
                expires_at=metadata.get("expires_at"),
                similarity=(1 - results.get("distances", [[]])[0][index]
                            if results.get("distances", [[]])[0] else None),
            ))
        return documents

    def get_vectors(self) -> Any:
        """Devuelve los vectores almacenados en la colección."""
        return self.collection.get(include=['embeddings', 'documents', 'metadatas'])

    def delete_document(self, document_id: str) -> int:
        total = 0
        for collection in self._collections.values():
            result = collection.get(where={"document_id": document_id}, include=["metadatas"])
            ids = result.get("ids", [])
            if ids:
                collection.delete(ids=ids)
                total += len(ids)
        return total

    def has_document(self, document_id: str, provider: str = "openai") -> bool:
        result = self._get_collection(provider).get(
            where={"document_id": document_id}, include=["metadatas"]
        )
        return bool(result.get("ids", []))

    def delete_expired_sessions(self) -> int:
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        result = self.collection.get(include=["metadatas"])
        ids = []
        for vector_id, metadata in zip(result.get("ids", []), result.get("metadatas", []) or []):
            raw_expiry = (metadata or {}).get("expires_at")
            try:
                if raw_expiry and datetime.fromisoformat(raw_expiry) <= now:
                    ids.append(vector_id)
            except ValueError:
                continue
        if ids:
            self.collection.delete(ids=ids)
        return len(ids)
