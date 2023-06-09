from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, status, Body, Path, Query
from sqlalchemy.orm import Session
from fastapi_pagination.ext.sqlalchemy import paginate

from app.openapidoc import (
    openapi_user_account_mgmt_role,
    openapi_user_account_mgmt_create,
    openapi_user_account_mgmt_search,
    openapi_user_account_mgmt_get_by_user_id,
    openapi_user_account_mgmt_delete_by_user_id,
    openapi_user_account_mgmt_edit_by_user_id,
)
from app import schemas, services
from app.models.aaa import Role, UserAccount

from app.common.customAPIRoute import HandleResponseRoute
from app.common.db import get_db
from app.common.customPage import Page
from app.common.elastic_query import ElasticQuery
from app.common.security import PermissionChecker, PermissionType, get_current_user
from fastapi_jwt_auth import AuthJWT
from datetime import timedelta


router = APIRouter(
    route_class=HandleResponseRoute,
    tags=["user_account_mgmt"],
    responses={404: {"detail": "Not found"}},
)
allow_create_user = PermissionChecker(
    [PermissionType.can_read_any.value, PermissionType.can_api_read.value]
)
allow_get_resource = PermissionChecker(
    [PermissionType.can_read_any.value, PermissionType.can_api_read.value]
)
allow_create_resource = PermissionChecker(
    [PermissionType.can_create_any.value])
allow_delete_resource = PermissionChecker(
    [PermissionType.can_delete_any.value])
allow_edit_resource = PermissionChecker([PermissionType.can_edit_any.value])

@router.get(
    "/role",
    dependencies=[Depends(allow_get_resource)],
    response_model=list[schemas.RoleOut],
    **openapi_user_account_mgmt_role,
)
def get_role_permissions(
    db: Session = Depends(get_db),
):

    try:
        res = db.query(Role).all()
        return res
    except:
        raise HTTPException(status_code=400, detail="Not found")

@router.get(
    "/search",
    response_model=Page[schemas.UserOut],
    dependencies=[Depends(allow_get_resource)],
    **openapi_user_account_mgmt_search,
)
def search_user_account(
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
            query_res = ElasticQuery(db, UserAccount, query)
            res = query_res.search()
        else:
            res = db.query(UserAccount)

        return paginate(res)
    except:
        raise HTTPException(status_code=400, detail="Not found")


@router.get(
    "/{user_account_id}",
    response_model=schemas.UserDetailOut,
    dependencies=[Depends(allow_get_resource)],
    **openapi_user_account_mgmt_get_by_user_id,
)
def get_user_account_detail(
    user_account_id: str = Path(default=None, description="user uuid"),
    db: Session = Depends(get_db),
    # current_user=Depends(services.can_readwrite),
):

    user_account = services.get_user_account_by_id(db, user_account_id)

    if not user_account:
        raise HTTPException(status_code=404, detail="Not found")

    return user_account


@router.delete(
    "/{user_account_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(allow_delete_resource)],
    **openapi_user_account_mgmt_delete_by_user_id,
)
def delete_sys_user(
    user_account_id: str = Path(default=None, description="user uuid"),
    db: Session = Depends(get_db),
    # current_user=Depends(services.is_super),
):
    """
    readwrite_permissions
    """

    will_del_user_account = services.get_user_account_by_id(
        db=db, user_account_id=user_account_id
    )

    if not will_del_user_account:
        raise HTTPException(status_code=404, detail="Not found")

    # if will_del_user_account.id == current_user.id or will_del_user_account.username == "admin":
    #     raise HTTPException(status_code=404, detail="This user can not be deleted")

    return services.delete_user_account(db, will_del_user_account)


@router.patch(
    "/edit",
    response_model=schemas.UserOut,
    dependencies=[Depends(allow_edit_resource)],
    **openapi_user_account_mgmt_edit_by_user_id,
)
def update_user_account(
    patch_config: schemas.UserPatch,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    return services.update_user_account(db, patch_config, current_user)


@router.patch(
    "/change_password",
    response_model=schemas.UserOut,
    dependencies=[Depends(allow_edit_resource)],
    **openapi_user_account_mgmt_edit_by_user_id,
)
def update_self_password(
    new_password: schemas.UserPassword,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    return services.change_password(db, new_password, current_user)


# TODO
# @router.patch(
#     "/role/{user_account_id}",
#     response_model=schemas.UserOut,
#     dependencies=[Depends(allow_edit_resource)],
#     summary="设置user account权限",
#     deprecated=True,
# )
# def patch_user_account_role(
#     user_account_id: str,
#     db: Session = Depends(get_db),
# ):

#     return {}


@router.get(
    "/list/user",
    response_model=List[schemas.UserOut],
    dependencies=[Depends(allow_get_resource)],
)
def list_all_user(
    db: Session = Depends(get_db),
):

    users = db.query(UserAccount).all()

    return users


@router.post(
    "/long_term_token",
    dependencies=[Depends(allow_get_resource)],
)
def get_long_term_token(
    current_user=Depends(get_current_user),
    Authorize: AuthJWT = Depends(),
    db: Session = Depends(get_db),
):

    # services.insert_event(
    #     db=db,
    #     category=services.EventCategory.get_token,
    #     req={"action": "get long term token"},
    #     user_id=current_user.username,
    # )
    expires = timedelta(days=365 * 99)
    access_token = Authorize.create_access_token(
        subject=current_user.id,
        user_claims={"role": current_user.role.name},
        expires_time=expires,
    )

    return access_token
