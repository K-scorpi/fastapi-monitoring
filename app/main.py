import logging
import logstash
from fastapi import FastAPI, Depends
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
import uvicorn
import aioredis

# Настройка логирования
host = 'logstash'
port = 5044

app = FastAPI(title="Monitoring Demo App")

# Добавляем обработчик logstash к корневому логгеру
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logstash.TCPLogstashHandler(host, port, version=1))

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://redis", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

@app.get("/")
@cache(expire=60)  # Кэшируем ответ на 60 секунд
def read_root():
    logging.info("Root endpoint was called")
    return {"message": "Hello from FastAPI with Redis!"}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    logging.info(f"Item {item_id} was requested")
    return {"item_id": item_id}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)