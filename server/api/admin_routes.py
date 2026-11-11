from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException

from server.api import dependencies
from server.api.schemas import UserInput, UserUpdateInput
from server.app import usecases
from server.services.admin_service import AdminService


admin_router = APIRouter()


def _audit(admin: dict, action: str, target: str) -> None:
    mongo, _, _, _ = dependencies.InfrastructureSingleton.get()
    try:
        mongo.record_audit_event(admin.get("sub", "unknown"), action, target)
    except Exception:
        # Auditing must not make a successful administrative action fail.
        pass


@admin_router.get("/admin/get-users", status_code=200)
def admin_get_users(
    _admin: dict = Depends(dependencies.require_admin),
    rag_service: AdminService = Depends(dependencies.get_admin_service),
) -> List[Dict[str, Any]]:
    users = rag_service.get_all_users()
    for user in users:
        user["_id"] = str(user["_id"])
        user.pop("password", None)
    return users


@admin_router.post("/admin/save-user", status_code=201)
def admin_save_user(
    user: UserInput,
    _admin: dict = Depends(dependencies.require_admin),
    rag_service: AdminService = Depends(dependencies.get_admin_service),
) -> Dict[str, Any]:
    saved_user = rag_service.save_user(user)
    if saved_user:
        _audit(_admin, "create_user", user.email)
        return {"status": "User saved successfully", "user": saved_user}
    raise HTTPException(status_code=400, detail="Error saving user")


@admin_router.put("/admin/update-user", status_code=200)
def admin_update_user(
    updated_data: UserUpdateInput,
    _admin: dict = Depends(dependencies.require_admin),
    rag_service: AdminService = Depends(dependencies.get_admin_service),
) -> Dict[str, str]:
    update_result = rag_service.update_user(updated_data)
    if update_result.get("modified_count", 0) > 0:
        _audit(_admin, "update_user", updated_data.email)
        return {"status": "User updated successfully"}
    if update_result.get("matched_count", 0) == 0:
        return {"status": "User not found"}
    return {"status": "No changes made to the user"}


@admin_router.delete("/admin/delete-user", status_code=200)
def admin_delete_user(
    email: str,
    _admin: dict = Depends(dependencies.require_admin),
    rag_service: AdminService = Depends(dependencies.get_admin_service),
) -> Dict[str, str]:
    result = rag_service.delete_user(email)
    if result["status"] == "User deleted":
        _audit(_admin, "delete_user", email)
        return {"status": "User deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")


@admin_router.get("/admin/get-documents", status_code=200)
def admin_get_documents(
    _admin: dict = Depends(dependencies.require_admin),
    rag_service: AdminService = Depends(dependencies.get_admin_service),
) -> List[Dict[str, Any]]:
    return [document.model_dump() for document in rag_service.get_documents()]


@admin_router.delete("/admin/delete-document", status_code=200)
def admin_delete_document(
    document_id: str,
    _admin: dict = Depends(dependencies.require_admin),
    rag_service: AdminService = Depends(dependencies.get_admin_service),
) -> Dict[str, str]:
    result = rag_service.delete_document(document_id)
    if result["status"] == "Document deleted":
        _audit(_admin, "delete_document", document_id)
        return {"status": "Document deleted successfully"}
    raise HTTPException(status_code=404, detail="Document not found")
