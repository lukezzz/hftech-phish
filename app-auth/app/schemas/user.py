from pydantic import BaseModel, validator, Field
from typing import Any, Dict, Optional, List
from email_validator import validate_email, EmailNotValidError

# from app.common.user_preference import AppUserPermissionRule
from pydantic import BaseModel, validator


class RegsiterVerify(BaseModel):
    token: str = Field(example="xxxxxxxxx.xxxxxxxx")
    username: str = Field(example="pengsy")
    password: str = Field(example="*****")
    role: str = Field(example="admin")

    @validator("username")
    def validate_username(cls: Any, username: str, **kwargs: Any) -> Any:
        if len(username) <= 3 or username == "admin":
            raise ValueError("Username is invalid")
        return username

    @validator("password")
    def validate_password(cls: Any, password: str, **kwargs: Any) -> Any:

        # TODO password complex required
        return password


# class UserCreate(BaseModel):
#     username: str = Field(example="pengsy")
#     password: str = Field(example="*****")
#     role: str = Field(example="admin")


class UserLogin(BaseModel):
    email: str = Field(example="admin@admin.com")
    password: str = Field(example="*****")


class UserBase(BaseModel):
    username: str = Field(example="Foo", description="登录名")
    display_name: Optional[str] = Field(
        default=None, example="Foo", description="显示名字")
    email: Optional[str] = Field(default=None, example="test@mail.com")
    phone: Optional[str] = Field(default=None, example="12388888")
    desc: Optional[str] = Field(default=None, example="This is description")


# class UserCreate(UserBase):
#     password: str = Field(example="*****")
#     role: str = Field(example=["admin"])

#     @validator("username")
#     def validate_username(cls: Any, username: str, **kwargs: Any) -> Any:
#         if len(username) <= 3 or username == "admin":
#             raise ValueError("Username is invalid")
#         return username

#     @validator("password")
#     def validate_password(cls: Any, password: str, **kwargs: Any) -> Any:

#         # TODO password complex required
#         return password

    # @validator("roles")
    # def validate_role(cls: Any, role: str, **kwargs: Any) -> Any:
    #     if not set(role).issubset(set(AppUserPermissionRule.all_permissions.value)):
    #         raise ValueError("Role is invalid")
    #     return role

    # @validator("email")
    # def validate_email(cls: Any, email: str, **kwargs: Any) -> Any:
    #     try:
    #         valid = validate_email(email)
    #         # Update with the normalized form.
    #         return valid.email
    #     except EmailNotValidError as e:
    #         raise ValueError(e)


class UserPatch(BaseModel):
    display_name: Optional[str] = Field(
        default=None, example="Foo", description="显示名字")
    phone: Optional[str] = Field(default=None, example="12388888")
    desc: Optional[str] = Field(default=None, example="This is description")

    password: Optional[str] = Field(example="*****")

    class Config:
        orm_mode: bool = True

    @validator("password")
    def validate_password(cls: Any, password: str, **kwargs: Any) -> Any:

        # TODO password complex required
        return password

    # @validator("email")
    # def validate_email(cls: Any, email: str, **kwargs: Any) -> Any:

    #     try:
    #         if email:
    #             valid = validate_email(email)
    #             # Update with the normalized form.
    #             return valid.email
    #     except EmailNotValidError as e:
    #         raise ValueError(e)


class UserPassword(BaseModel):
    password: str = Field(example="*****")

    @validator("password")
    def validate_password(cls: Any, password: str, **kwargs: Any) -> Any:

        # TODO password complex required
        return password


class UserQuery(BaseModel):
    query: Optional[Dict] = Field(
        default=None,
        description="elk style query",
        example={
            "filter": {
                "or": {
                    "firstname": {"equals": "Jhon"},
                    "lastname": "Galt",
                    "uid": {"like": "111111"},
                },
                "and": {"status": "active", "age": {"gt": 18}},
            },
            "sort": {"firstname": "asc", "age": "desc"},
            "limit": 5,
            "offset": 2,
        },
    )


class UserRole(BaseModel):
    name: str = Field(example="Role name, eg: 'admin'", description="角色名字")

    class Config:
        orm_mode = True


class User(UserBase):
    role: UserRole = Field(example="Role name list, eg: ['admin']")

    class Config:
        orm_mode: bool = True

    # @validator("role")
    # def validate_roles(cls: Any, role: int, **kwargs: Any) -> Any:
    #     if not set(role).issubset(set(AppUserPermissionRule.all_permissions.value)):
    #         raise ValueError("Role is invalid")
    #     return role


class UserOut(User):
    id: str = Field(example="uuid", description="系统生成id")

    class Config:
        orm_mode: bool = True


class UserDetailOut(User):
    pass


class PermissionOut(BaseModel):
    name: str

    class Config:
        orm_mode: bool = True


class RoleOut(BaseModel):

    name: str
    permissions: list[PermissionOut]

    class Config:
        orm_mode: bool = True
