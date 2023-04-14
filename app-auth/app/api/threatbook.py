from fastapi import APIRouter, HTTPException, Depends, status, Body, Request
from sqlalchemy.orm import Session

from app.common.customAPIRoute import HandleResponseRoute
from app.common.db import get_db
from app.common.security import PermissionChecker, PermissionType

from app import schemas, services
from app.models.system import Threatbook

import json

router = APIRouter(
    route_class=HandleResponseRoute,
    tags=["threatbook"],
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
    "/config",
    response_model=schemas.ThreatbookBase,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(allow_create_resource)],
)
def post_config(
    req: schemas.ThreatbookBase = Body(
        default=None,
    ),
    db: Session = Depends(get_db),
):
    config = services.get_threatbook_config(db)
    if not config:
        config = Threatbook()
        db.add(config)
    config.api_key = req.api_key
    db.commit()
    return config


@router.get(
    "/config",
    response_model=schemas.ThreatbookBase,
    dependencies=[Depends(allow_get_resource)],
)
def get_config(
    db: Session = Depends(get_db),
):
    config = services.get_threatbook_config(db)

    if not config:
        raise HTTPException(status_code=400, detail="threatbook config not found")

    return config


@router.post(
    "/intel_query",
    dependencies=[Depends(allow_create_resource)],
)
async def intel_query(
    request: Request,
    req: schemas.ThreatbookIntelQuery = Body(
        default=None,
    ),
    db: Session = Depends(get_db),
):
    intel = await request.app.state.data_redis.get(f"intel:{req.sha1}")
    if not intel:
        # query sha1 to threatbook via request
        threatbook_config = services.get_threatbook_config(db)
        intel = services.threat_book_file_query(threatbook_config, req.sha1)
        # store the result to redis
        await request.app.state.data_redis.set(f"intel:{req.sha1}", json.dumps(intel))
        return intel

    return json.loads(intel)


@router.post(
    "/clear_cache",
    dependencies=[Depends(allow_create_resource)],
)
async def clear_cache(
    request: Request,
):
    keys = await request.app.state.data_redis.keys("intel:*")
    for key in keys:
        await request.app.state.data_redis.delete(key)
    return {"message": "cache cleared"}
