# redis

from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI
from .fastapi_logger import fastapi_logger
from typing import Generator


def register_mongodb_client(app: FastAPI, url):
    @app.on_event("startup")
    async def startup_event():
        app.state.mongo_client = AsyncIOMotorClient(url)
        fastapi_logger.warning(f"connected with mongodb : {app.state.mongo_client}")

    @app.on_event("shutdown")
    async def shutdown_event():
        app.state.mongo_client.close()
        fastapi_logger.warning(f"disconnected mongo_client")


from app.config import settings


def get_mongo_client() -> Generator:
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        yield client
    finally:
        client.close()
