from server.core.models import Document, User
from server.core import ports
from server.helpers.strategies import FileReader
import os
from fastapi import UploadFile
from server.middlewares.jwt import create_access_token
from datetime import timedelta
import bcrypt

class RAGService:
    def __init__(self, document_repo: ports.DocumentRepositoryPort, mongo_repo: ports.MongoDBRepositoryPort, openai_adapter: ports.LlmPort):
        self.document_repo = document_repo
        self.mongo_repo = mongo_repo
        self.openai_adapter = openai_adapter

    # RAG methods
    def generate_answer(self, query: str) -> str:
        documents = self.document_repo.get_documents(query, self.openai_adapter)
        print(f"Documents: {documents}")
        context = " ".join([doc.content for doc in documents])
        return self.openai_adapter.generate_text(prompt=query, retrieval_context=context)

    def save_document(self, file: UploadFile) -> dict:
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
                return {"status": content}  # Devolver mensaje de error específico

            self.mongo_repo.save_document(document)
            self.document_repo.save_document(document, content, self.openai_adapter)

            return {"status": "Document saved successfully"}

        except ValueError as ve:
            return {"status": str(ve)}  # Si el archivo no es soportado, devolver mensaje claro
        except Exception as e:
            return {"status": str(e)}  # Otros errores

    def save_user(self, user: User) -> dict | None:
        try:
            # Llamada al método de guardado del repositorio
            saved_user = self.mongo_repo.save_user(user)
            return saved_user
        except Exception as e:
            print(f"Error in save_user: {e}")
            return None

    def get_user(self, email: str, password: str) -> dict | None:
        try:
            user = self.mongo_repo.get_user(email, password)
            if user:
                # Crear el token de acceso (expira en 30 minutos)
                token_data = {
                    "sub": user["email"],  # Cambiar a user["email"]
                    "username": user["username"]  # Cambiar a user["username"]
                }
                access_token = create_access_token(token_data, expires_delta=timedelta(minutes=30))

                return {
                    "access_token": access_token,
                    "token_type": "bearer",
                    "username": user["username"],  # Cambiar a user["username"]
                    "email": user["email"]  # Cambiar a user["email"]
                }
            return None
        except Exception as e:
            print(f"Error in get_user: {e}")  # Imprimir el error en la consola
            return None

    def get_document(self, id: str) -> Document:
        return self.mongo_repo.get_document(id)

    def get_vectors(self):
        return self.document_repo.get_vectors()
