from typing import List, Optional, Dict, Any
from server.core import ports
from server.core import models
import pymongo as pm
import bcrypt
from server.middlewares.jwt import validate_token
from fastapi import Request


class MongoDBAdapter(ports.MongoDBRepositoryPort):
    def __init__(self, uri: str, database: str, users_collection: str, documents_collection: str) -> None:
        self.client = pm.MongoClient(uri)
        self.db = self.client[database]
        self.users = self.db[users_collection]
        self.documents = self.db[documents_collection]

    # User methods --------------------------------
    def save_user(self, user: models.User) -> Optional[Dict[str, Any]]:
        # Verificar si el usuario ya existe
        user_found = self.users.find_one({"email": user.email})
        if user_found:
            return {"status": "User already exists"}

        # Hashear la contraseña antes de guardarla
        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())

        # Actualizar el modelo de usuario con la contraseña hasheada y estado "active"
        user_dict = user.dict()
        user_dict["password"] = hashed_password.decode('utf-8')
        user_dict["isActive"] = True

        # Guardar el usuario en la base de datos
        self.users.insert_one(user_dict)

        return {
            "username": user.username,
            "email": user.email,
            "isActive": user.isActive
        }

    def get_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        user = self.users.find_one({"email": email})
        if user:
            password_bytes = password.encode()
            hashed_bytes = user["password"].encode()
            if bcrypt.checkpw(password_bytes, hashed_bytes):
                return {
                    "_id": str(user["_id"]),
                    "username": user["username"],
                    "email": user["email"],
                    "role": user["role"],
                    "isActive": user["isActive"],
                    "password": user["password"]
                }
        return None

    def is_logged_in(self, request: Request) -> bool:
        token = request.cookies.get("access_token")
        if not token:
            return False  # Sin token, el usuario no está autenticado

        # Intenta validar el token
        return validate_token(token)

    def get_all_users(self) -> List[models.User]:
        return list(self.db.users.find())

    def update_user(self, updated_data: models.User) -> Optional[Dict[str, Any]]:
        """Llamar al repositorio para actualizar un usuario."""
        user_dict = updated_data.dict()
        try:
            result = self.db.users.update_one({"email": user_dict.get("email")}, {"$set": user_dict})
            if result.matched_count > 0:
                return {"status": "User updated successfully", "matched_count": result.matched_count}
            else:
                return {"status": "User not found"}
        except Exception as e:
            print(f"Error in update_user: {e}")
            return {"status": "Error updating user"}

    def delete_user(self, email: str) -> Optional[Dict[str, Any]]:
        """Eliminar un usuario por email."""
        result = self.users.delete_one({"email": email})
        if result.deleted_count > 0:
            return {"status": "User deleted"}
        return {"status": "User not found"}

    # Document methods --------------------------------
    def get_documents(self, n_results: Optional[int] = None) -> List[models.Document]:
        if n_results:
            documents = self.db.documents.find().limit(n_results)
        else:
            documents = self.db.documents.find()
        return [models.Document(id=document["id"], title=document["title"], path=document["path"],
                                content=document["content"]) for document in documents]

    def save_document(self, document: models.Document) -> None:
        self.documents.insert_one(
            {"id": document.id, "title": document.title, "path": document.path, "content": document.content})

    def get_document(self, id: str) -> Optional[models.Document]:
        document = self.documents.find_one({"id": id})
        if document:
            return models.Document(id=document["id"], title=document["title"],
                                   path=document["path"], content=document["content"])
        return None

    def delete_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        result = self.documents.delete_one({"id": document_id})
        if result.deleted_count > 0:
            return {"status": "Document deleted"}
        return {"status": "Document not found"}
