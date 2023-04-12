import enum
import datetime

from app.api.models.common import BaseModelMixin
from core.database.settings.base import Base
from sqlalchemy import Column, Integer, String, Enum
from json import dumps


class CeleryTaskStatus(int, enum.Enum):
    received = 1
    revoked = 2
    success = 3
    failed = 4


class MapperTask(BaseModelMixin, Base):
    company_id = Column(Integer, index=True)
    task_id = Column(String(length=255), nullable=True)
    file_id = Column(Integer, nullable=True)
    task_name = Column(String(length=255), nullable=True)
    status = Column(Enum(CeleryTaskStatus), default=None)

    def as_dict(self):
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        for i in data:
            if isinstance(data[i], (datetime.datetime, datetime.date)):
                data[i] = dumps(data[i], indent=4, sort_keys=True, default=str)
        return data
