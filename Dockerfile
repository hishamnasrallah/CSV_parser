FROM python:3.9.10-slim
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
RUN pip install poetry
WORKDIR /app
COPY  pyproject.toml /app/
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY . /app
CMD CMD ["/usr/bin/supervisord"]
