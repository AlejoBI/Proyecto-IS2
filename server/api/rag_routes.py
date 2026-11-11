import hashlib
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from starlette.concurrency import run_in_threadpool

from server.api import dependencies
from server.api.schemas import AnswerResponse, DocumentOperationResponse
from server.core.models import DocumentStatus
from server.app import configurations, usecases
from server.services.sessions import SessionContext


rag_router = APIRouter()


@rag_router.get("/session", status_code=200)
def create_session(session: SessionContext = Depends(dependencies.get_session_context)) -> Dict[str, Any]:
    configs = configurations.Settings()
    return {
        "session_id": session.id,
        "expires_at": session.expires_at.isoformat(),
        "limits": {
            "max_file_size_bytes": configs.MAX_FILE_SIZE_BYTES,
            "max_documents": configs.MAX_DOCUMENTS_PER_SESSION,
            "max_questions": configs.MAX_QUESTIONS_PER_SESSION,
        },
    }


@rag_router.get("/generate-answer", status_code=200)
def generate_answer(
    query: str,
    session: SessionContext = Depends(dependencies.get_rate_limit),
    rag_service: usecases.RAGService = Depends(dependencies.get_rag_service),
    current_user: Optional[dict] = Depends(dependencies.get_optional_user),
) -> AnswerResponse:
    configs = configurations.Settings()
    if len(query) > configs.MAX_QUERY_LENGTH:
        raise HTTPException(status_code=413, detail="Question is too long")
    _, _, sessions, _ = dependencies.InfrastructureSingleton.get()
    if not sessions.mongo.increment_question_count(session.id, configs.MAX_QUESTIONS_PER_SESSION):
        raise HTTPException(status_code=429, detail="The question limit for this session was reached")
    try:
        owner_email = current_user.get("sub") if current_user else None
        provider = rag_service.openai_adapter.provider
        return rag_service.generate_answer_with_sources(
            query, session_id=session.id, owner_email=owner_email, provider=provider
        )
    except Exception:
        raise HTTPException(status_code=502,
                            detail="OpenAI request failed. Verify your key and try again.") from None


@rag_router.post("/save-document", status_code=201, response_model=DocumentOperationResponse)
async def save_document(
    file: UploadFile = File(...),
    session: SessionContext = Depends(dependencies.get_rate_limit),
    rag_service: usecases.RAGService = Depends(dependencies.get_rag_service),
    current_user: Optional[dict] = Depends(dependencies.get_optional_user),
) -> Dict[str, str]:
    configs = configurations.Settings()
    extension = Path(file.filename or "").suffix.lower()
    allowed_extensions = {item.strip().lower() for item in configs.ALLOWED_FILE_EXTENSIONS.split(",")}
    if extension not in allowed_extensions:
        raise HTTPException(status_code=415, detail="Unsupported file type")

    payload = await file.read(configs.MAX_FILE_SIZE_BYTES + 1)
    await file.seek(0)
    if len(payload) > configs.MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds the maximum allowed size")

    _, _, sessions, _ = dependencies.InfrastructureSingleton.get()
    checksum = hashlib.sha256(payload).hexdigest()
    if sessions.mongo.document_exists(session.id, checksum):
        raise HTTPException(status_code=409, detail="This document is already in the session")
    if not sessions.mongo.reserve_document_slot(session.id, len(payload),
                                                configs.MAX_DOCUMENTS_PER_SESSION,
                                                configs.MAX_STORAGE_BYTES_PER_SESSION):
        raise HTTPException(status_code=429, detail="The document or storage limit for this session was reached")

    owner_email = current_user.get("sub") if current_user else None
    provider = rag_service.openai_adapter.provider
    result = await run_in_threadpool(
        rag_service.save_document,
        file,
        session_id=session.id,
        expires_at=None if owner_email else session.expires_at,
        max_file_size=configs.MAX_FILE_SIZE_BYTES,
        checksum=checksum,
        owner_email=owner_email,
        provider=provider,
    )
    if result.get("status") != "Document saved successfully":
        sessions.mongo.sessions.update_one(
            {"id": session.id},
            {"$inc": {"document_count": -1, "storage_used": -len(payload)}}
        )
        message = result.get("message", result.get("status", "Document processing failed"))
        status_code = 401 if "401" in message or "invalid_api_key" in message else 400
        raise HTTPException(status_code=status_code,
                            detail="OpenAI rejected the supplied key" if status_code == 401 else message)
    return {
        "status": DocumentStatus.COMPLETED,
        "document_id": result.get("document_id"),
    }


@rag_router.get("/me/documents")
def get_my_documents(
    current_user: dict = Depends(dependencies.get_current_user),
) -> list[Dict[str, Any]]:
    mongo, _, _, _ = dependencies.InfrastructureSingleton.get()
    return [document.model_dump() for document in mongo.get_user_documents(current_user["sub"])]


@rag_router.get("/me/history")
def get_my_history(
    current_user: dict = Depends(dependencies.get_current_user),
) -> list[Dict[str, Any]]:
    mongo, _, _, _ = dependencies.InfrastructureSingleton.get()
    return mongo.get_question_history(current_user["sub"])


@rag_router.get("/get-document")
def get_document(
    document_id: str,
    _admin: dict = Depends(dependencies.require_admin),
    rag_service: usecases.RAGService = Depends(dependencies.get_base_service),
) -> Optional[Dict[str, Any]]:
    document = rag_service.get_document(document_id)
    if document:
        return document.model_dump()
    return {"status": "Document not found"}


@rag_router.get("/get-vectors", status_code=201)
def get_vectors(
    _admin: dict = Depends(dependencies.require_admin),
    rag_service: usecases.RAGService = Depends(dependencies.get_base_service),
) -> Any:
    return rag_service.get_vectors()
