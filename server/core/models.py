from typing import Optional
import pydantic
from pydantic import EmailStr, constr
import uuid
from enum import Enum


def generate_uuid() -> str:
    return str(uuid.uuid4())


class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(pydantic.BaseModel):
    id: str = pydantic.Field(default_factory=generate_uuid)
    title: Optional[str] = None
    path: Optional[str] = None
    content: Optional[str] = None
    session_id: Optional[str] = None
    owner_email: Optional[str] = None
    expires_at: Optional[str] = None
    checksum: Optional[str] = None
    size_bytes: Optional[int] = None
    provider: Optional[str] = None
    indexed_providers: list[str] = pydantic.Field(default_factory=list)
    created_at: Optional[str] = None
    status: DocumentStatus = DocumentStatus.COMPLETED
    similarity: Optional[float] = None


class User(pydantic.BaseModel):
    id: str = pydantic.Field(default_factory=generate_uuid)
    username: str = constr(min_length=3, max_length=50)
    email: EmailStr
    password: str = constr(min_length=8)
    role: str
    isActive: bool = True
