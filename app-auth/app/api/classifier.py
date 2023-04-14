from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from app.common.customAPIRoute import HandleResponseRoute
from app.common.db import get_db
from app.common.security import PermissionChecker, PermissionType
from app.utils.nmf import nmf_train, nmf_get_topic, nmf_predict
from app.models.ticket import Ticket
from app import schemas
import json


router = APIRouter(
    route_class=HandleResponseRoute,
    tags=["classifier"],
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
    "/config_model",
    response_model=schemas.ClassifierConfig,
    dependencies=[Depends(allow_get_resource)],
)
async def get_config(
    request: Request,
):
    config = await request.app.state.data_redis.hgetall("classifier")

    if not config:
        default_config = {"topic": 3, "random_state": 23, "top_word": 4}
        await request.app.state.data_redis.hmset("classifier", default_config)
        return default_config

    return config


@router.post(
    "/config_model",
    response_model=schemas.ClassifierConfig,
    dependencies=[Depends(allow_edit_resource)],
)
async def set_config(config: schemas.ClassifierConfig, request: Request):
    await request.app.state.data_redis.hmset("classifier", config.__dict__)

    return config


async def preprocess_config(request):
    config = await request.app.state.data_redis.hgetall("classifier")
    if not config:
        raise HTTPException(status_code=400, detail="No config found")
    cfg = schemas.ClassifierConfig(**config)

    return cfg


@router.post(
    "/train_model",
    dependencies=[Depends(allow_get_resource)],
)
async def train_model(
    request: Request,
    db: Session = Depends(get_db),
):
    cfg = await preprocess_config(request)
    query = db.query(Ticket)

    # res = nmf_train(cfg, query)

    nmf_train(cfg, query)
    res = nmf_get_topic(cfg, query)
    await request.app.state.data_redis.set("topic", json.dumps(res))

    return {}


@router.get(
    "/get_topic_and_top_words",
    dependencies=[Depends(allow_get_resource)],
)
async def get_topic_and_top_words(
    request: Request,
    db: Session = Depends(get_db),
):
    cfg = await preprocess_config(request)
    query = db.query(Ticket)

    try:
        res = nmf_get_topic(cfg, query)
        topic_data = await request.app.state.data_redis.get("topic")
        if not topic_data:
            await request.app.state.data_redis.set("topic", json.dumps(res))
            return res
        topic = json.loads(topic_data)
        if topic:
            for i in res:
                for j in topic:
                    if i["topic"] == j["topic"]:
                        i["label"] = j["label"]
        return res
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="No topic found")


@router.post(
    "/set_topic_label",
    dependencies=[Depends(allow_create_resource)],
)
async def set_topic_label(
    req: list[schemas.TopicLabel],
    request: Request,
):
    topic_data = await request.app.state.data_redis.get("topic")
    topic = json.loads(topic_data)

    for i in req:
        for j in topic:
            if i.topic == j["topic"]:
                j["label"] = i.label

    await request.app.state.data_redis.set("topic", json.dumps(topic))
    return topic


@router.post(
    "/ticket_predict",
    dependencies=[Depends(allow_create_resource)],
)
async def ticket_predict(
    request: Request,
    db: Session = Depends(get_db),
):
    query = db.query(Ticket)

    topic = await request.app.state.data_redis.get("topic")
    # create new dict from topic data, key is topic number, value is label
    topic_dict = {i["topic"]: i["label"] for i in json.loads(topic)}
    # topic_dict = {0: "suspicious", 1: "malicious", 2: "exposed"}

    df = nmf_predict(query, topic_dict)

    ticket_dict = df.to_dict(orient="records")

    ticket_event = []

    for ticket in ticket_dict:
        db_ticket = query.filter(Ticket.id == ticket["id"]).first()
        ticket["event"] = db_ticket.events[0].name
        ticket_event.append(ticket)

    return ticket_event
