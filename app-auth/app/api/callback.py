from fastapi import APIRouter, HTTPException, Depends, Header, Body, Request
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT

from app.common.customAPIRoute import HandleResponseRoute
from app.common.db import get_db
from airflow_client.client import ApiClient

from app import schemas, services
import json

router = APIRouter(
    route_class=HandleResponseRoute,
    tags=["contacts"],
    responses={404: {"detail": "Not found"}},
)


# verify token for all airflow api request
async def verify_token(authorization: str = Header()):
    jwt_auth = AuthJWT()
    get_raw_jwt = jwt_auth.get_raw_jwt(authorization)
    if get_raw_jwt["sub"] != "airflow":
        raise HTTPException(
            status_code=401, detail="Sorry, you are not authorized to access this API."
        )


@router.get(
    "/o365config",
    response_model=schemas.O365ConfigOut,
    dependencies=[Depends(verify_token)],
)
def get_o365_config(
    db: Session = Depends(get_db),
):
    config = services.get_o365(db)

    if not config:
        raise HTTPException(status_code=400, detail="o365 config not found")

    return config


@router.get(
    "/o365mail/count",
    dependencies=[Depends(verify_token)],
)
def get_o365_mail_count(
    db: Session = Depends(get_db),
):
    return services.count_mail(db)


@router.post(
    "/o365mail/new",
    response_model=schemas.MailOut,
    dependencies=[Depends(verify_token)],
)
def add_new_mail(
    req: schemas.MailCreate = Body(
        default=None,
    ),
    db: Session = Depends(get_db),
):
    mail = services.get_mail_by_id(db, req.id)

    if not mail:
        return services.add_new_mail(db, req)

    return mail


@router.post(
    "/o365mail/add_text_body",
    response_model=schemas.MailOut,
    dependencies=[Depends(verify_token)],
)
async def add_text_body(
    request: Request,
    req: schemas.ADDMailTextBody = Body(
        default=None,
    ),
    db: Session = Depends(get_db),
    api: ApiClient = Depends(services.airflow_dag_run),
):
    topic = await request.app.state.data_redis.get("topic")
    topic_dict = {i["topic"]: i["label"] for i in json.loads(topic)}
    return services.add_text_body(db, req, api, topic_dict)
