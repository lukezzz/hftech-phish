from fastapi.testclient import TestClient
from sqlalchemy import create_engine, engine
from sqlalchemy.orm import sessionmaker
from app.config import Settings, get_settings
from app.db.base import Base
from app.main import app
from app.common.db import get_db
from app.common.system_init import init_aaa


# Default to using sqlite in memory for fast tests.
# Can be overridden by environment variable for testing in CI against other
# database engines
APP_DB_URI = "sqlite:////:memory:"


def get_settings_override():
    return Settings(APP_DB_URI=APP_DB_URI)


app.dependency_overrides[get_settings] = get_settings_override

engine = create_engine(
    APP_DB_URI, connect_args={"check_same_thread": False}, pool_pre_ping=True
)  # noqa
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = TestingSessionLocal()


class CookieConfigurableTestClient(TestClient):
    _access_token = None
    _refresh_token = None

    def set_access_token(self, access_token, refresh_token):
        self._access_token = access_token
        self._refresh_token = refresh_token

    def reset(self):
        self._access_token = None
        self._refresh_token = None

    def request(self, *args, **kwargs):
        cookies = kwargs.get("cookies")
        if cookies is None and self._access_token:
            kwargs["cookies"] = {
                "access_token": self._access_token,
                "refresh_token": self._refresh_token,
            }

        return super().request(*args, **kwargs)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


client = CookieConfigurableTestClient(app)


# init app

## init aaa user
init_aaa(db)
