FROM python:3.6-alpine

RUN pip install poetry

WORKDIR /yeyo
COPY ./pyproject.toml ./poetry.lock ./

RUN poetry config settings.virtualenvs.create false
RUN poetry install

COPY ./ ./
RUN poetry install

WORKDIR /app

ENTRYPOINT ["yeyo"]