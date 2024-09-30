from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # Configuración de la aplicación
    APP_HOST: str
    APP_PORT: int

    # Config react_vite
    REACT_VITE_CONNECTION: str

    # Hashing
    SECRET_ACCESS_TOKEN: str
    ALGORITHM: str

    # Configuración para mongodb
    MONGODB_URI: str
    MONGODB_DATABASE: str
    MONGODB_COLLECTION_USERS: str
    MONGODB_COLLECTION_DOCUMENTS: str

    # Configuración para OpenAI
    OPENAI_API_KEY: str
    MODEL: str
    MAX_TOKENS: int
    TEMPERATURE: float
    NUMBER_OF_VECTORIAL_RESULTS: int

    class Config:
        # Determina la ruta raíz del proyecto (sube dos niveles desde Backend/app/)
        project_root = Path(__file__).resolve().parents[2]
        env_file = project_root / ".env"
        # Busca el archivo .env en la raíz del proyecto

settings = Settings()