# 用户AAA模型

from app.models.base import BaseModel
from sqlalchemy import Column, String, ForeignKey, Table, DateTime, Boolean
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.common.security import get_password_hash, gen_guid


# user_accounts_m2m_roles = Table(
#     "user_accounts_m2m_roles",
#     Base.metadata,
#     Column("user_account_id", String, ForeignKey("user_accounts.id")),
#     Column("role_id", String, ForeignKey("roles.id")),
# )


class Permission(BaseModel):
    __tablename__ = "permissions"
    id = Column(String(64), primary_key=True, default=gen_guid)
    name = Column(String(64), unique=True, index=True)

    role_id = Column(String(64), ForeignKey("roles.id"))
    role = relationship("Role", backref="permissions")


class Role(BaseModel):
    __tablename__ = "roles"
    id = Column(String(64), primary_key=True, default=gen_guid)
    name = Column(String(64), unique=True, index=True)

    # user_accounts = relationship(
    #     "UserAccount", secondary="user_accounts_m2m_roles", back_populates="roles"
    # )


# class App_User_Locale(BaseModel):
#     __tablename__ = "app_user_locale"

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     locale_name = Column(String(64), index=True)


class UserAccount(BaseModel):
    __tablename__ = "user_accounts"

    id = Column(String(64), primary_key=True, default=gen_guid)
    username = Column(String(64), unique=True, index=True)
    display_name = Column(String(128))
    first_name = Column(String(64))
    last_name = Column(String(64))
    password_hashed = Column(String, nullable=False)
    email = Column(String(64), unique=True)
    address = Column(String(128))
    phone = Column(String(32))

    desc = Column(String(256))

    is_blocked = Column(Boolean, default=False, nullable=False)

    # roles = relationship(
    #     "Role", secondary="user_accounts_m2m_roles", back_populates="user_accounts"
    # )

    role_id = Column(String(64), ForeignKey("roles.id"))
    role = relationship("Role", backref="users")

    last_logon = Column(DateTime)

    def set_password(self, password):
        self.password_hashed = get_password_hash(password)


# class APIAccount(BaseModel):
#     __tablename__ = "api_accounts"

#     id = Column(String(64), primary_key=True, default=gen_guid)
#     account_id = Column(String(64), unique=True, index=True)

#     desc = Column(String(256))

#     is_blocked = Column(Boolean, default=False, nullable=False)

#     def set_password(self, password):
#         self.password_hashed = get_password_hash(password)
