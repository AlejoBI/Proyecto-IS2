from fastapi import FastAPI
from api import routers

app = FastAPI()

app.include_router(routers.rag_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8080)

#to execute the server
#uvicorn main:app --host 127.0.0.1 --port 8080 --reload