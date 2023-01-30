import datetime

from pydantic import validator

from core.database.settings.base import Base
from sqlalchemy import Column, Integer, DateTime


class IDModelMixin(Base):
    id = Column(Integer, unique=True, primary_key=True, autoincrement=True)


class DateTimeModelMixin(Base):
    id = Column(Integer, unique=True, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, unique=False, index=False, default=None)
    updated_at = Column(DateTime, unique=False, index=False, default=None)

    @validator("created_at", "updated_at", pre=True)
    def default_datetime(
            cls,  # noqa: N805
            value: datetime.datetime,  # noqa: WPS110
    ) -> datetime.datetime:
        return value or datetime.datetime.now()
