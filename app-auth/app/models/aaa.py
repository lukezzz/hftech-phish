from sqlalchemy import Boolean, Column, DateTime, Integer, String, Table,ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel, metadata

from app.models.base import BaseModel
from sqlalchemy import Column, String, ForeignKey, Table, DateTime, Boolean
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.common.security import get_password_hash, gen_guid

class UserRegister(BaseModel):
    __tablename__ = "user_register"
    id =  Column(String(64), primary_key=True, default=gen_guid)
    email =  Column(String(64), unique=True)
    is_success = Column(Boolean, default=False)

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

class UserAccount(BaseModel):
    __tablename__ = "user_accounts"

    id = Column(String(64), primary_key=True, default=gen_guid)
    username = Column(String(64), unique=True, index=True)
    display_name = Column(String(128))
    first_name = Column(String(64))
    last_name = Column(String(64))
    password_hashed = Column(String, nullable=False)
    email = Column(String(64), unique=True, nullable=False)
    address = Column(String(128))
    phone = Column(String(32))

    desc = Column(String(256))

    is_blocked = Column(Boolean, default=False, nullable=False)

    role_id = Column(String(64), ForeignKey("roles.id"))
    role = relationship("Role", backref="users")

    last_login = Column(DateTime)
    vip_account = Column(Boolean, default=False)

    def set_password(self, password):
        self.password_hashed = get_password_hash(password)
