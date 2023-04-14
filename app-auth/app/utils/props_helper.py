from app.models.ticket import Department, Source, Asset, Event
from app.models.o365 import O365EmailAddress
from enum import IntEnum, Enum
from fastapi import HTTPException


class CheckPropsModel(Enum):
    department = Department
    source = Source
    asset = Asset
    event = Event
    email = O365EmailAddress

    @classmethod
    def get_model(cls, value):
        if value not in cls._member_map_:
            raise HTTPException(status_code=404, detail="asset prop name not existed!")

        return cls[value].value
