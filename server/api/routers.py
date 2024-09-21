import pydantic
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app import usecases
from api import dependencies

rag_router = APIRouter()


class DocumentInput(BaseModel):
    content: str = pydantic.Field(..., min_length=1)


@rag_router.post("/generate-answer/", status_code=200)
def generate_answer(query: str,
                    rag_service: usecases.RAGService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    return {"answer": rag_service.generate_answer(query)}


@rag_router.post("/save-document/", status_code=201)
def save_document(document: DocumentInput,
                  rag_service: usecases.RAGService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    rag_service.save_document(content=document.content)
    return {"status": "Document saved successfully"}

class UserInput(BaseModel):
    name: str = pydantic.Field(..., min_length=1)
    email: str = pydantic.Field(..., min_length=1)
    password: str = pydantic.Field(..., min_length=1)
    role: str = pydantic.Field(..., min_length=1)

