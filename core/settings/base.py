import os
from dotenv import load_dotenv
from enum import Enum
from pydantic import BaseSettings
from sqlalchemy_utils import database_exists, create_database
from core.exceptions.database import DataBaseConnectionException

load_dotenv()


class AppEnvTypes(str, Enum):
    prod: str = "prod"
    dev: str = "dev"
    staging: str = "staging"
    local: str = "local"


class BaseAppSettings(BaseSettings):
    env: AppEnvTypes = os.environ.get('ENVIRONMENT', AppEnvTypes.local)

    db_engine: str = os.environ.get('DB_ENGINE')
    db_name: str = os.environ.get('DB_NAME')
    db_username: str = os.environ.get('DB_USERNAME')
    db_password: str = os.environ.get('DB_PASSWORD')
    db_host: str = os.environ.get('DB_HOST')
    db_port: str = os.environ.get('DB_PORT')

    @property
    def db_url(self):
        try:
            return self.db_engine + "://" + self.db_username + ":" + self.db_password + \
                "@" + self.db_host + ":" + self.db_port + "/" + self.db_name
        except:
            raise DataBaseConnectionException

    @property
    def celery_db_url(self):
        try:
            return "db+postgresql://" + self.db_username + ":" + self.db_password + \
                "@" + self.db_host + ":" + self.db_port + "/" + self.db_name
        except:
            raise DataBaseConnectionException

    @property
    def celery(self):
        return {
            "CELERY_BROKER_URL": os.environ.get('CELERY_BROKER_URL',
                                                "redis://127.0.0.1:6379/0"),
            "CELERY_RESULT_BACKEND": self.celery_db_url
        }


def validate_database():
    if not database_exists(settings.db_url):
        create_database(settings.db_url)


settings = BaseAppSettings()
