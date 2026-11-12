import hashlib
import logging
from time import perf_counter
from uuid import uuid4
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from starlette.concurrency import run_in_threadpool

from server.api import dependencies
from server.api.schemas import AnswerResponse, DocumentOperationResponse
from server.core.models import DocumentStatus
from server.app import configurations, usecases
from server.services.sessions import SessionContext
from server.adapters.chromadb_adapter import NoDocumentsIndexedError
from server.adapters.openai_adapter import ProviderError


rag_router = APIRouter()
logger = logging.getLogger(__name__)


def _document_summary(document) -> Dict[str, Any]:
    return {
        "id": document.id,
        "title": document.title,
        "status": document.status.value,
        "provider": document.provider,
        "indexed_providers": document.indexed_providers,
        "size_bytes": document.size_bytes,
        "created_at": document.created_at,
        "checksum": document.checksum[:12] if document.checksum else None,
        "error": "Document processing failed"
        if document.status == DocumentStatus.FAILED else None,
    }


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


@rag_router.get("/session/documents", status_code=200)
def get_session_documents(
    session: SessionContext = Depends(dependencies.get_session_context),
) -> list[Dict[str, Any]]:
    mongo, _, _, _ = dependencies.InfrastructureSingleton.get()
    return [_document_summary(document) for document in mongo.get_session_documents(session.id)]


@rag_router.delete("/session/documents/{document_id}", status_code=200)
def delete_session_document(
    document_id: str,
    session: SessionContext = Depends(dependencies.get_session_context),
    current_user: Optional[dict] = Depends(dependencies.get_optional_user),
) -> Dict[str, str]:
    mongo, chroma, _, _ = dependencies.InfrastructureSingleton.get()
    document = next(
        (item for item in mongo.get_session_documents(session.id) if item.id == document_id),
        None,
    )
    if not document or (current_user and document.owner_email != current_user.get("sub")):
        raise HTTPException(status_code=404, detail="Document not found in this session")

    chroma.delete_document(document_id)
    mongo.delete_document(document_id)
    if document.path:
        Path(document.path).unlink(missing_ok=True)
    mongo.sessions.update_one(
        {"id": session.id},
        {"$inc": {"document_count": -1, "storage_used": -(document.size_bytes or 0)}},
    )
    return {"status": "Document deleted"}


@rag_router.post("/session/documents/{document_id}/index", status_code=200)
async def index_session_document(
    document_id: str,
    session: SessionContext = Depends(dependencies.get_session_context),
    rag_service: usecases.RAGService = Depends(dependencies.get_rag_service),
    current_user: Optional[dict] = Depends(dependencies.get_optional_user),
) -> Dict[str, Any]:
    mongo, chroma, _, _ = dependencies.InfrastructureSingleton.get()
    document = next(
        (item for item in mongo.get_session_documents(session.id) if item.id == document_id),
        None,
    )
    if not document or (current_user and document.owner_email != current_user.get("sub")):
        raise HTTPException(status_code=404, detail="Document not found in this session")
    if document.status != DocumentStatus.COMPLETED or not document.content:
        raise HTTPException(status_code=400, detail="Document is not ready for indexing")

    provider = rag_service.openai_adapter.provider
    if not chroma.has_document(document.id, provider):
        try:
            await run_in_threadpool(
                chroma.save_document,
                document,
                document.content,
                rag_service.openai_adapter,
                provider,
            )
            mongo.add_document_provider(document.id, provider)
        except ProviderError as error:
            raise HTTPException(
                status_code=error.status_code or 502,
                detail=str(error),
            ) from None
    return {
        "status": "Document indexed successfully",
        "document_id": document.id,
        "provider": provider,
    }


@rag_router.get("/generate-answer", status_code=200)
def generate_answer(
    query: str,
    session: SessionContext = Depends(dependencies.get_rate_limit),
    rag_service: usecases.RAGService = Depends(dependencies.get_rag_service),
    current_user: Optional[dict] = Depends(dependencies.get_optional_user),
    response: Response = None,
) -> AnswerResponse:
    configs = configurations.Settings()
    if len(query) > configs.MAX_QUERY_LENGTH:
        raise HTTPException(status_code=413, detail="Question is too long")
    _, _, sessions, _ = dependencies.InfrastructureSingleton.get()
    if not sessions.mongo.increment_question_count(session.id, configs.MAX_QUESTIONS_PER_SESSION):
        raise HTTPException(status_code=429, detail="The question limit for this session was reached")
    provider = rag_service.openai_adapter.provider
    request_id = uuid4().hex[:12]
    rag_service.openai_adapter._request_id = request_id
    if response:
        response.headers["X-Request-ID"] = request_id
    started_at = perf_counter()
    logger.info(
        "rag.answer.request.started provider=%s request_id=%s authenticated=%s query_length=%d",
        provider,
        request_id,
        bool(current_user),
        len(query),
    )
    try:
        owner_email = current_user.get("sub") if current_user else None
        result = rag_service.generate_answer_with_sources(
            query, session_id=session.id, owner_email=owner_email, provider=provider
        )
        logger.info(
            "rag.answer.request.completed provider=%s request_id=%s sources=%d duration_ms=%.2f",
            provider,
            request_id,
            len(result.get("sources", [])),
            (perf_counter() - started_at) * 1000,
        )
        return result
    except NoDocumentsIndexedError:
        raise HTTPException(
            status_code=400,
            detail="Upload and process a document for this provider before asking a question.",
        ) from None
    except ProviderError as error:
        logger.warning(
            "rag.answer.provider_failed provider=%s request_id=%s error_type=%s status_code=%s duration_ms=%.2f",
            provider,
            request_id,
            type(error).__name__,
            error.status_code,
            (perf_counter() - started_at) * 1000,
        )
        detail = str(error)
        if error.request_id:
            detail = f"{detail}. Request ID: {error.request_id}"
        raise HTTPException(
            status_code=error.status_code or 502,
            detail=detail,
            headers={"X-Request-ID": request_id},
        ) from None
    except Exception as error:
        logger.warning(
            "rag.answer.failed provider=%s request_id=%s error_type=%s status_code=%s duration_ms=%.2f",
            provider,
            request_id,
            type(error).__name__,
            getattr(error, "status_code", None),
            (perf_counter() - started_at) * 1000,
        )
        raise HTTPException(
            status_code=502,
            detail=f"{provider.capitalize()} request failed. Request ID: {request_id}",
            headers={"X-Request-ID": request_id},
        ) from None


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
        if "no remaining credits" in message.lower():
            status_code = 429
        elif "rate limit" in message.lower():
            status_code = 429
        else:
            status_code = 401 if "401" in message or "invalid_api_key" in message else 400
        provider_name = provider.capitalize()
        raise HTTPException(status_code=status_code,
                            detail=f"{provider_name} rejected the supplied key"
                            if status_code == 401 else message)
    return {
        "status": DocumentStatus.COMPLETED,
        "document_id": result.get("document_id"),
    }


@rag_router.get("/me/documents")
def get_my_documents(
    current_user: dict = Depends(dependencies.get_current_user),
) -> list[Dict[str, Any]]:
    mongo, _, _, _ = dependencies.InfrastructureSingleton.get()
    return [_document_summary(document) for document in mongo.get_user_documents(current_user["sub"])]


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
