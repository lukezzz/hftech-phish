from logging import Logger
from typing import Any, Optional
import os
from functools import lru_cache
from pydantic import PostgresDsn, RedisDsn, Field
from pydantic.env_settings import BaseSettings
from starlette.config import Config


class Settings(BaseSettings):
    ENVIRONMENT: str
    SECRET_KEY: Optional[str]
    ORIGINS: Optional[str]
    OTELE_TRACE: bool = False
    LOGGING_LEVEL: str = "DEBUG"

    authjwt_secret_key: str = Field(..., env="SECRET_KEY")
    authjwt_token_location: set = {"cookies", "headers"}
    authjwt_cookie_csrf_protect: bool = False
    authjwt_access_token_expires: int
    authjwt_refresh_token_expires: int
    authjwt_denylist_enabled: bool = True
    authjwt_denylist_token_checks: set = {"access", "refresh"}
    COOKIE_AGE: int

    APP_DB_URI: Optional[PostgresDsn]
    AUTH_REDIS_URI: Optional[RedisDsn]

    MESSAGE_REDIS_URI: Optional[RedisDsn]
    AIRFLOW_URI: str = "http://airflow-webserver:8080/api/v1"
    AIRFLOW_USERNAME: str
    AIRFLOW_PASSWORD: str

    HTTP_CALL_BACK_PREFIX: str
    HTTP_CALL_BACK_HOST: str
    HTTP_CALL_BACK_PORT: int

    REDIS_CALL_BACK_PREFIX: str
    REDIS_CALL_BACK_HOST: str
    REDIS_CALL_BACK_PORT: int

    # custom var
    app_title = "app-auth"


# we are using the @lru_cache() decorator on top,
# the Settings object will be created only once, the first time it's called.
@lru_cache()
def get_settings():
    return Settings()


settings: Any = get_settings()


from pathlib import Path
from fastapi.templating import Jinja2Templates

# BASE_PATH = Path(__file__).resolve().parent
# templates = Jinja2Templates(directory=str(BASE_PATH / "templates"))
