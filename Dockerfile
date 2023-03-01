FROM python:3-alpine as python_builder
RUN apk update && \
  apk add \
  build-base \
  curl \
  git \
  libffi-dev \
  openssh-client \
  postgresql-dev

# Install Poetry & ensure it is in $PATH
RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | POETRY_PREVIEW=1 python
ENV PATH "/root/.poetry/bin:/opt/venv/bin:${PATH}"

# Install any dependencies, this step will be cached so long as pyproject.toml is unchanged
# This could (should?) probably be changed to do a "pip install -r requirements.txt" in order
# to remain more cacheable, but it really depends on how long your dependencies take to install
COPY poetry.lock pyproject.toml /opt/project
RUN python -m venv /opt/venv && \
  source /opt/venv/bin/activate && \
  pip install -U pip && \
  cd /opt/project && \
  poetry install --no-dev --no-interaction

# Install the project itself (this is almost never cached)
COPY . /opt/project
RUN source /opt/venv/bin/activate && \
  cd /opt/project && \
  poetry install --no-dev --no-interaction

# Below this line is now creating the deployed container
# Anything installed above but not explicitly copied below is *not* available in the final container!
FROM python:3-alpine

# Any general deployed container setup that you want cached should go here

# Copy Project Virtual Environment from python_builder
COPY --from=python_builder /opt /opt

# Add the VirtualEnv to the beginning of $PATH
ENV PATH="/opt/venv/bin:$PATH"

CMD poetry run alembic upgrade head && \
    poetry run uvicorn --host=0.0.0.0 app.main:app
