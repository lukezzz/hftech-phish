import airflow_client.client
from airflow_client.client.api import (
    config_api,
    dag_api,
    monitoring_api,
    connection_api,
    dag_run_api,
    event_log_api,
    import_error_api,
    pool_api,
    task_instance_api,
    variable_api,
    x_com_api,
)

from typing import Generator
from app.config import settings


configuration = airflow_client.client.Configuration(
    host=settings.AIRFLOW_URI,
    username=settings.AIRFLOW_USERNAME,
    password=settings.AIRFLOW_PASSWORD,
)


def airflow_health() -> Generator:
    with airflow_client.client.ApiClient(configuration) as api_client:
        api_instance = monitoring_api.MonitoringApi(api_client)
        try:
            yield api_instance
        finally:
            api_instance.api_client.close()


def airflow_config() -> Generator:
    with airflow_client.client.ApiClient(configuration) as api_client:
        api_instance = config_api.ConfigApi(api_client)
        try:
            yield api_instance
        finally:
            api_instance.api_client.close()


def airflow_dag() -> Generator:
    with airflow_client.client.ApiClient(configuration) as api_client:
        api_instance = dag_api.DAGApi(api_client)
        try:
            yield api_instance
        finally:
            api_instance.api_client.close()


def airflow_connection() -> Generator:
    with airflow_client.client.ApiClient(configuration) as api_client:
        api_instance = connection_api.ConnectionApi(api_client)
        try:
            yield api_instance
        finally:
            api_instance.api_client.close()


def airflow_dag_run() -> Generator:
    with airflow_client.client.ApiClient(configuration) as api_client:
        api_instance = dag_run_api.DAGRunApi(api_client)
        try:
            yield api_instance
        finally:
            api_instance.api_client.close()


def airflow_task() -> Generator:
    with airflow_client.client.ApiClient(configuration) as api_client:
        api_instance = task_instance_api.TaskInstanceApi(api_client)
        try:
            yield api_instance
        finally:
            api_instance.api_client.close()


def airflow_pool() -> Generator:
    with airflow_client.client.ApiClient(configuration) as api_client:
        api_instance = pool_api.PoolApi(api_client)
        try:
            yield api_instance
        finally:
            api_instance.api_client.close()


def airflow_event_log() -> Generator:
    with airflow_client.client.ApiClient(configuration) as api_client:
        api_instance = event_log_api.EventLogApi(api_client)
        try:
            yield api_instance
        finally:
            api_instance.api_client.close()


def airflow_import_err() -> Generator:
    with airflow_client.client.ApiClient(configuration) as api_client:
        api_instance = import_error_api.ImportErrorApi(api_client)
        try:
            yield api_instance
        finally:
            api_instance.api_client.close()


def airflow_variable() -> Generator:
    with airflow_client.client.ApiClient(configuration) as api_client:
        api_instance = variable_api.VariableApi(api_client)
        try:
            yield api_instance
        finally:
            api_instance.api_client.close()


def airflow_xcom() -> Generator:
    with airflow_client.client.ApiClient(configuration) as api_client:
        api_instance = x_com_api.XComApi(api_client)
        try:
            yield api_instance
        finally:
            api_instance.api_client.close()
