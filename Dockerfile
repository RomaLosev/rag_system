FROM python:3.11

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install --upgrade pip \
    && pip install poetry --no-cache-dir

RUN poetry config virtualenvs.create false \
    && poetry install --no-root --without dev

COPY . .
