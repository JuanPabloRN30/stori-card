FROM python:3.11-slim

RUN apt-get update && apt-get install -y curl gcc libpq-dev && apt-get clean

RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/etc/poetry python3 -
ENV PATH="${PATH}:/etc/poetry/bin"

ENV PYTHONPATH="${PYTHONPATH}:/app"
WORKDIR /app
COPY poetry.lock pyproject.toml /app/
RUN poetry install

COPY ./src /app/
COPY ./migrations /app/migrations
COPY alembic.ini /app/alembic.ini
COPY ./tx_files /app/tx_files

ENTRYPOINT ["poetry", "run"]
