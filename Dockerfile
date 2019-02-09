FROM python:3.6-alpine

LABEL version="0.2.0"

RUN apk add --no-cache git
RUN pip install poetry==0.12.10

WORKDIR /yeyo
COPY ./pyproject.toml ./poetry.lock ./

RUN poetry config settings.virtualenvs.create false
RUN poetry install --no-dev

COPY ./ ./
RUN poetry install --no-dev \
        && find . -name "*.pyc" -delete \
        && find . -name "__pycache__" -delete

WORKDIR /project

ENTRYPOINT ["yeyo"]
