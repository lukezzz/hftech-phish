from wsgiref import headers
import httpx
from typing import Generator
from app.config import settings


headers = {
    "Content-Type": "application/json",
}


def airflow_client() -> Generator:
    client = httpx.Client()
    try:
        client.headers = headers
        client.auth = (settings.AIRFLOW_USERNAME, settings.AIRFLOW_PASSWORD)

        yield client

    finally:
        client.close()
