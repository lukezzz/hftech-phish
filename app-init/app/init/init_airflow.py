import airflow_client.client
from airflow_client.client.api import variable_api, connection_api, dag_api

from app.config import settings
from fastapi_jwt_auth import AuthJWT
from pathlib import Path
from sqlalchemy.orm import Session
import time
from airflow_client.client.model.dag import DAG

BASE_PATH = Path(__file__).resolve().parent


configuration = airflow_client.client.Configuration(
    host=settings.AIRFLOW_URI,
    username=settings.AIRFLOW_USERNAME,
    password=settings.AIRFLOW_PASSWORD,
)


def add_var(api_instance, key):
    try:
        api_instance.get_variable(key)
    except:
        api_instance.post_variables({"key": key, "value": ""})


def init_airflow(db: Session):
    with airflow_client.client.ApiClient(configuration) as api_client:
        # add var
        api_instance = variable_api.VariableApi(api_client)

        # add callback token var
        jwt = AuthJWT()
        token = jwt.create_access_token(
            subject="airflow",
            expires_time=315360000,
            # algorithm="HS256",
            user_claims={"username": "airflow"},
        )
        api_instance.post_variables(
            {"key": f"{settings.HTTP_CALL_BACK_PREFIX}_callback_token", "value": token}
        )

        # init airflow variables
        add_var(api_instance, "o365_client_id")

        # init airflow connection
        api_instance = connection_api.ConnectionApi(api_client)
        # TODO add db config via env setting
        connection_list = [
            {
                "connection_id": f"{settings.HTTP_CALL_BACK_PREFIX}_backend",
                "conn_type": "http",
                "host": settings.HTTP_CALL_BACK_HOST,
                "port": settings.HTTP_CALL_BACK_PORT,
            },
            {
                "connection_id": f"{settings.REDIS_CALL_BACK_PREFIX}_redis",
                "conn_type": "redis",
                "host": settings.REDIS_CALL_BACK_HOST,
                "port": settings.REDIS_CALL_BACK_PORT,
                "extra": '{"db": 2 }',
            },
        ]
        for conn in connection_list:
            try:
                api_instance.post_connection(conn)
                time.sleep(1)
            except Exception as e:
                print(e)


def enable_airflow_dags():
    dag_list = [
        # "o365_mail_count",
        # "o365_get_mail_message",
        # "o365_get_mail_body",
        # "o365_send_mail",
    ]

    config = {"is_paused": False}

    dag_config = DAG(**config)

    with airflow_client.client.ApiClient(configuration) as api_client:
        api_instance = dag_api.DAGApi(api_client)

        for dag in dag_list:
            api_instance.patch_dag(dag, dag_config)
