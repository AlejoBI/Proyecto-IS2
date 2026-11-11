from typing import Any, Dict, List, Optional

from server.core import models, ports


class AdminService:
    def __init__(self, repository: ports.MongoDBRepositoryPort) -> None:
        self.repository = repository

    def get_all_users(self) -> List[models.User]:
        return self.repository.get_all_users()

    def save_user(self, user: models.User) -> Optional[Dict[str, Any]]:
        return self.repository.save_user(user)

    def update_user(self, user: models.User) -> Optional[Dict[str, Any]]:
        return self.repository.update_user(user)

    def delete_user(self, email: str) -> Optional[Dict[str, Any]]:
        return self.repository.delete_user(email)

    def get_documents(self) -> List[models.Document]:
        return self.repository.get_documents()

    def get_document(self, document_id: str) -> Optional[models.Document]:
        return self.repository.get_document(document_id)

    def delete_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        return self.repository.delete_document(document_id)
