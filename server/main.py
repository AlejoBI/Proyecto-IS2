from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return "Hello, World!"

@app.get("/items/{item_id}")
def mostrar_item(item_id: int):
    return {"item_id": item_id}

#to execute the server
#uvicorn main:app --host 127.0.0.1 --port 8080 --reload