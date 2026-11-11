from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import asyncio
from server.api.routers import rag_router
from server.app import configurations
from fastapi.middleware.cors import CORSMiddleware

configs = configurations.Settings()


async def cleanup_loop() -> None:
    from server.api.dependencies import InfrastructureSingleton
    while True:
        try:
            _, _, sessions, limiter = InfrastructureSingleton.get()
            sessions.cleanup_expired()
            limiter.cleanup()
        except Exception:
            # Cleanup must never bring down the API. The next interval retries.
            pass
        await asyncio.sleep(configs.CLEANUP_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(_: FastAPI):
    task = asyncio.create_task(cleanup_loop())
    try:
        yield
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict[str, str]:
    """Readiness probe that verifies MongoDB before accepting traffic."""
    try:
        from server.api.dependencies import InfrastructureSingleton
        mongo, _, _, _ = InfrastructureSingleton.get()
        mongo.client.admin.command("ping")
        return {"status": "ready"}
    except Exception:
        raise HTTPException(status_code=503, detail="Persistence service is unavailable") from None

# Configuración CORS
origins = [origin.strip() for origin in configs.ALLOWED_ORIGINS.split(",") if origin.strip()]
if configs.REACT_VITE_CONNECTION not in origins:
    origins.append(configs.REACT_VITE_CONNECTION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(rag_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server.main:app", host=configs.APP_HOST, port=configs.APP_PORT, reload=True)
