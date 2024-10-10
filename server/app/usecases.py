from server.core.models import Document, User
from server.core import ports
from server.helpers.strategies import FileReader
import os
from fastapi import UploadFile


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

    # User methods
    def save_user(self, user) -> None:
        self.mongo_repo.save_user(user)

    def get_user(self, email: str, password: str) -> User:
        return self.mongo_repo.get_user(email, password)

    def get_document(self, id: str) -> Document:
        return self.mongo_repo.get_document(id)

    def get_vectors(self):
        return self.document_repo.get_vectors()
