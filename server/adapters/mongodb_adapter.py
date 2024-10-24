from typing import List
from server.core import ports
from server.core import models
import pymongo as pm
import bcrypt
from server.middlewares.jwt import create_access_token
from datetime import timedelta

class MongoDBAdapter(ports.MongoDBRepositoryPort):
    def __init__(self, uri: str, database: str, users_collection: str, documents_collection: str) -> None:
        self.client = pm.MongoClient(uri)
        self.db = self.client[database]
        self.users = self.db[users_collection]
        self.documents = self.db[documents_collection]

    # User methods --------------------------------
    def save_user(self, user: models.User) -> dict | None:
        # Hashear la contraseña antes de guardarla
        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())

        # Actualizar el modelo de usuario con la contraseña hasheada
        user_dict = user.dict()
        user_dict["password"] = hashed_password.decode('utf-8')

        # Guardar el usuario con la contraseña hasheada en la base de datos
        self.users.insert_one(user_dict)

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
            {"id": document.id, "title": document.title, "path": document.path, "content": document.content})

    def get_document(self, id: str) -> models.Document | None:
        document = self.documents.find_one({"id": id})
        if document:
            return models.Document(id=document["id"], title=document["title"],
                                   path=document["path"], content=document["content"])
        return None