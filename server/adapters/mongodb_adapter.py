from abc import ABC
from typing import List
from server.core import ports
from server.core import models
import pymongo as pm
import bcrypt
from server.middlewares import jwt

class MongoDBAdapter(ports.MongoDBRepositoryPort, ABC):
    def __init__(self, uri: str, database: str, users_collection: str, documents_collection: str) -> None:
        self.client = pm.MongoClient(uri)
        self.db = self.client[database]
        self.users = self.db[users_collection]
        self.documents = self.db[documents_collection]

    # User methods --------------------------------
    def save_user(self, user: models.User) -> dict | None:
        self.users.insert_one(user.dict())
        return {
            "username": user.username,
            "email": user.email
        }

    def get_user(self, email: str, password: str) -> dict | None:
        user = self.users.find_one({"email": email})
        if user:
            password_bytes = password.encode()
            hashed_bytes = user["password"].encode()
            if bcrypt.checkpw(password_bytes, hashed_bytes):
                return {
                    "username": user["username"],
                    "email": user["email"]
                }
        return None

    # Document methods --------------------------------
    def save_document(self, document: models.Document) -> None:
        self.documents.insert_one(
            {"document_id": document.id, "tittle": document.tittle, "path": document.path, "content": document.content})

    def get_document(self, document_id: str) -> models.Document | None:
        document = self.documents.find_one({"document_id": document_id})
        if document:
            return models.Document(id=document["document_id"], tittle=document["tittle"],
                                   path=document["path"], content=document["content"])
        return None