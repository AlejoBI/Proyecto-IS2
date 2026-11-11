from fastapi import APIRouter

from server.api.admin_routes import admin_router
from server.api.auth_routes import auth_router
from server.api.rag_routes import rag_router as public_rag_router


# Compatibility registry: existing imports can continue using rag_router while
# each bounded context remains implemented in its own module.
rag_router = APIRouter()
rag_router.include_router(public_rag_router)
rag_router.include_router(auth_router)
rag_router.include_router(admin_router)
