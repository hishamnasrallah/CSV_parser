FROM python:3.9.10-slim

ENV PYTHONUNBUFFERED 1

EXPOSE 8000
WORKDIR /app

RUN apt-get update && apt-get -y install libpq-dev gcc && \
    apt-get upgrade -y pip \
    && pip install --upgrade pip

RUN apt-get install python3-pip

RUN apt-get install python3-dev

RUN pip install psycopg2

RUN apt-get update && \
    apt-get -y install libpq-dev gcc && \
    apt-get install -y --no-install-recommends netcat && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY pyproject.toml ./
RUN pip install poetry==1 && \
    poetry install --no-dev

COPY . ./

CMD poetry run alembic upgrade head && \
FROM python:3.9.10-slim

ENV PYTHONUNBUFFERED 1

EXPOSE 8000
WORKDIR /app

RUN apt-get update && apt-get -y install libpq-dev gcc && \
    apt-get upgrade -y pip \
    && pip install --upgrade pip

RUN apt-get install python3-pip

RUN apt-get install python3-dev

RUN pip install psycopg2

RUN apt-get update && \
    apt-get -y install libpq-dev gcc && \
    apt-get install -y --no-install-recommends netcat && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY pyproject.toml ./
RUN pip install poetry==1 && \
    poetry install --no-dev

COPY . ./
COPY celery_config/celery_utils.py /app/celery_config

CMD poetry run alembic upgrade head &
CMD celery -A app.tasks.celery worker --loglevel=info &
CMD celery -A app.tasks.celery flower --port=5555 &
CMD poetry run uvicorn --host=0.0.0.0 app.main:app

