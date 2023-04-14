from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from app import services, schemas
from app.config import settings

from app.common.customAPIRoute import HandleResponseRoute
from app.common.db import get_db

from datetime import datetime

import redis

# import aioredis

from app.openapidoc import openapi_auth_login, openapi_auth_logout
from app.models import UserAccount

redis_conn = redis.StrictRedis.from_url(settings.AUTH_REDIS_URI, decode_responses=True)
# redis_conn = aioredis.from_url(settings.AUTH_REDIS_URI, decode_responses=True)

router = APIRouter(
    route_class=HandleResponseRoute,
    tags=["auth"],
    responses={404: {"detail": "Not found"}},
)


@AuthJWT.token_in_denylist_loader
def check_if_token_in_denylist(decrypted_token):
    jti = decrypted_token["jti"]
    entry = redis_conn.get(jti)
    return entry and entry == "true"


@router.post("/login", **openapi_auth_login)
async def login_for_access_token(
    request: Request,
    db: Session = Depends(get_db),
    form_data: services.LoginWithCookieForm = Depends(),
    Authorize: AuthJWT = Depends(),
):
    user = services.auth_user(db, form_data.username, form_data.password)

    if form_data.remember == True:
        Authorize._cookie_max_age = settings.COOKIE_AGE

    access_token = Authorize.create_access_token(
        subject=user.id, user_claims={"role": user.role.name}
    )
    refresh_token = Authorize.create_refresh_token(
        subject=user.id, user_claims={"role": user.role.name}
    )
    # Set the JWT cookies in the response
    data = {"access_token": access_token, "refresh_token": refresh_token}
    response = JSONResponse(content={"success": True, "data": data})
    Authorize.set_access_cookies(access_token, response)
    Authorize.set_refresh_cookies(refresh_token, response)

    # services.insert_event(
    #     db=db,
    #     category=services.EventCategory.user_login,
    #     req={"username": form_data.username, "ip": request.client.host},
    #     user_id=form_data.username,
    # )

    return response


# Standard refresh endpoint. Token in denylist will not
# be able to access this endpoint
# @router.post("/refresh", summary="刷新 access_token")
# def refresh(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
#     Authorize.jwt_refresh_token_required()

#     user_id = Authorize.get_jwt_subject()
#     user = services.get_admin_by_user_id(db, user_id)
#     new_access_token = Authorize.create_access_token(
#         subject=user.id, user_claims={"role": user.role.name}
#     )
#     Authorize.set_access_cookies(new_access_token)
#     return {"success": True, "data": "The token has been refresh"}


@router.post("/logout", **openapi_auth_logout)
async def logout(
    request: Request,
    Authorize: AuthJWT = Depends(),
    db: Session = Depends(get_db),
):
    try:
        Authorize.jwt_required()
        jti = Authorize.get_raw_jwt()["jti"]
        redis_client = request.app.state.redis
        await redis_client.setex(jti, settings.authjwt_access_token_expires, "true")
        Authorize.unset_jwt_cookies()

        current_user_id = Authorize.get_jwt_subject()
        user: UserAccount = services.get_user_account_by_id(db, current_user_id)
        # services.insert_event(
        #     db=db,
        #     category=services.EventCategory.user_logout,
        #     req={"username": user.username, "ip": request.client.host},
        #     user_id=user.username,
        # )

        return {
            "success": True,
            "data": "Logout successfully",
            "errorMessage": "",
        }
    except Exception as e:
        print(e)
        return {"success": True}


@router.get("/self", response_model=schemas.UserOut, summary="获取当前用户信息")
def get_self(Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    Authorize.jwt_required()

    current_user_id = Authorize.get_jwt_subject()
    admin = services.get_user_account_by_id(db, current_user_id)
    if admin:
        admin.last_logon = datetime.utcnow()
        db.commit()
        return admin
    else:
        raise HTTPException(
            status_code=404,
            detail="Not found",
        )
