FROM python:3.7-alpine

RUN apk add --no-cache git=2.22.0-r0
RUN pip install poetry==0.12.17

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
