from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response

from server.api import dependencies
from server.api.schemas import LoginInput, UserInput
from server.app import configurations
from server.services.auth_service import AuthService


auth_router = APIRouter()


@auth_router.post("/register", status_code=201)
def register_user(
    user: UserInput,
    user_service: AuthService = Depends(dependencies.get_auth_service),
) -> Dict[str, str]:
    user.role = "user"
    result = user_service.save_user(user)
    if result and result.get("status") == "User already exists":
        raise HTTPException(status_code=400, detail="User already exists")
    return {"status": "User saved successfully"}


@auth_router.post("/login", status_code=200)
def login_user(
    user: LoginInput,
    response: Response,
    user_service: AuthService = Depends(dependencies.get_auth_service),
) -> Dict[str, Any]:
    user_data = user_service.authenticate(user.email, user.password)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if user_data.get("status") == "User is not active":
        raise HTTPException(status_code=403, detail="User is not active")

    configs = configurations.Settings()
    response.set_cookie(
        key="access_token",
        value=user_data["access_token"],
        httponly=True,
        secure=configs.COOKIE_SECURE,
        samesite="lax",
        max_age=1800,
    )
    return {
        "_id": user_data.get("_id", ""),
        "username": user_data.get("username", ""),
        "email": user_data.get("email", ""),
        "role": user_data.get("role", ""),
        "isActive": user_data.get("isActive", ""),
    }


@auth_router.get("/checkauth", status_code=200)
def check_auth(current_user: Optional[dict] = Depends(dependencies.get_optional_user)) -> Dict[str, Any]:
    if not current_user:
        return {"status": "Unauthenticated"}
    return {"status": "Authenticated", "user": current_user}


@auth_router.post("/logout", status_code=200)
def logout_user(response: Response) -> Dict[str, str]:
    response.delete_cookie(key="access_token")
    return {"status": "User logged out successfully"}
