from json import dumps

from pydantic import BaseModel as PBaseModel

import datetime


class BaseModel(PBaseModel):
    def dict(self):
        data = {k: v for k, v in self.__dict__.items() if v is not None}
        for i in data:
            if isinstance(data[i], (datetime.datetime, datetime.date)):
                data[i] = dumps(data[i], indent=4, sort_keys=True, default=str)
        return data
