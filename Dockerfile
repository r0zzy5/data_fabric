FROM python:3.12-alpine3.18 as base
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install -r requirements.txt

FROM base as dev
RUN apk add --no-cache git