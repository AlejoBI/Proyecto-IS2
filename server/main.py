from fastapi import FastAPI
from server.api.routers import rag_router
from server.app import configurations
from fastapi.middleware.cors import CORSMiddleware

configs = configurations.Settings()
app = FastAPI()

# Configuración CORS
origins = [
    configs.APP_HOST,
    configs.REACT_VITE_CONNECTION
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.include_router(rag_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.main:app", host=configs.APP_HOST, port=configs.APP_PORT, reload=True)