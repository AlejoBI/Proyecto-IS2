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
    isActive: bool = True


@rag_router.post("/register", status_code=201)
def register_user(user: UserInput,
                  user_service: usecases.RAGService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    result = user_service.save_user(user)
    if result and result.get("status") == "User already exists":
        raise HTTPException(status_code=400, detail="User already exists")
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
    if "access_token" in user_data:
        response.set_cookie(key="access_token", value=user_data["access_token"], httponly=True,
                            max_age=1800)  # Expira en 30 minutos

    return {
        "_id": user_data.get("_id", ""),
        "username": user_data.get("username", ""),
        "email": user_data.get("email", ""),
        "role": user_data.get("role", ""),
        "isActive": user_data.get("isActive", ""),
        "password": user_data.get("password", "")
    }


@rag_router.get("/checkauth", status_code=200)
def check_auth(request: Request,
               rag_service: usecases.RAGService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    if not rag_service.is_logged_in(request):
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"status": "Authenticated"}


@rag_router.post("/logout", status_code=200)
def logout_user(response: Response):
    # Eliminar la cookie del token
    response.delete_cookie(key="access_token")
    return {"status": "User logged out successfully"}


@rag_router.get("/admin/get-users", status_code=200)
def admin_get_users(rag_service: usecases.RAGService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    users = rag_service.get_all_users()
    # Convertir ObjectId a string
    for user in users:
        user["_id"] = str(user["_id"])
    return users


@rag_router.post("/admin/save-user", status_code=201)
def admin_save_user(user: UserInput,
                    rag_service: usecases.RAGService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    saved_user = rag_service.save_user(user)
    if saved_user:
        return {"status": "User saved successfully", "user": saved_user}
    raise HTTPException(status_code=400, detail="Error saving user")


@rag_router.put("/admin/update-user", status_code=200)
def admin_update_user(updated_data: UserInput,
                      rag_service: usecases.RAGService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    UpdateResult = rag_service.update_user(updated_data)
    if UpdateResult.modified_count > 0:
        return {"status": "User updated successfully"}
    elif UpdateResult.matched_count == 0:
        return {"status": "User not found"}
    else:
        return {"status": "No changes made to the user"}


@rag_router.delete("/admin/delete-user", status_code=200)
def admin_delete_user(
        email: str,
        rag_service: usecases.RAGService = Depends(dependencies.RAGServiceSingleton.get_instance)
):
    result = rag_service.delete_user(email)
    if result["status"] == "User deleted":
        return {"status": "User deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")


@rag_router.get("/admin/get-documents", status_code=200)
def admin_get_documents(rag_service: usecases.RAGService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    documents = rag_service.get_documents()
    return documents


@rag_router.delete("/admin/delete-document", status_code=200)
def admin_delete_document(document_id: str,
                          rag_service: usecases.RAGService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    result = rag_service.delete_document(document_id)
    if result["status"] == "Document deleted":
        return {"status": "Document deleted successfully"}
    raise HTTPException(status_code=404, detail="Document not found")
