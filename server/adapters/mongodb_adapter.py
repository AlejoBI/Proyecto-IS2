from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from uuid import uuid4
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
        self.sessions = self.db["rag_sessions"]
        self.audit_events = self.db["audit_events"]
        self.question_history = self.db["question_history"]
        self.sessions.create_index("expires_at", expireAfterSeconds=0)
        self.audit_events.create_index("created_at")
        self.documents.create_index([("session_id", 1), ("checksum", 1)], unique=True,
                                    partialFilterExpression={"checksum": {"$type": "string"}})
        self.documents.create_index([("owner_email", 1), ("created_at", -1)])
        self.question_history.create_index([("owner_email", 1), ("created_at", -1)])

    @staticmethod
    def _expiry_as_string(value: Any) -> Optional[str]:
        if value is None:
            return None
        return value.isoformat() if hasattr(value, "isoformat") else str(value)

    # User methods --------------------------------
    def save_user(self, user: models.User) -> Optional[Dict[str, Any]]:
        # Verificar si el usuario ya existe
        user_found = self.users.find_one({"email": user.email})
        if user_found:
            return {"status": "User already exists"}

        # Hashear la contraseña antes de guardarla
        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())

        # Actualizar el modelo de usuario con la contraseña hasheada y estado "active"
        user_dict = user.model_dump()
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
                    "isActive": user["isActive"]
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
        user_dict = updated_data.model_dump(exclude_none=True)
        user_dict.pop("password", None)
        try:
            if updated_data.password:
                user_dict["password"] = bcrypt.hashpw(
                    updated_data.password.encode("utf-8"), bcrypt.gensalt()
                ).decode("utf-8")
            result = self.db.users.update_one({"email": user_dict.get("email")}, {"$set": user_dict})
            if result.matched_count > 0:
                return {
                    "status": "User updated successfully",
                    "matched_count": result.matched_count,
                    "modified_count": result.modified_count,
                }
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
        return [models.Document(id=document["id"], title=document["title"], path=document.get("path"),
                                content=document.get("content"), session_id=document.get("session_id"),
                                owner_email=document.get("owner_email"),
                                expires_at=self._expiry_as_string(document.get("expires_at")),
                                checksum=document.get("checksum"), size_bytes=document.get("size_bytes"),
                                provider=document.get("provider"),
                                indexed_providers=document.get("indexed_providers", []),
                                created_at=self._expiry_as_string(document.get("created_at")),
                                status=document.get("status", "completed"))
                for document in documents]

    def save_document(self, document: models.Document) -> None:
        expires_at = document.expires_at
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
        self.documents.insert_one(
            {"id": document.id, "title": document.title, "path": document.path, "content": document.content,
             "session_id": document.session_id, "expires_at": expires_at,
             "checksum": document.checksum, "size_bytes": document.size_bytes,
             "provider": document.provider, "status": document.status.value,
             "indexed_providers": document.indexed_providers or ([document.provider]
                                                                  if document.provider else []),
             "owner_email": document.owner_email,
             "created_at": datetime.now(timezone.utc)})

    def update_document_status(self, document_id: str, status: models.DocumentStatus) -> None:
        self.documents.update_one({"id": document_id}, {"$set": {"status": status.value}})

    def document_exists(self, session_id: str, checksum: str) -> bool:
        document = self.documents.find_one(
            {"session_id": session_id, "checksum": checksum},
            {"_id": 1, "status": 1},
        )
        if not document:
            return False

        # A failed processing attempt must not block a retry. The unique index
        # on session/checksum requires removing the failed record before the
        # next upload can create its new document record.
        if document.get("status") == models.DocumentStatus.FAILED.value:
            self.documents.delete_one({"_id": document["_id"]})
            return False

        return True

    def get_document(self, id: str) -> Optional[models.Document]:
        document = self.documents.find_one({"id": id})
        if document:
            return models.Document(id=document["id"], title=document["title"],
                                   path=document["path"], content=document["content"],
                                   session_id=document.get("session_id"),
                                   owner_email=document.get("owner_email"),
                                   expires_at=self._expiry_as_string(document.get("expires_at")),
                                   checksum=document.get("checksum"), size_bytes=document.get("size_bytes"),
                                   provider=document.get("provider"),
                                   indexed_providers=document.get("indexed_providers", []),
                                   created_at=self._expiry_as_string(document.get("created_at")),
                                   status=document.get("status", "completed"))
        return None

    def get_user_documents(self, email: str) -> List[models.Document]:
        documents = self.documents.find({"owner_email": email}).sort("created_at", -1)
        return [models.Document(
            id=document["id"], title=document.get("title"), path=document.get("path"),
            content=document.get("content"), session_id=document.get("session_id"),
            owner_email=document.get("owner_email"),
            expires_at=self._expiry_as_string(document.get("expires_at")),
            checksum=document.get("checksum"), size_bytes=document.get("size_bytes"),
            provider=document.get("provider"),
            indexed_providers=document.get("indexed_providers", []),
            created_at=self._expiry_as_string(document.get("created_at")),
            status=document.get("status", "completed"),
        ) for document in documents]

    def get_session_documents(self, session_id: str) -> List[models.Document]:
        documents = self.documents.find({"session_id": session_id})
        return [models.Document(
            id=document["id"], title=document.get("title"), path=document.get("path"),
            content=document.get("content"), session_id=document.get("session_id"),
            owner_email=document.get("owner_email"),
            expires_at=self._expiry_as_string(document.get("expires_at")),
            checksum=document.get("checksum"), size_bytes=document.get("size_bytes"),
            provider=document.get("provider"),
            indexed_providers=document.get("indexed_providers", []),
            created_at=self._expiry_as_string(document.get("created_at")),
            status=document.get("status", "completed"),
        ) for document in documents]

    def add_document_provider(self, document_id: str, provider: str) -> None:
        self.documents.update_one(
            {"id": document_id},
            {"$addToSet": {"indexed_providers": provider}},
        )

    def save_question_history(self, email: str, question: str, answer: str,
                              sources: list[dict], provider: str = "openai") -> None:
        self.question_history.insert_one({
            "owner_email": email,
            "question": question,
            "answer": answer,
            "sources": sources,
            "provider": provider,
            "created_at": datetime.now(timezone.utc),
        })

    def get_question_history(self, email: str, limit: int = 50) -> List[dict]:
        history = self.question_history.find(
            {"owner_email": email}, {"_id": 0, "owner_email": 0}
        ).sort("created_at", -1).limit(limit)
        return [
            {**item, "created_at": self._expiry_as_string(item.get("created_at"))}
            for item in history
        ]

    def delete_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        result = self.documents.delete_one({"id": document_id})
        if result.deleted_count > 0:
            return {"status": "Document deleted"}
        return {"status": "Document not found"}

    # Temporary public-demo session methods -------------------------------
    def get_or_create_session(self, session_id: Optional[str], idle_minutes: int,
                              max_hours: int) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        if session_id:
            existing = self.sessions.find_one({"id": session_id})
            existing_expires = existing.get("expires_at") if existing else None
            if existing_expires and existing_expires.tzinfo is None:
                existing_expires = existing_expires.replace(tzinfo=timezone.utc)
            existing_created = existing.get("created_at") if existing else None
            if existing_created and existing_created.tzinfo is None:
                existing_created = existing_created.replace(tzinfo=timezone.utc)
            if existing and existing_expires and existing_expires > now:
                expires_at = min(now + timedelta(minutes=idle_minutes),
                                 existing_created + timedelta(hours=max_hours))
                self.sessions.update_one({"id": session_id}, {"$set": {
                    "last_activity": now, "expires_at": expires_at,
                }})
                existing["expires_at"] = expires_at
                return existing

        new_session = {
            "id": str(uuid4()),
            "created_at": now,
            "last_activity": now,
            "expires_at": now + timedelta(minutes=idle_minutes),
            "document_count": 0,
            "storage_used": 0,
            "question_count": 0,
        }
        self.sessions.insert_one(new_session)
        return new_session

    def reserve_document_slot(self, session_id: str, file_size: int,
                              max_documents: int, max_storage: int) -> bool:
        result = self.sessions.update_one(
            {"id": session_id, "document_count": {"$lt": max_documents},
             "$expr": {"$lte": [{"$add": ["$storage_used", file_size]}, max_storage]}},
            {"$inc": {"document_count": 1, "storage_used": file_size},
             "$set": {"last_activity": datetime.now(timezone.utc)}})
        return result.modified_count == 1

    def increment_question_count(self, session_id: str, max_questions: int) -> bool:
        result = self.sessions.update_one(
            {"id": session_id, "question_count": {"$lt": max_questions}},
            {"$inc": {"question_count": 1},
             "$set": {"last_activity": datetime.now(timezone.utc)}})
        return result.modified_count == 1

    def delete_expired_documents(self) -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        documents = list(self.documents.find({"expires_at": {"$lte": now}}))
        if documents:
            self.documents.delete_many({"_id": {"$in": [doc["_id"] for doc in documents]}})
        return documents

    def delete_expired_sessions(self) -> int:
        result = self.sessions.delete_many({"expires_at": {"$lte": datetime.now(timezone.utc)}})
        return result.deleted_count

    def record_audit_event(self, actor: str, action: str, target: str) -> None:
        self.audit_events.insert_one({
            "actor": actor,
            "action": action,
            "target": target,
            "created_at": datetime.now(timezone.utc),
        })
