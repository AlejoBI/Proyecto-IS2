import pydantic
from pydantic import BaseModel
from server.core.models import DocumentStatus


class UserInput(BaseModel):
    username: str = pydantic.Field(..., min_length=3, max_length=50)
    email: str = pydantic.Field(..., min_length=3)
    password: str = pydantic.Field(..., min_length=8)
    role: str = pydantic.Field(..., min_length=1)
    isActive: bool = True


class UserUpdateInput(BaseModel):
    username: str = pydantic.Field(..., min_length=3, max_length=50)
    email: str = pydantic.Field(..., min_length=3)
    role: str = pydantic.Field(..., min_length=1)
    isActive: bool = True
    password: str | None = pydantic.Field(default=None, min_length=8)


class LoginInput(BaseModel):
    email: str
    password: str


class SourceResponse(BaseModel):
    document_id: str
    title: str | None = None
    similarity: float | None = None


class AnswerResponse(BaseModel):
    answer: str
    sources: list[SourceResponse]
    provider: str = "openai"


class DocumentOperationResponse(BaseModel):
    status: DocumentStatus
    document_id: str | None = None


class ErrorResponse(BaseModel):
    detail: str
