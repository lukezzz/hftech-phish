from passlib.context import CryptContext
from typing import Any, List
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.common.db import get_db
from fastapi_jwt_auth import AuthJWT
import uuid, logging
from enum import Enum, IntEnum
from app import models
from cryptography.fernet import Fernet


pwd_context = CryptContext(schemes=["pbkdf2_sha512"], deprecated="auto")

## password func
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


## generate uuid
def gen_guid():
    return str(uuid.uuid4())


## encrypt password/token 加密
def encrypt_pwd(password: str, key: str) -> str:
    try:
        fernet = Fernet(key)
        enc_password = fernet.encrypt(password.encode())
        return enc_password
    except Exception as err:
        print(err)


## decrypt password/token 解密
def decrypt_pwd(enc_password: str, key: str) -> str:
    try:
        fernet = Fernet(key)
        dec_password = fernet.decrypt(enc_password).decode()
        return dec_password
    except Exception as err:
        print(err)


## role, permssion depends
### get current user object
def get_current_user(
    db: Session = Depends(get_db), Authorize: AuthJWT = Depends()
) -> Any:
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    user = (
        db.query(models.UserAccount)
        .filter(models.UserAccount.id == current_user)
        .first()
    )
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    return user


### check permission via comapre user->roles->permssions with api permission list
class PermissionChecker:
    def __init__(self, allowed_permissions: List):
        self.allowed_permissions = allowed_permissions

    def __call__(self, user: Any = Depends(get_current_user)):

        user_permissions = []
        for role in user.roles:
            for permission in role.permissions:
                user_permissions.append(permission.name)

        # print(user_permissions, self.allowed_permissions)

        if not set(user_permissions) & set(self.allowed_permissions):
            logging.debug(
                f"User with permision {user_permissions} not in {self.allowed_permissions}"
            )
            raise HTTPException(status_code=403, detail="No permission")


class PermissionType(Enum):
    can_read_any = "can_read_any"
    can_edit_any = "can_edit_any"
    can_create_any = "can_create_any"
    can_delete_any = "can_delete_any"
    can_send_sms = "can_send_sms"
    can_make_call = "can_make_call"
    can_change_password = "can_change_password"
