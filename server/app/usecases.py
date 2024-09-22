from core.models import Document
from core import ports


class RAGService:
    def __init__(self, document_repo: ports.DocumentRepositoryPort, openai_adapter: ports.LlmPort):
        self.document_repo = document_repo
        self.openai_adapter = openai_adapter

    def generate_answer(self, query: str) -> str:
        documents = self.document_repo.get_documents(query)
        print(f"Documents: {documents}")
        context = " ".join([doc.content for doc in documents])
        return self.openai_adapter.generate_text(prompt=query, retrieval_context=context)

    def save_document(self, content: str) -> None:
        document = Document(content=content)
        self.document_repo.save_document(document)


class UserService:
    def __init__(self, user_repo: ports.UserRepositoryPort):
        self.user_repo = user_repo

    def register_user(self, user):
        self.user_repo.register_user(user)

    def get_user_by_id(self, user_id: str):
        return self.user_repo.get_user_by_id(user_id)

    def get_users(self, query: str = None):
        return self.user_repo.get_users(query)

    def delete_user(self, user_id: str):
        self.user_repo.delete_user(user_id)