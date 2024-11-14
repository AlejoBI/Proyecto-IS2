from typing import List, Optional, Dict, Any
from server.core.models import Document, User
from server.core import ports
from server.helpers.strategies import FileReader
import os
from fastapi import UploadFile, Request
from server.middlewares.jwt import create_access_token
from datetime import timedelta


class RAGService:
    def __init__(self, document_repo: ports.DocumentRepositoryPort, mongo_repo: ports.MongoDBRepositoryPort,
                 openai_adapter: ports.LlmPort) -> None:
        self.document_repo = document_repo
        self.mongo_repo = mongo_repo
        self.openai_adapter = openai_adapter

    # RAG methods
    def generate_answer(self, query: str) -> str:
        documents = self.document_repo.get_documents(query, self.openai_adapter)
        print(f"Documents: {documents}")
        context = " ".join([doc.content for doc in documents if doc.content is not None])
        return self.openai_adapter.generate_text(prompt=query, retrieval_context=context)

    def save_document(self, file: UploadFile) -> Dict[str, str]:
        # Obtener el nombre del archivo
        file_name = file.filename

        # Crear la carpeta 'media' si no existe
        os.makedirs('media', exist_ok=True)

        # Guardar el archivo en la carpeta 'media'
        file_path = os.path.join('media', file_name)
        with open(file_path, 'wb') as f:
            f.write(file.file.read())

        # Crear el modelo del documento con valores iniciales
        document = Document(title=file_name, path=file_path)

        # strategies
        try:
            content = FileReader(document.path).read_file()
            if isinstance(content, str) and content.startswith("File not found") or content.startswith(
                    "An error occurred"):
                return {"status": content}

            self.mongo_repo.save_document(document)
            self.document_repo.save_document(document, content, self.openai_adapter)

            return {"status": "Document saved successfully"}

        except ValueError as ve:
            return {"status": str(ve)}
        except Exception as e:
            return {"status": str(e)}

    def save_user(self, user: User) -> Optional[Dict[str, Any]]:
        try:
            self.mongo_repo.save_user(user)
            return user.dict()
        except Exception as e:
            print(f"Error in save_user: {e}")
            return None

    def get_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        try:
            user = self.mongo_repo.get_user(email, password)
            if user:
                if not user.get("isActive", False):
                    return {"status": "User is not active"}

                token_data = {
                    "sub": user["email"],
                    "username": user["username"]
                }
                access_token = create_access_token(token_data, expires_delta=timedelta(minutes=30))

                return {
                    "access_token": access_token,
                    "token_type": "bearer",
                    "_id": str(user.get("_id", "")),
                    "username": user["username"],
                    "email": user["email"],
                    "role": user.get("role", ""),
                    "isActive": user["isActive"],
                    "password": user["password"]
                }
            return None
        except Exception as e:
            print(f"Error in get_user: {e}")
            return None

    def is_logged_in(self, request: Request) -> bool:
        return self.mongo_repo.is_logged_in(request)

    def get_all_users(self) -> List[User]:
        return self.mongo_repo.get_all_users()

    def update_user(self, user: User) -> Optional[Dict[str, Any]]:
        """Actualizar un usuario por email."""
        user_dict = user.dict()
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
