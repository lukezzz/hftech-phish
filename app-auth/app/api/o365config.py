from fastapi import APIRouter, HTTPException, Depends, status, Body
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT


from app.common.customAPIRoute import HandleResponseRoute
from app.common.db import get_db
from app.common.customPage import Page
from app.common.elastic_query import ElasticQuery
from app.common.security import PermissionChecker, PermissionType

from app import schemas, services
from airflow_client.client import ApiClient
from airflow_client.client.model.dag_collection import DAGCollection
from airflow_client.client.model.dag import DAG
from airflow_client.client.model.dag_run import DAGRun
from datetime import datetime

router = APIRouter(
    route_class=HandleResponseRoute,
    tags=["o365config"],
    responses={404: {"detail": "Not found"}},
)


allow_get_resource = PermissionChecker(
    [
        PermissionType.can_read_any.value,
    ]
)
allow_create_resource = PermissionChecker([PermissionType.can_create_any.value])
allow_delete_resource = PermissionChecker([PermissionType.can_delete_any.value])
allow_edit_resource = PermissionChecker([PermissionType.can_edit_any.value])


@router.post(
    "/",
    response_model=schemas.O365ConfigOut,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(allow_create_resource)],
)
def post_config(
    airflow: ApiClient = Depends(services.airflow_variable),
    req: schemas.O365ConfigUpdate = Body(
        default=None,
    ),
    db: Session = Depends(get_db),
):
    config = services.update_o365_config(db, airflow, req)

    return config


@router.get(
    "/",
    response_model=schemas.O365ConfigOut,
    dependencies=[Depends(allow_get_resource)],
)
def get_config(
    db: Session = Depends(get_db),
):
    config = services.get_o365(db)

    if not config:
        raise HTTPException(status_code=400, detail="o365 config not found")

    return config


@router.get(
    "/dags",
    dependencies=[Depends(allow_get_resource)],
)
def get_mail_dag(
    api: ApiClient = Depends(services.airflow_dag),
):
    api_response: DAGCollection = api.get_dag("o365_token_checker")
    return api_response.to_dict()


@router.post(
    "/dags",
    dependencies=[Depends(allow_get_resource)],
)
def set_mail_dag(
    config: schemas.PatchDAG,
    api: ApiClient = Depends(services.airflow_dag),
):
    config = DAG(**config.dict(exclude_none=True))
    api_response: DAG = api.patch_dag("o365_token_checker", config)
    return api_response.to_dict()


@router.post(
    "/token",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(allow_create_resource)],
)
def post_o365_config(
    airflow: ApiClient = Depends(services.airflow_variable),
    req: schemas.O365ConfigUpdate = Body(
        default=None,
    ),
    db: Session = Depends(get_db),
):
    config = services.update_o365_config(db, airflow, req)

    return config


@router.post(
    "/trigger_mail_sync",
    summary="trigger mail sync task",
)
def trigger_mail_sync_task(
    api: ApiClient = Depends(services.airflow_dag_run),
):
    dag_id = "o365_token_checker"
    config = {
        "dag_run_id": f"o365_token_checker_manual_{datetime.timestamp(datetime.now())}"
    }

    dag_run = DAGRun(**config)
    api_response: DAGRun = api.post_dag_run(dag_id, dag_run)
    return api_response.to_dict()


@router.post(
    "/update_token",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(allow_create_resource)],
)
def update_token(
    airflow: ApiClient = Depends(services.airflow_variable),
    req: schemas.O365PostToken = Body(
        default=None,
    ),
):
    services.update_at_and_rt(airflow, req)

    return {}
