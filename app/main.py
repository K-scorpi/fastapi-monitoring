from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
import uvicorn

app = FastAPI(title="Monitoring Demo App")

# Подключаем метрики
Instrumentator().instrument(app).expose(app)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI!"}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}

@app.get("/healthz")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)