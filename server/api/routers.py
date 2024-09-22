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

@rag_router.post("/register", status_code=201)
def register_user(user: UserInput,
              user_service: usecases.UserService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    user_service.register_user(user)
    return {"status": "User saved successfully"}

@rag_router.post("/login", status_code=200)
def login_user(user: UserInput,
               user_service: usecases.UserService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    return user_service.login_user(user)

@rag_router.post("/logout", status_code=200)
def logout_user():
    return {"status": "User logged out successfully"}

@rag_router.get("/check-auth", status_code=200)
def check_auth(user_service: usecases.UserService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    return user_service.check_auth()

@rag_router.get("/get-users", status_code=200)
def get_users(query: str = None,
              user_service: usecases.UserService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    return user_service.get_users(query)

@rag_router.get("/get-user/{user_id}", status_code=200)
def get_user(user_id: str,
             user_service: usecases.UserService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    return user_service.get_user_by_id(user_id)

@rag_router.put("/update-user/{user_id}", status_code=200)
def update_user(user_id: str, user: UserInput,
                user_service: usecases.UserService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    user_service.update_user_by_id(user_id, user)
    return {"status": "User updated successfully"}

@rag_router.delete("/delete-user/{user_id}", status_code=204)
def delete_user(user_id: str,
                user_service: usecases.UserService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    user_service.delete_user(user_id)
    return {"status": "User deleted successfully"}
    