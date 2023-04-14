from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, status, Body, Path, Query
from sqlalchemy.orm import Session
from fastapi_pagination.ext.sqlalchemy import paginate

from app import schemas, services
from app.models.o365 import O365MailMessage

from app.common.customAPIRoute import HandleResponseRoute
from app.common.db import get_db
from app.common.customPage import Page
from app.common.elastic_query import ElasticQuery
from app.common.security import PermissionChecker, PermissionType, get_current_user


router = APIRouter(
    route_class=HandleResponseRoute,
    tags=["message"],
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
    "/parse_subject/{mail_id}",
    response_model=schemas.ParsedSubject,
    dependencies=[Depends(allow_create_resource)],
)
def parse_subject(
    mail_id: str = Path(default=None, description="mail id"),
    db: Session = Depends(get_db),
):
    mail = services.get_mail_by_id(db, mail_id)
    if not mail:
        raise HTTPException(status_code=404, detail="Not found")

    return services.mail_parse_subject(mail)


@router.post(
    "/bind_ticket/{mail_id}",
    response_model=schemas.TicketOut,
    dependencies=[Depends(allow_create_resource)],
)
def bind_ticket(
    mail_id: str = Path(default=None, description="mail id"),
    db: Session = Depends(get_db),
):
    mail = services.get_mail_by_id(db, mail_id)
    if not mail:
        raise HTTPException(status_code=404, detail="Not found")

    return services.bind_ticket(db, mail)
