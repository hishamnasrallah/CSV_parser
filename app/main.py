import logging
from fastapi_utils.tasks import repeat_every
import uvicorn
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from starlette.middleware.cors import CORSMiddleware
from app.api.models import ProcessConfig
from app.api.repositories.common import CRUD
from app.api.v1.routers import api_router
from app.tasks import add_tasks
from sqlalchemy.orm import Session
from celery_config.celery_utils import create_celery

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


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Parser",
        version="1.0.0",
        description="The documentation of Parser service",
        routes=app.routes,
    )

    app.openapi_schema = openapi_schema
    return app.openapi_schema


@app.on_event("startup")
@repeat_every(seconds=5)
def init_tasks(db: Session = CRUD().db_conn()):
    """
    this function works every 5 seconds to check CSV files configuration model
    if there is any record need to be run using celery
    """
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
