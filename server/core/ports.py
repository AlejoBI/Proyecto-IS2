from abc import ABC, abstractmethod
from typing import List, Optional, Any
from server.core import models
from fastapi import Request


class DocumentRepositoryPort(ABC):
    @abstractmethod
    def save_document(self, document: models.Document, content: str, openai_client: Any) -> None:
        pass

    @abstractmethod
    def get_documents(self, query: str, openai_client: Any, n_results: Optional[int] = None,
                      session_id: Optional[str] = None) -> List[models.Document]:
        pass

    @abstractmethod
    def get_vectors(self) -> Any:
        pass

    @abstractmethod
    def delete_document(self, document_id: str) -> int:
        pass

    @abstractmethod
    def has_document(self, document_id: str, provider: str = "openai") -> bool:
        pass


class MongoDBRepositoryPort(ABC):
    @abstractmethod
    def save_user(self, user: models.User) -> None:
        pass

    @abstractmethod
    def get_user(self, email: str, password: str) -> models.User:
        pass

    @abstractmethod
    def save_document(self, document: models.Document) -> None:
        pass

    @abstractmethod
    def update_document_status(self, document_id: str, status: models.DocumentStatus) -> None:
        pass

    @abstractmethod
    def get_document(self, document_id: str) -> Optional[models.Document]:
        pass

    @abstractmethod
    def get_user_documents(self, email: str) -> List[models.Document]:
        pass

    @abstractmethod
    def get_session_documents(self, session_id: str) -> List[models.Document]:
        pass

    @abstractmethod
    def save_question_history(self, email: str, question: str, answer: str,
                              sources: list[dict], provider: str = "openai") -> None:
        pass

    @abstractmethod
    def get_question_history(self, email: str, limit: int = 50) -> List[dict]:
        pass

    @abstractmethod
    def is_logged_in(self, request: Request) -> bool:
        pass

    @abstractmethod
    def get_all_users(self) -> List[models.User]:
        pass

    @abstractmethod
    def update_user(self, user: models.User) -> Optional[dict]:
        pass

    @abstractmethod
    def delete_user(self, email: str) -> Optional[dict]:
        pass

    @abstractmethod
    def get_documents(self, n_results: Optional[int] = None) -> List[models.Document]:
        pass

    @abstractmethod
    def delete_document(self, document_id: str) -> Optional[dict]:
        pass


class LlmPort(ABC):
    @abstractmethod
    def generate_text(self, prompt: str, retrieval_context: str) -> str:
        pass
