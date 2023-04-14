from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status, Body, Path, Query
from sqlalchemy.orm import Session
from fastapi_pagination.ext.sqlalchemy import paginate

from app import schemas, services
from app.models.o365 import O365MailMessage, O365EmailAddress

from app.common.customAPIRoute import HandleResponseRoute
from app.common.db import get_db
from app.common.customPage import Page
from app.common.elastic_query import ElasticQuery
from app.common.security import PermissionChecker, PermissionType

router = APIRouter(
    route_class=HandleResponseRoute,
    tags=["mail"],
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


@router.get(
    "/search",
    response_model=Page[schemas.MailOut],
    dependencies=[Depends(allow_get_resource)],
)
def search_mail(
    query: Optional[str] = Query(
        default=None,
        description="""
```
{
    "filter": {
        "or": {`
            "firstname": {
                "equals": "Jhon"
            },
            "lastname": "Galt",
            "uid": {
                "like": "111111"
            },
        },
        "and": {
            "status": "active",
            "age": {
                "gt": 18
            }
        },
    },
    "sort": {
        "firstname": "asc",
        "age": "desc"
    },
    "limit": 5,
    "offset": 2,
}
```
        """,
    ),
    db: Session = Depends(get_db),
):
    try:
        if query and query != "null":
            query_res = ElasticQuery(db, O365MailMessage, query)
            res = query_res.search()
        else:
            res = db.query(O365MailMessage)

        res = res.order_by(O365MailMessage.receivedDateTime.desc())
        return paginate(res)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Not found")


@router.post(
    "/new",
    response_model=schemas.MailOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(allow_create_resource)],
)
def add_new_mail(
    req: schemas.MailCreate = Body(
        default=None,
    ),
    db: Session = Depends(get_db),
):
    return services.add_new_mail(db, req)


@router.post(
    "/mail_body",
    response_model=schemas.MailBody,
    dependencies=[Depends(allow_get_resource)],
)
def get_mail_body(
    req: schemas.MailGetBody = Body(
        default=None,
    ),
    db: Session = Depends(get_db),
):
    mail = services.get_mail_by_id(db, req.id)
    if not mail:
        raise HTTPException(status_code=400, detail="Not found")

    return services.get_mail_body(mail, req)


@router.delete(
    "/delete_all",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(allow_delete_resource)],
)
def delete_all(
    db: Session = Depends(get_db),
):
    """
    readwrite_permissions
    """

    mails = db.query(O365MailMessage).all()

    for mail in mails:
        db.delete(mail)

    email_addresses = db.query(O365EmailAddress).all()
    for addr in email_addresses:
        db.delete(addr)
    db.commit()
    return {}


@router.delete(
    "/{mail_id}",
    dependencies=[Depends(allow_delete_resource)],
)
def delete_mail(
    mail_id: str,
    db: Session = Depends(get_db),
):
    """
    readwrite_permissions
    """

    mail = services.get_mail_by_id(db, mail_id)

    if not mail:
        raise HTTPException(status_code=404, detail="Not found")

    db.delete(mail)
    db.commit()

    return {}


@router.get(
    "/list_text_body",
    dependencies=[Depends(allow_get_resource)],
)
def list_text_body(
    db: Session = Depends(get_db),
):
    mails = db.query(O365MailMessage).all()

    body_list = [mail.body_text for mail in mails]

    return body_list


@router.get(
    "/forward_rule/{rule_name}",
    response_model=schemas.ForwardRuleOut,
    dependencies=[Depends(allow_get_resource)],
)
def get_forward_rule(
    rule_name: str,
    db: Session = Depends(get_db),
):
    rule = services.get_forward_rule(db, rule_name)

    if not rule:
        raise HTTPException(status_code=400, detail="forward rule not found")

    return rule


@router.patch(
    "/forward_rule/{rule_name}",
    response_model=schemas.ForwardRuleOut,
    dependencies=[Depends(allow_edit_resource)],
)
def update_forward_rule(
    req: schemas.ForwardRuleEdit,
    rule_name: str,
    db: Session = Depends(get_db),
):
    rule = services.get_forward_rule(db, rule_name)

    if not rule:
        raise HTTPException(status_code=400, detail="forward rule not found")

    return services.update_forward_rule(db, rule, req)
