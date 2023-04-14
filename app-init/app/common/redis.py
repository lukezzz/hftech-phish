# redis

import aioredis
from fastapi import FastAPI
from .fastapi_logger import fastapi_logger

# redis_conn = redis.StrictRedis.from_url(settings.REDIS_URI, decode_responses=True)


def register_auth_redis(app: FastAPI, redis_url):
    @app.on_event("startup")
    async def startup_event():
        app.state.redis = await aioredis.from_url(redis_url, decode_responses=True)
        fastapi_logger.warning(f"connected with redis: {app.state.redis}")

    @app.on_event("shutdown")
    async def shutdown_event():
        await app.state.redis.close()
        fastapi_logger.warning(f"disconnected redis")
