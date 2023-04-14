# System模型

from app.models.base import BaseModel
from sqlalchemy import Column, String, ForeignKey, Table, DateTime, Boolean
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.common.security import get_password_hash, gen_guid


class Space(BaseModel):
    __tablename__ = "sys_spaces"

    id = Column(String(64), primary_key=True, default=gen_guid)
    name = Column(String(64), unique=True, index=True)
    desc = Column(String(256))
