from abc import ABC, abstractmethod
from typing import List, Optional
from server.core import models
from fastapi import Request

class DocumentRepositoryPort(ABC):
    @abstractmethod
    def save_document(self, document: models.Document, content: str, openai_client) -> None:
        pass

    @abstractmethod
    def get_documents(self, query: str, openai_client, n_results: int | None = None) -> List[models.Document]:
        pass

    @abstractmethod
    def get_vectors(self):
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
    def get_document(self, document_id: str) -> models.Document | None:
        pass

    @abstractmethod
    def is_logged_in(self, request: Request) -> bool:
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: str) -> models.User | None:
        pass

    @abstractmethod
    def get_all_users(self) -> List[models.User]:
        pass

    @abstractmethod
    def update_user(self, user: models.User) -> dict | None:
        pass

    @abstractmethod
    def delete_user(self, email: str) -> dict | None:
        pass

    @abstractmethod
    def get_documents(self, n_results: int | None = None) -> List[models.Document]:
        pass

    @abstractmethod
    def delete_document(self, document_id: str) -> dict | None:
        pass

class LlmPort(ABC):
    @abstractmethod
    def generate_text(self, prompt: str, retrieval_context: str) -> str:
        pass