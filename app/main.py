import logging

from celery.result import ResultSet
from fastapi_utils.tasks import repeat_every

import uvicorn
from fastapi import FastAPI, Depends
from fastapi.openapi.utils import get_openapi
from starlette.middleware.cors import CORSMiddleware

from app.api.v1.models import ProcessConfig
from app.api.v1.routers import api_router
from app.tasks import add_tasks
from sqlalchemy.orm import Session
from app.api.v1.repositories.common import CRUD
from celery_config.celery_utils import create_celery

# from utils.time_difference import time_difference_in_minutes

logger = logging.getLogger(__name__)

app = FastAPI(title="Parser", docs_url="/parser/docs",
              openapi_url="/parser/openapi.json")

app.celery_app = create_celery()
celery = app.celery_app

# CORS
origins = []

# Set all CORS enabled origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
# app.add_event_handler('startup', sqs_event_listener)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Parser",
        version="1.0.0",
        description="The documentation for Parser service",
        routes=app.routes,
    )

    app.openapi_schema = openapi_schema
    return app.openapi_schema


# @celery.task(name='test')
# def test(file_name, file_path):
#     return f"{file_path}//////{file_name}"


# @celery.task(name='add')
# def add_tasks(file_path, file_name, frequency, company_id, last_run):
#
#     print(time.time())
#     print(frequency)
#     print(last_run)
#     time_diff_minutes = 0
#     if last_run:
#         time_diff_minutes = time_difference_in_minutes(last_run)
#         print(time_diff_minutes)
#     else:
#         print(frequency)
#
#     if time_diff_minutes > frequency or not last_run:
#         print("time_diff_minutes", time_diff_minutes)
#         print("frequency", frequency)
#     file_received_time = time.time()
#     # last_run
#
#
#     return f"FILE: '{file_name}' sent to celery"






@app.on_event("startup")
@repeat_every(seconds=5)
def init_tasks(db: Session = CRUD().db_conn()):

    tasks = db.query(ProcessConfig).all()
    for task in tasks:
        file_path = task.file_path
        file_name = task.file_name
        frequency = task.frequency.value
        company_id = task.company_id
        last_run = task.last_run
        file_id = task.id
        add_tasks.delay(file_id=file_id, file_path=file_path, file_name=file_name, frequency=frequency,
                        company_id=company_id, last_run=last_run)





app.openapi = custom_openapi

if __name__ == "__main__":
    uvicorn.run(app)

