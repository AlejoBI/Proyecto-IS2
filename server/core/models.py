from typing import Optional
import pydantic
from pydantic import EmailStr, constr
import uuid

def generate_uuid() -> str:
    return str(uuid.uuid4())


class Document(pydantic.BaseModel):
    id: str = pydantic.Field(default_factory=generate_uuid)
    tittle: Optional[str] = None
    path: Optional[str] = None
    content: Optional[str] = None

class User(pydantic.BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    password: constr(min_length=8)
    role: str