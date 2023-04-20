import datetime
from app.api.models.common import BaseModelMixin
from core.database.settings.base import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, \
    BigInteger, JSON
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


class Parser(BaseModelMixin, Base):
    file_name = Column(String(length=255))
    file_path = Column(String(length=255), nullable=True)
    frequency = Column(Enum(Frequency), default=None)
    description = Column(String(length=255))
    company_id = Column(Integer)
    process_id = Column(Integer)
    last_run = Column(DateTime, index=False, default=datetime.datetime.now())
    set_active_at = Column(DateTime, index=False, nullable=True)
    is_active = Column(Boolean, default=True)

    def as_dict(self):
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        for i in data:
            if isinstance(data[i], (datetime.datetime, datetime.date)):
                data[i] = dumps(data[i], indent=4, sort_keys=True, default=str)
        return data


class ProcessMapField(BaseModelMixin, Base):
    file_id = Column(Integer, index=True)
    field_name = Column(String(length=255), nullable=True)
    map_field_name = Column(String(length=255), nullable=True)
    is_ignored = Column(Boolean, default=False)

    def as_dict(self):
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        for i in data:
            if isinstance(data[i], (datetime.datetime, datetime.date)):
                data[i] = dumps(data[i], indent=4, sort_keys=True, default=str)
        return data


class Status(int, enum.Enum):
    pending = 1
    in_progress = 2
    success = 3
    failed = 4


class FileHistory(BaseModelMixin, Base):
    file_id = Column(Integer, index=True)
    file_size_kb = Column(BigInteger, nullable=True)
    file_name_as_received = Column(String(length=255), nullable=True)
    task_id = Column(String(length=255), nullable=True)
    history_status = Column(Enum(Status), default=Status.pending)


class FileReceiveHistoryDetail(BaseModelMixin, Base):
    history_id = Column(Integer, index=True, nullable=False)
    file_id = Column(Integer, index=True, nullable=False)
    total_rows = Column(Integer)
    total_success = Column(Integer)
    total_failure = Column(Integer)


class FileHistoryFailedRows(BaseModelMixin, Base):
    history_id = Column(Integer, index=True, nullable=False)
    file_id = Column(Integer, index=True, nullable=False)
    row_number = Column(Integer, nullable=False)
    number_of_reties = Column(Integer, nullable=False)
    row_data = Column(JSON, nullable=False)
    is_success = Column(Boolean, default=False)
    task_id = Column(String(length=255), nullable=True)
