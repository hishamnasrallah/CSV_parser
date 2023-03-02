FROM python:3.9.10-slim

ENV PYTHONUNBUFFERED 1

EXPOSE 8000
WORKDIR /app

RUN apt-get update && apt-get -y install libpq-dev gcc && pip install psycopg2

RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY pyproject.toml ./
RUN pip install poetry==1.1 && \
    poetry config virtualenvs.in-project true && \
    poetry install

COPY . ./
COPY celery/celery_utils.py /app/celery_config

CMD poetry run alembic upgrade head && celery -A app.tasks.celery worker --loglevel=info && celery -A app.tasks.celery flower --port=5555 && poetry run uvicorn --host=0.0.0.0 app.main:app

