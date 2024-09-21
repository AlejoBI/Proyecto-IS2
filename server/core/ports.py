from abc import ABC, abstractmethod
from typing import List

from core import models


class DocumentRepositoryPort(ABC):
    @abstractmethod
    def save_document(self, document: models.Document) -> None:
        pass

    @abstractmethod
    def get_documents(self, query: str, n_results: int | None = None) -> List[models.Document]:
        pass

class UserRepositoryPort(ABC):
    @abstractmethod
    def save_user(self, user: models.User) -> None:
        pass

    @abstractmethod
    def get_users(self, query: str = None) -> List[models.User]:
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: str) -> models.User | None:
        pass

    @abstractmethod
    def delete_user(self, user_id: str) -> None:
        pass

class LlmPort(ABC):
    @abstractmethod
    def generate_text(self, prompt: str, retrieval_context: str) -> str:
        pass