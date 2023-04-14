from typing import Optional
from app.models.ticket import Ticket, Asset, Department, Source
from fastapi import APIRouter, HTTPException, Depends, status, Body, Path, Query
from sqlalchemy.orm import Session
from fastapi_pagination.ext.sqlalchemy import paginate
from app.common.customAPIRoute import HandleResponseRoute
from app.common.db import get_db
from app.common.customPage import Page
from app.common.elastic_query import ElasticQuery
from app.common.security import PermissionChecker, PermissionType, get_current_user
from app import schemas, services
from app.utils.props_helper import CheckPropsModel
from app.utils.nlp_parser import parse_threat_file
from datetime import datetime, timedelta

router = APIRouter(
    route_class=HandleResponseRoute,
    tags=["tickets"],
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
    "/create",
    response_model=schemas.TicketOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(allow_create_resource)],
)
def create_new_ticket(
    req: schemas.TicketCreate = Body(
        default=None,
    ),
    db: Session = Depends(get_db),
):
    return services.create_ticket(db, req)


@router.get(
    "/count",
    dependencies=[Depends(allow_create_resource)],
)
def ticket_count(
    db: Session = Depends(get_db),
):
    return services.ticket_count(db)


@router.get(
    "/search",
    response_model=Page[schemas.TicketOut],
    dependencies=[Depends(allow_get_resource)],
)
def search_ticket(
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
            query_res = ElasticQuery(db, Ticket, query)
            res = query_res.search()
        else:
            res = db.query(Ticket)

        res = res.order_by(Ticket.updated_at.desc())
        return paginate(res)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Not found")


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

    tickets = db.query(Ticket).all()

    for ticket in tickets:
        db.delete(ticket)

    assets = db.query(Asset).all()

    for asset in assets:
        db.delete(asset)

    departements = db.query(Department).all()

    for dep in departements:
        db.delete(dep)

    sources = db.query(Source).all()

    for src in sources:
        db.delete(src)

    db.commit()

    return {}


@router.get(
    "/{ticket_id}",
    response_model=schemas.TicketDetailOut,
    dependencies=[Depends(allow_get_resource)],
)
def get_ticket_detail(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    ticket = services.get_ticket_by_id(db, ticket_id)

    if not ticket:
        raise HTTPException(status_code=404, detail="ticket not existed!")

    return ticket


@router.patch(
    "/{ticket_id}",
    response_model=schemas.TicketOut,
    dependencies=[Depends(allow_edit_resource)],
)
def patch_ticket(
    patch_config: schemas.TicketEdit,
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    patch_ticket = services.get_ticket_by_id(db, ticket_id)

    if not patch_ticket:
        raise HTTPException(status_code=404, detail="ticket not existed!")

    return services.update_ticket(db, patch_config, patch_ticket)


@router.delete(
    "/{ticket_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(allow_delete_resource)],
)
def delete_ticket(
    ticket_id: str = Path(default=None, description="ticket uuid"),
    db: Session = Depends(get_db),
):
    """
    readwrite_permissions
    """

    will_del_ticket = services.get_ticket_by_id(db=db, ticket_id=ticket_id)

    if not will_del_ticket:
        raise HTTPException(status_code=404, detail="Not found")

    # if will_del_user_account.id == current_user.id or will_del_user_account.username == "admin":
    #     raise HTTPException(status_code=404, detail="This user can not be deleted")

    return services.delete_ticket(db, will_del_ticket)


@router.post(
    "/create_props/{prop_name}",
    response_model=schemas.TicketPropOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(allow_create_resource)],
)
def create_new_ticket_props(
    prop_name: str,
    req: schemas.TicketPropBase = Body(
        default=None,
    ),
    db: Session = Depends(get_db),
):
    asset = services.get_props_by_name(
        db, CheckPropsModel.get_model(prop_name), req.name
    )

    if asset:
        raise HTTPException(status_code=400, detail="asset name already existed")

    return services.create_ticket_props(db, CheckPropsModel.get_model(prop_name), req)


@router.get(
    "/list_props/{prop_name}",
    # dependencies=[Depends(allow_get_resource)],
)
def list_asset(
    prop_name: str,
    db: Session = Depends(get_db),
):
    ticket_prop = db.query(CheckPropsModel.get_model(prop_name)).all()

    return ticket_prop


@router.delete(
    "/delete_props/{prop_name}/{props_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(allow_delete_resource)],
)
def delete_props(
    prop_name: str,
    props_id: str = Path(default=None, description="props uuid"),
    db: Session = Depends(get_db),
):
    """
    readwrite_permissions
    """

    model = CheckPropsModel.get_model(prop_name)

    will_del_props = services.get_props_by_id(db=db, model=model, id=props_id)

    if not will_del_props:
        raise HTTPException(status_code=404, detail="Not found")

    # if will_del_user_account.id == current_user.id or will_del_user_account.username == "admin":
    #     raise HTTPException(status_code=404, detail="This user can not be deleted")

    return services.delete_ticket_props(db, model, will_del_props)


@router.get(
    "/count_props/asset",
    dependencies=[Depends(allow_create_resource)],
)
def ticket_count_asset(
    db: Session = Depends(get_db),
):
    return services.ticket_count_asset(db)


@router.get(
    "/threat_file/{ticket_id}",
    dependencies=[Depends(allow_get_resource)],
)
def get_threat_file(
    ticket_id: str,
    db: Session = Depends(get_db),
):
    ticket = services.get_ticket_by_id(db, ticket_id)

    if not ticket:
        raise HTTPException(status_code=404, detail="ticket not existed!")

    mails = ticket.mails
    for mail in mails:
        res = parse_threat_file(mail.body_text)
        print(res)
        if res:
            return res

    return None


@router.get(
    "/count/weekly",
    dependencies=[Depends(allow_get_resource)],
)
def weekly_report(
    db: Session = Depends(get_db),
):
    # get last week first day and last day
    now = datetime.now()
    last_week = now - timedelta(days=7)
    last_week_first_day = last_week - timedelta(days=last_week.weekday())
    last_week_last_day = last_week_first_day + timedelta(days=6)

    # get last week ticket
    last_week_tickets = (
        db.query(Ticket)
        .filter(
            Ticket.started_at >= last_week_first_day,
            Ticket.started_at <= last_week_last_day,
        )
        .all()
    )

    # get last week ticket count
    total = len(last_week_tickets)

    # get ticket count by state is 2
    complete_count = len([ticket for ticket in last_week_tickets if ticket.state == 2])

    # get ticket count by state is 1 or 0
    not_complete_count = len(
        [
            ticket
            for ticket in last_week_tickets
            if ticket.state == 1 or ticket.state == 0
        ]
    )

    # average day for ticket.closed_at - ticket.started_at which state is 2
    complete_tickets = [ticket for ticket in last_week_tickets if ticket.state == 2]
    complete_tickets_time = [
        (ticket.closed_at - ticket.started_at).days for ticket in complete_tickets
    ]
    if len(complete_tickets_time) > 0:
        average_complete_time = sum(complete_tickets_time) / len(complete_tickets_time)
    else:
        average_complete_time = 0

    # count ticket which state is 2 and department name is China Corp
    china_corp_complete_count = len(
        [
            ticket
            for ticket in complete_tickets
            if ticket.department.name == "China CORP"
        ]
    )

    china_corp_total = len(
        [
            ticket
            for ticket in last_week_tickets
            if ticket.department.name == "China CORP"
        ]
    )


    china_rest_complete_count = len(
        [
            ticket
            for ticket in complete_tickets
            if ticket.department.name == "China REST"
        ]
    )

    china_rest_total = len(
        [
            ticket
            for ticket in last_week_tickets
            if ticket.department.name == "China REST"
        ]
    )


    return {
        "date_range": f'{last_week_first_day.strftime("%Y-%m-%d")} - {last_week_last_day.strftime("%Y-%m-%d")}',
        "total": total,
        "complete_count": complete_count,
        "not_complete_count": not_complete_count,
        "average_complete_time": average_complete_time,
        "china_corp_complete_count": china_corp_complete_count,
        "china_rest_complete_count": china_rest_complete_count,
        "china_coprp_percentage": china_corp_total / total * 100
        if total > 0
        else 0,
        "china_rest_percentage": china_rest_total / total * 100
        if total > 0
        else 0,
    }
