from sqlalchemy.orm import Session
from typing import Any
from app.models import UserAccount, Role
from app.schemas import UserCreate, UserBase, UserPatch, UserPassword
from app.common.security import get_password_hash
from fastapi.param_functions import Form


class LoginWithCookieForm:
    def __init__(
        self,
        username: str = Form(...),
        password: str = Form(...),
        remember: bool = Form(...),
    ):
        self.username = username
        self.password = password
        self.remember = remember


# from app.common.user_preference import SysRoleTypes
from fastapi.exceptions import HTTPException


def get_user_account_by_username(db: Session, username: str) -> Any:
    return db.query(UserAccount).filter(UserAccount.username == username).first()


def get_user_account_by_id(db: Session, user_account_id: str) -> Any:
    return db.query(UserAccount).filter(UserAccount.id == user_account_id).first()


def create_user_account(db: Session, req: UserCreate):

    try:
        password_hashed = get_password_hash(req.password)

        user_data = req.dict(exclude_none=True)
        del user_data["password"]

        del user_data["role"]

        user_data["password_hashed"] = password_hashed

        user_post = UserAccount(**user_data)
        db.add(user_post)

        role = db.query(Role).filter(Role.name == req.role).first()
        if role:
            user_post.role = role

        db.commit()
        db.refresh(user_post)
        return user_post

    except Exception as err:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=err,
        )


def delete_user_account(db: Session, user: UserBase):

    try:
        sys_user_del = (
            db.query(UserAccount)
            .filter(
                UserAccount.id == user.id,
            )
            .first()
        )
        if sys_user_del:
            db.delete(sys_user_del)
            db.commit()
            return True
        else:
            return False
    except Exception as err:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=err,
        )


def update_user_account(db: Session, patch_config: UserPatch, patch_user: any):

    try:
        user_data = patch_config.dict(exclude_none=True)
        for item in user_data:
            if item == "password":
                hashed_password = get_password_hash(user_data["password"])
                setattr(patch_user, "hashed_password", hashed_password)
            setattr(patch_user, item, user_data[item])

        db.commit()
        db.refresh(patch_user)
        return patch_user
    except Exception as err:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=err,
        )


def change_password(db: Session, new_password: UserPassword, current_user: UserAccount):
    current_user.set_password(new_password.password)
    db.commit()
    db.refresh(current_user)
    return current_user


# TODO role -> udpate list
# def update_user_account_role(db: Session, role: int, patch_user: any):

#     try:
#         post_role = db.query(Role).filter_by(id=role).first()
#         patch_user.roles = post_role

#         db.commit()
#         db.refresh(patch_user)
#         return patch_user
#     except Exception as err:
#         db.rollback()
#         raise HTTPException(
#             status_code=500,
#             detail=err,
#         )
