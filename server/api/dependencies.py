from server.adapters.openai_adapter import OpenAIAdapter
from server.adapters.chromadb_adapter import ChromaDBAdapter
from server.adapters.mongodb_adapter import MongoDBAdapter
from server.app import usecases, configurations
from fastapi import Depends, Header, HTTPException, Request, Response
from server.services.rate_limiter import InMemoryRateLimiter, RedisRateLimiter
from server.services.sessions import SessionContext, SessionService
from server.services.auth_service import AuthService
from server.services.admin_service import AdminService
from server.middlewares.jwt import decode_token


class RAGServiceSingleton:
    _instance = None

    @classmethod
    def get_instance(cls) -> usecases.RAGService:
        if cls._instance is None:
            configs = configurations.Settings()
            openai_adapter = OpenAIAdapter(api_key=configs.OPENAI_API_KEY, model=configs.MODEL,
                                           embedding_model=configs.EMBEDDING_MODEL,
                                           max_tokens=configs.MAX_TOKENS, temperature=configs.TEMPERATURE,
                                           timeout=configs.OPENAI_TIMEOUT_SECONDS,
                                           max_retries=configs.OPENAI_MAX_RETRIES)
            document_repo = ChromaDBAdapter(number_of_vectorial_results=configs.NUMBER_OF_VECTORIAL_RESULTS,
                                            path=configs.CHROMA_PATH)
            mongo_repo = MongoDBAdapter(uri=configs.MONGODB_URI, database=configs.MONGODB_DATABASE, users_collection=configs.MONGODB_COLLECTION_USERS,
                                        documents_collection=configs.MONGODB_COLLECTION_DOCUMENTS)
            cls._instance = usecases.RAGService(document_repo=document_repo, mongo_repo=mongo_repo, openai_adapter=openai_adapter)
        return cls._instance


class InfrastructureSingleton:
    _mongo = None
    _chroma = None
    _sessions = None
    _limiter = None

    @classmethod
    def get(cls):
        configs = configurations.Settings()
        if cls._mongo is None:
            cls._mongo = MongoDBAdapter(uri=configs.MONGODB_URI, database=configs.MONGODB_DATABASE,
                                        users_collection=configs.MONGODB_COLLECTION_USERS,
                                        documents_collection=configs.MONGODB_COLLECTION_DOCUMENTS)
            cls._chroma = ChromaDBAdapter(number_of_vectorial_results=configs.NUMBER_OF_VECTORIAL_RESULTS,
                                          path=configs.CHROMA_PATH,
                                          chunk_size_tokens=configs.CHUNK_SIZE_TOKENS)
            cls._sessions = SessionService(cls._mongo, cls._chroma, configs.MEDIA_PATH)
            if configs.REDIS_URL:
                cls._limiter = RedisRateLimiter(
                    configs.REDIS_URL,
                    configs.RATE_LIMIT_REQUESTS,
                    configs.RATE_LIMIT_WINDOW_SECONDS,
                    configs.REDIS_RATE_LIMIT_PREFIX,
                )
            else:
                cls._limiter = InMemoryRateLimiter(configs.RATE_LIMIT_REQUESTS,
                                                   configs.RATE_LIMIT_WINDOW_SECONDS)
        return cls._mongo, cls._chroma, cls._sessions, cls._limiter


def get_base_service() -> usecases.RAGService:
    mongo, chroma, _, _ = InfrastructureSingleton.get()
    return usecases.RAGService(chroma, mongo, None)


def get_auth_service() -> AuthService:
    mongo, _, _, _ = InfrastructureSingleton.get()
    return AuthService(mongo)


def get_admin_service() -> AdminService:
    mongo, _, _, _ = InfrastructureSingleton.get()
    return AdminService(mongo)


def get_session_context(request: Request, response: Response) -> SessionContext:
    configs = configurations.Settings()
    _, _, sessions, _ = InfrastructureSingleton.get()
    context = sessions.create_or_refresh(request.cookies.get("rag_session_id"),
                                         configs.SESSION_IDLE_MINUTES,
                                         configs.SESSION_MAX_HOURS)
    response.set_cookie("rag_session_id", context.id, httponly=True,
                        samesite=configs.COOKIE_SAMESITE,
                        secure=configs.COOKIE_SECURE,
                        max_age=configs.SESSION_MAX_HOURS * 3600)
    return context


def get_rate_limit(request: Request, session: SessionContext = Depends(get_session_context)) -> SessionContext:
    _, _, _, limiter = InfrastructureSingleton.get()
    client_ip = request.client.host if request.client else "unknown"
    if not limiter.allow(f"{client_ip}:{session.id}"):
        raise HTTPException(status_code=429, detail="Too many requests. Try again later.")
    return session


def get_rag_service(
    api_key: str = Header(default="", alias="X-LLM-API-Key"),
    legacy_api_key: str = Header(default="", alias="X-OpenAI-API-Key"),
    provider: str = Header(default="openai", alias="X-LLM-Provider"),
) -> usecases.RAGService:
    provider = provider.lower().strip()
    api_key = api_key or legacy_api_key
    if not api_key or api_key.lower().startswith("replace-with") or "placeholder" in api_key.lower():
        raise HTTPException(status_code=401, detail="Provide your provider API key in X-LLM-API-Key")
    if provider not in {"openai", "gemini"}:
        raise HTTPException(status_code=400, detail="Unsupported LLM provider")
    configs = configurations.Settings()
    mongo, chroma, _, _ = InfrastructureSingleton.get()
    is_gemini = provider == "gemini"
    adapter = OpenAIAdapter(api_key=api_key,
                            model=configs.GEMINI_MODEL if is_gemini else configs.MODEL,
                            embedding_model=(configs.GEMINI_EMBEDDING_MODEL
                                             if is_gemini else configs.EMBEDDING_MODEL),
                            max_tokens=configs.MAX_TOKENS, temperature=configs.TEMPERATURE,
                            timeout=configs.OPENAI_TIMEOUT_SECONDS,
                            max_retries=configs.OPENAI_MAX_RETRIES,
                            base_url=configs.GEMINI_BASE_URL if is_gemini else None,
                            provider=provider)
    return usecases.RAGService(chroma, mongo, adapter)


def get_current_user(request: Request) -> dict:
    token = request.cookies.get("access_token")
    claims = decode_token(token) if token else None
    if not claims:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return claims


def get_optional_user(request: Request) -> dict | None:
    token = request.cookies.get("access_token")
    return decode_token(token) if token else None


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Administrator role required")
    return current_user
