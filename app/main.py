import logging

import uvicorn
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routers import api_router
from core.middlewares.catch_exception import ExceptionMiddleWare

logger = logging.getLogger(__name__)
logger.level = logging.INFO
logger.info("echoing something from the uicheckapp logger")

app = FastAPI(title="Parser", docs_url="/parser/docs",
              openapi_url="/parser/openapi.json")


# CORS
origins = ["*"]

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(ExceptionMiddleWare)
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


app.openapi = custom_openapi

if __name__ == "__main__":
    uvicorn.run(app)
