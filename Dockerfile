FROM python:3.9.10-slim
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
RUN pip install poetry
WORKDIR /app
COPY  pyproject.toml /app/
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction
COPY . /app
CMD poetry run alembic upgrade head && \
#     poetry run uvicorn --host=0.0.0.0 app.main:app && \
    celery -A app.tasks.celery worker --loglevel=info
