from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from server.adapters.mongodb_adapter import MongoDBAdapter
from server.adapters.chromadb_adapter import ChromaDBAdapter


@dataclass(frozen=True)
class SessionContext:
    id: str
    expires_at: datetime


class SessionService:
    """Coordinates temporary session metadata and periodic data deletion."""

    def __init__(self, mongo: MongoDBAdapter, chroma: ChromaDBAdapter, media_path: str) -> None:
        self.mongo = mongo
        self.chroma = chroma
        self.media_path = media_path

    def create_or_refresh(self, session_id: Optional[str], idle_minutes: int, max_hours: int) -> SessionContext:
        session = self.mongo.get_or_create_session(session_id, idle_minutes, max_hours)
        return SessionContext(id=session["id"], expires_at=session["expires_at"])

    def cleanup_expired(self) -> dict[str, int]:
        expired_documents = self.mongo.delete_expired_documents()
        deleted_vectors = 0
        deleted_files = 0
        for document in expired_documents:
            document_id = document.get("id")
            if document_id:
                deleted_vectors += self.chroma.delete_document(document_id)
            path = document.get("path")
            if path:
                try:
                    from pathlib import Path
                    file_path = Path(path)
                    if file_path.exists() and file_path.is_file():
                        file_path.unlink()
                        deleted_files += 1
                except OSError:
                    pass

        deleted_sessions = self.mongo.delete_expired_sessions()
        self.chroma.delete_expired_sessions()
        return {
            "sessions": deleted_sessions,
            "documents": len(expired_documents),
            "vectors": deleted_vectors,
            "files": deleted_files,
        }
