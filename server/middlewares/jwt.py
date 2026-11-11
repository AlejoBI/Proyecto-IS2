from typing import Optional
import jwt
from server.app import configurations
from datetime import datetime, timedelta, timezone

configs = configurations.Settings()
SECRET_ACCESS_TOKEN = configs.SECRET_ACCESS_TOKEN
ALGORITHM = configs.ALGORITHM


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_ACCESS_TOKEN, algorithm=ALGORITHM)
    return str(encoded_jwt)


def validate_token(token: str) -> bool:
    return decode_token(token) is not None


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_ACCESS_TOKEN, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
