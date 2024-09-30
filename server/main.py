from fastapi import FastAPI
from server.api.routers import rag_router
from server.app import configurations

configs = configurations.Settings()
app = FastAPI()
app.include_router(rag_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.main:app", host=configs.APP_HOST, port=configs.APP_PORT, reload=True)