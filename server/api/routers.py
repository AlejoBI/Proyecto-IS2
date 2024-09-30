import pydantic
from fastapi import APIRouter, Depends, UploadFile, File
from pydantic import BaseModel
from server.app import usecases
from server.api import dependencies

rag_router = APIRouter()


class DocumentInput(BaseModel):
    content: str = pydantic.Field(..., min_length=1)

@rag_router.get("/generate-answer", status_code=201)
def generate_answer(query: str,
                    rag_service: usecases.RAGService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    return rag_service.generate_answer(query)

@rag_router.post("/save-document", status_code=201)
def save_document(file: UploadFile = File(...),
                        rag_service: usecases.RAGService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    # Guardar la información del archivo en MongoDB
    rag_service.save_document(file)
    return {"status": "Document saved successfully"}

@rag_router.get("/get-document")
def get_document(document_id: str,
                 rag_service: usecases.RAGService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    document = rag_service.get_document(document_id)
    if document:
        return document
    return {"status": "Document not found"}

@rag_router.get("/get-vectors", status_code=201)
def get_vectors(rag_service: usecases.RAGService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    return rag_service.get_vectors()

class UserInput(BaseModel):
    username: str = pydantic.Field(..., min_length=1)
    email: str = pydantic.Field(..., min_length=1)
    password: str = pydantic.Field(..., min_length=1)
    role: str = pydantic.Field(..., min_length=1)


@rag_router.post("/register", status_code=201)
def register_user(user: UserInput,
                  user_service: usecases.RAGService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    user_service.save_user(user)
    return {"status": "User saved successfully"}

@rag_router.post("/login", status_code=200)
def login_user(email: str, password: str,
               user_service: usecases.RAGService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    return user_service.get_user(email, password)

@rag_router.post("/logout", status_code=200)
def logout_user():
    return {"status": "User logged out successfully"}

