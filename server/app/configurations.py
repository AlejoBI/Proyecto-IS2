from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    # Configuración de la aplicación
    APP_HOST: str
    APP_PORT: int

    # Config react_vite
    REACT_VITE_CONNECTION: str
    ALLOWED_ORIGINS: str = "http://localhost:5173"
    COOKIE_SECURE: bool = False

    # Hashing
    SECRET_ACCESS_TOKEN: str
    ALGORITHM: str

    # Configuracion para mongodb
    MONGODB_URI: str
    MONGODB_DATABASE: str
    MONGODB_COLLECTION_USERS: str
    MONGODB_COLLECTION_DOCUMENTS: str

    # ConfiguraciÃ³n para OpenAI
    # Optional legacy key for local development. Public deployments must use
    # the request-scoped X-OpenAI-API-Key instead.
    OPENAI_API_KEY: str = ""
    MODEL: str
    GEMINI_MODEL: str = "gemini-3.8-flash"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    GEMINI_EMBEDDING_MODEL: str = "gemini-embedding-001"
    GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    MAX_TOKENS: int
    TEMPERATURE: float
    NUMBER_OF_VECTORIAL_RESULTS: int
    CHROMA_PATH: str = "./chroma_data"
    MEDIA_PATH: str = "./media"
    SESSION_IDLE_MINUTES: int = 30
    SESSION_MAX_HOURS: int = 2
    MAX_FILE_SIZE_BYTES: int = 10485760
    MAX_DOCUMENTS_PER_SESSION: int = 5
    MAX_STORAGE_BYTES_PER_SESSION: int = 52428800
    MAX_QUESTIONS_PER_SESSION: int = 20
    MAX_QUERY_LENGTH: int = 2000
    CHUNK_SIZE_TOKENS: int = 2048
    OPENAI_TIMEOUT_SECONDS: float = 30.0
    OPENAI_MAX_RETRIES: int = 2
    RATE_LIMIT_REQUESTS: int = 30
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    REDIS_URL: str = ""
    REDIS_RATE_LIMIT_PREFIX: str = "proyecto-is2:rate"
    CLEANUP_INTERVAL_SECONDS: int = 600
    BACKUP_DIR: str = "./backups"
    BACKUP_RETENTION_DAYS: int = 7
    ALLOWED_FILE_EXTENSIONS: str = ".pdf,.docx,.txt"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        extra="ignore",
    )
