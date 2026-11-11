from datetime import timedelta
from typing import Any, Dict, Optional

from fastapi import Request

from server.core import models, ports
from server.middlewares.jwt import create_access_token


class AuthService:
    def __init__(self, repository: ports.MongoDBRepositoryPort) -> None:
        self.repository = repository

    def save_user(self, user: models.User) -> Optional[Dict[str, Any]]:
        return self.repository.save_user(user)

    def authenticate(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        user = self.repository.get_user(email, password)
        if not user:
            return None
        if not user.get("isActive", False):
            return {"status": "User is not active"}
        token_data = {
            "sub": user["email"],
            "username": user["username"],
            "role": user.get("role", "user"),
        }
        return {
            "access_token": create_access_token(token_data, expires_delta=timedelta(minutes=30)),
            "token_type": "bearer",
            "_id": str(user.get("_id", "")),
            "username": user["username"],
            "email": user["email"],
            "role": user.get("role", ""),
            "isActive": user["isActive"],
        }

    def is_logged_in(self, request: Request) -> bool:
        return self.repository.is_logged_in(request)
