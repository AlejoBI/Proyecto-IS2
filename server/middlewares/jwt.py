import jwt
from server.app import configurations
from datetime import datetime, timedelta

configs = configurations.Settings()
SECRET_ACCESS_TOKEN = configs.SECRET_ACCESS_TOKEN
ALGORITHM = configs.ALGORITHM

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_ACCESS_TOKEN, algorithm=ALGORITHM)

def validate_token(token: str) -> bool:
    try:
        decoded_token = jwt.decode(token, SECRET_ACCESS_TOKEN, algorithms=[ALGORITHM])
        return True
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False


