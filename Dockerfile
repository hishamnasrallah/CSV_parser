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

COPY . ./

RUN pip install poetry==1 && \
    poetry install --no-dev

COPY . ./

CMD poetry run alembic upgrade head && \
    poetry run uvicorn --host=0.0.0.0 app.main:app
