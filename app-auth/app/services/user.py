from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from typing import Any
from app.models import UserAccount, Role, UserRegister
from app.schemas import UserBase, UserPatch, UserPassword
from app.common.security import get_password_hash
from fastapi.param_functions import Form

from airflow_client.client.model.dag_run import DAGRun
from airflow_client.client.api_client import ApiClient
from datetime import datetime


import uuid
import re


class LoginWithCookieForm:
    def __init__(
        self,
        email: str = Form(...),
        password: str = Form(...),
        remember: bool = Form(...),
    ):
        self.email = email
        self.password = password
        self.remember = remember


def is_email(email):
    # 正则表达式匹配Email地址的格式
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# from app.common.user_preference import SysRoleTypes

# 注册方法


def user_register(auth, db: Session, email: str, api):
    # 判断email格式
    if not is_email(email):
        raise Exception("email格式有误")

    # 查询注册数据库中是否已存在当前邮箱
    obj = db.query(UserRegister).filter(UserRegister.email == email).first()
    if obj:
        raise Exception("email已经注册")

    
    random_uuid = uuid.uuid4()
    register_id = str(random_uuid)

    # auth.create_access_token 生成注册key 并发邮件给用户
    register_key = auth.create_access_token(
        subject=register_id, user_claims={"email": email}
    )
    dag_id = "mail_user_register"
    config = {
        "dag_run_id": f"phish_mail_user_register_{datetime.timestamp(datetime.now())}",
        "conf":
        {"mail_to": email,
            "token": register_key}
    }
    dag_run = DAGRun(**config)
    api_response: DAGRun = api.post_dag_run(dag_id, dag_run)
    print("api_response", api_response)
    
    # 向数据库中插入注册信息
    db_obj = UserRegister(id=register_id, email=email, is_success=False)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    

    return "邮件已发送"
# 注册验证方法


def verify_register(req, auth, db: Session):
    # 尝试解出token中的注册信息，无法接触则抛出"token信息有误"错误
    try:
        register_info = auth.get_raw_jwt(req.token)
    except:
        raise Exception("token信息有误")
    # 验证注册表中是否存在此id 以及对应db对象的email是否与token中的email一致，不一致或者对象不存在，则抛出"token信息有误"错误
    register_db_obj = db.query(UserRegister).filter(
        UserRegister.id == register_info["sub"]).first()
    if not register_db_obj:
        raise Exception("token信息有误")
    if not register_db_obj.email == register_info["email"]:
        raise Exception("token信息有误")
    # 添加用户
    user_db_obj = create_user_account(db, req, register_info["email"])
    # 修改注册表中是否注册成功的状态为True
    register_db_obj.is_success = True
    db.add(register_db_obj)
    db.commit()
    db.refresh(register_db_obj)
    return user_db_obj


def get_user_account_by_username(db: Session, username: str) -> Any:
    return db.query(UserAccount).filter(UserAccount.username == username).first()


def get_user_account_by_id(db: Session, user_account_id: str) -> Any:
    return db.query(UserAccount).filter(UserAccount.id == user_account_id).first()


def create_user_account(db: Session, req: UserRegister, email: str):

    try:
        password_hashed = get_password_hash(req.password)
        user_data = req.dict(exclude_none=True)
        del user_data["password"]

        del user_data["role"]
        del user_data["token"]
        user_data["password_hashed"] = password_hashed
        obj_user = db.query(UserAccount).filter(
            UserAccount.username == user_data["username"]).first()
        if obj_user:
            raise Exception("用户名已存在")

        user_post = UserAccount(**user_data)
        user_post.email = email
        db.add(user_post)

        role = db.query(Role).filter(Role.name == req.role).first()
        if role:
            user_post.role = role

        db.commit()
        db.refresh(user_post)
        return user_post

    except Exception as err:
        db.rollback()
        raise Exception(err)


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
