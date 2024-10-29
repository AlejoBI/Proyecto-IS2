import pydantic
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Response, Request
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
    return rag_service.save_document(file)

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

class LoginInput(BaseModel):
    email: str
    password: str

@rag_router.post("/login", status_code=200)
def login_user(user: LoginInput, response: Response,
               user_service: usecases.RAGService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    user_data = user_service.get_user(user.email, user.password)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Guardar el token en la cookie
    response.set_cookie(key="access_token", value=user_data["access_token"], httponly=True, max_age=1800)  # Expira en 30 minutos

    return {
        "status": "Login successful",
        "username": user_data["username"],
        "email": user_data["email"]
    }

@rag_router.get("/checkauth", status_code=200)
def check_auth(request: Request, rag_service: usecases.RAGService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    if not rag_service.is_logged_in(request):
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"status": "Authenticated"}

@rag_router.post("/logout", status_code=200)
def logout_user():
    return {"status": "User logged out successfully"}

