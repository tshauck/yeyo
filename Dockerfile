FROM python:3.6-alpine

RUN apk add git
RUN pip install poetry

WORKDIR /yeyo
COPY ./pyproject.toml ./poetry.lock ./

RUN poetry config settings.virtualenvs.create false
RUN poetry install --no-dev

COPY ./ ./
RUN poetry install --no-dev

WORKDIR /project

ENTRYPOINT ["yeyo"]
