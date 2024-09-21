import pydantic
import uuid

def generate_uuid() -> str:
    return str(uuid.uuid4())


class Document(pydantic.BaseModel):
    id: str = pydantic.Field(default_factory=generate_uuid)
    content: str

class User(pydantic.BaseModel):
    id: str = pydantic.Field(default_factory=generate_uuid)
    name: str
    email: str
    password: str
    role: str