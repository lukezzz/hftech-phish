from app.db.base import Base
from datetime import datetime
from sqlalchemy import (
    Column,
    DateTime,
)


class BaseModel(Base):
    __abstract__ = True

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


metadata = Base.metadata
