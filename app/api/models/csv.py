import datetime

from app.api.models.common import BaseModelMixin
from core.database.settings.base import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, BigInteger
import enum
from json import dumps


class Frequency(int, enum.Enum):
    min_1 = 1
    min_15 = 15
    min_30 = 30
    hour_1 = 60
    hour_2 = 120
    hour_3 = 180
    hour_6 = 360
    hour_12 = 720
    hour_24 = 1440


class ProcessConfig(BaseModelMixin, Base):
    file_name = Column(String)
    file_path = Column(String, nullable=True)
    frequency = Column(Enum(Frequency), default=None)
    description = Column(String)
    company_id = Column(Integer)
    process_id = Column(Integer)
    last_run = Column(DateTime, index=False, default=datetime.datetime.now())
    set_active_at = Column(DateTime, index=False)
    is_active = Column(Boolean, default=True)

    def as_dict(self):
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        for i in data:
            if isinstance(data[i], (datetime.datetime, datetime.date)):
                data[i] = dumps(data[i], indent=4, sort_keys=True, default=str)
        return data


class ProcessMapField(BaseModelMixin, Base):
    file_id = Column(Integer, index=True)
    field_name = Column(String, nullable=True)
    map_field_name = Column(String, nullable=True)
    is_ignored = Column(Boolean, default=False)

    def as_dict(self):
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        for i in data:
            if isinstance(data[i], (datetime.datetime, datetime.date)):
                data[i] = dumps(data[i], indent=4, sort_keys=True, default=str)
        return data


class FileReceiveHistory(BaseModelMixin, Base):
    file_id = Column(Integer, index=True)
    file_size_kb = Column(BigInteger, nullable=True)
    file_name_as_received = Column(String, nullable=True)
    task_id = Column(String, nullable=True)
