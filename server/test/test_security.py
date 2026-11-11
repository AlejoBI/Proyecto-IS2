import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException

from server.api.dependencies import require_admin
from server.app.usecases import RAGService
from server.core.models import Document
from server.core import ports
from server.services.rate_limiter import InMemoryRateLimiter
from server.services.sessions import SessionService


def test_rate_limiter_rejects_burst():
    limiter = InMemoryRateLimiter(max_requests=2, window_seconds=60)
    assert limiter.allow("client")
    assert limiter.allow("client")
    assert not limiter.allow("client")


def test_admin_dependency_requires_admin_role():
    assert require_admin({"role": "admin"})["role"] == "admin"
    with pytest.raises(HTTPException) as error:
        require_admin({"role": "user"})
    assert error.value.status_code == 403


def test_rag_response_contains_session_sources():
    document_repo = MagicMock(spec=ports.DocumentRepositoryPort)
    mongo_repo = MagicMock(spec=ports.MongoDBRepositoryPort)
    llm = MagicMock(spec=ports.LlmPort)
    document_repo.get_documents.return_value = [
        Document(id="doc-1", title="guide.txt", content="Relevant context", similarity=0.91)
    ]
    llm.generate_text.return_value = "Answer"

    result = RAGService(document_repo, mongo_repo, llm).generate_answer_with_sources("question", "session-1")

    assert result == {
        "answer": "Answer",
        "sources": [{"document_id": "doc-1", "title": "guide.txt", "similarity": 0.91}],
    }
    document_repo.get_documents.assert_called_once_with("question", llm, session_id="session-1")


def test_authenticated_rag_response_is_saved_to_user_history():
    document_repo = MagicMock(spec=ports.DocumentRepositoryPort)
    mongo_repo = MagicMock(spec=ports.MongoDBRepositoryPort)
    llm = MagicMock(spec=ports.LlmPort)
    document_repo.get_documents.return_value = []
    llm.generate_text.return_value = "Answer"

    result = RAGService(document_repo, mongo_repo, llm).generate_answer_with_sources(
        "question", "session-1", owner_email="user@example.com"
    )

    assert result["answer"] == "Answer"
    document_repo.get_documents.assert_called_once_with(
        "question", llm, session_id="session-1", owner_email="user@example.com"
    )
    mongo_repo.save_question_history.assert_called_once_with(
        "user@example.com", "question", "Answer", []
    )


def test_session_cleanup_removes_expired_resources():
    mongo = MagicMock()
    chroma = MagicMock()
    mongo.delete_expired_documents.return_value = [{"id": "doc-1"}]
    mongo.delete_expired_sessions.return_value = 1
    chroma.delete_document.return_value = 3

    result = SessionService(mongo, chroma, "media").cleanup_expired()

    assert result == {"sessions": 1, "documents": 1, "vectors": 3, "files": 0}
    chroma.delete_document.assert_called_once_with("doc-1")
    chroma.delete_expired_sessions.assert_called_once()
