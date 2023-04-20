from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_jwt_auth import AuthJWT


from app.config import settings
from app.common.fastapi_logger import fastapi_logger

from app.db.session import engine, SessionLocal
from app.init.init_db import init_aaa
from app.init.init_airflow import init_airflow, enable_airflow_dags

# Base.metadata.create_all(bind=engine)

app: Any = FastAPI(title=settings.app_title)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# set log level
fastapi_logger.setLevel(settings.LOGGING_LEVEL)

app_trace = None

db = SessionLocal()


@AuthJWT.load_config
def get_config():
    return settings


@app.on_event("startup")
async def init_db_defaults():
    print("db init started")

    # init app user
    init_aaa(db)

    # init sys
    # init_sys(db)


    # init airflow
    init_airflow(db)
    enable_airflow_dags()

    print("db init done")


@app.on_event("shutdown")
async def shutdown_event():
    pass
