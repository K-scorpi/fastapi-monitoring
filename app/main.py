import logging
import logstash
from fastapi import FastAPI, Depends, HTTPException
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
import uvicorn
import aioredis
from typing import List, Optional
import httpx
from fastapi.openapi.docs import get_swagger_ui_html

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
    app.state.redis = aioredis.from_url("redis://redis", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(app.state.redis), prefix="fastapi-cache")

# Dependency to get redis connection
async def get_redis():
    return app.state.redis

@app.post("/redis/set")
async def redis_set(key: str, value: str, redis=Depends(get_redis)):
    await redis.set(key, value)
    return {"status": "ok", "key": key, "value": value}

@app.get("/redis/get")
async def redis_get(key: str, redis=Depends(get_redis)):
    value = await redis.get(key)
    if value is None:
        raise HTTPException(status_code=404, detail="Key not found")
    return {"key": key, "value": value}

@app.delete("/redis/delete")
async def redis_delete(key: str, redis=Depends(get_redis)):
    result = await redis.delete(key)
    if result == 0:
        raise HTTPException(status_code=404, detail="Key not found")
    return {"status": "deleted", "key": key}

@app.get("/redis/keys")
async def redis_keys(pattern: Optional[str] = "*", redis=Depends(get_redis)):
    keys = await redis.keys(pattern)
    return {"keys": keys}

@app.get("/services/status")
async def services_status(redis=Depends(get_redis)):
    statuses = {}
    # Проверка Redis
    try:
        pong = await redis.ping()
        statuses["redis"] = pong is True
    except Exception:
        statuses["redis"] = False
    # Проверка Prometheus
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            r = await client.get("http://prometheus:9090/-/ready")
            statuses["prometheus"] = r.status_code == 200
    except Exception:
        statuses["prometheus"] = False
    # Проверка Grafana
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            r = await client.get("http://grafana:3000/api/health")
            statuses["grafana"] = r.status_code == 200
    except Exception:
        statuses["grafana"] = False
    return statuses

@app.get("/")
@cache(expire=60)  # Кэшируем ответ на 60 секунд
def read_root():
    logging.info("Root endpoint was called")
    return {"message": "Hello from FastAPI with Redis!"}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    logging.info(f"Item {item_id} was requested")
    return {"item_id": item_id}

@app.get("/custom-docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="FastAPI Monitoring — Красивое API",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css"
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)