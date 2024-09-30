import jwt
from server.app import configurations

configs = configurations.Settings()

SECRET_ACCESS_TOKEN = configs.SECRET_ACCESS_TOKEN
ALGORITHM = configs.ALGORITHM

def create_access_token(data: dict):
    return jwt.encode(data, SECRET_ACCESS_TOKEN, algorithm=ALGORITHM)

def validate_token(token: str):
    try:
        jwt.decode(token, SECRET_ACCESS_TOKEN, algorithms=[ALGORITHM])
        return True
    except:
        return False