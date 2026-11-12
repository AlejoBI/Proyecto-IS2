from typing import List, Optional, Dict, Any
from server.core.models import Document, DocumentStatus, User
from server.core import ports
from server.helpers.strategies import FileReader
import os
import hashlib
import logging
from time import perf_counter
from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile, Request
from server.middlewares.jwt import create_access_token
from datetime import timedelta, datetime, timezone


logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self, document_repo: ports.DocumentRepositoryPort, mongo_repo: ports.MongoDBRepositoryPort,
                 openai_adapter: ports.LlmPort) -> None:
        self.document_repo = document_repo
        self.mongo_repo = mongo_repo
        self.openai_adapter = openai_adapter

    # RAG methods
    def generate_answer(self, query: str, session_id: Optional[str] = None) -> str:
        if session_id:
            documents = self.document_repo.get_documents(query, self.openai_adapter,
                                                          session_id=session_id)
        else:
            documents = self.document_repo.get_documents(query, self.openai_adapter)
        context = "\n\n---\n\n".join(
            doc.content for doc in documents if doc.content is not None
        )
        return self.openai_adapter.generate_text(prompt=query, retrieval_context=context)

    def generate_answer_with_sources(self, query: str, session_id: str,
                                     owner_email: Optional[str] = None,
                                     provider: str = "openai") -> Dict[str, Any]:
        started_at = perf_counter()
        self._ensure_documents_indexed(session_id, owner_email, provider)
        if owner_email:
            if provider == "openai":
                documents = self.document_repo.get_documents(
                    query, self.openai_adapter, session_id=session_id, owner_email=owner_email
                )
            else:
                documents = self.document_repo.get_documents(
                    query, self.openai_adapter, session_id=session_id,
                    owner_email=owner_email, provider=provider
                )
        else:
            if provider == "openai":
                documents = self.document_repo.get_documents(
                    query, self.openai_adapter, session_id=session_id
                )
            else:
                documents = self.document_repo.get_documents(
                    query, self.openai_adapter, session_id=session_id, provider=provider
                )
        context = "\n\n---\n\n".join(
            doc.content for doc in documents if doc.content is not None
        )
        answer = self.openai_adapter.generate_text(prompt=query, retrieval_context=context)
        result = {
            "answer": answer,
            "sources": [
                {"document_id": doc.id, "title": doc.title, "similarity": doc.similarity}
                for doc in documents
            ],
        }
        if provider != "openai":
            result["provider"] = provider
        if owner_email:
            if provider == "openai":
                self.mongo_repo.save_question_history(owner_email, query, answer, result["sources"])
            else:
                self.mongo_repo.save_question_history(
                    owner_email, query, answer, result["sources"], provider=provider
                )
        logger.info(
            "rag.answer.completed provider=%s sources=%d duration_ms=%.2f authenticated=%s",
            provider,
            len(result["sources"]),
            (perf_counter() - started_at) * 1000,
            bool(owner_email),
        )
        return result

    def _ensure_documents_indexed(self, session_id: str, owner_email: Optional[str],
                                  provider: str) -> None:
        documents = (self.mongo_repo.get_user_documents(owner_email)
                     if owner_email else self.mongo_repo.get_session_documents(session_id))
        for document in documents:
            if document.status != DocumentStatus.COMPLETED or not document.content:
                continue
            if self.document_repo.has_document(document.id, provider):
                continue
            if provider == "openai":
                self.document_repo.save_document(document, document.content, self.openai_adapter)
            else:
                self.document_repo.save_document(
                    document, document.content, self.openai_adapter, provider=provider
                )

    def save_document(self, file: UploadFile, session_id: Optional[str] = None,
                      expires_at: Optional[datetime] = None,
                      max_file_size: Optional[int] = None,
                       checksum: Optional[str] = None,
                       owner_email: Optional[str] = None,
                       provider: str = "openai") -> Dict[str, str]:
        started_at = perf_counter()
        # Obtener el nombre del archivo
        file_name = Path(file.filename or "document.txt").name

        # Crear la carpeta 'media' si no existe
        media_root = Path(os.getenv("MEDIA_PATH", "media"))
        target_dir = media_root / "sessions" / session_id if session_id else media_root
        target_dir.mkdir(parents=True, exist_ok=True)

        # Guardar el archivo en la carpeta 'media'
        file_path = target_dir / f"{uuid4()}-{file_name}"
        payload = file.file.read((max_file_size or 2**31 - 1) + 1)
        if max_file_size is not None and len(payload) > max_file_size:
            return {"status": "File exceeds the maximum allowed size"}
        with open(file_path, "wb") as f:
            f.write(payload)

        # Crear el modelo del documento con valores iniciales
        document = Document(title=file_name, path=str(file_path), session_id=session_id,
                            owner_email=owner_email,
                            expires_at=expires_at.isoformat() if expires_at else None,
                            checksum=checksum or hashlib.sha256(payload).hexdigest(),
                            size_bytes=len(payload), provider=provider,
                            status=DocumentStatus.PROCESSING)

        # strategies
        try:
            content = FileReader(document.path).read_file()
            if isinstance(content, str) and (
                    content.startswith("File not found") or
                    content.startswith("An error occurred")):
                file_path.unlink(missing_ok=True)
                return {"status": content}

            self.mongo_repo.save_document(document)
            try:
                if provider == "openai":
                    self.document_repo.save_document(document, content, self.openai_adapter)
                else:
                    self.document_repo.save_document(
                        document, content, self.openai_adapter, provider=provider
                    )
                self.mongo_repo.update_document_status(document.id, DocumentStatus.COMPLETED)
            except Exception:
                self.mongo_repo.update_document_status(document.id, DocumentStatus.FAILED)
                delete_vector = getattr(self.document_repo, "delete_document", None)
                if delete_vector:
                    delete_vector(document.id)
                raise

            document.status = DocumentStatus.COMPLETED
            result = {"status": "Document saved successfully"}
            if session_id:
                result["document_id"] = document.id
            logger.info(
                "rag.document.completed provider=%s document_id=%s duration_ms=%.2f",
                provider,
                document.id,
                (perf_counter() - started_at) * 1000,
            )
            return result

        except ValueError as ve:
            file_path.unlink(missing_ok=True)
            return {"status": str(ve)}
        except Exception as e:
            file_path.unlink(missing_ok=True)
            logger.warning(
                "rag.document.failed provider=%s duration_ms=%.2f error_type=%s",
                provider,
                (perf_counter() - started_at) * 1000,
                type(e).__name__,
            )
            return {"status": str(e)}

    def save_user(self, user: User) -> Optional[Dict[str, Any]]:
        try:
            result = self.mongo_repo.save_user(user)
            return result
        except Exception as e:
            logger.exception("Unable to save user")
            return None

    def get_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        try:
            user = self.mongo_repo.get_user(email, password)
            if user:
                if not user.get("isActive", False):
                    return {"status": "User is not active"}

                token_data = {
                    "sub": user["email"],
                    "username": user["username"],
                    "role": user.get("role", "user"),
                }
                access_token = create_access_token(token_data, expires_delta=timedelta(minutes=30))

                return {
                    "access_token": access_token,
                    "token_type": "bearer",
                    "_id": str(user.get("_id", "")),
                    "username": user["username"],
                    "email": user["email"],
                    "role": user.get("role", ""),
                    "isActive": user["isActive"]
                }
            return None
        except Exception as e:
            logger.exception("Unable to authenticate user")
            return None

    def is_logged_in(self, request: Request) -> bool:
        return self.mongo_repo.is_logged_in(request)

    def get_all_users(self) -> List[User]:
        return self.mongo_repo.get_all_users()

    def update_user(self, user: User) -> Optional[Dict[str, Any]]:
        """Actualizar un usuario por email."""
        user_dict = user.model_dump()
        try:
            result = self.mongo_repo.users.update_one({"email": user_dict.get("email")}, {"$set": user_dict})
            return result.raw_result
        except Exception as e:
            print(f"Error in update_user: {e}")
            return None

    def delete_user(self, email: str) -> Optional[Dict[str, Any]]:
        """Eliminar un usuario por su email."""
        try:
            return self.mongo_repo.delete_user(email)
        except Exception as e:
            print(f"Error in delete_user: {e}")
            return None

    def get_documents(self, n_results: Optional[int] = None) -> List[Document]:
        return self.mongo_repo.get_documents(n_results)

    def get_document(self, id: str) -> Optional[Document]:
        return self.mongo_repo.get_document(id)

    def get_vectors(self) -> Any:
        return self.document_repo.get_vectors()

    def delete_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        try:
            return self.mongo_repo.delete_document(document_id)
        except Exception as e:
            print(f"Error in delete_document: {e}")
            return None
